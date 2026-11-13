# Figure Sources and Permissions

Notebook plots and circuit drawings produced by executable cells can be regenerated from their code. Embedded photographs, screenshots, book figures, article figures, and third-party diagrams require a source citation and redistribution permission.

## Licensing boundary

- Original instructor-created educational figures are licensed under CC BY 4.0 together with the lecture text.
- Code-generated figures inherit the reuse status of their repository code and original course content: the code is BSD-3-Clause, and the rendered original educational output may be reused under CC BY 4.0.
- Third-party figures are not relicensed by this repository. Their original license or written permission controls reuse.
- When adapting a figure, credit its creator, link to the applicable license, and identify the modification. Do not assume that citing a paper grants image-republication rights.

## Inventory

| Material | Embedded figures | Code-generated figures | Main provenance concern |
|---|---:|---:|---|
| Python primer | 1 | 4 | Mechanics diagram |
| Homework notebooks | 5 | 0 | Circuit diagrams |
| Lecture 0 | 4 | 0 | Original Chapter 1 figures supplied by A. Krasnok |
| Lectures 1–4 | 14 | 14 | Mathematical and conceptual diagrams |
| Lectures 5–8 | 25 | 44 | Measurement, Bloch-sphere, gate, and Qiskit illustrations |
| Lectures 9–10 | 9 | 1 | Protocol and algorithm diagrams |
| Lectures 11–12 | 53 | 0 | Experimental photographs, device schematics, and article figures |
| Supplementary lecture | 2 | 0 | Original roadmap and AI-workflow figures supplied by A. Krasnok |

## Portable image archive

Every one of the 111 embedded attachments and 63 saved generated outputs has a standalone backup PNG copy under `assets/figures/`. The [Notebook Image Archive](IMAGE_MANIFEST.md) summarizes the collection, while [`manifest.json`](assets/figures/manifest.json) records the source notebook, stable cell ID, filename, dimensions, byte count, and SHA-256 hash for every copy.

The four Lecture 0 diagrams (semiconductor scaling, Bloch-sphere coordinates, the maze analogy for search and interference, and the Hadamard–$R_z$–Hadamard interferometer) were supplied with Chapter 1 of A. Krasnok's book manuscript. They are treated as original instructor-created educational figures under the repository's CC BY 4.0 terms.

The two diagrams of the supplementary lecture, one showing the three roles that connect AI and quantum computing and one showing the closed verification loop, were supplied with the corresponding book appendices. They are treated as original instructor-created educational figures under the same CC BY 4.0 terms.

`python scripts/validate_repository.py` checks that each image stored in a notebook agrees with its archive copy and its manifest hash. This detects an accidentally cleared output, removed attachment, damaged archive file, or missing record. Repository history or an external backup is still required to protect against deliberate deletion of every copy and the validation rule itself.

For every third-party figure retained in a public distribution, record the creator, title, original source or DOI, license or written permission, required attribution, and any modifications. A citation identifies a source but does not by itself grant redistribution rights.

When permission is unclear, link to the source or replace the image with an original diagram or code-generated visualization.

The repository's general reuse terms are in [LICENSE](LICENSE). The inventory above does not yet record provenance item by item, so no retained third-party image should be described as openly licensed until its own source and license are recorded.
