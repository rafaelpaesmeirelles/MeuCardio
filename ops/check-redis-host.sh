#!/usr/bin/env bash
set -euo pipefail

# Valida o requisito de kernel recomendado pelo Redis para fork de background
# (RDB/AOF/replicação). O script é somente-leitura: nunca tenta alterar sysctl
# nem requer privilégios administrativos.
readonly VALUE_PATH="${OVERCOMMIT_MEMORY_PATH:-/proc/sys/vm/overcommit_memory}"

json_escape() {
  local value=${1-}
  value=${value//\\/\\\\}
  value=${value//\"/\\\"}
  value=${value//$'\n'/\\n}
  printf '%s' "$value"
}

emit() {
  local status=$1
  local code=$2
  local message=$3
  local value=${4-}
  printf '{"status":"%s","code":"%s","overcommit_memory":"%s","message":"%s"}\n' \
    "$(json_escape "$status")" \
    "$(json_escape "$code")" \
    "$(json_escape "$value")" \
    "$(json_escape "$message")"
}

if [[ ! -r "$VALUE_PATH" ]]; then
  emit "error" "OVERCOMMIT_UNREADABLE" \
    "Não foi possível ler $VALUE_PATH; execute o preflight no host Linux que executará o Redis."
  exit 3
fi

value=$(tr -d '[:space:]' < "$VALUE_PATH")
if [[ ! "$value" =~ ^[0-2]$ ]]; then
  emit "error" "OVERCOMMIT_INVALID" \
    "O valor de vm.overcommit_memory não é reconhecido." "$value"
  exit 3
fi

if [[ "$value" != "1" ]]; then
  emit "blocked" "OVERCOMMIT_NOT_ENABLED" \
    "Redis requer vm.overcommit_memory=1 no host. Aplique via sysctl e persista em /etc/sysctl.d antes do deploy." "$value"
  exit 2
fi

emit "ok" "REDIS_HOST_READY" \
  "Host apto para operações de background do Redis." "$value"
