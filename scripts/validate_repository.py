# SPDX-License-Identifier: BSD-3-Clause
"""Validate notebook structure, links, execution state, and credentials."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_ROOTS = (ROOT / "lectures", ROOT / "assignments", ROOT / "appendices")

REQUIRED_FILES = (
    "README.md",
    "00_course_contents.md",
    "REFERENCES.md",
    "FIGURE_SOURCES.md",
    "SECURITY.md",
    "LICENSE",
    "CITATION.cff",
    "TEACHING_AND_SELF_STUDY.md",
    "IMAGE_MANIFEST.md",
    "assets/figures/manifest.json",
    "requirements.txt",
    ".gitignore",
    ".gitattributes",
)

EXPECTED_THEORY_REVIEWS = {
    "01_homework.ipynb": 12,
    "02_homework.ipynb": 12,
    "03_homework.ipynb": 15,
    "04_homework.ipynb": 12,
}

ASSIGNMENT_LECTURE_RANGES = {
    "01_homework.ipynb": (0, 3),
    "02_homework.ipynb": (3, 5),
    "03_homework.ipynb": (6, 8),
    "04_homework.ipynb": (8, 13),
}

DIRECT_LECTURE_DEPENDENCIES = (
    "qiskit",
    "qiskit-aer",
    "qiskit-ibm-runtime",
    "numpy",
    "scipy",
    "sympy",
    "matplotlib",
    "scienceplots",
    "qutip",
    "ipython",
)

LEGACY_CODE = {
    "removed IBMQ account API": re.compile(r"\bIBMQ\b"),
    "removed BasicAer API": re.compile(r"\bBasicAer\b"),
    "removed qiskit.execute API": re.compile(r"(?<![\w.])execute\s*\("),
    "obsolete IBMProvider": re.compile(r"\bIBMProvider\b|qiskit_ibm_provider"),
    "legacy conditional instruction": re.compile(r"\.c_if\s*\("),
    "legacy top-level Aer import": re.compile(
        r"from\s+qiskit\s+import[^\n]*(?:\bAer\b|\bexecute\b)"
    ),
    "legacy Aer.get_backend call": re.compile(r"\bAer\.get_backend\s*\("),
    "V1 Aer Sampler": re.compile(
        r"from\s+qiskit_aer\.primitives\s+import[^\n]*\bSampler\b"
    ),
    "wildcard Qiskit import": re.compile(r"from\s+qiskit(?:\.[\w.]+)?\s+import\s+\*"),
    "obsolete Qiskit 0.x install": re.compile(r"qiskit(?:-aer)?\s*==\s*0\."),
}

SECRET_PATTERNS = {
    "literal token or API key": re.compile(
        r"(?i)\b(?:token|api[_-]?key|access[_-]?key)\s*=\s*[\"'][^\"'\r\n]{20,}[\"']"
    ),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "long opaque credential-like string": re.compile(r"\b[A-Za-z0-9_-]{80,}\b"),
}

LOCAL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+", re.IGNORECASE),
    re.compile(r"/(?:home|Users)/[^/\s]+/"),
    re.compile(r"(?<![A-Za-z0-9+.-])[A-Za-z]:[\\/][A-Za-z0-9_. -]+[\\/]"),
    re.compile(r"\bfile:(?:/{2,3}|\\{2,3})", re.IGNORECASE),
    re.compile(r"(?:^|[\\/])(?:AppData|OneDrive|Dropbox)(?:[\\/])", re.IGNORECASE),
)

PROHIBITED_PROSE = {
    "automated-authorship disclosure": re.compile(
        r"(?i)\b(?:A[I]|artificial intelli" r"gence|Chat" r"GPT|large language mod" r"el)"
        r"[- ]?(?:generated|assisted|authored|written|revised)\b"
    ),
    "automated-authorship attribution": re.compile(
        r"(?i)\b(?:generated|assisted|authored|written|revised)\s+(?:by|with)\s+"
        r"(?:A[I]|artificial intelligence|ChatGPT|a large language model)\b"
    ),
    "editorial revision boilerplate": re.compile(
        r"(?i)\b(?:student edi" r"tion|publication place" r"holder|publication-ori" r"ented|"
        r"modernized pub" r"lic|original lecture con" r"tent (?:was )?(?:retained|preserved)|"
        r"at the author['’]s re" r"quest|as requested by the au" r"thor)\b"
    ),
    "internal revision metadata": re.compile(r"(?i)\bcourse[_]revision\b"),
    "template or editorial placeholder": re.compile(
        r"(?im)^\s*(?:[#>*-]+\s*)?(?:TODO|FIXME|placeholder text|lorem ipsum)\b"
    ),
    "editorial conversational residue": re.compile(
        r"(?i)\b(?:template" r"[- ]like|meta" r"[- ]response|revision no" r"te|"
        r"editorial no" r"te|in this revi" r"sion|this revised ver" r"sion)\b"
    ),
    "first-person automated-system disclaimer": re.compile(
        r"(?i)\bas an " r"A[I]\b"
    ),
    "embedded web frame": re.compile(r"(?i)<ifr" r"ame\b"),
    "embedded video URL": re.compile(r"(?i)youtube[.]com/embed/"),
    "placeholder video identifier": re.compile(r"(?i)your[_]video[_]id"),
}

MOJIBAKE = re.compile(
    r"(?:\u00c3[\u0080-\u00ff]|\u00e2(?:\u0080|\u20ac)|\ufffd)"
)

ATTACHMENT_LINK = re.compile(r"attachment:([^\s)>'\"]+)")
ATTACHMENT_IMAGE = re.compile(
    r"!\[([^\]]*)\]\(attachment:([^\s)>'\"]+)\)"
)
GENERIC_IMAGE_ALT = re.compile(r"(?i)^\s*(?:image(?:-\d+)?(?:[.]png)?|figure|plot)\s*$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_SOURCE = re.compile(r"\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
TEX_COMMAND = re.compile(
    r"\\(?:frac|tfrac|sqrt|langle|rangle|lvert|rvert|psi|phi|theta|rho|sigma|"
    r"sum|otimes|dagger|Delta|alpha|beta|gamma|lambda|mathcal|mathbf|boldsymbol|"
    r"mathrm|operatorname|begin|end)\b"
)
IMPORT_LINE = re.compile(
    r"(?m)^\s*(?:import\s+.+|from\s+\S+\s+import\s+.+)\s*$"
)


def is_remote_or_anchor(target: str) -> bool:
    return bool(
        not target
        or target.startswith("#")
        or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
    )


def normalized_local_target(raw: str) -> str | None:
    target = raw.strip().strip("<>")
    if not target or target.startswith("attachment:") or is_remote_or_anchor(target):
        return None
    # Markdown may append a quoted link title after a path without spaces.
    target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
    path_part = urlsplit(target).path
    return unquote(path_part) if path_part else None


def scan_secrets(text: str, label: str, errors: list[str]) -> None:
    for description, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            errors.append(f"{label}: possible {description}")


def scan_local_paths(text: str, label: str, errors: list[str]) -> None:
    if any(pattern.search(text) for pattern in LOCAL_PATH_PATTERNS):
        errors.append(f"{label}: contains a machine-specific user path")


def scan_prohibited_prose(text: str, label: str, errors: list[str]) -> None:
    for description, pattern in PROHIBITED_PROSE.items():
        if pattern.search(text):
            errors.append(f"{label}: contains {description}")


def scan_text_integrity(text: str, label: str, errors: list[str]) -> None:
    if any(ord(character) < 32 and character not in "\t\n\r" for character in text):
        errors.append(f"{label}: contains an unexpected control character")
    if MOJIBAKE.search(text):
        errors.append(f"{label}: contains likely character-encoding corruption")


def scan_markdown_structure(text: str, label: str, errors: list[str]) -> None:
    if text.count("```") % 2:
        errors.append(f"{label}: has an unclosed fenced code block")
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    strong_markers = re.findall(r"(?<!\*)\*\*(?!\*)", prose)
    if len(strong_markers) % 2:
        errors.append(f"{label}: has an unmatched strong-emphasis marker")
    display_count = len(re.findall(r"(?<!\\)\$\$", prose))
    if display_count % 2:
        errors.append(f"{label}: has an unmatched display-math delimiter")
    without_display = re.sub(r"(?<!\\)\$\$", "", prose)
    if len(re.findall(r"(?<!\\)\$", without_display)) % 2:
        errors.append(f"{label}: has an unmatched inline-math delimiter")
    if prose.count(r"\(") != prose.count(r"\)"):
        errors.append(f"{label}: has unmatched inline LaTeX delimiters")
    if prose.count(r"\[") != prose.count(r"\]"):
        errors.append(f"{label}: has unmatched display LaTeX delimiters")
    if any(delimiter in prose for delimiter in (r"\(", r"\)", r"\[", r"\]")):
        errors.append(
            f"{label}: uses escaped LaTeX delimiters that are not preserved "
            "reliably by notebook HTML/GitHub rendering; use $ or $$"
        )

    outside_math = re.sub(r"(?<!\\)\$\$.*?(?<!\\)\$\$", "", prose, flags=re.DOTALL)
    outside_math = re.sub(r"\\\[.*?\\\]", "", outside_math, flags=re.DOTALL)
    outside_math = re.sub(r"\\\(.*?\\\)", "", outside_math, flags=re.DOTALL)
    outside_math = re.sub(r"(?<!\\)\$(?:\\.|[^$\n])*?(?<!\\)\$", "", outside_math)
    if TEX_COMMAND.search(outside_math):
        errors.append(f"{label}: contains a TeX command outside math delimiters")

    for line in prose.splitlines():
        if not re.match(r"^\s*\|.*\|\s*$", line):
            continue
        for inline_math in re.findall(r"(?<!\\)\$([^$\n]+?)(?<!\\)\$", line):
            if "|" in inline_math:
                errors.append(
                    f"{label}: Markdown table contains a bare | inside inline math; "
                    "use \\lvert/\\rvert so the table renders correctly"
                )
                break


def check_local_link(raw: str, base: Path, label: str, errors: list[str]) -> None:
    target = normalized_local_target(raw)
    if target is None:
        return
    candidate = (base / target).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        errors.append(f"{label}: local link escapes repository: {raw}")
        return
    if not candidate.exists():
        errors.append(f"{label}: broken local link: {raw}")


def validate_notebook(
    path: Path, errors: list[str], warnings: list[str]
) -> tuple[int, int]:
    relative = path.relative_to(ROOT)
    try:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
    except Exception as exc:
        errors.append(f"{relative}: invalid notebook: {type(exc).__name__}: {exc}")
        return 0, 0

    attachments = 0
    generated_images = 0
    is_assignment = path.parent == ROOT / "assignments"

    notebook_metadata = json.dumps(notebook.get("metadata", {}), ensure_ascii=False)
    scan_secrets(notebook_metadata, f"{relative}:metadata", errors)
    scan_local_paths(notebook_metadata, f"{relative}:metadata", errors)
    scan_prohibited_prose(notebook_metadata, f"{relative}:metadata", errors)
    scan_text_integrity(notebook_metadata, f"{relative}:metadata", errors)
    unexpected_notebook_metadata = set(notebook.get("metadata", {})) - {
        "kernelspec",
        "language_info",
    }
    if unexpected_notebook_metadata:
        errors.append(
            f"{relative}: unexpected notebook metadata keys: "
            f"{sorted(unexpected_notebook_metadata)}"
        )

    if path.parent == ROOT / "lectures":
        opening = notebook.cells[0].get("source", "") if notebook.cells else ""
        for required in (
            "[Course contents](../00_course_contents.md)",
            "## Learning objectives",
            "## Core ideas",
        ):
            if required not in opening:
                errors.append(f"{relative}: opening cell is missing {required!r}")
        if not any(
            re.search(r"(?m)^## Key takeaways\s*$", cell.get("source", ""))
            for cell in notebook.cells
            if cell.cell_type == "markdown"
        ):
            errors.append(f"{relative}: missing a Key takeaways section")
        level_one_headings = [
            (index, line)
            for index, cell in enumerate(notebook.cells)
            if cell.cell_type == "markdown"
            for line in re.sub(
                r"```.*?```", "", cell.get("source", ""), flags=re.DOTALL
            ).splitlines()
            if re.match(r"^#\s+", line)
        ]
        if len(level_one_headings) != 1 or level_one_headings[0][0] != 0:
            errors.append(
                f"{relative}: expected one level-one lecture title, found "
                f"{level_one_headings}"
            )
        code_indices = [
            index
            for index, cell in enumerate(notebook.cells)
            if cell.cell_type == "code"
        ]
        if code_indices:
            if len(notebook.cells) < 3 or notebook.cells[1].cell_type != "markdown":
                errors.append(
                    f"{relative}: code-bearing lecture lacks an early software section"
                )
            else:
                environment = notebook.cells[1].get("source", "")
                for required in (
                    "## Software environment",
                    "[`requirements.txt`](../requirements.txt)",
                    "%pip install -r ../requirements.txt",
                ):
                    if required not in environment:
                        errors.append(
                            f"{relative}: software section is missing {required!r}"
                        )
            first_code = code_indices[0]
            if (
                first_code != 2
                or notebook.cells[first_code].get("id") != "complete-imports"
                or not IMPORT_LINE.search(notebook.cells[first_code].get("source", ""))
            ):
                errors.append(
                    f"{relative}: first code cell must be the complete import block"
                )
            for index in code_indices[1:]:
                if IMPORT_LINE.search(notebook.cells[index].get("source", "")):
                    errors.append(
                        f"{relative}:cell {index}: library import appears after the "
                        "complete import block"
                    )

    if is_assignment:
        opening = notebook.cells[0].get("source", "") if notebook.cells else ""
        if "## Theory navigation" not in opening:
            errors.append(f"{relative}: opening cell is missing the theory-review guide")
        review_cells = [
            (index, cell.get("source", ""))
            for index, cell in enumerate(notebook.cells)
            if cell.cell_type == "markdown"
            and "> **Theory review:**" in cell.get("source", "")
        ]
        expected_reviews = EXPECTED_THEORY_REVIEWS.get(path.name)
        if expected_reviews is None:
            errors.append(f"{relative}: no expected theory-review count is defined")
        elif len(review_cells) != expected_reviews:
            errors.append(
                f"{relative}: expected {expected_reviews} problem theory reviews, "
                f"found {len(review_cells)}"
            )
        for index, source in review_cells:
            if source.count("> **Theory review:**") != 1:
                errors.append(
                    f"{relative}:cell {index}: expected exactly one theory-review block"
                )
            if "../lectures/" not in source:
                errors.append(
                    f"{relative}:cell {index}: theory review does not link to a lecture"
                )
            lecture_numbers = [
                int(number)
                for number in re.findall(r"\.\./lectures/(\d{2})_", source)
            ]
            allowed = ASSIGNMENT_LECTURE_RANGES.get(path.name)
            if not lecture_numbers:
                errors.append(
                    f"{relative}:cell {index}: theory review has no numbered lecture"
                )
            elif allowed and any(
                number < allowed[0] or number > allowed[1]
                for number in lecture_numbers
            ):
                errors.append(
                    f"{relative}:cell {index}: lecture references {lecture_numbers} "
                    f"fall outside the allowed range {allowed[0]}–{allowed[1]}"
                )

    duplicate_sources: dict[tuple[str, str], list[int]] = {}
    for index, cell in enumerate(notebook.cells):
        normalized = " ".join(cell.get("source", "").split())
        if len(normalized) >= 120:
            duplicate_sources.setdefault((cell.cell_type, normalized), []).append(index)
    for indices in duplicate_sources.values():
        if len(indices) > 1:
            errors.append(f"{relative}: duplicate cells at indices {indices}")

    if path.parent == ROOT / "lectures" and not any(
        re.search(r"(?im)^#{1,3}\s+(?:references|primary references)\b", cell.get("source", ""))
        for cell in notebook.cells
        if cell.cell_type == "markdown"
    ):
        errors.append(f"{relative}: missing a lecture reference section")

    if not notebook.cells or "**Open course material.**" not in notebook.cells[0].get(
        "source", ""
    ):
        errors.append(f"{relative}: opening cell is missing the reuse notice")

    for index, cell in enumerate(notebook.cells):
        label = f"{relative}:cell {index}"
        source = cell.get("source", "")
        scan_secrets(source, label, errors)
        scan_local_paths(source, label, errors)
        scan_prohibited_prose(source, label, errors)
        scan_text_integrity(source, label, errors)

        cell_metadata = json.dumps(cell.get("metadata", {}), ensure_ascii=False)
        scan_secrets(cell_metadata, f"{label}:metadata", errors)
        scan_local_paths(cell_metadata, f"{label}:metadata", errors)
        scan_prohibited_prose(cell_metadata, f"{label}:metadata", errors)
        scan_text_integrity(cell_metadata, f"{label}:metadata", errors)
        if cell.get("metadata"):
            errors.append(f"{label}: contains stale cell metadata or annotations")

        if cell.cell_type == "code":
            for description, pattern in LEGACY_CODE.items():
                if pattern.search(source):
                    errors.append(f"{label}: {description}")

            outputs = cell.get("outputs", [])
            if is_assignment and (cell.get("execution_count") is not None or outputs):
                errors.append(f"{label}: student assignment code/output was not cleared")
            if not is_assignment and source.strip() and cell.get("execution_count") is None:
                errors.append(f"{label}: instructional code cell has not been executed")

            for output in outputs:
                if output.get("output_type") == "error":
                    errors.append(
                        f"{label}: saved {output.get('ename', 'execution')} error output"
                    )
                data = output.get("data", {})
                generated_images += sum(
                    mime in data for mime in ("image/png", "image/jpeg", "image/svg+xml")
                )
                if "image/png" in data:
                    alt = (
                        output.get("metadata", {})
                        .get("image/png", {})
                        .get("alt", "")
                        .strip()
                    )
                    if not alt:
                        errors.append(f"{label}: generated PNG output has no alt text")
                output_metadata = output.get("metadata", {})
                if output_metadata:
                    allowed_output_metadata = (
                        set(output_metadata) == {"image/png"}
                        and set(output_metadata["image/png"]) == {"alt"}
                    )
                    if not allowed_output_metadata:
                        errors.append(
                            f"{label}: output contains metadata other than image alt text"
                        )
                safe_output = dict(output)
                safe_output["data"] = {
                    mime: value
                    for mime, value in data.items()
                    if not mime.startswith("image/")
                }
                rendered = json.dumps(safe_output, ensure_ascii=False)
                scan_secrets(rendered, f"{label}:output", errors)
                scan_local_paths(rendered, f"{label}:output", errors)
                scan_prohibited_prose(rendered, f"{label}:output", errors)
                scan_text_integrity(rendered, f"{label}:output", errors)

        if cell.cell_type == "markdown":
            scan_markdown_structure(source, label, errors)
            cell_attachments = cell.get("attachments", {})
            attachments += len(cell_attachments)
            referenced = {
                unquote(match.group(1)) for match in ATTACHMENT_LINK.finditer(source)
            }
            for name in referenced:
                if name not in cell_attachments:
                    errors.append(f"{label}: missing embedded attachment {name!r}")
            for name in cell_attachments:
                if name not in referenced:
                    warnings.append(f"{label}: unreferenced embedded attachment {name!r}")
            for match in ATTACHMENT_IMAGE.finditer(source):
                alt = match.group(1).strip()
                if not alt or GENERIC_IMAGE_ALT.fullmatch(alt):
                    errors.append(
                        f"{label}: embedded figure has missing or generic alt text"
                    )

            for match in MARKDOWN_LINK.finditer(source):
                check_local_link(match.group(1), path.parent, label, errors)
            for match in HTML_SOURCE.finditer(source):
                check_local_link(match.group(1), path.parent, label, errors)

    if path.parent in {ROOT / "lectures", ROOT / "appendices"}:
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code" or not any(
                "image/png" in output.get("data", {})
                for output in cell.get("outputs", [])
            ):
                continue
            expected = f"figure-description-{cell.get('id', '')}"
            if index + 1 >= len(notebook.cells) or notebook.cells[index + 1].get(
                "id"
            ) != expected:
                errors.append(
                    f"{relative}:cell {index}: generated figure is not followed by "
                    "its visible description"
                )

    return attachments, generated_images


def validate_plain_files(errors: list[str]) -> None:
    text_suffixes = {".md", ".py", ".ps1", ".txt", ".yml", ".yaml", ".cff"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".venv" in path.parts or ".git" in path.parts:
            continue
        if path.suffix not in text_suffixes and path.name != "LICENSE":
            continue
        text = path.read_text(encoding="utf-8")
        label = str(path.relative_to(ROOT))
        scan_secrets(text, label, errors)
        scan_local_paths(text, label, errors)
        scan_prohibited_prose(text, label, errors)
        scan_text_integrity(text, label, errors)
        if path.suffix == ".md":
            for match in MARKDOWN_LINK.finditer(text):
                check_local_link(match.group(1), path.parent, label, errors)


def decode_image_payload(mime_type: str, payload: str) -> bytes:
    if mime_type == "image/svg+xml":
        return payload.encode("utf-8")
    return base64.b64decode(payload)


def embedded_image_payloads(notebooks: list[Path]) -> dict[tuple, bytes]:
    payloads: dict[tuple, bytes] = {}
    image_mimes = ("image/png", "image/jpeg", "image/svg+xml")
    for path in notebooks:
        relative = path.relative_to(ROOT).as_posix()
        notebook = nbformat.read(path, as_version=4)
        for cell_index, cell in enumerate(notebook.cells):
            cell_id = cell.get("id", f"cell-{cell_index}")
            for attachment_name, variants in cell.get("attachments", {}).items():
                for mime_type, payload in variants.items():
                    if mime_type not in image_mimes:
                        continue
                    key = (
                        relative,
                        cell_id,
                        "attachment",
                        attachment_name,
                        None,
                        mime_type,
                    )
                    payloads[key] = decode_image_payload(mime_type, payload)
            if cell.cell_type != "code":
                continue
            image_number = 0
            for output in cell.get("outputs", []):
                for mime_type in image_mimes:
                    if mime_type not in output.get("data", {}):
                        continue
                    key = (
                        relative,
                        cell_id,
                        "generated-output",
                        "saved code-cell output",
                        image_number,
                        mime_type,
                    )
                    payloads[key] = decode_image_payload(
                        mime_type, output["data"][mime_type]
                    )
                    image_number += 1
    return payloads


def validate_image_archive(
    notebooks: list[Path],
    errors: list[str],
    *,
    allow_regenerated_images: bool = False,
) -> None:
    manifest_path = ROOT / "assets" / "figures" / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"assets/figures/manifest.json: invalid JSON: {exc}")
        return
    if manifest.get("schema_version") != 1:
        errors.append("assets/figures/manifest.json: unsupported schema version")
    records = manifest.get("records")
    if not isinstance(records, list):
        errors.append("assets/figures/manifest.json: records must be a list")
        return

    embedded = embedded_image_payloads(notebooks)
    manifest_keys: set[tuple] = set()
    tracked_archive_paths: set[Path] = set()
    for index, record in enumerate(records):
        label = f"assets/figures/manifest.json:record {index}"
        try:
            key = (
                record["notebook"],
                record["cell_id"],
                record["kind"],
                record["source_name"],
                record.get("source_index"),
                record["mime_type"],
            )
            archive_path = (ROOT / record["archive_path"]).resolve()
            archive_path.relative_to(ROOT / "assets" / "figures")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{label}: malformed record: {exc}")
            continue
        if key in manifest_keys:
            errors.append(f"{label}: duplicate image-source record")
        manifest_keys.add(key)
        tracked_archive_paths.add(archive_path)
        if not archive_path.exists():
            errors.append(f"{label}: missing archive file {record['archive_path']}")
            continue
        archive_bytes = archive_path.read_bytes()
        archive_hash = hashlib.sha256(archive_bytes).hexdigest()
        if archive_hash != record.get("sha256"):
            errors.append(f"{label}: archive SHA-256 does not match manifest")
        if len(archive_bytes) != record.get("bytes"):
            errors.append(f"{label}: archive byte count does not match manifest")
        embedded_bytes = embedded.get(key)
        if embedded_bytes is None:
            errors.append(f"{label}: source image is missing from its notebook cell")
        elif (
            record["kind"] != "generated-output" or not allow_regenerated_images
        ) and hashlib.sha256(embedded_bytes).hexdigest() != record.get("sha256"):
            errors.append(f"{label}: notebook image differs from archived copy")

    missing_records = set(embedded) - manifest_keys
    for key in sorted(missing_records, key=str):
        errors.append(
            "assets/figures/manifest.json: embedded notebook image has no archive "
            f"record: {key}"
        )
    extra_records = manifest_keys - set(embedded)
    if extra_records:
        # Individual records have already received a source-missing error above.
        pass
    if manifest.get("image_count") != len(records):
        errors.append("assets/figures/manifest.json: image_count is inconsistent")
    expected_unique = len({record.get("sha256") for record in records})
    if manifest.get("unique_sha256_count") != expected_unique:
        errors.append(
            "assets/figures/manifest.json: unique_sha256_count is inconsistent"
        )

    archive_image_paths = {
        path.resolve()
        for path in (ROOT / "assets" / "figures").rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    for path in sorted(archive_image_paths - tracked_archive_paths):
        errors.append(
            "assets/figures: untracked archive image: "
            f"{path.relative_to(ROOT)}"
        )

    for index, record in enumerate(manifest.get("additional_assets", [])):
        label = f"assets/figures/manifest.json:additional asset {index}"
        try:
            path = (ROOT / record["path"]).resolve()
            path.relative_to(ROOT)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{label}: malformed record: {exc}")
            continue
        if not path.exists():
            errors.append(f"{label}: missing file {record.get('path')}")
            continue
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record.get("sha256"):
            errors.append(f"{label}: SHA-256 does not match manifest")
        if len(raw) != record.get("bytes"):
            errors.append(f"{label}: byte count does not match manifest")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-regenerated-images",
        action="store_true",
        help=(
            "allow successfully regenerated code-cell images to differ from the "
            "archived PNG bytes; attachment and archive hashes remain strict"
        ),
    )
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    for item in REQUIRED_FILES:
        if not (ROOT / item).exists():
            errors.append(f"missing required repository file: {item}")

    license_path = ROOT / "LICENSE"
    if license_path.exists():
        license_text = license_path.read_text(encoding="utf-8")
        for identifier in ("CC-BY-4.0", "BSD-3-Clause"):
            if identifier not in license_text:
                errors.append(f"LICENSE: missing {identifier} reuse terms")

    requirements_path = ROOT / "requirements.txt"
    if requirements_path.exists():
        requirements_text = requirements_path.read_text(encoding="utf-8").lower()
        for package in DIRECT_LECTURE_DEPENDENCIES:
            pattern = rf"(?m)^\s*{re.escape(package)}(?:\[[^\]]+\])?\s*=="
            if not re.search(pattern, requirements_text):
                errors.append(
                    f"requirements.txt: direct lecture dependency {package!r} "
                    "is not explicitly pinned"
                )

    for path in ROOT.iterdir():
        if path.is_file() and (
            path.name.lower().startswith(".codex")
            or path.suffix.lower() in {".bak", ".tmp"}
        ):
            errors.append(f"temporary root artifact must be removed: {path.name}")

    notebooks = sorted(
        path for base in NOTEBOOK_ROOTS for path in base.glob("*.ipynb")
    )
    if len(list((ROOT / "lectures").glob("*.ipynb"))) != 14:
        errors.append("lectures/: expected exactly 14 course lecture notebooks")
    if len(list((ROOT / "assignments").glob("*.ipynb"))) != 4:
        errors.append("assignments/: expected exactly 4 student notebooks")
    assignment_names = {
        path.name for path in (ROOT / "assignments").glob("*.ipynb")
    }
    if assignment_names != set(EXPECTED_THEORY_REVIEWS):
        errors.append(
            "assignments/: expected sequential files "
            f"{sorted(EXPECTED_THEORY_REVIEWS)}, found {sorted(assignment_names)}"
        )

    total_attachments = 0
    total_images = 0
    for path in notebooks:
        attachments, images = validate_notebook(path, errors, warnings)
        total_attachments += attachments
        total_images += images

    validate_plain_files(errors)
    validate_image_archive(
        notebooks,
        errors,
        allow_regenerated_images=args.allow_regenerated_images,
    )

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(
            f"FAILED: {len(errors)} issue(s), {len(warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1

    print(
        "PASS: "
        f"{len(notebooks)} notebooks; {total_attachments} embedded attachments; "
        f"{total_images} generated image outputs; {len(warnings)} warning(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
