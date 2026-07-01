# Quantum Computing (Cookbook)

Builds from `quay.io/jupyter/scipy-notebook:python-3.11` plus `qiskit`/`qiskit-aer` - see
`context/requirements.txt`. This has a real build step: after importing, click **Build**
before creating a workspace. No GPU needed.

`notebook.ipynb` simulates a Bell state (entanglement) and Grover's search algorithm - no data
download required.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/quantum-computing/notebook.ipynb` in JupyterLab.
