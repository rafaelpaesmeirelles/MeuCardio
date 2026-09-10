#!/usr/bin/env bash
# Entrada de contingência para o radar adaptativo de publicações desde
# 10/08/2026. A rotina só cria o alerta factual e a fila de revisão; não altera
# automaticamente recomendações ou conteúdo clínico.
#
# Produção usa o serviço supervisionado intelligence-radar (4h / 1h em picos).
# Não instalar um segundo cron: esta entrada compartilha a trava/cadência do
# worker e permanece disponível para manutenção operacional autorizada.
set -euo pipefail

PROJETO="/opt/meucardio"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"

cd "$PROJETO"
echo "[$(date -Is)] Checando novas diretrizes oficiais"
$COMPOSE exec -T backend python -m app.services.guideline_discovery_cli
echo "[$(date -Is)] Fim"
