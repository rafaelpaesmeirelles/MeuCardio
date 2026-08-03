#!/usr/bin/env bash
set -Eeuo pipefail

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Comando obrigatório ausente: $1" >&2
    exit 2
  }
}

require_command pg_restore
require_command sha256sum

BACKUP_FILE="${1:-}"
: "${BACKUP_FILE:?Uso: ops/restore-postgres.sh CAMINHO_DO_BACKUP}"
: "${TARGET_PGDATABASE:?Defina TARGET_PGDATABASE com o banco de destino já criado.}"
: "${CONFIRM_RESTORE_TARGET:?Repita o banco de destino em CONFIRM_RESTORE_TARGET.}"

if [[ "$CONFIRM_RESTORE_TARGET" != "$TARGET_PGDATABASE" ]]; then
  echo "Confirmação divergente; restauração cancelada." >&2
  exit 3
fi
if [[ -n "${PGDATABASE:-}" && "$TARGET_PGDATABASE" == "$PGDATABASE" ]]; then
  echo "O destino não pode ser o mesmo banco configurado em PGDATABASE." >&2
  exit 3
fi
if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup não encontrado: $BACKUP_FILE" >&2
  exit 4
fi

CHECKSUM_FILE="${BACKUP_FILE}.sha256"
if [[ -f "$CHECKSUM_FILE" ]]; then
  (
    cd "$(dirname "$BACKUP_FILE")"
    sha256sum --check "$(basename "$CHECKSUM_FILE")"
  )
else
  echo "Arquivo de checksum ausente: $CHECKSUM_FILE" >&2
  exit 4
fi

RESTORE_INPUT="$BACKUP_FILE"
TMP_DUMP=""
cleanup() {
  if [[ -n "$TMP_DUMP" ]]; then
    rm -f "$TMP_DUMP"
  fi
  return 0
}
trap cleanup EXIT

if [[ "$BACKUP_FILE" == *.age ]]; then
  require_command age
  : "${BACKUP_AGE_IDENTITY:?Defina BACKUP_AGE_IDENTITY para descriptografar o backup.}"
  TMP_DUMP="$(mktemp)"
  age --decrypt --identity "$BACKUP_AGE_IDENTITY" --output "$TMP_DUMP" "$BACKUP_FILE"
  RESTORE_INPUT="$TMP_DUMP"
fi

# Verifica o catálogo antes de modificar o banco de destino.
pg_restore --list "$RESTORE_INPUT" >/dev/null

PGDATABASE="$TARGET_PGDATABASE" pg_restore \
  --exit-on-error \
  --no-owner \
  --no-privileges \
  --dbname "$TARGET_PGDATABASE" \
  "$RESTORE_INPUT"

# Um dump restaurado sem a versão Alembic não representa uma recuperação válida.
PGDATABASE="$TARGET_PGDATABASE" psql \
  --no-psqlrc \
  --tuples-only \
  --command "SELECT version_num FROM alembic_version;" >/dev/null

printf 'Restauração validada no banco %s.\n' "$TARGET_PGDATABASE"
