# Quantum Chemistry (Cookbook)

Builds from `quay.io/jupyter/scipy-notebook:python-3.11` plus `pyscf` - see
`context/requirements.txt`. This has a real build step: import with **Build now** checked, or
import with **Build later** and click **Build** before enabling the template. No GPU needed.

`notebook.ipynb` computes the H2 molecule's Hartree-Fock energy and scans bond length to find
the equilibrium - no data download required.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/quantum-chemistry/notebook.ipynb` in JupyterLab.
