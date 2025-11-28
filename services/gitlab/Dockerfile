ARG GITLAB_TAG=17.6.0-ce.0
FROM gitlab/gitlab-ce:${GITLAB_TAG}

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates curl jq vim-tiny less \
      iproute2 net-tools dnsutils procps lsof \
      openssl tzdata; \
    rm -rf /var/lib/apt/lists/*

COPY certs/ /usr/local/share/ca-certificates/custom/
RUN set -eux; \
    if [ -d /usr/local/share/ca-certificates/custom ] && \
       [ "$(find /usr/local/share/ca-certificates/custom -type f -name '*.crt' | wc -l)" -gt 0 ]; then \
      update-ca-certificates; \
    fi

COPY gitlab-entrypoint.sh /usr/local/bin/gitlab-entrypoint.sh
RUN chmod +x /usr/local/bin/gitlab-entrypoint.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=2m --retries=5 \
  CMD curl -fsS http://127.0.0.1/-/health || exit 1

EXPOSE 80 443 22
ENTRYPOINT ["/usr/local/bin/gitlab-entrypoint.sh"]

# To build the image:
# docker build -f ./services/gitlab/Dockerfile -t my-gitlab:20252911_0900 ./services/gitlab/