#!/usr/bin/env bash
# Descoberta diária de novas diretrizes oficiais publicadas a partir de
# 10/08/2026. A rotina só cria o alerta factual e a fila de revisão; não altera
# automaticamente recomendações ou conteúdo clínico.
#
# Instalar no host de produção após o deploy:
#   crontab -e
#   30 7 * * * /opt/meucardio/infra/guideline_cron.sh >> /opt/meucardio/infra/guideline_cron.log 2>&1
set -euo pipefail

PROJETO="/opt/meucardio"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"

cd "$PROJETO"
echo "[$(date -Is)] Checando novas diretrizes oficiais"
$COMPOSE exec -T backend python -m app.services.guideline_discovery_cli
echo "[$(date -Is)] Fim"
