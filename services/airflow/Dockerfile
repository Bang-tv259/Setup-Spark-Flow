ARG AIRFLOW_IMAGE=apache/airflow:slim-latest-python3.13
FROM ${AIRFLOW_IMAGE}

USER root

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates curl wget \
      iproute2 iputils-ping dnsutils netcat-traditional \
      procps lsof jq less vim-tiny \
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

USER airflow

RUN set -eux; \
    pip install --no-cache-dir --upgrade pip; \
    pip install --no-cache-dir --constraint /home/airflow/constraints.txt \
      apache-airflow-providers-cncf-kubernetes \
      apache-airflow-providers-celery \
      apache-airflow-providers-postgres \
      apache-airflow-providers-amazon \
      apache-airflow-providers-apache-spark \
      apache-airflow-providers-http \
      psycopg2-binary

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# To build the image:
# docker build -f ./services/airflow/Dockerfile -t my-airflow-py313:20252911_0900 ./services/airflow/