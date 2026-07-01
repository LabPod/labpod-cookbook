# MATLAB (with Deep Learning Toolbox) browser workspace via MathWorks
# matlab-proxy. Mirrors LabPod's built-in tmpl-matlab-proxy exactly, except
# the base image: mathworks/matlab-deep-learning (not plain mathworks/matlab)
# so Deep Learning Toolbox / trainnet actually work - the plain matlab image
# does not include it.
#
# BRING YOUR OWN LICENSE, with Deep Learning Toolbox and Parallel Computing
# Toolbox entitlements specifically - a base MATLAB-only license is not
# enough for this image's examples. Reach it via a network license manager
# (MLM_LICENSE_FILE=port@host) or MathWorks online licensing at runtime.
#
# Pick the MATLAB_RELEASE tag your license supports.
ARG MATLAB_RELEASE=r2024b
FROM docker.io/mathworks/matlab-deep-learning:${MATLAB_RELEASE}

USER root
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages matlab-proxy \
    && matlab-proxy-app --version

WORKDIR /work
EXPOSE 8888

ENV PATH=/opt/matlab/bin:${PATH}

ENTRYPOINT ["sleep", "infinity"]
