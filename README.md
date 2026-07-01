# LabPod Cookbook

Ready-to-run research environments and starter notebooks for [LabPod](https://labpod.ai) — aimed
at junior researchers who want to go from "I have a GPU workstation" to "I'm training something"
in a few minutes.

Each cookbook is a **LabPod template bundle** (environment: base image + `Dockerfile` +
`requirements.txt`) plus a **starter notebook** (the actual research content). The two are
imported separately — see [How to use a cookbook](#how-to-use-a-cookbook) below.

## Cookbooks

| Domain | Directory | Bundle | Notes |
|---|---|---|---|
| _more coming soon_ | | | |

## How to use a cookbook

1. **Import the environment.** Download `<cookbook>.labpod-bundle.tar` from the
   [latest release](../../releases/latest) (or build it yourself — see below), then import it
   in LabPod: **Images → My templates → Import**. This creates a private, disabled template.
2. **Build it.** Select the imported template and click **Build**. This builds the Dockerfile
   once; the image is reused by every workspace you create from it afterward.
3. **Enable it**, then create a workspace from the template as usual.
4. **Get the notebook.** Open the LabPod Terminal (or a Jupyter terminal) inside the workspace
   and clone this repo into `/work`, which persists across stop/start:
   ```bash
   git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
   ```
5. Open the cookbook's notebook from `/work/labpod-cookbook/<cookbook>/notebook.ipynb` in
   JupyterLab and run it.

Notebooks are not bundled inside the template import — LabPod's bundle format only allows a
small whitelist of build-context file types (`.py`, `.txt`, `.yaml`, etc., no `.ipynb`), by
design: bundles describe the *environment*, not your working files. Environments should be
built once and reused; notebooks and data belong in `/work`, which is what actually survives a
workspace stop/start.

## Building a bundle yourself

Each cookbook directory is the *unpacked* form of its LabPod bundle:

```
<cookbook>/
  bundle.json
  README.md
  context/
    Dockerfile
    requirements.txt
  notebook.ipynb        # not part of the bundle - lives in /work at runtime, see above
```

`scripts/build-bundle.sh <cookbook>` packs `bundle.json`, `README.md`, and `context/` into
`dist/<cookbook>.labpod-bundle.tar` (a plain, uncompressed POSIX tar - LabPod's bundle decoder
does not accept gzip). CI runs the same script for every cookbook on each tagged release and
attaches the resulting `.tar` files as release assets, so most users never need to run it
themselves.

## Contributing a cookbook

Open a PR adding a new `<cookbook>/` directory following the layout above. Keep the environment
minimal - prefer extending an existing bundle's `requirements.txt` over adding a whole new
Dockerfile when the dependencies mostly overlap.
