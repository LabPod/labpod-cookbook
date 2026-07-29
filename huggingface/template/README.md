# Hugging Face Basics (Cookbook)

Builds from LabPod's `ghcr.io/labpod/pytorch-jupyter:cu126` composite image (the same base as
the `pytorch-scientific-ml` cookbook) plus `transformers` and `accelerate` - see
`context/requirements.txt`. The base provides Python 3.12, PyTorch, JupyterLab, TensorBoard,
and code-server without baking a container user. This has a real build step: import with
**Build now** checked, or import with **Build later** and click **Build** before enabling the
template.

The committed bundle targets LabPod's default `cu126` line. To build for an older CUDA host,
change `LABPOD_BASE_IMAGE` in `context/Dockerfile` to the published `cu121` tag before packing
the bundle; use `cu129` on a sufficiently new driver and a Volta-or-newer GPU.

Unlike the other cookbooks in this repo, the notebook here downloads pretrained model weights
from the Hugging Face Hub the first time each model is used - your workspace needs internet
access for that. Weights are cached under `HF_HOME`, which LabPod redirects to
`/work/.hf-cache`, so a download only happens once even across workspace stop/start.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/huggingface/notebook.ipynb` in JupyterLab.
