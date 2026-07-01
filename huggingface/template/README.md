# Hugging Face Basics (Cookbook)

Builds from `quay.io/jupyter/pytorch-notebook:cuda12-python-3.11` (same base as the
`pytorch-scientific-ml` cookbook) plus `transformers` and `accelerate` - see
`context/requirements.txt`. This one has a real build step: after importing, click **Build**
before creating a workspace.

Unlike the other cookbooks in this repo, the notebook here downloads pretrained model weights
from the Hugging Face Hub the first time each model is used - your workspace needs internet
access for that. Weights are cached under `HF_HOME`, which LabPod redirects to
`/work/.hf-cache`, so a download only happens once even across workspace stop/start.

After building and starting a workspace from this template, get the notebook:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open `/work/labpod-cookbook/huggingface/notebook.ipynb` in JupyterLab.
