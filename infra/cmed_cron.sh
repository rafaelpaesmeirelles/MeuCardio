#!/usr/bin/env bash
# Atualização diária da lista de preços da CMED (Tarefa A, CLAUDE.md). Roda
# no host via cron, chamando o mesmo caminho de código da rota
# POST /api/admin/cmed/atualizar — só baixa de novo se o timestamp da lista
# mudou, então rodar todo dia é barato quando não há novidade.
#
# Instalar (uma vez):
#   crontab -e
#   # adicionar a linha:
#   0 6 * * * /opt/meucardio/infra/cmed_cron.sh >> /opt/meucardio/infra/cmed_cron.log 2>&1
set -euo pipefail

PROJETO="/opt/meucardio"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"

cd "$PROJETO"
echo "[$(date -Is)] Checando atualização da CMED"
$COMPOSE exec -T backend python -m app.services.cmed_precos_cli
echo "[$(date -Is)] Fim"
