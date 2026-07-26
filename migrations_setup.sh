#!/usr/bin/env bash
# Adota o Alembic num banco que já existe e já está no esquema atual (é o
# caso de produção agora). Gera a migração de linha de base comparando o
# banco real com os modelos do app, e marca essa migração como já aplicada
# — sem recriar nem alterar nenhuma tabela.
#
# Rodar UMA VEZ, depois do deploy do pacote que traz backend/migrations/.
set -euo pipefail

PROJETO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="docker compose -f $PROJETO/docker-compose.prod.yml"
cd "$PROJETO"

JA_TEM_VERSAO=$($COMPOSE exec -T backend sh -c "ls migrations/versions/*.py 2>/dev/null | wc -l" | tr -d '[:space:]')
if [ "$JA_TEM_VERSAO" != "0" ]; then
  echo "Já existe migração em migrations/versions/ — isto não é a primeira vez."
  echo "Se a intenção era mesmo recriar a linha de base, apague os arquivos antes."
  exit 1
fi

echo "Gerando a migração de linha de base a partir do banco real..."
$COMPOSE exec -T backend alembic revision --autogenerate -m "linha de base - esquema em producao"

echo
echo "Revise o arquivo gerado em backend/migrations/versions/ antes de continuar."
echo "O esperado é um diff vazio ou quase vazio (o banco já está no esquema atual)."
echo "Índices e o gatilho de busca full-text não aparecem no diff — são geridos"
echo "à parte em bootstrap.py, isso é esperado."
read -rp "Conferiu e está tudo certo? Digite CONFIRMAR para marcar como aplicada: " ok
[ "$ok" = "CONFIRMAR" ] || { echo "Cancelado — nada foi marcado."; exit 1; }

$COMPOSE exec -T backend alembic stamp head
echo
echo "Pronto. A partir de agora, mudança de esquema é:"
echo "  1. Editar o modelo em backend/app/models/"
echo "  2. docker compose exec backend alembic revision --autogenerate -m \"descricao\""
echo "  3. Revisar o arquivo gerado em migrations/versions/"
echo "  4. docker compose exec backend alembic upgrade head"
echo "Sem mais ALTER TABLE manual."
