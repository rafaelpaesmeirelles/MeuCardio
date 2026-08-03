#!/usr/bin/env bash
set -Eeuo pipefail

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Comando obrigatório ausente: $1" >&2
    exit 2
  }
}

require_command pg_dump
require_command pg_restore
require_command sha256sum

: "${PGDATABASE:?Defina PGDATABASE.}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_PREFIX="${BACKUP_PREFIX:-corvia}"
ALLOW_UNENCRYPTED_BACKUP="${ALLOW_UNENCRYPTED_BACKUP:-0}"
BACKUP_AGE_RECIPIENT="${BACKUP_AGE_RECIPIENT:-}"

umask 077
mkdir -p "$BACKUP_DIR"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BASE_NAME="${BACKUP_PREFIX}-${PGDATABASE}-${TIMESTAMP}"
TMP_DUMP="$(mktemp "${BACKUP_DIR}/.${BASE_NAME}.XXXXXX.dump")"
trap 'rm -f "$TMP_DUMP"' EXIT

pg_dump \
  --format=custom \
  --compress=9 \
  --no-owner \
  --no-privileges \
  --file "$TMP_DUMP"

# Garante que o arquivo custom está estruturalmente legível antes de publicá-lo.
pg_restore --list "$TMP_DUMP" >/dev/null

if [[ -n "$BACKUP_AGE_RECIPIENT" ]]; then
  require_command age
  OUTPUT_FILE="${BACKUP_DIR}/${BASE_NAME}.dump.age"
  age --recipient "$BACKUP_AGE_RECIPIENT" --output "$OUTPUT_FILE" "$TMP_DUMP"
else
  if [[ "$ALLOW_UNENCRYPTED_BACKUP" != "1" ]]; then
    echo "Backup não será salvo sem criptografia. Defina BACKUP_AGE_RECIPIENT." >&2
    echo "Somente testes isolados podem usar ALLOW_UNENCRYPTED_BACKUP=1." >&2
    exit 3
  fi
  OUTPUT_FILE="${BACKUP_DIR}/${BASE_NAME}.dump"
  mv "$TMP_DUMP" "$OUTPUT_FILE"
fi

chmod 600 "$OUTPUT_FILE"
(
  cd "$(dirname "$OUTPUT_FILE")"
  sha256sum "$(basename "$OUTPUT_FILE")" > "$(basename "$OUTPUT_FILE").sha256"
  chmod 600 "$(basename "$OUTPUT_FILE").sha256"
)

trap - EXIT
printf '%s\n' "$OUTPUT_FILE"
