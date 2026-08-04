#!/usr/bin/env bash
# Restaura um backup específico. USO RARO E DESTRUTIVO: valida integralmente o
# arquivo antes de apagar o banco e mantém o backend parado se a carga falhar.
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO="${PROJETO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
COMPOSE=(docker compose -f "$PROJETO/docker-compose.prod.yml")
ARQUIVO="${1:-}"
RESTAURACAO_INICIADA=0
BACKEND_RELIGADO=0

falha() {
  local status=$?
  trap - ERR
  if [[ "$RESTAURACAO_INICIADA" == "1" ]]; then
    if [[ "$BACKEND_RELIGADO" == "1" ]]; then
      echo "Falha após tentar religar o backend; parando-o novamente." >&2
      if ! "${COMPOSE[@]}" stop backend; then
        echo "CRÍTICO: não foi possível confirmar a parada do backend; bloqueie o tráfego antes de nova tentativa." >&2
      fi
    fi
    echo "ERRO: restauração interrompida. O backend deve permanecer parado para evitar uso de banco incompleto." >&2
    "${COMPOSE[@]}" ps || true
    "${COMPOSE[@]}" logs --tail=150 db backend || true
  fi
  exit "$status"
}
trap falha ERR

validar_checksum_vinculado() {
  local arquivo="$1" sidecar="$2"
  local hash_esperado nome_registrado hash_calculado

  if [[ ! -f "$sidecar" ]]; then
    echo "Checksum obrigatório não encontrado: $sidecar" >&2
    return 1
  fi

  read -r hash_esperado nome_registrado < "$sidecar" || true
  nome_registrado="${nome_registrado#\*}"
  if [[ ! "$hash_esperado" =~ ^[0-9a-fA-F]{64}$ ]] || \
     [[ "$nome_registrado" != "$(basename "$arquivo")" ]]; then
    echo "Checksum não corresponde ao dump selecionado: $sidecar" >&2
    return 1
  fi

  hash_calculado="$(sha256sum "$arquivo" | awk '{print $1}')"
  if [[ "${hash_calculado,,}" != "${hash_esperado,,}" ]]; then
    echo "Checksum inválido para o dump selecionado: $arquivo" >&2
    return 1
  fi
}

if [[ -z "$ARQUIVO" || ! -f "$ARQUIVO" ]]; then
  echo "Uso: $0 <backup.dump|backup.sql.gz>"
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

for comando in docker sha256sum awk; do
  if ! command -v "$comando" >/dev/null 2>&1; then
    echo "Comando obrigatório ausente no host: $comando" >&2
    exit 1
  fi
done

ARQUIVO="$(cd "$(dirname "$ARQUIVO")" && pwd)/$(basename "$ARQUIVO")"
CHECKSUM="${ARQUIVO}.sha256"
FORMATO=""

case "$ARQUIVO" in
  *.dump)
    FORMATO="custom"
    validar_checksum_vinculado "$ARQUIVO" "$CHECKSUM"
    ;;
  *.sql.gz)
    FORMATO="sql-gzip-legado"
    if [[ -f "$CHECKSUM" ]]; then
      validar_checksum_vinculado "$ARQUIVO" "$CHECKSUM"
    fi
    gzip -t "$ARQUIVO"
    ;;
  *)
    echo "Formato não suportado. Use .dump ou .sql.gz." >&2
    exit 1
    ;;
esac

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
BACKEND_CONTAINER="$("${COMPOSE[@]}" ps -a -q backend)"
if [[ -n "$BACKEND_CONTAINER" ]]; then
  echo "Parando o backend para evitar escrita durante a restauração..."
  "${COMPOSE[@]}" stop backend
else
  echo "Backend não existe neste projeto Compose; não há processo da aplicação para parar."
fi

echo "Recriando o banco vazio..."
"${COMPOSE[@]}" exec -T db dropdb -U "$POSTGRES_USER" --if-exists --force "$POSTGRES_DB"
"${COMPOSE[@]}" exec -T db createdb -U "$POSTGRES_USER" "$POSTGRES_DB"

echo "Restaurando backup validado..."
if [[ "$FORMATO" == "custom" ]]; then
  "${COMPOSE[@]}" exec -T db pg_restore \
    -U "$POSTGRES_USER" --dbname="$POSTGRES_DB" --exit-on-error \
    --no-owner --no-privileges < "$ARQUIVO"
else
  gunzip -c "$ARQUIVO" | "${COMPOSE[@]}" exec -T db psql \
    -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" "$POSTGRES_DB"
fi

echo "Religando o backend e aplicando migrations idempotentes..."
# Marca antes do comando: até uma falha parcial de `up` aciona nova tentativa de parada.
BACKEND_RELIGADO=1
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

BACKEND_RELIGADO=0
RESTAURACAO_INICIADA=0
trap - ERR
echo "Restauração concluída e backend pronto. Confira o site e o inventário antes de encerrar o incidente."
