# PyTorch Scientific ML (Cookbook)

Builds from `quay.io/jupyter/pytorch-notebook:cuda12-python-3.11` (same base image as LabPod's
built-in "PyTorch JupyterLab" template) plus `tensorboard` - see `context/requirements.txt`.
This has a real build step: import with **Build now** checked, or import with **Build later** and
click **Build** before enabling the template.

Shared by several notebooks - build this template once, then run any of them:

- `notebooks/gpu-basics.ipynb` - confirm the GPU is visible, a CPU-vs-GPU benchmark, a tiny
  training loop.
- `notebooks/neural-operator.ipynb` - a minimal Fourier Neural Operator.
- `notebooks/pinn.ipynb` - a physics-informed neural network.
- `notebooks/unet.ipynb` - a small U-Net for segmentation.
- `notebooks/diffusion.ipynb` - a minimal denoising diffusion model.
- `notebooks/transformer.ipynb` - multi-head self-attention from scratch, with a positional-
  encoding ablation.
- `notebooks/gnn.ipynb` - a graph neural network, denoising per-node signals via message
  passing, versus a no-graph MLP baseline.
- `notebooks/rl.ipynb` - a policy-gradient (REINFORCE) agent on a hand-rolled grid world.
- `notebooks/ddp_basics.py` - multi-GPU training with `DistributedDataParallel`. A plain
  script, not a notebook - see the file's own docstring, it needs `torchrun` from a terminal.

All use synthetic/toy data generated in the notebook - no dataset download required, so these
work on an offline / air-gapped workspace too.

After building and starting a workspace from this template, get the notebooks:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open any notebook under
`/work/labpod-cookbook/pytorch-scientific-ml/notebooks/` in JupyterLab.

## Watching training in TensorBoard

All notebooks except `ddp_basics.py` log their training curves to `/work/runs/<notebook-name>`.
TensorBoard is already installed (baked in by this template's Dockerfile) - just open the
**TensorBoard** app from LabPod's Apps page (default log directory `/work/runs` shows every
notebook's runs at once).
