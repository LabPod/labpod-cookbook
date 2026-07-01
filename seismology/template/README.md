# Seismology (Cookbook)

Builds from `quay.io/jupyter/scipy-notebook:python-3.11` plus `obspy` - see
`context/requirements.txt`. This has a real build step: after importing, click **Build**
before creating a workspace. No GPU needed.

`notebook.ipynb` detrends and bandpass-filters ObsPy's bundled real 3-component example
seismogram - no data download required.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/seismology/notebook.ipynb` in JupyterLab.
