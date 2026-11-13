# Course Contents

## Quantum Computing: Foundations, Circuits, Algorithms, and Hardware

The course is written for engineering students who have taken introductory Python and undergraduate linear algebra. The Python primer and the early mathematics lectures review the tools that the later lectures use.

Instructors at any institution, from universities to training programs, may download the complete course and adapt it for their own teaching. Learners can also use it for self-study, exam preparation, and preparation for jobs in quantum software, applications, controls, photonics, and hardware. The [Teaching and Self-Study Guide](TEACHING_AND_SELF_STUDY.md) describes the recommended pathways.

## Learning pathways

- A fourteen-week course follows Lectures 0–12 in order and ends with the supplementary lecture on systems and evidence. Students work through the Python primer before the course starts and complete the four homework sets in sequence.
- A compressed module starts with Lecture 0, concentrates on Lectures 1–4 and 6–10, adds the hardware material most relevant to the class, and ends with selected supplementary sections.
- For self-study, run every example, reproduce the main derivations, and use each homework set to confirm that you have mastered the material before moving on. Finish with the roadmap and verification problems of the supplementary lecture.
- For exam review, start from the learning outcomes, solve the analytical problems without notes, and then check the answers with Python.
- For career preparation, combine the software pathway through Lecture 10 with Lectures 11–12 and the supplementary material on roadmaps, AI-enabled workflows, verification, and professional evidence.

### Course-level learning outcomes

By the end of the course, a student should be able to:

1. Explain why quantum engineering helps with selected tasks, and why the size of the state space alone does not prove a practical speedup.
2. Represent quantum states and operators in finite-dimensional and function Hilbert spaces using bases, spectral decompositions, tensor products, and Dirac notation.
3. Apply the postulates of quantum mechanics, including unitary evolution, projective measurement, density operators, partial trace, and composite-system structure.
4. Analyze single- and multi-qubit gates, entanglement, circuit ordering, and measurement conventions.
5. Build and simulate current Qiskit 2.x circuits with local V2 primitives and Aer.
6. Derive the central ideas in teleportation, amplitude amplification, phase-kickback algorithms, the quantum Fourier transform, phase estimation, and quantum order finding.
7. Distinguish oracle-query, gate, and end-to-end resource costs when evaluating quantum speedup or cryptographic claims.
8. Compare leading hardware modalities using explicit encodings, operations, benchmarks, loss and noise models, connectivity, control, and scaling constraints.
9. Connect superconducting and photonic components to system architecture, physical-to-logical error budgets, fault tolerance, networking, and algorithm-level resource estimates.
10. Evaluate roadmaps, machine-learning applications, and hybrid quantum-classical claims using dated evidence, uncertainty, verification gates, and strong baselines.

## Lecture sequence

