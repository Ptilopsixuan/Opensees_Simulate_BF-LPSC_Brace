# LLPSCB OpenSees Simulations

This repository provides Python-based OpenSeesPy tooling to model and simulate LLPSCB — a tension-only, low-prestressed self-centering brace (AHSC-TOB style). The code supports component-level tests and will be extended to integrate multiple braces into frame-level simulations for axial and lateral loading.

Repository layout

- test1.py          : Canonical OpenSeesPy example that builds a two-node brace test, runs cyclic displacement-control sequences and writes recorder outputs to `.out/`.
- test.py           : Development/testing script.
- lib/
  - material.py     : Material classes and helpers.
  - brace.py        : Brace classes (Brace, LLPSCB) with OpenSeesPy registration methods.
  - setter.py       : ModelSetter and AnalysisSetter utilities.
- .out/             : Runtime output directory (created automatically by test1.py).

Quick start

1. Install dependencies:
   pip install openseespy numpy matplotlib
   Note: import path is typically `import openseespy.opensees as ops`.

2. Run the example:
   python test1.py
   Results are written to `.out/`.

How to use

- Instantiate materials from lib.material.
- Create an LLPSCB from lib.brace and call `build_in_opensees()` to register the uniaxial materials used by the brace.
- Initialize the model with `ModelSetter.initialize()` and configure analysis with `AnalysisSetter`.

Planned work

- Integrate LLPSCB instances into frame-level scripts that auto-create nodes/elements, connect braces to beams/columns and apply lateral loading.
- Add parameter-sweep utilities and example notebooks for batch simulations.
- Add unit tests and CI for quick regression checks.

Troubleshooting

- Ensure openseespy is installed and available in the Python environment.
- If OpenSeesPy raises `OpenSeesError` about unrecognized material arguments, verify your OpenSees build supports the uniaxial materials used here (Ratchet, ReinforcingSteel, ElasticMultiLinear, etc.).

License: MIT
