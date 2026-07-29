ARG LABPOD_BASE_IMAGE=ghcr.io/labpod/scipy-jupyter:py312
FROM ${LABPOD_BASE_IMAGE}

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --no-cache -r /tmp/requirements.txt
