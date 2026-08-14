# SPDX-License-Identifier: BSD-3-Clause
"""Export redundant copies of every image embedded in the course notebooks."""

from __future__ import annotations

import base64
import argparse
import hashlib
import io
import json
import re
import shutil
import uuid
from collections import Counter, defaultdict
from pathlib import Path

import nbformat
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "assets" / "figures"
MANIFEST_JSON = ARCHIVE / "manifest.json"
MANIFEST_MD = ROOT / "IMAGE_MANIFEST.md"
NOTEBOOK_DIRS = (ROOT / "lectures", ROOT / "assignments", ROOT / "appendices")
MIME_EXTENSION = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/svg+xml": ".svg",
}


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned or "image"


def decode_payload(mime: str, payload: str) -> bytes:
    if mime == "image/svg+xml":
        return payload.encode("utf-8")
    return base64.b64decode(payload)


def dimensions(mime: str, raw: bytes) -> tuple[int | None, int | None]:
    if mime == "image/svg+xml":
        return None, None
    with Image.open(io.BytesIO(raw)) as image:
        image.verify()
    with Image.open(io.BytesIO(raw)) as image:
        return image.size


def store_record(
    records: list[dict],
    *,
    notebook_path: Path,
    cell_index: int,
    cell_id: str,
    kind: str,
    source_name: str,
    source_index: int | None,
    mime: str,
    payload: str,
) -> None:
    raw = decode_payload(mime, payload)
    width, height = dimensions(mime, raw)
    notebook_key = f"{notebook_path.parent.name}__{notebook_path.stem}"
    subdirectory = "attachments" if kind == "attachment" else "generated"
    suffix = MIME_EXTENSION[mime]
    if kind == "attachment":
        filename = (
            f"cell-{cell_index:03d}_{safe_name(cell_id)}_"
            f"attachment_{safe_name(source_name)}"
        )
        if not filename.lower().endswith(suffix):
            filename += suffix
    else:
        filename = (
            f"cell-{cell_index:03d}_{safe_name(cell_id)}_"
            f"output-{source_index:02d}{suffix}"
        )
    archive_path = ARCHIVE / notebook_key / subdirectory / filename
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        raise RuntimeError(f"archive collision: {archive_path.relative_to(ROOT)}")
    archive_path.write_bytes(raw)
    records.append(
        {
            "archive_path": archive_path.relative_to(ROOT).as_posix(),
            "notebook": notebook_path.relative_to(ROOT).as_posix(),
            "cell_id": cell_id,
            "cell_index": cell_index,
            "kind": kind,
            "source_name": source_name,
            "source_index": source_index,
            "mime_type": mime,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "width": width,
            "height": height,
        }
    )


def build_manifest(records: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "description": (
            "Redundant archive of every image payload embedded in the distributed "
            "notebooks. Notebook attachments and outputs remain the primary copies."
        ),
        "image_count": len(records),
        "unique_sha256_count": len({record["sha256"] for record in records}),
        "records": records,
        "additional_assets": [],
    }


