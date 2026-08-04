#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$ROOT_DIR/ops/check-redis-host.sh"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

expect_status() {
  local expected=$1
  local value_file=$2
  local output_file=$3
  set +e
  OVERCOMMIT_MEMORY_PATH="$value_file" bash "$SCRIPT" > "$output_file"
  local actual=$?
  set -e
  if [[ "$actual" -ne "$expected" ]]; then
    printf 'Status inesperado: esperado=%s atual=%s saída=%s\n' \
      "$expected" "$actual" "$(cat "$output_file")" >&2
    exit 1
  fi
}

printf '1\n' > "$TMP_DIR/enabled"
expect_status 0 "$TMP_DIR/enabled" "$TMP_DIR/ok.json"
grep -Fq '"code":"REDIS_HOST_READY"' "$TMP_DIR/ok.json"
grep -Fq '"overcommit_memory":"1"' "$TMP_DIR/ok.json"

printf '0\n' > "$TMP_DIR/disabled"
expect_status 2 "$TMP_DIR/disabled" "$TMP_DIR/blocked.json"
grep -Fq '"code":"OVERCOMMIT_NOT_ENABLED"' "$TMP_DIR/blocked.json"

printf 'invalido\n' > "$TMP_DIR/invalid"
expect_status 3 "$TMP_DIR/invalid" "$TMP_DIR/invalid.json"
grep -Fq '"code":"OVERCOMMIT_INVALID"' "$TMP_DIR/invalid.json"

expect_status 3 "$TMP_DIR/ausente" "$TMP_DIR/missing.json"
grep -Fq '"code":"OVERCOMMIT_UNREADABLE"' "$TMP_DIR/missing.json"

printf 'Preflight Redis aprovado: estados pronto, bloqueado, inválido e ilegível.\n'
