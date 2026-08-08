#!/usr/bin/env bash
# Sincronização periódica automática das contas de Agenda/Contatos conectadas
# (Google/Microsoft/Apple/Yahoo). Pedido do Rafael em 08/08/2026: manter as
# contas sempre sincronizadas e o conteúdo sempre atualizado, sem depender de
# alguém clicar em "Sincronizar agora". Mesmo padrão de cron dos outros dois
# jobs deste projeto (cmed_cron.sh, guideline_cron.sh) — script no host,
# chamando o mesmo caminho de código via `docker compose exec`.
#
# Instalar (uma vez):
#   crontab -e
#   # adicionar a linha (a cada 15 minutos):
#   */15 * * * * /opt/meucardio/infra/agenda_sync_cron.sh >> /opt/meucardio/infra/agenda_sync_cron.log 2>&1
#
# O que isto NÃO faz: reconectar uma conta cujo acesso foi revogado pelo
# próprio usuário ou pelo provedor. Isso sempre vai exigir passar pela tela
# "Sincronize suas contas" e clicar em "Reconectar" de novo — é a segurança
# do OAuth funcionando como desenhado, nenhum script deve tentar contornar.
set -euo pipefail

PROJETO="/opt/meucardio"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"

cd "$PROJETO"
echo "[$(date -Is)] Sincronizando contas de agenda conectadas"
$COMPOSE exec -T backend python -m app.services.agenda_sync_cli
echo "[$(date -Is)] Fim"
