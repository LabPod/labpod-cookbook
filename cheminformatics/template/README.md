# Cheminformatics (Cookbook)

Builds from LabPod's CPU-only `ghcr.io/labpod/scipy-jupyter:py312` composite image plus
`rdkit` - see `context/requirements.txt`. The base provides Python 3.12, JupyterLab, and the
common scientific Python stack without baking a container user. The derived image also adds
the small X11 runtime libraries that RDKit's headless molecule renderer links against. The
bundle prepares the unchanged definition by pulling the immutable prebuilt image; its
**approximate pull size is 380 MB**. The Dockerfile remains available for review, customization,
air-gapped fallback, and a local build when the definition is changed. No GPU needed.

`notebook.ipynb` parses molecules from SMILES, computes descriptors, and compares them with
Tanimoto similarity - no data download required.

After starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/cheminformatics/notebook.ipynb` in JupyterLab.
