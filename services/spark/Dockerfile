FROM spark:3.5.7

USER root

ARG PYTHON_VERSION=3.12.9

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        ca-certificates \
        git \
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
    python3.12 -m ensurepip; \
    python3.12 -m pip install --no-cache-dir --upgrade pip setuptools wheel; \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python3; \
    ln -sf /usr/local/bin/python3.12 /usr/bin/python; \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3; \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip

COPY requirements.txt /tmp/requirements.txt

RUN set -eux; \
    if [ -s /tmp/requirements.txt ]; then \
        python -m pip install --no-cache-dir -r /tmp/requirements.txt; \
    fi; \
    rm -f /tmp/requirements.txt

ENV PYSPARK_PYTHON=/usr/bin/python

# OpenSSL 1.1 runtime for Spark native library
RUN apt-get update && \
    apt-get install -y wget && \
    wget http://archive.debian.org/debian/pool/main/o/openssl/libssl1.1_1.1.1w-0+deb11u1_amd64.deb && \
    dpkg -i libssl1.1_1.1.1w-0+deb11u1_amd64.deb && \
    rm libssl1.1_1.1.1w-0+deb11u1_amd64.deb

# Preload Spark Hadoop + AWS dependencies
RUN mkdir -p /opt/spark/jars && \
    wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P /opt/spark/jars && \
    wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.517/aws-java-sdk-bundle-1.12.517.jar -P /opt/spark/jars && \
    wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar -P /opt/spark/jars && \
    wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.4/hadoop-client-3.3.4.jar -P /opt/spark/jars

# To build the image:
# docker build -f ./services/spark/Dockerfile -t my-spark-py312:20253011_0900 ./services/spark/

# To save the image to a compressed tar file:
# docker save my-spark-py312:20253011_0900 | gzip > ./docker_image/my-spark-py312_20253011_0900.tar.gz