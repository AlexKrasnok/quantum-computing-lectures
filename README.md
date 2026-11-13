# Quantum Computing Lectures

This engineering course starts from the motivation and mathematical foundations of quantum computing and continues through circuits, algorithms, noise, and hardware. The supplementary final lecture covers technology roadmaps and AI-enabled workflows whose results are verified before use. The notebooks combine derivations, numerical examples, Qiskit circuits, assignments, experimental context, and references to the primary literature.

The materials are open for reuse. Instructors may download, adapt, translate, and teach them at their own institutions. Students and independent learners may use them for self-study, exam review, and preparation for jobs in quantum technology. The section [Reuse and attribution](#reuse-and-attribution) explains how to credit the course and which third-party items the open license does not cover.

Start with [Course Contents](00_course_contents.md), which gives the lecture order, prerequisites, learning outcomes, and the homework map. The [Teaching and Self-Study Guide](TEACHING_AND_SELF_STUDY.md) describes paths through the material for a complete course, a compressed course, self-study, exam preparation, and career preparation.

## Contents

| Path | Material |
|---|---|
| `lectures/` | Fourteen notebooks: Lectures 0–12 and a final supplementary lecture |
| `assignments/` | Four sequential homework sets aligned with Lectures 0–3, 4–5, 6–8, and 9–13 |
| `appendices/python_primer.ipynb` | Python, NumPy, SymPy, Matplotlib, and quantum-array conventions |
| `assets/figures/` | Standalone backup copies of every embedded or generated notebook image |
| `IMAGE_MANIFEST.md` | Human-readable image inventory, recovery instructions, and archive summary |
| `REFERENCES.md` | Course-wide books, papers, and software documentation |
| `FIGURE_SOURCES.md` | Figure provenance and permissions |
| `TEACHING_AND_SELF_STUDY.md` | Paths for institutional teaching, independent learning, exams, and career preparation |
| `LICENSE` and `CITATION.cff` | Reuse terms and citation metadata |
| `scripts/` | Notebook execution and validation tools |

## Intended users

- Instructors can teach the full sequence, select modules, translate notebooks, or add problems to an existing course.
- Enrolled students follow the local syllabus, run the examples, and submit the Python and handwritten homework that the instructor assigns.
- Independent learners can study the notebooks in order and use the assignments as checkpoints.
- Exam candidates can review the learning outcomes, rederive the formulas, and solve the analytical parts under time limits before checking their answers with Python.
- Job seekers and working engineers can build evidence of current skills in Qiskit, quantum information, algorithms, noise, hardware systems, roadmap analysis, and verification.

## Software environment

- Python 3.12
- Qiskit 2.5.2
- Qiskit Aer 0.17.2
- Qiskit IBM Runtime 0.49.0
- NumPy 2.5.2, SciPy 1.18.0, and SymPy 1.14.0
- Matplotlib 3.11.1, QuTiP 5.3.1, and SciencePlots 2.2.2

Install Qiskit as a complete package; do not install the retired standalone `qiskit-terra` distribution.

## Installation

Download the course as a ZIP from the [GitHub repository](https://github.com/AlexKrasnok/quantum-computing-lectures) or clone it directly. Keep the directory structure intact so that notebook navigation and local figures work.

```bash
git clone https://github.com/AlexKrasnok/quantum-computing-lectures.git
cd quantum-computing-lectures
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

macOS or Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

## Running the notebooks

The lecture code uses local state-vector simulation, Qiskit V2 primitives, and Aer by default. IBM Quantum hardware examples require an explicit change to `RUN_ON_HARDWARE = True`.

Never paste an IBM Quantum token into a notebook. Configure credentials with the supported IBM credential store or an environment variable outside the repository. Hardware backends are selected from the service at run time because backend names and availability change.

To validate the notebooks:

```bash
python scripts/validate_repository.py
python scripts/check_external_links.py
```

Repository validation also checks the image archive: every embedded attachment and saved figure output must match its standalone copy and SHA-256 record in `assets/figures/manifest.json`.

On macOS or Linux, execute the complete lecture set with:

```bash
python scripts/execute_notebooks.py lectures/*.ipynb appendices/python_primer.ipynb
```

PowerShell does not expand native-program wildcards, so use:

```powershell
Get-ChildItem lectures\*.ipynb | ForEach-Object {
    python scripts\execute_notebooks.py $_.FullName
}
python scripts\execute_notebooks.py appendices\python_primer.ipynb
```

## Videos

Course videos are ordinary YouTube links instead of embedded `iframe` elements, so they open from Jupyter, from GitHub, and from exported HTML.

## Reuse and attribution

You may copy, teach, translate, modify, and redistribute the original course materials under the following terms:

- Lecture text, assignments, explanatory Markdown, course organization, and original educational media are licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
- Python code cells and repository scripts are licensed under the [BSD 3-Clause License](https://opensource.org/license/BSD-3-clause).
- Give appropriate credit, link to the applicable license, and identify modifications. Do not imply endorsement by the author or Florida International University.

Suggested attribution:

> Based on *Quantum Computing Lectures: Foundations, Circuits, Algorithms, and Hardware* by Aleksandr Krasnok, licensed under CC BY 4.0. Changes, if any, are identified by the adapter.

GitHub can generate a formatted citation from [CITATION.cff](CITATION.cff). The full legal terms, including which files count as code and which as course content, are in [LICENSE](LICENSE).

## Figures and third-party material

All 174 notebook images are stored twice: once inside their notebook attachment or output and once under `assets/figures/`. See the [Notebook Image Archive](IMAGE_MANIFEST.md) for the inventory, hashes, and restoration procedure. Code-generated plots and circuit diagrams can also be regenerated from their adjacent cells.

Every embedded figure has descriptive alternative text. Each generated plot or circuit is followed by a short written description, and the execution script copies that description into the metadata of the saved image when the notebooks are rerun.

External photographs, screenshots, diagrams, and article figures remain subject to their source licenses. See [Figure Sources](FIGURE_SOURCES.md) before redistributing course images.

CC BY 4.0 applies only to original material that the author has authority to license. A citation alone does not grant permission to republish a third-party image; link to its source or replace it with an original or openly licensed figure when permission is unclear.