def build_markdown(manifest: dict) -> str:
    by_notebook: dict[str, Counter] = defaultdict(Counter)
    for record in manifest["records"]:
        by_notebook[record["notebook"]][record["kind"]] += 1
        by_notebook[record["notebook"]]["bytes"] += record["bytes"]
    rows = []
    for notebook, counts in sorted(by_notebook.items()):
        rows.append(
            f"| `{notebook}` | {counts['attachment']} | {counts['generated-output']} "
            f"| {(counts['bytes'] / 1024 / 1024):.2f} |"
        )
    return f"""# Notebook Image Archive

Every picture currently stored in a notebook has two copies:

1. the primary embedded copy inside the `.ipynb` file, as a Markdown attachment or saved code-cell output; and
2. a redundant standalone copy under `assets/figures/`.

This design keeps notebooks portable while making the image collection easy to inspect, back up, and restore. The machine-readable [`manifest.json`](assets/figures/manifest.json) maps each archived file to its notebook and stable cell ID and records its SHA-256 hash, byte size, MIME type, and dimensions.

The repository validator checks both directions: every embedded notebook image must have a manifest entry and matching archive file, and every manifest record must match the current notebook payload. An accidental deletion or changed image therefore causes validation to fail instead of silently removing a figure.

No technical mechanism can prevent a person with write access from deliberately deleting both copies and the validation rule. Preserve repository history or an external backup in addition to this redundancy.

## Inventory

| Notebook | Embedded attachments | Generated outputs | Archived MiB |
|---|---:|---:|---:|
{chr(10).join(rows)}

**Total:** {manifest['image_count']} archived notebook images representing {manifest['unique_sha256_count']} unique SHA-256 hashes.

## Restoring a figure

- If a Markdown attachment is removed, locate the record by notebook and `cell_id` in `manifest.json`, then reattach the corresponding archive file to that Markdown cell.
- If a generated output is cleared, rerun its code cell. The archived output remains available for comparison.
- Run `python scripts/validate_repository.py` after any notebook edit.

## Licensing

Archiving a figure does not change its copyright status. Original course figures follow [LICENSE](LICENSE); third-party figures remain subject to their source permissions and the requirements in [FIGURE_SOURCES.md](FIGURE_SOURCES.md).
"""


def write_archive() -> dict:
    paths = sorted(path for directory in NOTEBOOK_DIRS for path in directory.glob("*.ipynb"))
    records: list[dict] = []
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        for cell_index, cell in enumerate(notebook.cells):
            cell_id = cell.get("id", f"cell-{cell_index}")
            for attachment_name, variants in cell.get("attachments", {}).items():
                for mime, payload in sorted(variants.items()):
                    if mime not in MIME_EXTENSION:
                        raise RuntimeError(f"unsupported attachment MIME type: {mime}")
                    store_record(
                        records,
                        notebook_path=path,
                        cell_index=cell_index,
                        cell_id=cell_id,
                        kind="attachment",
                        source_name=attachment_name,
                        source_index=None,
                        mime=mime,
                        payload=payload,
                    )
            if cell.cell_type == "code":
                image_number = 0
                for output in cell.get("outputs", []):
                    for mime in MIME_EXTENSION:
                        if mime not in output.get("data", {}):
                            continue
                        store_record(
                            records,
                            notebook_path=path,
                            cell_index=cell_index,
                            cell_id=cell_id,
                            kind="generated-output",
                            source_name="saved code-cell output",
                            source_index=image_number,
                            mime=mime,
                            payload=output["data"][mime],
                        )
                        image_number += 1
    manifest = build_manifest(records)
    MANIFEST_JSON.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    MANIFEST_MD.write_text(build_markdown(manifest), encoding="utf-8")
    print(
        f"ARCHIVED {manifest['image_count']} images "
        f"({manifest['unique_sha256_count']} unique hashes)"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replace",
        action="store_true",
        help="transactionally replace an existing redundant image archive",
    )
    args = parser.parse_args()
    if not ARCHIVE.exists():
        write_archive()
        return
    if not args.replace:
        raise RuntimeError(f"archive already exists: {ARCHIVE}")

    resolved = ARCHIVE.resolve()
    if resolved != (ROOT / "assets" / "figures").resolve():
        raise RuntimeError(f"refusing unexpected archive target: {resolved}")
    backup = ARCHIVE.with_name(f"figures-backup-{uuid.uuid4().hex}")
    old_markdown = MANIFEST_MD.read_bytes() if MANIFEST_MD.exists() else None
    ARCHIVE.rename(backup)
    try:
        write_archive()
    except Exception:
        if ARCHIVE.exists():
            shutil.rmtree(ARCHIVE)
        backup.rename(ARCHIVE)
        if old_markdown is not None:
            MANIFEST_MD.write_bytes(old_markdown)
        raise
    shutil.rmtree(backup)


if __name__ == "__main__":
    main()
