# Hugging Face Basics (Cookbook)

Builds from LabPod's `ghcr.io/labpod/pytorch-jupyter:cu126` composite image (the same base as
the `pytorch-scientific-ml` cookbook) plus `transformers` and `accelerate` - see
`context/requirements.txt`. The base provides Python 3.12, PyTorch, JupyterLab, TensorBoard,
and code-server without baking a container user. The bundle prepares the unchanged definition
by pulling an immutable prebuilt image. **Approximate pull size:** cu121 4.8 GB, cu126 5.4 GB,
cu129 7.4 GB. The Dockerfile remains available for review, customization, air-gapped fallback,
and a local build when the definition is changed.

The committed bundle defaults to `cu126`; LabPod may select the declared `cu121` or `cu129`
published variant against the host driver. A custom local build can make the same selection by
changing `LABPOD_BASE_IMAGE` in `context/Dockerfile`.

Unlike the other cookbooks in this repo, the notebook here downloads pretrained model weights
from the Hugging Face Hub the first time each model is used - your workspace needs internet
access for that. Weights are cached under `HF_HOME`, which LabPod redirects to
`/work/.hf-cache`, so a download only happens once even across workspace stop/start.

After starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/huggingface/notebook.ipynb` in JupyterLab.
