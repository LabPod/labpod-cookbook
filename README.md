# LabPod Cookbook

Ready-to-run research environments and starter notebooks for [LabPod](https://labpod.ai) — aimed
at junior researchers who want to go from "I have a GPU workstation" to "I'm training something"
in a few minutes.

Most top-level directories are a **LabPod template bundle** (environment: base image,
optionally a `Dockerfile` + `requirements.txt`) plus one or more **starter notebooks or scripts**
(the actual research content - usually a `.ipynb`, but a plain `.m`/`.c`/`.cu` file or a
walkthrough doc where that fits the tool better), imported separately — see
[How to use a cookbook](#how-to-use-a-cookbook) below. A few instead reuse one of LabPod's
existing built-in templates and ship only example code - see `parallel-programming/`.

## Cookbooks

| Bundle | Notebook | Notes |
|---|---|---|
| [`pytorch-scientific-ml/`](pytorch-scientific-ml/) ([`.tar`](dist/pytorch-scientific-ml.labpod-bundle.tar)) | [gpu-basics](pytorch-scientific-ml/notebooks/gpu-basics.ipynb) | Confirm the GPU is visible, CPU-vs-GPU benchmark, tiny training loop. Start here. |
| same bundle | [neural-operator](pytorch-scientific-ml/notebooks/neural-operator.ipynb) | Fourier Neural Operator learning the 1D heat equation's solution operator, scored against the exact closed-form solution. |
| same bundle | [pinn](pytorch-scientific-ml/notebooks/pinn.ipynb) | Physics-informed neural network solving a damped harmonic oscillator, scored against the analytic solution. |
| same bundle | [unet](pytorch-scientific-ml/notebooks/unet.ipynb) | Small U-Net for synthetic circle segmentation, scored with IoU. |
| same bundle | [diffusion](pytorch-scientific-ml/notebooks/diffusion.ipynb) | Minimal DDPM trained and sampled on a 2D toy ring distribution. |
| same bundle | [transformer](pytorch-scientific-ml/notebooks/transformer.ipynb) | Multi-head self-attention from scratch on a sequence-reversal task, with a positional-encoding ablation. |
| same bundle | [gnn](pytorch-scientific-ml/notebooks/gnn.ipynb) | Graph neural network denoising noisy per-node signals via message passing, versus a no-graph MLP baseline. |
| same bundle | [rl](pytorch-scientific-ml/notebooks/rl.ipynb) | REINFORCE policy-gradient agent on a hand-rolled grid world, converges to the exact optimal path. |
| same bundle | [ddp_basics](pytorch-scientific-ml/notebooks/ddp_basics.py) | Multi-GPU training with `DistributedDataParallel`. A script, not a notebook - run via `torchrun` from a terminal. |
| [`huggingface/`](huggingface/) ([`.tar`](dist/huggingface.labpod-bundle.tar)) | [notebook](huggingface/notebook.ipynb) | Sentiment classification + text generation with `transformers` pipelines. Needs internet access at runtime to download model weights (the other bundles don't). |
| [`parallel-programming/`](parallel-programming/) (no bundle - uses LabPod's built-in **Parallel Programming (CUDA/MPI/OpenMP)** template) | [openmp](parallel-programming/openmp/pi_openmp.c) / [mpi](parallel-programming/mpi/pi_mpi.c) / [cuda](parallel-programming/cuda/vector_add.cu) | The same problem (or the CUDA equivalent) solved with three different parallelism models: shared-memory threads, distributed-memory processes, GPU SIMT. |
| [`openfoam-cfd/`](openfoam-cfd/) ([`.tar`](dist/openfoam-cfd.labpod-bundle.tar)) | [WALKTHROUGH](openfoam-cfd/WALKTHROUGH.md) | The official OpenCFD image, terminal-only (no web app). Runs OpenFOAM's own lid-driven-cavity tutorial. Not run against a real OpenFOAM install while writing it - see the walkthrough's verification note. |
| [`matlab-deep-learning/`](matlab-deep-learning/) ([`.tar`](dist/matlab-deep-learning.labpod-bundle.tar)) | [digit_classifier.m](matlab-deep-learning/digit_classifier.m) | MATLAB (with Deep Learning Toolbox) via matlab-proxy. **Requires your own MATLAB license** (Deep Learning + Parallel Computing Toolbox) - unusable without one. Not run against a real MATLAB install - see the template README's verification note. |
| [`gromacs-md/`](gromacs-md/) ([`.tar`](dist/gromacs-md.labpod-bundle.tar)) | [README](gromacs-md/template/README.md) points to the canonical external tutorial | The official GROMACS image, terminal-only. No self-contained tutorial here - a real MD protocol is a long multi-step pipeline too easy to get subtly wrong unverified, so this points at the actively-maintained, de facto standard external GROMACS tutorial instead. |
| [`quantum-chemistry/`](quantum-chemistry/) ([`.tar`](dist/quantum-chemistry.labpod-bundle.tar)) | [notebook](quantum-chemistry/notebook.ipynb) | Electronic structure with PySCF - H2 bond energy, verified against the textbook value and a bond-length scan that finds the right minimum. |
| [`quantum-computing/`](quantum-computing/) ([`.tar`](dist/quantum-computing.labpod-bundle.tar)) | [notebook](quantum-computing/notebook.ipynb) | Quantum circuit simulation with Qiskit - a Bell state (entanglement) and Grover's search, both verified numerically. |
| [`cheminformatics/`](cheminformatics/) ([`.tar`](dist/cheminformatics.labpod-bundle.tar)) | [notebook](cheminformatics/notebook.ipynb) | Molecule parsing, descriptors, and Tanimoto similarity search with RDKit, verified against known chemistry (aspirin closer to ibuprofen than to caffeine). |
| [`materials-science/`](materials-science/) ([`.tar`](dist/materials-science.labpod-bundle.tar)) | [notebook](materials-science/notebook.ipynb) | Crystal structure and lattice-constant optimization with ASE, verified within ~1% of the experimental Cu lattice constant. |
| [`seismology/`](seismology/) ([`.tar`](dist/seismology.labpod-bundle.tar)) | [notebook](seismology/notebook.ipynb) | Real seismic waveform processing (detrend, bandpass filter) with ObsPy's bundled example data, verified for real. |
| [`bioinformatics-alignment/`](bioinformatics-alignment/) ([`.tar`](dist/bioinformatics-alignment.labpod-bundle.tar)) | [alignment-basics](bioinformatics-alignment/notebooks/alignment-basics.ipynb) | Read alignment with `bwa` + `samtools` on synthetic reference/reads (data generation verified; the CLI tools themselves were not run in development - see the template README). |

All `pytorch-scientific-ml` notebooks use synthetic/toy data generated in the notebook itself -
no dataset download required, so they work on an offline / air-gapped workspace too. Every
notebook except `ddp_basics.py` logs to TensorBoard - the bundle's Dockerfile bakes it in, so
the TensorBoard app just works after building.

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

Prefer adding a **notebook** to an existing bundle only when it genuinely needs the same
dependencies for the same kind of work (see `pytorch-scientific-ml/notebooks/` - eight
notebooks and a script, all plain PyTorch, no extra deps). Do **not** group unrelated fields
into one bundle just because they're each small - `quantum-chemistry/`, `quantum-computing/`,
`cheminformatics/`, `materials-science/`, and `seismology/` are separate single-package bundles
on purpose, even though they'd technically all fit in one lightweight pure-Python image:
someone who wants cheminformatics shouldn't have to build an environment that also drags in a
seismology library and a quantum circuit simulator they'll never use. When in doubt, default to
a new minimal bundle rather than adding to an existing one.
