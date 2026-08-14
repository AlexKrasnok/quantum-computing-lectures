# SPDX-License-Identifier: BSD-3-Clause
"""Check external course links, DOI records, and YouTube video availability."""

from __future__ import annotations

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse, urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
URL = re.compile(r"https?://[^\s<>\"']+")
USER_AGENT = "Mozilla/5.0 (compatible; course-link-check/1.0)"
TIMEOUT_SECONDS = 25


def trim_url(raw: str) -> str:
    value = raw.rstrip(".,;:!?'\"*")
    while value.endswith(")") and value.count("(") < value.count(")"):
        value = value[:-1]
    return value.rstrip(".,;:!?'\"*")


def source_texts(path: Path) -> list[str]:
    if path.suffix == ".ipynb":
        notebook = json.loads(path.read_text(encoding="utf-8"))
        return [
            "".join(cell.get("source", []))
            for cell in notebook.get("cells", [])
        ]
    return [path.read_text(encoding="utf-8")]


def collect_links() -> dict[str, list[str]]:
    locations: dict[str, list[str]] = {}
    paths = [*ROOT.rglob("*.md"), *ROOT.rglob("*.ipynb")]
    for path in sorted(paths):
        if any(part in {".git", ".venv", "_rendered"} for part in path.parts):
            continue
        relative = str(path.relative_to(ROOT))
        for text in source_texts(path):
            for match in URL.finditer(text):
                url = trim_url(match.group(0))
                locations.setdefault(url, []).append(relative)
    return locations


def youtube_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host == "youtu.be":
        return parsed.path.strip("/").split("/", 1)[0] or None
    if host not in {"youtube.com", "m.youtube.com"}:
        return None
    if parsed.path == "/watch":
        return parse_qs(parsed.query).get("v", [None])[0]
    pieces = parsed.path.strip("/").split("/")
    if len(pieces) >= 2 and pieces[0] in {"embed", "shorts", "live"}:
        return pieces[1]
    return None


def get_json(url: str) -> dict:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)


def check_youtube(url: str, video_id: str) -> tuple[str, str]:
    watch_url = f"https://www.youtube.com/watch?{urlencode({'v': video_id})}"
    endpoint = "https://www.youtube.com/oembed?" + urlencode(
        {"url": watch_url, "format": "json"}
    )
    payload = get_json(endpoint)
    title = str(payload.get("title", "available video")).strip()
    return "OK", f"YouTube: {title}"


def check_doi(url: str) -> tuple[str, str]:
    doi = unquote(urlsplit(url).path.lstrip("/"))
    endpoint = "https://doi.org/api/handles/" + quote(doi, safe="/")
    payload = get_json(endpoint)
    if payload.get("responseCode") == 1 and payload.get("values"):
        return "OK", f"DOI record: {doi}"
    return "BROKEN", f"DOI did not resolve: {doi}"


def check_http(url: str) -> tuple[str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
            "Range": "bytes=0-4095",
        },
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            final_url = response.geturl()
        if status < 400:
            note = f"HTTP {status}"
            if final_url != url:
                note += f" -> {final_url}"
            return "OK", note
        return "BROKEN", f"HTTP {status}"
    except HTTPError as exc:
        if exc.code in {401, 403, 429}:
            return "RESTRICTED", f"HTTP {exc.code}; server blocks automated checks"
        return "BROKEN", f"HTTP {exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        return "BROKEN", f"{type(exc).__name__}: {exc}"


def check(url: str) -> tuple[str, str, str]:
    state = "BROKEN"
    detail = "link check did not run"
    for attempt in range(2):
        try:
            video_id = youtube_id(url)
            if video_id:
                state, detail = check_youtube(url, video_id)
            elif urlparse(url).netloc.lower() in {"doi.org", "dx.doi.org"}:
                state, detail = check_doi(url)
            else:
                state, detail = check_http(url)
            break
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            detail = f"{type(exc).__name__}: {exc}"
            if attempt == 0:
                time.sleep(1)
    return state, url, detail


def main() -> int:
    links = collect_links()
    results: list[tuple[str, str, str]] = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(check, url): url for url in links}
        for future in as_completed(futures):
            results.append(future.result())

    rank = {"BROKEN": 0, "RESTRICTED": 1, "OK": 2}
    results.sort(key=lambda item: (rank[item[0]], item[1]))
    for state, url, detail in results:
        if state != "OK":
            where = ", ".join(sorted(set(links[url])))
            print(f"{state}: {url}\n  {detail}\n  {where}")

    counts = {state: sum(item[0] == state for item in results) for state in rank}
    print(
        f"Checked {len(results)} unique links: {counts['OK']} available, "
        f"{counts['RESTRICTED']} restricted to automated requests, "
        f"{counts['BROKEN']} broken."
    )
    return 1 if counts["BROKEN"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
