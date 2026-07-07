FROM quay.io/jupyter/scipy-notebook:python-3.11

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --prefer-binary -r /tmp/requirements.txt
