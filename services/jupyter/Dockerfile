FROM spark:3.5.7

USER root

ARG PYTHON_VERSION=3.13.7

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        ca-certificates \
        libssl-dev \
        zlib1g-dev \
        libncurses5-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libffi-dev \
        liblzma-dev \
        tk-dev \
        uuid-dev \
        python3 \
        python3-pip \
        tini; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    cd /tmp; \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz; \
    tar -xzf Python-${PYTHON_VERSION}.tgz; \
    cd Python-${PYTHON_VERSION}; \
    ./configure --enable-optimizations; \
    make -j"$(nproc)"; \
    make altinstall; \
    ldconfig; \
    cd /; \
    rm -rf /tmp/Python-${PYTHON_VERSION}*

RUN set -eux; \
    python3.13 -m ensurepip; \
    python3.13 -m pip install --no-cache-dir --upgrade pip setuptools wheel; \
    ln -sf /usr/local/bin/python3.13 /usr/bin/python3; \
    ln -sf /usr/local/bin/python3.13 /usr/bin/python; \
    ln -sf /usr/local/bin/pip3.13 /usr/bin/pip3; \
    ln -sf /usr/local/bin/pip3.13 /usr/bin/pip

COPY requirements.txt /tmp/requirements.txt

RUN set -eux; \
    python -m pip install --no-cache-dir \
        jupyterlab \
        notebook \
        ipykernel \
        pandas \
        findspark; \
    if [ -f /tmp/requirements.txt ]; then \
        python -m pip install --no-cache-dir -r /tmp/requirements.txt; \
    fi; \
    rm -f /tmp/requirements.txt

RUN set -eux; \
    ln -sf "$(ls /opt/spark/python/lib/py4j*-src.zip | head -n1)" /opt/spark/python/lib/py4j.zip

ENV SPARK_HOME=/opt/spark
ENV PYSPARK_PYTHON=/usr/bin/python
ENV PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j.zip

WORKDIR /work

ENTRYPOINT ["/usr/bin/tini","--"]

# To build the image:
# docker build -f ./services/jupyter/Dockerfile -t my-jupyter:20252911_0900 ./services/jupyter/

