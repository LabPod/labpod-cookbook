# Quantum Chemistry (Cookbook)

Builds from LabPod's CPU-only `ghcr.io/labpod/scipy-jupyter:v1-py312` composite image plus `pyscf`
- see `context/requirements.txt`. The base provides Python 3.12, JupyterLab, and the common
scientific Python stack without baking a container user. The bundle prepares the unchanged
definition by pulling the immutable prebuilt image; its **approximate pull size is 430 MB**.
The Dockerfile remains available for review, customization, air-gapped fallback, and a local
build when the definition is changed. No GPU needed.

`notebook.ipynb` computes the H2 molecule's Hartree-Fock energy and scans bond length to find
the equilibrium - no data download required.

After starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/quantum-chemistry/notebook.ipynb` in JupyterLab.
