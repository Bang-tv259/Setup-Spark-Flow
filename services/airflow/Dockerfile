ARG AIRFLOW_IMAGE=apache/airflow:slim-2.10.5-python3.12

FROM ${AIRFLOW_IMAGE}

USER root

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates curl wget git \
      iproute2 iputils-ping dnsutils netcat-traditional \
      procps lsof jq less vim-tiny nano \
      openssl tzdata; \
    rm -rf /var/lib/apt/lists/*

# Optional certs 
# COPY certs/ /tmp/certs/
# RUN set -eux; \
#     if [ -d /tmp/certs ] && ls -1 /tmp/certs/*.crt >/dev/null 2>&1; then \
#       cp /tmp/certs/*.crt /usr/local/share/ca-certificates/; \
#       update-ca-certificates; \
#     fi; \
#     rm -rf /tmp/certs

# Install Spark 3.5.7 (precompiled for Hadoop 3)
# Set Spark environment
ENV SPARK_VERSION=3.5.7
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Copy offline Spark tarball and extract
COPY ./spark/spark-3.5.7-bin-hadoop3.tgz /tmp/
RUN mkdir -p $SPARK_HOME && \
    tar -xzf /tmp/spark-3.5.7-bin-hadoop3.tgz -C $SPARK_HOME --strip-components=1 && \
    rm /tmp/spark-3.5.7-bin-hadoop3.tgz

# Preload Hadoop + AWS dependencies
RUN mkdir -p $SPARK_HOME/jars && \
    wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P $SPARK_HOME/jars && \
    wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.517/aws-java-sdk-bundle-1.12.517.jar -P $SPARK_HOME/jars && \
    wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar -P $SPARK_HOME/jars && \
    wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.4/hadoop-client-3.3.4.jar -P $SPARK_HOME/jars

# Set JAVA_HOME
RUN apt-get update && apt-get install -y openjdk-17-jdk-headless
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow
RUN set -eux; \
    pip install --no-cache-dir --upgrade pip; \
    pip install --no-cache-dir --constraint /home/airflow/constraints.txt \
      apache-airflow-providers-cncf-kubernetes \
      apache-airflow-providers-celery \
      apache-airflow-providers-postgres \
      apache-airflow-providers-amazon \
      apache-airflow-providers-apache-spark \
      apache-airflow-providers-fab \
      apache-airflow-providers-http \
      psycopg2-binary

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# To build the image:
# docker build -f ./services/airflow/Dockerfile -t my-airflow-py312:20250112_1800 ./services/airflow/

# To save the image to a compressed tar file:
# docker save my-airflow-py312:20250112_1800 | gzip > ./docker_image/my-airflow-py312_20250112_1800.tar.gz