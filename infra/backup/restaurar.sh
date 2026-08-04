#!/usr/bin/env bash
# Restaura um backup específico. USO RARO E DESTRUTIVO: valida integralmente o
# arquivo antes de apagar o banco e mantém o backend parado se a carga falhar.
#
#   PROJETO=/opt/meucardio bash ./infra/backup/restaurar.sh \
#     infra/backup/dumps/meucardio_2026-08-03_230000.dump
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO="${PROJETO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
COMPOSE=(docker compose -f "$PROJETO/docker-compose.prod.yml")
ARQUIVO="${1:-}"
RESTAURACAO_INICIADA=0

falha() {
  local status=$?
  trap - ERR
  if [[ "$RESTAURACAO_INICIADA" == "1" ]]; then
    echo "ERRO: restauração interrompida. O backend permanece parado para evitar uso de banco incompleto." >&2
    "${COMPOSE[@]}" ps || true
    "${COMPOSE[@]}" logs --tail=150 db backend || true
  fi
  exit "$status"
}
trap falha ERR

if [[ -z "$ARQUIVO" || ! -f "$ARQUIVO" ]]; then
  echo "Uso: $0 <backup.dump|backup.sql.gz>"
  echo
  echo "Backups disponíveis:"
  ls -lh "$PROJETO/infra/backup/dumps/" 2>/dev/null || echo "  (nenhum encontrado)"
  exit 1
fi

cd "$PROJETO"
if [[ ! -f .env ]]; then
  echo "Arquivo .env não encontrado em $PROJETO." >&2
  exit 1
fi
# shellcheck disable=SC1091
source .env
: "${POSTGRES_USER:?Defina POSTGRES_USER no .env.}"
: "${POSTGRES_DB:?Defina POSTGRES_DB no .env.}"

ARQUIVO="$(cd "$(dirname "$ARQUIVO")" && pwd)/$(basename "$ARQUIVO")"
CHECKSUM="${ARQUIVO}.sha256"
FORMATO=""

case "$ARQUIVO" in
  *.dump)
    FORMATO="custom"
    if [[ ! -f "$CHECKSUM" ]]; then
      echo "Checksum obrigatório não encontrado: $CHECKSUM" >&2
      exit 1
    fi
    (
      cd "$(dirname "$ARQUIVO")"
      sha256sum -c "$(basename "$CHECKSUM")"
    )
    ;;
  *.sql.gz)
    FORMATO="sql-gzip-legado"
    if [[ -f "$CHECKSUM" ]]; then
      (
        cd "$(dirname "$ARQUIVO")"
        sha256sum -c "$(basename "$CHECKSUM")"
      )
    fi
    gzip -t "$ARQUIVO"
    ;;
  *)
    echo "Formato não suportado. Use .dump ou .sql.gz." >&2
    exit 1
    ;;
esac

# O banco precisa estar acessível para validar o catálogo e executar a carga,
# mas iniciar somente `db` não executa migrations nem toca no conteúdo.
"${COMPOSE[@]}" up -d --no-deps db
DB_PRONTO=0
for _ in $(seq 1 30); do
  if "${COMPOSE[@]}" exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; then
    DB_PRONTO=1
    break
  fi
  sleep 2
done
if [[ "$DB_PRONTO" != "1" ]]; then
  echo "PostgreSQL não ficou pronto para validar a restauração." >&2
  exit 1
fi

# Valida o formato custom dentro da mesma imagem PostgreSQL que fará a carga,
# antes de qualquer operação destrutiva.
if [[ "$FORMATO" == "custom" ]]; then
  "${COMPOSE[@]}" exec -T db pg_restore --list < "$ARQUIVO" >/dev/null
fi

echo "ATENÇÃO: isso vai APAGAR o banco '$POSTGRES_DB' e substituir pelo conteúdo de:"
echo "  $ARQUIVO"
read -r -p "Digite RESTAURAR para confirmar: " confirmacao
[[ "$confirmacao" == "RESTAURAR" ]] || { echo "Cancelado."; exit 1; }
read -r -p "Digite o nome do banco ($POSTGRES_DB) para confirmar novamente: " banco_confirmado
[[ "$banco_confirmado" == "$POSTGRES_DB" ]] || { echo "Cancelado: banco não confirmado."; exit 1; }

RESTAURACAO_INICIADA=1
echo "Parando o backend para evitar escrita durante a restauração..."
"${COMPOSE[@]}" stop backend >/dev/null 2>&1 || true

echo "Recriando o banco vazio..."
"${COMPOSE[@]}" exec -T db dropdb \
  -U "$POSTGRES_USER" --if-exists --force "$POSTGRES_DB"
"${COMPOSE[@]}" exec -T db createdb \
  -U "$POSTGRES_USER" "$POSTGRES_DB"

echo "Restaurando backup validado..."
if [[ "$FORMATO" == "custom" ]]; then
  "${COMPOSE[@]}" exec -T db pg_restore \
    -U "$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --exit-on-error \
    --no-owner \
    --no-privileges \
    < "$ARQUIVO"
else
  gunzip -c "$ARQUIVO" | "${COMPOSE[@]}" exec -T db psql \
    -v ON_ERROR_STOP=1 \
    -U "$POSTGRES_USER" \
    "$POSTGRES_DB"
fi

# `up` recria o backend quando necessário e executa o comando operacional de
# migrations antes de iniciar o Uvicorn.
echo "Religando o backend e aplicando migrations idempotentes..."
"${COMPOSE[@]}" up -d backend

BACKEND_PRONTO=0
for _ in $(seq 1 60); do
  if "${COMPOSE[@]}" exec -T backend python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=3).read()" \
    >/dev/null 2>&1; then
    BACKEND_PRONTO=1
    break
  fi
  sleep 2
done
if [[ "$BACKEND_PRONTO" != "1" ]]; then
  echo "Backend não atingiu readiness após a restauração." >&2
  false
fi

RESTAURACAO_INICIADA=0
trap - ERR
echo "Restauração concluída e backend pronto. Confira o site e o inventário antes de encerrar o incidente."
