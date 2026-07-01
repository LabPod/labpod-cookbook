# Scientific Computing (Cookbook)

Builds from `quay.io/jupyter/scipy-notebook:python-3.11` plus `pyscf`, `qiskit`/`qiskit-aer`,
`rdkit`, `ase`, and `obspy` - see `context/requirements.txt`. This has a real build step: after
importing, click **Build** before creating a workspace. No GPU needed for anything here.

Five notebooks covering five unrelated fields that just happen to share one lightweight,
pure-Python environment:

- `notebooks/pyscf-quantum-chemistry.ipynb` - electronic structure calculations (how molecules'
  electrons actually behave), using PySCF.
- `notebooks/qiskit-basics.ipynb` - quantum circuit simulation (qubits, gates, entanglement),
  using Qiskit.
- `notebooks/rdkit-cheminformatics.ipynb` - molecule parsing, descriptors, and similarity
  search, using RDKit.
- `notebooks/ase-materials-science.ipynb` - crystal structure, lattice constants, and geometry
  optimization, using ASE (Atomic Simulation Environment).
- `notebooks/obspy-seismology.ipynb` - real seismic waveform processing (filtering, basic
  feature extraction), using ObsPy's bundled example data.

All use tiny built-in/synthetic examples - no data download required.

After building and starting a workspace from this template, get the notebooks:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open any notebook from `/work/labpod-cookbook/scientific-computing/notebooks/` in
JupyterLab.
