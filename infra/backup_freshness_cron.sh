#!/usr/bin/env bash
# Monitoramento de idade/integridade do backup diário — issue #52, fase de
# hardening pós-gate-final (achado: existia script de checagem testado,
# ops/check-backup-freshness.sh, mas nada o chamava periodicamente).
#
# Roda DEPOIS do backup diário documentado em DEPLOY.md ("Backup
# automático", 0 3 * * *) — o horário abaixo dá 30 minutos de folga para o
# dump e o empacotamento dos volumes sensíveis terminarem antes da checagem.
#
# Instalação no host, junto das outras entradas já documentadas
# (infra/agenda_sync_cron.sh, infra/cmed_cron.sh):
#   30 3 * * * /opt/meucardio/infra/backup_freshness_cron.sh >> /opt/meucardio/infra/backup_freshness_cron.log 2>&1
#
# Este script SÓ verifica e loga — não cria backup (isso é
# infra/backup/backup.sh, já cron'd) nem envia alerta externo (não há
# integração de e-mail/SMS/webhook de alerta configurada neste projeto;
# ver ressalva no corpo do relatório do RC). Saída não-zero fica registrada
# no log e pode ser lida por qualquer monitoramento externo que o Rafael
# configurar depois — ação operacional documentada, não implementada aqui.
set -euo pipefail

PROJETO="/opt/meucardio"
export BACKUP_DIR="${BACKUP_DIR:-$PROJETO/infra/backup/dumps}"
export BACKUP_NAME_PREFIX="${BACKUP_NAME_PREFIX:-meucardio_}"
# 30h — folga sobre o intervalo diário de 24h para tolerar um backup que
# atrasou um pouco sem gerar alarme falso a cada rodada.
export MAX_BACKUP_AGE_SECONDS="${MAX_BACKUP_AGE_SECONDS:-108000}"

echo "[$(date -Is)] Checando idade/integridade do backup em $BACKUP_DIR"
if "$PROJETO/ops/check-backup-freshness.sh"; then
  echo "[$(date -Is)] Backup OK"
else
  codigo=$?
  echo "[$(date -Is)] ALERTA: backup não passou na checagem (código $codigo) — ver saída acima."
  exit "$codigo"
fi
