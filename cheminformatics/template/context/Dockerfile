ARG LABPOD_BASE_IMAGE=ghcr.io/labpod/scipy-jupyter:v1-py312
FROM ${LABPOD_BASE_IMAGE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends libx11-6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --no-cache -r /tmp/requirements.txt
