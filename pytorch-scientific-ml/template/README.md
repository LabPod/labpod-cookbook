# PyTorch Scientific ML (Cookbook)

Pull-only environment - `quay.io/jupyter/pytorch-notebook:cuda12-python-3.11`, no custom build.
Same image as LabPod's built-in "PyTorch JupyterLab" template, packaged standalone so these
cookbooks work even on a LabPod install where that managed template is disabled.

Shared by several notebooks - build this template once, then run any of them:

- `notebooks/gpu-basics.ipynb` - confirm the GPU is visible, a CPU-vs-GPU benchmark, a tiny
  training loop.
- `notebooks/neural-operator.ipynb` - a minimal Fourier Neural Operator.
- `notebooks/pinn.ipynb` - a physics-informed neural network.
- `notebooks/unet.ipynb` - a small U-Net for segmentation.
- `notebooks/diffusion.ipynb` - a minimal denoising diffusion model.

All use synthetic/toy data generated in the notebook - no dataset download required, so these
work on an offline / air-gapped workspace too.

After building and starting a workspace from this template, get the notebooks:

```bash
git clone https://github.com/LabPod/labpod-cookbook /work/labpod-cookbook
```

Then open any notebook under
`/work/labpod-cookbook/pytorch-scientific-ml/notebooks/` in JupyterLab.
