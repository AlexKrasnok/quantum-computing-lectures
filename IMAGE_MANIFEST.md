# Notebook Image Archive

Every picture currently stored in a notebook has two copies:

1. the primary embedded copy inside the `.ipynb` file, as a Markdown attachment or saved code-cell output; and
2. a redundant standalone copy under `assets/figures/`.

This design keeps notebooks portable while making the image collection easy to inspect, back up, and restore. The machine-readable [`manifest.json`](assets/figures/manifest.json) maps each archived file to its notebook and stable cell ID and records its SHA-256 hash, byte size, MIME type, and dimensions.

The repository validator checks both directions: every embedded notebook image must have a manifest entry and matching archive file, and every manifest record must match the current notebook payload. An accidental deletion or changed image therefore causes validation to fail instead of silently removing a figure.

No technical mechanism can prevent a person with write access from deliberately deleting both copies and the validation rule. Preserve repository history or an external backup in addition to this redundancy.

## Inventory

| Notebook | Embedded attachments | Generated outputs | Archived MiB |
|---|---:|---:|---:|
| `appendices/python_primer.ipynb` | 1 | 4 | 0.08 |
| `assignments/03_homework.ipynb` | 3 | 0 | 0.02 |
| `lectures/00_why_quantum_engineering.ipynb` | 4 | 0 | 4.66 |
| `lectures/01_introduction_and_python.ipynb` | 1 | 7 | 0.28 |
| `lectures/02_linear_algebra.ipynb` | 3 | 2 | 0.15 |
| `lectures/03_complex_numbers_and_operators.ipynb` | 3 | 5 | 0.15 |
| `lectures/04_hilbert_space_and_quantum_mechanics.ipynb` | 7 | 0 | 1.72 |
| `lectures/05_quantum_dynamics_and_measurement.ipynb` | 5 | 0 | 0.31 |
| `lectures/06_density_matrices_and_entanglement.ipynb` | 2 | 0 | 0.02 |
| `lectures/07_bloch_sphere_and_quantum_gates.ipynb` | 17 | 22 | 1.51 |
| `lectures/08_quantum_circuits_with_qiskit.ipynb` | 1 | 22 | 0.30 |
| `lectures/09_teleportation_and_grover.ipynb` | 4 | 0 | 0.06 |
| `lectures/10_quantum_algorithms.ipynb` | 5 | 1 | 0.19 |
| `lectures/11_quantum_computer_architectures.ipynb` | 27 | 0 | 8.64 |
| `lectures/12_superconducting_qubits.ipynb` | 26 | 0 | 9.38 |
| `lectures/13_quantum_technology_roadmaps_and_ai.ipynb` | 2 | 0 | 1.71 |

**Total:** 174 archived notebook images representing 144 unique SHA-256 hashes.

## Restoring a figure

- If a Markdown attachment is removed, locate the record by notebook and `cell_id` in `manifest.json`, then reattach the corresponding archive file to that Markdown cell.
- If a generated output is cleared, rerun its code cell. The archived output remains available for comparison.
- Run `python scripts/validate_repository.py` after any notebook edit.

## Licensing

Archiving a figure does not change its copyright status. Original course figures follow [LICENSE](LICENSE); third-party figures remain subject to their source permissions and the requirements in [FIGURE_SOURCES.md](FIGURE_SOURCES.md).
