# R statistics workspace: R-first, Python alongside.
#
# The base is rocker's CPU line, not rocker/ml: rocker/ml is 6.2 GB
# compressed and stops at R 4.4.1 / CUDA 11.8, while the CPU line tracks
# current R (4.5.3, 0.9 GB) and carries the same P3M binary CRAN repo, so
# install.packages() unpacks binaries instead of compiling. Classical
# statistics is CPU/RAM bound; for GPU deep learning use LabPod's PyTorch
# template or this cookbook's pytorch-scientific-ml bundle. If you do want
# GPU torch here, add `torch --index-url https://download.pytorch.org/whl/cu126`
# to requirements.txt — the pip wheels ship their own CUDA runtime, so no
# CUDA base image is needed.
ARG BASE_IMAGE=docker.io/rocker/tidyverse:4.5.3
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive

# rocker bakes uid 1000 as `rstudio`. LabPod runs the container as the workspace
# owner and passes a --passwd-entry naming that owner, but Podman keeps the
# image's existing line when the uid is taken. An owner on uid 1000 then gets
# the baked account's identity: RStudio resolves the session home through
# getpwuid(), lands on /home/rstudio inside the throwaway container layer
# instead of the persistent home LabPod mounts, and every R package, preference
# and saved file is discarded on Stop with no error. Free the uid so LabPod's
# entry always wins.
RUN userdel rstudio 2>/dev/null || true; rm -rf /home/rstudio

# libzmq5 is a runtime dependency of pbdZMQ (IRkernel's ZMQ transport):
# the P3M binary package links against it but does not carry it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        libzmq5 \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
        tmux \
        vim \
    && rm -rf /var/lib/apt/lists/*

# One Python interpreter for everything: the JupyterLab server, the
# python3 kernel, and reticulate. Splitting them is the usual way an
# R+Python image ends up with `import pandas` working in a notebook but
# not from R.
ENV VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    RETICULATE_PYTHON=/opt/venv/bin/python

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages uv \
    && uv venv "$VIRTUAL_ENV" \
    && uv pip install --no-cache -r /tmp/requirements.txt \
    && python -c "import pandas, statsmodels, sklearn, pyarrow"

COPY r-packages.txt /tmp/r-packages.txt
RUN Rscript -e 'p <- trimws(readLines("/tmp/r-packages.txt")); \
      p <- p[nzchar(p) & !startsWith(p, "#")]; \
      install.packages(p, Ncpus = max(1L, parallel::detectCores())); \
      missing <- setdiff(p, rownames(installed.packages())); \
      if (length(missing)) stop("failed to install: ", paste(missing, collapse = ", "))'

# P3M binary packages link against system libraries they don't carry, so a
# package can install cleanly and still fail to load. Load every requested
# package here rather than leaving that for someone's first notebook.
RUN Rscript -e 'p <- trimws(readLines("/tmp/r-packages.txt")); \
      p <- p[nzchar(p) & !startsWith(p, "#")]; \
      bad <- p[!vapply(p, requireNamespace, logical(1), quietly = TRUE)]; \
      if (length(bad)) stop("failed to load: ", paste(bad, collapse = ", "))'

# System-wide (user=FALSE) so JupyterLab finds the R kernel whichever
# Linux account owns the workspace.
RUN Rscript -e 'IRkernel::installspec(user = FALSE)'

# reticulate resolves the venv above; check the R -> Python bridge at
# build time rather than leaving it for the first notebook to discover.
RUN Rscript -e 'library(reticulate); print(py_config()$python); \
      stopifnot(py_eval("1 + 1") == 2)'

COPY labpod-rstudio.sh /usr/local/bin/labpod-rstudio
RUN chmod 0755 /usr/local/bin/labpod-rstudio

WORKDIR /work
EXPOSE 8888 8787

ENTRYPOINT ["sleep", "infinity"]
