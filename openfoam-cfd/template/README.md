# OpenFOAM CFD (Cookbook)

Uses the official OpenCFD image (`docker.io/opencfd/openfoam-default:2512`), no custom
Dockerfile. After importing this bundle, pull that image from LabPod's Images page, then enable
the template. This is a **terminal-only** template - 0 HTTP ports, no JupyterLab or code-server.
You work through LabPod's built-in Terminal, running OpenFOAM's own command-line solvers
directly.

After creating and starting a workspace from this template, open the **Terminal** app (LabPod's
built-in terminal, not a Jupyter one - there's no Jupyter here) and follow
[`../WALKTHROUGH.md`](../WALKTHROUGH.md) in this repo, cloned into `/work`:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
cat /work/labpod-cookbook/openfoam-cfd/WALKTHROUGH.md
```

**Note on verification**: unlike every other cookbook in this repo, the walkthrough below was
**not run against a real OpenFOAM installation** while writing it (no OpenFOAM available in
that environment) - it follows OpenFOAM's own official tutorial workflow closely, but verify
each step yourself the first time through.
