#!/usr/bin/env bash
# Restaura um backup específico. USO RARO E PERIGOSO — apaga o banco atual
# antes de restaurar. Confirma duas vezes de propósito.
#
#   ./infra/backup/restaurar.sh dumps/meucardio_2026-07-24_0300.sql.gz
set -euo pipefail

PROJETO="/opt/meucardio"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"
ARQUIVO="${1:-}"

if [ -z "$ARQUIVO" ] || [ ! -f "$ARQUIVO" ]; then
  echo "Uso: $0 <caminho-do-backup.sql.gz>"
  echo
  echo "Backups disponíveis:"
  ls -lh "$PROJETO/infra/backup/dumps/" 2>/dev/null || echo "  (nenhum encontrado)"
  exit 1
fi

cd "$PROJETO"
# shellcheck disable=SC1091
source .env

echo "ATENÇÃO: isso vai APAGAR o banco atual e substituir pelo conteúdo de:"
echo "  $ARQUIVO"
read -rp "Digite RESTAURAR (maiúsculas) para confirmar: " confirmacao
[ "$confirmacao" = "RESTAURAR" ] || { echo "Cancelado."; exit 1; }

echo "Parando o backend para evitar escrita durante a restauração..."
$COMPOSE stop backend

echo "Recriando o banco vazio..."
$COMPOSE exec -T db psql -U "${POSTGRES_USER}" -d postgres -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"
$COMPOSE exec -T db psql -U "${POSTGRES_USER}" -d postgres -c "CREATE DATABASE ${POSTGRES_DB};"

echo "Restaurando..."
gunzip -c "$ARQUIVO" | $COMPOSE exec -T db psql -U "${POSTGRES_USER}" "${POSTGRES_DB}"

echo "Religando o backend..."
$COMPOSE start backend

echo "Restauração concluída. Confira o site antes de considerar terminado."
