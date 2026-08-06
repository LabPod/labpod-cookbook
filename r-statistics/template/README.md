# R Statistics (Cookbook)

An R-first statistics workspace with Python alongside: RStudio Server for
the R work, JupyterLab for notebooks (R **and** Python kernels), and one
shared Python interpreter so `reticulate` and `arrow` move data between the
two without a second environment.

CPU-only. Classical statistics — mixed models, GAMs, survival, MCMC — is
CPU/RAM bound, so this template defaults to no GPU.

The bundle prepares the unchanged definition by pulling the immutable prebuilt image; its
**approximate pull size is 2.8 GB**. The complete Dockerfile and package lists remain available
for review, customization, air-gapped fallback, and a local build when the definition changes.

## Installed

**R 4.5 (rocker/tidyverse base: tidyverse, RStudio Server, Quarto)**

- Modeling: `lme4`, `lmerTest`, `nlme`, `mgcv`, `survival`, `survminer`,
  `glmnet`, `car`, `sandwich`, `lmtest`
- Inference and reporting: `emmeans`, `marginaleffects`, `broom`,
  `broom.mixed`, `performance`
- Machine learning: `tidymodels`, `ranger`, `xgboost`
- Time series: `forecast`, `fable`, `tsibble`, `feasts`
- Latent variable / missing data: `lavaan`, `psych`, `mice`
- Data and interop: `data.table`, `arrow`, `reticulate`, `IRkernel`

**Python 3 (`/opt/venv`, on `PATH`)**

- `jupyterlab`, `ipywidgets`, `jupyter-resource-usage`
- `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn`,
  `matplotlib`, `seaborn`, `pyarrow`, `polars`

`RETICULATE_PYTHON` points at that venv, so `reticulate::import("pandas")`
from R and `import pandas` in the Python kernel are the same install.

## Launchers and ports

- `rstudio`: RStudio Server on container port `8787`. Runs rootless as the
  workspace owner with `--auth-none` — LabPod's reverse proxy (JWT +
  workspace-owner check) is the access boundary, exactly as for the other
  launchers.
- `jupyter`: JupyterLab on container port `8888` (primary). Pick the **R**
  or **Python 3** kernel per notebook.

## Usage

Import the bundle, let LabPod pull the published image, enable the template, then create a
workspace. Work under `/work` — it persists across workspace stop/start,
and your R session state lands in the workspace's persistent home.

## Adding heavier pieces

Both are deliberately left out to keep the build lean; add either to the
template's build context and rebuild.

- **Bayesian (`brms`)** — add `brms` and `rstan` to `r-packages.txt`. Stan
  compiles each model at run time, so expect a slow first fit per model.
- **GPU deep learning in Python** — add
  `torch --index-url https://download.pytorch.org/whl/cu126` to
  `requirements.txt` and allocate a GPU to the workspace. The pip wheels
  ship their own CUDA runtime, so the CPU base image is not a limitation.
  For serious deep learning work prefer LabPod's PyTorch template or this
  cookbook's `pytorch-scientific-ml` bundle.

## Verification

Built and run against real Podman on a Linux host with LabPod's workspace
security flags (`--cap-drop=ALL`, `--security-opt no-new-privileges`,
`--userns=keep-id`, non-root owner uid, loopback-only port publishing):

- the R package set installs from the base image's P3M binary CRAN repo and
  every listed package is checked present at build time;
- `reticulate` resolves the bundled venv (checked at build time);
- rootless `rserver` starts, `--auth-none` issues the session cookie,
  `rsession` spawns as the workspace owner, and RStudio's session state is
  written to the owner's **persistent** home — including on a host where the
  owner's Linux account is uid 1000, which the rocker base otherwise bakes as
  `rstudio` (that clash sends the R library and preferences into the throwaway
  container layer, so the image frees the uid);
- JupyterLab serves with both the `ir` and `python3` kernels registered.

RStudio serves at the server root and only *generates* URLs under
`--www-root-path`, so the `rstudio` port sets `proxy_strip_prefix: true` —
LabPod strips `/ws/<id>/rstudio` before forwarding, and RStudio's own
prefixed redirects and cookies pass through unchanged.
