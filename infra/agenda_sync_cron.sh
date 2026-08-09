#!/usr/bin/env bash
# Sincronização periódica automática das contas externas da CorvIA.
# Instalação no host (a cada 15 minutos):
#   */15 * * * * /opt/meucardio/infra/agenda_sync_cron.sh >> /opt/meucardio/infra/agenda_sync_cron.log 2>&1
#
# O lock evita que uma rodada lenta se sobreponha à seguinte, protegendo
# cursores incrementais, refresh tokens e gravações concorrentes.
set -euo pipefail

PROJETO="/opt/meucardio"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"
LOCKFILE="$PROJETO/infra/agenda_sync_cron.lock"

cd "$PROJETO"

exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "[$(date -Is)] Sincronização anterior ainda em execução; rodada atual ignorada com segurança."
  exit 0
fi

echo "[$(date -Is)] Sincronizando contas externas"
$COMPOSE exec -T backend python -m app.services.agenda_sync_cli
echo "[$(date -Is)] Fim"
