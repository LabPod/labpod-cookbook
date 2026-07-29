ARG LABPOD_BASE_IMAGE=ghcr.io/labpod/pytorch-jupyter:cu126
FROM ${LABPOD_BASE_IMAGE}

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --no-cache -r /tmp/requirements.txt
