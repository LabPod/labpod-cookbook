# Quantum Science (Cookbook)

Builds from `quay.io/jupyter/scipy-notebook:python-3.11` plus `pyscf` and `qiskit`/`qiskit-aer`
- see `context/requirements.txt`. This has a real build step: after importing, click **Build**
before creating a workspace. No GPU needed for anything here.

Two notebooks covering two unrelated fields that just happen to share the word "quantum":

- `notebooks/pyscf-quantum-chemistry.ipynb` - electronic structure calculations (how molecules'
  electrons actually behave), using PySCF.
- `notebooks/qiskit-basics.ipynb` - quantum circuit simulation (qubits, gates, entanglement),
  using Qiskit.

Both use tiny built-in examples - no data download required.

After building and starting a workspace from this template, get the notebooks:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open either notebook from `/work/labpod-cookbook/quantum-science/notebooks/` in JupyterLab.