| No. | Notebook | Main content | What students should be able to do |
|---:|---|---|---|
| 0 | [Why quantum engineering?](lectures/00_why_quantum_engineering.ipynb) | Why quantum systems motivate new computational tools; state-space scaling; amplitude, phase, and interference; computing, sensing, networking, and fault tolerance | Evaluate quantum-advantage claims, estimate dense-state memory, explain phase-to-probability conversion, and distinguish the three principal quantum-technology domains |
| 1 | [Introduction and the Python toolkit](lectures/01_introduction_and_python.ipynb) | Reproducible Jupyter workflows; numerical and symbolic tools; complex state arrays; Qiskit state vectors; finite-shot statistics | Select an appropriate tool, validate states and operators numerically, and distinguish exact probabilities from sampling fluctuations |
| 2 | [Linear algebra](lectures/02_linear_algebra.ipynb) | Complex vector spaces; inner, outer, and tensor products; Gram–Schmidt and QR; projectors; linear systems; conditioning; Hermitian spectra | Construct orthonormal bases and projectors, compute composite-space operations, and recognize numerically sensitive calculations |
| 3 | [Complex numbers, operators, and Dirac notation](lectures/03_complex_numbers_and_operators.ipynb) | Global and relative phase; interference; Hermitian and unitary operators; spectral projectors; operator exponentials; basis changes | Use spectral decompositions, generate unitaries from Hermitian operators, and translate between coordinates and basis-independent notation |
| 4 | [Hilbert space and quantum mechanics I](lectures/04_hilbert_space_and_quantum_mechanics.ipynb) | Function Hilbert spaces; completeness and Parseval's identity; truncation; physical rays; qubit bases; projective measurement; composite systems | Expand states in orthonormal bases, quantify truncation error, compute Born probabilities, and distinguish basis changes from different measurements |
| 5 | [Quantum dynamics and measurement](lectures/05_quantum_dynamics_and_measurement.ipynb) | Projective measurements; POVMs and instruments; expectation and variance; Robertson uncertainty; Hamiltonian evolution; shot statistics | Calculate outcome probabilities, conditional states, uncertainty bounds, driven-qubit rotations, and finite-shot errors |
| 6 | [Density operators, decoherence, and entanglement](lectures/06_density_matrices_and_entanglement.ipynb) | Ensembles and reduced states; CPTP/Kraus channels; Lindblad dynamics; partial trace; Schmidt decomposition; entropy; CHSH and no-signaling | Test whether a density matrix is physical, model relaxation/dephasing, and quantify subsystem entanglement and correlations |
| 7 | [Bloch sphere and quantum gates](lectures/07_bloch_sphere_and_quantum_gates.ipynb) | Bloch vector/tomography; global and relative phase; SU(2); Euler decompositions; reversible embeddings; Clifford and universal gates | Reconstruct qubit states, derive gate action, distinguish local from entangling resources, and track bit-order conventions |
| 8 | [Quantum circuits with current Qiskit](lectures/08_quantum_circuits_with_qiskit.ipynb) | Circuit/state/operator representations; bit order; V2 primitive PUBs/results; shots and noise; transpilation/ISA; dynamic circuits; Runtime cost | Build and audit Qiskit 2.x workflows, distinguish exact and sampled results, transpile to a target, and use optional hardware safely |
| 9 | [Teleportation and Grover search](lectures/09_teleportation_and_grover.ipynb) | Teleportation identity, resources, no-signaling, fidelity, and feed-forward; Grover geometry; reversible phase oracles and implementation cost | Derive the correction table, assess teleportation evidence, implement dynamic control, and account for the full cost of a small Grover search |
| 10 | [Introductory quantum algorithms](lectures/10_quantum_algorithms.ipynb) | Complexity models; Grover scaling; Deutsch and Deutsch–Jozsa; phase kickback; QFT; phase estimation; Shor order finding | Identify promises and resource measures, connect QFT and phase estimation to order finding, and interpret algorithmic and cryptographic claims carefully |
| 11 | [Quantum-computer architectures](lectures/11_quantum_computer_architectures.ipynb) | DiVincenzo criteria; benchmark hierarchy; fault tolerance; modular links; resource estimation; photonic encodings, components, loss, and feed-forward | Compare modalities with compatible metrics and turn photonic components, network links, and logical operations into explicit system-resource budgets |
| 12 | [Superconducting qubits](lectures/12_superconducting_qubits.ipynb) | Transmon Hamiltonian and spectrum; microwave control and leakage; dispersive readout; decoherence; cryogenics; coupling; gates; logical error budgets | Relate circuit parameters and control Hamiltonians to gate, readout, and coherence tradeoffs, and evaluate system performance beyond headline qubit counts |
| S | [Quantum-technology roadmaps and AI workflows](lectures/13_quantum_technology_roadmaps_and_ai.ipynb) | Roadmap evidence; system metrics; reliability and logical-error models; sensing limits; AI for quantum systems; quantum methods for learning; validation and safe control | Distinguish targets from demonstrations, audit simplified models, verify quantum code, and evaluate learned or hybrid workflows against uncertainty and classical baselines |

## Assignments

| Assignment | Primary preparation | Scope |
|---|---|---|
| [Homework 1](assignments/01_homework.ipynb) | Python primer; Lectures 0–3 | Complex vectors, tensor products, projectors, Gram–Schmidt, spectra, unitary generators, basis changes, and conditioning |
| [Homework 2](assignments/02_homework.ipynb) | Lectures 4–5 | Qubit bases, measurement, observables, uncertainty, POVMs, unitary dynamics, Rabi oscillations, and shot statistics |
| [Homework 3](assignments/03_homework.ipynb) | Lectures 6–8 | Density operators, channels, entanglement, Bloch coordinates, gates, circuit ordering, bit order, and Qiskit sampling |
| [Homework 4](assignments/04_homework.ipynb) | Lectures 9–13 | Teleportation, Grover search, Deutsch–Jozsa, QFT, phase estimation, order finding, hardware budgets, and evidence assessment |

## Conventions used throughout

- Computational basis labels are written as `|q_(n-1) ... q_0>` unless a problem states another convention.
- Statevector index `x` stores the amplitude of `|x>`; Qiskit circuit drawings place `q_0` at the top.
- Matrix products act on kets from right to left.
- State equality is normally interpreted up to global phase, but relative phase is observable.
- Inner products conjugate the first vector; in NumPy use `np.vdot(u, v)`.
- `@` is matrix multiplication, `*` is elementwise multiplication, and `np.kron` is the Kronecker product.

## Suggested pacing

- Before Week 1: Python primer
- Week 1: Motivation and course map (Lecture 0)
- Week 2: Python quantum-computing workflow (Lecture 1)
- Weeks 3–5: Mathematical and quantum-mechanical foundations (Lectures 2–4)
- Weeks 6–7: Dynamics, measurement, noise, and entanglement (Lectures 5–6)
- Weeks 8–9: Qubits, gates, and Qiskit (Lectures 7–8)
- Weeks 10–11: Protocols and algorithms (Lectures 9–10)
- Weeks 12–13: Architectures and superconducting hardware (Lectures 11–12)
- Week 14: Roadmaps, AI workflows, verification, and professional preparation (supplementary lecture)

Course-wide sources are collected in [REFERENCES.md](REFERENCES.md); each notebook also ends with topic-specific references.

## Reuse

Original educational materials are available under CC BY 4.0 and repository code under BSD-3-Clause. Educators and learners may copy and adapt them with attribution. See [LICENSE](LICENSE), [CITATION.cff](CITATION.cff), and the third-party figure guidance in [FIGURE_SOURCES.md](FIGURE_SOURCES.md).
