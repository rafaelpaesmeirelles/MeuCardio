#!/usr/bin/env bash
# Backup diário/pré-deploy do PostgreSQL. Roda no host e executa pg_dump dentro
# do container, sem expor credenciais adicionais fora do .env.
set -Eeuo pipefail

# O cron pode continuar definindo /opt/meucardio. Durante deploy e testes, o
# projeto é derivado do próprio script ou informado explicitamente por PROJETO.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO="${PROJETO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
DESTINO="${BACKUP_DESTINO:-$PROJETO/infra/backup/dumps}"
RETENCAO_DIAS="${BACKUP_RETENCAO_DIAS:-14}"
COMPOSE=(docker compose -f "$PROJETO/docker-compose.prod.yml")

mkdir -p "$DESTINO"
cd "$PROJETO"

if [[ ! -f .env ]]; then
  echo "Arquivo .env não encontrado em $PROJETO." >&2
  exit 1
fi

# shellcheck disable=SC1091
source .env
: "${POSTGRES_USER:?Defina POSTGRES_USER no .env.}"
: "${POSTGRES_DB:?Defina POSTGRES_DB no .env.}"

DATA="$(date +%Y-%m-%d_%H%M%S)"
ARQUIVO="$DESTINO/meucardio_${DATA}.sql.gz"
TEMPORARIO="${ARQUIVO}.tmp"

umask 077
trap 'rm -f "$TEMPORARIO"' EXIT

echo "[$(date -Is)] Iniciando backup em $ARQUIVO"

if ! "${COMPOSE[@]}" exec -T db \
  pg_dump -U "$POSTGRES_USER" --no-owner --no-privileges "$POSTGRES_DB" \
  | gzip -9 > "$TEMPORARIO"; then
  echo "[$(date -Is)] ERRO: pg_dump falhou. Removendo arquivo parcial." >&2
  exit 1
fi

# Prova mínima de legibilidade antes de publicar o arquivo.
gzip -t "$TEMPORARIO"
mv "$TEMPORARIO" "$ARQUIVO"
chmod 600 "$ARQUIVO"
sha256sum "$ARQUIVO" > "${ARQUIVO}.sha256"
chmod 600 "${ARQUIVO}.sha256"
trap - EXIT

TAMANHO="$(du -h "$ARQUIVO" | cut -f1)"
echo "[$(date -Is)] Backup concluído: $ARQUIVO ($TAMANHO)"

REMOVIDOS="$(find "$DESTINO" -name 'meucardio_*.sql.gz' -mtime "+${RETENCAO_DIAS}" -print -delete | wc -l)"
find "$DESTINO" -name 'meucardio_*.sql.gz.sha256' -mtime "+${RETENCAO_DIAS}" -delete
if [[ "$REMOVIDOS" -gt 0 ]]; then
  echo "[$(date -Is)] Removidos $REMOVIDOS backup(s) com mais de ${RETENCAO_DIAS} dias."
fi

printf '%s\n' "$ARQUIVO"
