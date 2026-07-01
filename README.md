# LabPod Cookbook

Ready-to-run research environments and starter notebooks for [LabPod](https://labpod.ai) — aimed
at junior researchers who want to go from "I have a GPU workstation" to "I'm training something"
in a few minutes.

Each top-level directory is a **LabPod template bundle** (environment: base image, optionally a
`Dockerfile` + `requirements.txt`) plus one or more **starter notebooks** (the actual research
content). The two are imported separately — see [How to use a cookbook](#how-to-use-a-cookbook)
below.

## Cookbooks

| Bundle | Notebook | Notes |
|---|---|---|
| [`pytorch-scientific-ml/`](pytorch-scientific-ml/) ([`.tar`](dist/pytorch-scientific-ml.labpod-bundle.tar)) | [gpu-basics](pytorch-scientific-ml/notebooks/gpu-basics.ipynb) | Confirm the GPU is visible, CPU-vs-GPU benchmark, tiny training loop. Start here. |
| same bundle | [neural-operator](pytorch-scientific-ml/notebooks/neural-operator.ipynb) | Fourier Neural Operator learning the 1D heat equation's solution operator, scored against the exact closed-form solution. |
| same bundle | [pinn](pytorch-scientific-ml/notebooks/pinn.ipynb) | Physics-informed neural network solving a damped harmonic oscillator, scored against the analytic solution. |
| same bundle | [unet](pytorch-scientific-ml/notebooks/unet.ipynb) | Small U-Net for synthetic circle segmentation, scored with IoU. |
| same bundle | [diffusion](pytorch-scientific-ml/notebooks/diffusion.ipynb) | Minimal DDPM trained and sampled on a 2D toy ring distribution. |
| [`huggingface/`](huggingface/) ([`.tar`](dist/huggingface.labpod-bundle.tar)) | [notebook](huggingface/notebook.ipynb) | Sentiment classification + text generation with `transformers` pipelines. Needs internet access at runtime to download model weights (the other bundles don't). |

All `pytorch-scientific-ml` notebooks use synthetic/toy data generated in the notebook itself -
no dataset download required, so they work on an offline / air-gapped workspace too. Its four
training notebooks (everything but `gpu-basics`) log to TensorBoard - the bundle's Dockerfile
bakes it in, so the TensorBoard app just works after building.

## How to use a cookbook

1. **Import the environment.** Download the bundle's `dist/<bundle>.labpod-bundle.tar` - either
   from this repo directly, or from its raw URL:
   `https://raw.githubusercontent.com/LabPod/labpod-cookbook/main/dist/<bundle>.labpod-bundle.tar`
   (that URL also works with LabPod's "import from URL" option, once that ships). Then import it
   in LabPod: **Images → My templates → Import**. This creates a private, disabled template.
2. **Build it.** Select the imported template and click **Build**. This builds the environment
   once (a no-op download-and-tag for a pull-only bundle, a real image build if it has a
   `Dockerfile`); the image is reused by every workspace and every notebook that uses this
   bundle afterward.
3. **Enable it**, then create a workspace from the template as usual.
4. **Get the notebook(s).** Open the LabPod Terminal (or a Jupyter terminal) inside the
   workspace and clone this repo into `/work`, which persists across stop/start:
   ```bash
   git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
   ```
5. Open the notebook(s) you want from `/work/labpod-cookbook/` in JupyterLab and run them. A
   bundle with several notebooks (like `pytorch-scientific-ml`) only needs importing/building
   once - you can run any or all of its notebooks in the same workspace.

Notebooks are not part of the template import — LabPod's bundle format only allows a small
whitelist of build-context file types (`.py`, `.txt`, `.yaml`, etc., no `.ipynb`), by design:
bundles describe the *environment*, not your working files. Environments should be built once
and reused; notebooks and data belong in `/work`, which is what actually survives a workspace
stop/start. The directory layout below keeps that split explicit: everything under `template/`
is what gets bundled, notebooks sit outside it.

## Building a bundle yourself

Each top-level directory separates its bundle from its notebook(s):

```
<bundle>/
  template/
    bundle.json
    README.md
    context/               # only if the environment needs a Dockerfile
      Dockerfile
      requirements.txt
  notebook.ipynb            # a single-notebook bundle
  # or, for a bundle shared by several notebooks:
  notebooks/
    <name>.ipynb
    <name>.ipynb
```

`scripts/build-bundle.sh <bundle-dir>` packs `<bundle-dir>/template/`'s `bundle.json`,
`README.md`, and `context/` into `dist/<bundle-dir>.labpod-bundle.tar` (a plain, uncompressed
POSIX tar - LabPod's bundle decoder does not accept gzip).

Built tars are committed to this repo under `dist/` rather than published only as release
assets - LabPod's own format caps a bundle tar at 1 MiB, so this is cheap, and it means every
tar is reachable at a stable `raw.githubusercontent.com` URL that a browser can `fetch()`
directly (GitHub release-asset download URLs don't send CORS headers, so they don't work for
that; committed repo files do). CI (`.github/workflows/build-bundles.yml`) rebuilds and commits
every bundle's tar automatically on push, so you generally don't need to run this by hand.

## Contributing a cookbook

Prefer adding a **notebook** to an existing bundle when the environment already has what you
need (see `pytorch-scientific-ml/notebooks/` - five notebooks, one shared plain-PyTorch
environment). Only add a new bundle when you need different dependencies (a new `Dockerfile` +
`requirements.txt`, like `huggingface/`). Keep environments minimal and shared where
dependencies overlap, rather than one bundle per notebook.
