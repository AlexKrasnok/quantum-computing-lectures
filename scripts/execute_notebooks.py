# SPDX-License-Identifier: BSD-3-Clause
"""Execute notebooks transactionally and save only successful runs."""

from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path
import re

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
MACHINE_PATH = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+[\\/]+")


def figure_descriptions(notebook) -> dict[str, str]:
    """Read visible figure descriptions that follow generated-image code cells."""

    descriptions: dict[str, str] = {}
    for index, cell in enumerate(notebook.cells[:-1]):
        if cell.cell_type != "code" or not cell.get("id"):
            continue
        expected_id = f"figure-description-{cell.id}"
        following = notebook.cells[index + 1]
        if following.cell_type != "markdown" or following.get("id") != expected_id:
            continue
        description = following.source.strip().strip("*").strip()
        if description:
            descriptions[cell.id] = description
    return descriptions


def execute_one(path: Path, timeout: int) -> None:
    original = nbformat.read(path, as_version=4)
    candidate = copy.deepcopy(original)
    output_alt = figure_descriptions(original)

    for cell in candidate.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
        cell.metadata.pop("execution", None)

    candidate.metadata.pop("widgets", None)
    client = NotebookClient(
        candidate,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
        allow_errors=False,
        record_timing=False,
    )
    client.execute()
    for cell in candidate.cells:
        # Execution timestamps create noisy, machine-specific notebook diffs.
        cell.metadata.pop("execution", None)
        if cell.cell_type == "code":
            for output in cell.get("outputs", []):
                if output.get("output_type") == "stream":
                    output["text"] = MACHINE_PATH.sub("<user-path>/", output.get("text", ""))
                if "image/png" in output.get("data", {}) and cell.get("id") in output_alt:
                    output["metadata"] = {
                        "image/png": {"alt": output_alt[cell.id]}
                    }
    nbformat.validate(candidate)
    nbformat.write(candidate, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Notebook paths relative to the repository root")
    parser.add_argument("--timeout", type=int, default=300, help="Per-cell timeout in seconds")
    args = parser.parse_args()

    os.environ.setdefault("MPLBACKEND", "Agg")
    # The bundled kernelspec invokes ``python`` by name.  Put this script's
    # interpreter first so a non-activated Windows shell still uses .venv.
    os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
    failures = 0
    for item in args.paths:
        path = (ROOT / item).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            print(f"REFUSED outside repository: {path}", file=sys.stderr)
            failures += 1
            continue

        try:
            execute_one(path, args.timeout)
            print(f"PASS {path.relative_to(ROOT)}")
        except Exception as exc:  # report all notebook failures in one run
            failures += 1
            print(f"FAIL {path.relative_to(ROOT)}: {type(exc).__name__}: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
