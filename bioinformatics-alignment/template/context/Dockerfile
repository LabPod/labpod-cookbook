# Read-alignment basics: JupyterLab plus samtools and bwa, the two most
# standard command-line tools in short-read genomics. Both are stable,
# long-standing Ubuntu packages - installed via apt, not built from source.
ARG LABPOD_BASE_IMAGE=ghcr.io/labpod/scipy-jupyter:v1-py312
FROM ${LABPOD_BASE_IMAGE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends samtools bwa \
    && rm -rf /var/lib/apt/lists/*
