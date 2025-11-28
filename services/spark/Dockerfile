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
        uuid-dev; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    cd /tmp; \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz; \
    tar -xzf Python-${PYTHON_VERSION}.tgz; \
    cd Python-${PYTHON_VERSION}; \
    ./configure --enable-optimizations; \
    make -j"$(nproc)"; \
    make altinstall; \
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
    if [ -s /tmp/requirements.txt ]; then \
        python -m pip install --no-cache-dir -r /tmp/requirements.txt; \
    fi; \
    rm -f /tmp/requirements.txt

ENV PYSPARK_PYTHON=/usr/bin/python

# To build the image:
# docker build -f ./services/spark/Dockerfile -t my-spark-py313:20252911_0900 ./services/spark/