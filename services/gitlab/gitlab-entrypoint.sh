#!/usr/bin/env bash
set -euo pipefail

: "${EXTERNAL_URL:=http://localhost:9084}"
: "${TZ:=Asia/Bangkok}"
: "${SSH_PORT:=22}"

# Registry 
: "${REGISTRY_ENABLE:=false}"
: "${REGISTRY_EXTERNAL_URL:=}"   

# SMTP (tuỳ chọn)
: "${SMTP_ENABLE:=false}"
: "${SMTP_ADDRESS:=}"
: "${SMTP_PORT:=587}"
: "${SMTP_USER:=}"
: "${SMTP_PASSWORD:=}"
: "${SMTP_DOMAIN:=}"
: "${SMTP_AUTH:=login}"
: "${SMTP_STARTTLS_AUTO:=true}"

: "${LETSENCRYPT_ENABLE:=false}"

if [[ "${EXTERNAL_URL}" == https://* ]]; then
  LISTEN_HTTPS=true
else
  LISTEN_HTTPS=false
fi

GITLAB_OMNIBUS_CONFIG="${GITLAB_OMNIBUS_CONFIG:-}
external_url '${EXTERNAL_URL}'
gitlab_rails['time_zone'] = '${TZ}'
gitlab_rails['gitlab_shell_ssh_port'] = ${SSH_PORT}
letsencrypt['enable'] = ${LETSENCRYPT_ENABLE}
nginx['listen_https'] = ${LISTEN_HTTPS}
"

if [[ "${REGISTRY_ENABLE}" == "true" ]]; then
  GITLAB_OMNIBUS_CONFIG="${GITLAB_OMNIBUS_CONFIG}
registry['enable'] = true
gitlab_rails['registry_enabled'] = true
"
  if [[ -n "${REGISTRY_EXTERNAL_URL}" ]]; then
    GITLAB_OMNIBUS_CONFIG="${GITLAB_OMNIBUS_CONFIG}
registry_external_url '${REGISTRY_EXTERNAL_URL}'
"
  fi
fi

if [[ "${SMTP_ENABLE}" == "true" ]]; then
  GITLAB_OMNIBUS_CONFIG="${GITLAB_OMNIBUS_CONFIG}
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = '${SMTP_ADDRESS}'
gitlab_rails['smtp_port'] = ${SMTP_PORT}
gitlab_rails['smtp_user_name'] = '${SMTP_USER}'
gitlab_rails['smtp_password'] = '${SMTP_PASSWORD}'
gitlab_rails['smtp_domain'] = '${SMTP_DOMAIN}'
gitlab_rails['smtp_authentication'] = '${SMTP_AUTH}'
gitlab_rails['smtp_enable_starttls_auto'] = ${SMTP_STARTTLS_AUTO}
"
fi

# Disable password policy and set initial root password
GITLAB_OMNIBUS_CONFIG="${GITLAB_OMNIBUS_CONFIG}
gitlab_rails['password_policy_enabled'] = false
gitlab_rails['password_policy_min_length'] = 0
gitlab_rails['password_policy_lowercase_required'] = false
gitlab_rails['password_policy_uppercase_required'] = false
gitlab_rails['password_policy_digit_required'] = false
gitlab_rails['password_policy_symbol_required'] = false
gitlab_rails['password_policy_common_passwords_enabled'] = false
gitlab_rails['initial_root_password'] = 'gitlab123'
"

export GITLAB_OMNIBUS_CONFIG

exec /assets/wrapper
