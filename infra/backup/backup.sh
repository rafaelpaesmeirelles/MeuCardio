#!/usr/bin/env bash
# Backup diário do Postgres do MeuCardio. Roda no host via cron, chamando
# pg_dump dentro do container — não precisa de credencial extra no host.
#
# Instalar (uma vez):
#   crontab -e
#   # adicionar a linha:
#   0 3 * * * /opt/meucardio/infra/backup/backup.sh >> /opt/meucardio/infra/backup/backup.log 2>&1
set -euo pipefail

PROJETO="/opt/meucardio"
DESTINO="$PROJETO/infra/backup/dumps"
RETENCAO_DIAS=14
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"

mkdir -p "$DESTINO"
cd "$PROJETO"

# shellcheck disable=SC1091
source .env
DATA=$(date +%Y-%m-%d_%H%M)
ARQUIVO="$DESTINO/meucardio_${DATA}.sql.gz"

echo "[$(date -Is)] Iniciando backup em $ARQUIVO"

if ! $COMPOSE exec -T db pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "$ARQUIVO.tmp"; then
  echo "[$(date -Is)] ERRO: pg_dump falhou. Removendo arquivo parcial."
  rm -f "$ARQUIVO.tmp"
  exit 1
fi
mv "$ARQUIVO.tmp" "$ARQUIVO"

TAMANHO=$(du -h "$ARQUIVO" | cut -f1)
echo "[$(date -Is)] Backup concluído: $ARQUIVO ($TAMANHO)"

# remove backups mais velhos que a retenção configurada
REMOVIDOS=$(find "$DESTINO" -name "meucardio_*.sql.gz" -mtime "+${RETENCAO_DIAS}" -print -delete | wc -l)
[ "$REMOVIDOS" -gt 0 ] && echo "[$(date -Is)] Removidos $REMOVIDOS backup(s) com mais de ${RETENCAO_DIAS} dias."

echo "[$(date -Is)] Backups atuais:"
ls -lh "$DESTINO" | tail -n +2
