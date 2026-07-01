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

1. **Import the environment.** Download `dist/<cookbook>.labpod-bundle.tar` - either from this
   repo directly, or from its raw URL:
   `https://raw.githubusercontent.com/LabPod/labpod-cookbook/main/dist/<cookbook>.labpod-bundle.tar`
   (that URL also works with LabPod's "import from URL" option, once that ships). Then import it
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

The notebook is not part of the template import — LabPod's bundle format only allows a small
whitelist of build-context file types (`.py`, `.txt`, `.yaml`, etc., no `.ipynb`), by design:
bundles describe the *environment*, not your working files. Environments should be built once
and reused; notebooks and data belong in `/work`, which is what actually survives a workspace
stop/start. The directory layout below keeps that split explicit: everything under `template/`
is what gets bundled, the notebook sits outside it.

## Building a bundle yourself

Each cookbook directory separates the bundle from the notebook:

```
<cookbook>/
  template/
    bundle.json
    README.md
    context/
      Dockerfile
      requirements.txt
  notebook.ipynb        # outside template/ - not part of the bundle, lives in /work at runtime
```

`scripts/build-bundle.sh <cookbook>` packs `<cookbook>/template/`'s `bundle.json`, `README.md`,
and `context/` into `dist/<cookbook>.labpod-bundle.tar` (a plain, uncompressed POSIX tar -
LabPod's bundle decoder does not accept gzip).

Built tars are committed to this repo under `dist/` rather than published only as release
assets - LabPod's own format caps a bundle tar at 1 MiB, so this is cheap, and it means every
tar is reachable at a stable `raw.githubusercontent.com` URL that a browser can `fetch()`
directly (GitHub release-asset download URLs don't send CORS headers, so they don't work for
that; committed repo files do). If you edit a cookbook's `template/`, rebuild and commit the
updated tar as part of the same PR.

## Contributing a cookbook

Open a PR adding a new `<cookbook>/` directory following the layout above. Keep the environment
minimal - prefer extending an existing bundle's `requirements.txt` over adding a whole new
Dockerfile when the dependencies mostly overlap.
