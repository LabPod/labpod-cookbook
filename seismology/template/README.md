# Seismology (Cookbook)

Builds from LabPod's CPU-only `ghcr.io/labpod/scipy-jupyter:py312` composite image plus `obspy`
- see `context/requirements.txt`. The base provides Python 3.12, JupyterLab, and the common
scientific Python stack without baking a container user. This has a real build step: import
with **Build now** checked, or import with **Build later** and click **Build** before enabling
the template. No GPU needed.

`notebook.ipynb` detrends and bandpass-filters ObsPy's bundled real 3-component example
seismogram - no data download required.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/seismology/notebook.ipynb` in JupyterLab.
