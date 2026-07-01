# Read-alignment basics: JupyterLab plus samtools and bwa, the two most
# standard command-line tools in short-read genomics. Both are stable,
# long-standing Ubuntu packages - installed via apt, not built from source.
FROM quay.io/jupyter/scipy-notebook:python-3.11

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends samtools bwa \
    && rm -rf /var/lib/apt/lists/*
USER ${NB_UID}
