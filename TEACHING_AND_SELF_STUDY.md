# Teaching and Self-Study Guide

This course is designed to be downloaded, reused, and adapted. Instructors may teach the complete sequence or select modules for an existing engineering, physics, computer-science, or quantum-technology course. Students and independent learners may use the same notebooks for structured self-study, examination review, and preparation for quantum-related academic or industry roles.

## Getting the course

From GitHub, either use **Code → Download ZIP** or clone the repository using the URL shown on its GitHub page. Keep the directory structure intact so that notebook navigation, figures, assignments, and references continue to work.

Install the tested environment from the repository root:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

Activate the virtual environment using the command appropriate to your operating system before starting JupyterLab. The detailed Windows, macOS, and Linux commands are in the [README](README.md#installation).

## Ways to use the material

| Goal | Recommended path | Evidence of progress |
|---|---|---|
| Full institutional course | Python primer; Lectures 0–12; supplementary roadmap and AI-workflow lecture; Homeworks 1–4 in sequence | Completed notebooks, handwritten derivations, reproducible code, a roadmap-evidence brief, and an oral or written final assessment |
| Eight-week quantum-computing module | Lecture 0; Lectures 1–3, 4, 6–10; selected material from 11–12 and the supplement | One mathematical assignment, one circuit assignment, and a small Qiskit project with an explicit baseline and verification plan |
| Independent self-study | Read each lecture in order, run every code cell, reproduce one derivation without looking, then attempt the matching homework | A clean restart-and-run notebook plus a written error log explaining corrected misconceptions |
| Examination preparation | Review learning goals and summary sections; rederive central formulas; solve homework analytical parts under time limits | Formula sheet created from memory, timed problem attempts, and corrected solutions |
| Quantum-software preparation | Lectures 0–10 and the supplementary verification sections, with emphasis on advantage criteria, bit ordering, state/operator representations, primitives, transpilation, noise, testing, and resource accounting | A small repository containing tested circuits, simulations, baselines, uncertainty, and explanations of results |
| Hardware, controls, or photonics preparation | Lectures 4–8 and 11–12; connect each physical component to its Hamiltonian, control, noise, benchmark, and scaling consequences | A comparative architecture report or device-to-algorithm resource budget |

## Guidance for instructors

1. Start from [Course Contents](00_course_contents.md) and select the learning outcomes appropriate to the local program.
2. Make a course-specific copy or branch. Record substantial changes and retain the attribution and license notice.
3. Run `python scripts/validate_repository.py` after editing notebooks, and execute the notebooks in the environment specified by `requirements.txt`. The validator also confirms that every embedded or generated picture still matches its redundant copy in `assets/figures/`.
4. Distribute student copies of the homework notebooks. Problems marked **Python + handwritten** include dedicated cells for scanned work.
5. Set local policies for collaboration, use of external code, grading, deadlines, and accessibility. Those institutional policies are not imposed by this repository.
6. Before redistributing retained third-party figures, review [Figure Sources and Permissions](FIGURE_SOURCES.md). Replace an image with a link or an original diagram when reuse rights are unclear.

The [Notebook Image Archive](IMAGE_MANIFEST.md) provides a browsable backup and restoration map for every figure used by the notebooks. Keep both the notebooks and `assets/figures/` when copying the course.

Instructors may reorder topics, translate the materials, add institution-specific examples, remove hardware sections, or combine notebooks into a shorter module. Under CC BY 4.0, shared adaptations must credit the original author, link to the license, and identify modifications.

## Guidance for students and independent learners

For each lecture:

1. Read the learning goals before studying the notebook.
2. Predict the result of each code cell before running it.
3. Change at least one parameter and explain the new result.
4. Reproduce the central derivation without copying it.
5. Complete the relevant homework problems and compare independent numerical and analytical checks.
6. Keep a short list of errors, convention mistakes, and concepts that require review.

The Python primer is the starting point for learners who need practice with complex arrays, conjugation, matrix products, tensor products, plotting, or Jupyter workflows.

## Preparing for examinations

Use the course learning outcomes as a checklist. Priority topics include complex inner products, tensor-product ordering, projectors and measurement, unitary evolution, reduced density matrices, entanglement, gate action, Qiskit bit order, teleportation, Grover geometry, QFT and phase estimation, noise channels, and hardware resource tradeoffs.

Do not limit revision to rereading. Derive formulas on paper, solve a problem without a notebook, then use Python to test the answer. The mixed-format homework problems are designed for this workflow.

## Preparing for quantum-technology roles

Job preparation benefits from evidence that connects theory, code, and engineering judgment. A useful portfolio can include:

- a current-Qiskit circuit with exact and finite-shot results;
- a clear explanation of qubit and classical-bit ordering;
- a noise-channel or open-system simulation;
- a comparison between logical circuits and transpiled instructions;
- a resource analysis that distinguishes query complexity from complete execution cost;
- a hardware comparison based on control, connectivity, coherence, readout, loss, and error-correction requirements.

The notebooks may be adapted into portfolio projects under the repository licenses. Identify your changes and do not present unmodified course material as original work.

## Attribution and citation

Educational materials are available under CC BY 4.0 and code under BSD-3-Clause. The exact scope and third-party exceptions are in [LICENSE](LICENSE).

Suggested attribution for a syllabus, learning-management system, adapted notebook, or course website:

> Based on *Quantum Computing Lectures: Foundations, Circuits, Algorithms, and Hardware* by Aleksandr Krasnok, licensed under CC BY 4.0. Changes, if any, are identified by the adapter.

For a bibliography or publication, use [CITATION.cff](CITATION.cff). When material from the companion book is used, retain its full Springer citation given in each lecture.
