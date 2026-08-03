#!/usr/bin/env bash
set -Eeuo pipefail

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Comando obrigatório ausente: $1" >&2
    exit 2
  }
}

require_command docker
require_command tar
require_command sha256sum

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_PREFIX="${BACKUP_PREFIX:-corvia}"
ALLOW_UNENCRYPTED_BACKUP="${ALLOW_UNENCRYPTED_BACKUP:-0}"
BACKUP_AGE_RECIPIENT="${BACKUP_AGE_RECIPIENT:-}"

BACKEND_CONTAINER="$(docker compose -f "$COMPOSE_FILE" ps -q backend)"
if [[ -z "$BACKEND_CONTAINER" ]]; then
  echo "Container backend não encontrado em $COMPOSE_FILE." >&2
  exit 3
fi

umask 077
mkdir -p "$BACKUP_DIR"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BASE_NAME="${BACKUP_PREFIX}-clinical-files-${TIMESTAMP}"
TMP_ARCHIVE="$(mktemp "${BACKUP_DIR}/.${BASE_NAME}.XXXXXX.tar.gz")"
trap 'rm -f "$TMP_ARCHIVE"' EXIT

# Usa os mesmos volumes montados no backend, mas em um container efêmero e
# somente-leitura. Os diretórios não publicados pelo Caddy continuam privados.
docker run --rm \
  --volumes-from "${BACKEND_CONTAINER}:ro" \
  alpine:3.20 \
  tar -C / -czf - \
    uploads \
    exames-pacientes \
    documentos-emitidos \
    materiais-curso \
  > "$TMP_ARCHIVE"

tar -tzf "$TMP_ARCHIVE" >/dev/null

if [[ -n "$BACKUP_AGE_RECIPIENT" ]]; then
  require_command age
  OUTPUT_FILE="${BACKUP_DIR}/${BASE_NAME}.tar.gz.age"
  age --recipient "$BACKUP_AGE_RECIPIENT" --output "$OUTPUT_FILE" "$TMP_ARCHIVE"
else
  if [[ "$ALLOW_UNENCRYPTED_BACKUP" != "1" ]]; then
    echo "Backup clínico não será salvo sem criptografia. Defina BACKUP_AGE_RECIPIENT." >&2
    exit 4
  fi
  OUTPUT_FILE="${BACKUP_DIR}/${BASE_NAME}.tar.gz"
  mv "$TMP_ARCHIVE" "$OUTPUT_FILE"
fi

chmod 600 "$OUTPUT_FILE"
(
  cd "$(dirname "$OUTPUT_FILE")"
  sha256sum "$(basename "$OUTPUT_FILE")" > "$(basename "$OUTPUT_FILE").sha256"
  chmod 600 "$(basename "$OUTPUT_FILE").sha256"
)

trap - EXIT
printf '%s\n' "$OUTPUT_FILE"
