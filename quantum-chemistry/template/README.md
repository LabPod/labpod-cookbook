# Quantum Chemistry (Cookbook)

Builds from LabPod's CPU-only `ghcr.io/labpod/scipy-jupyter:py312` composite image plus `pyscf`
- see `context/requirements.txt`. The base provides Python 3.12, JupyterLab, and the common
scientific Python stack without baking a container user. This has a real build step: import
with **Build now** checked, or import with **Build later** and click **Build** before enabling
the template. No GPU needed.

`notebook.ipynb` computes the H2 molecule's Hartree-Fock energy and scans bond length to find
the equilibrium - no data download required.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/quantum-chemistry/notebook.ipynb` in JupyterLab.
