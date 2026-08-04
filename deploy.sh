#!/usr/bin/env bash
# Deploy de produção certificado: backup, build, migrations, corpus e HTTPS.
# Rodar no servidor, dentro da pasta do projeto (/opt/meucardio).
set -Eeuo pipefail

COMPOSE=(docker compose -f docker-compose.prod.yml)

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

backend_exec() {
  "${COMPOSE[@]}" exec -T backend "$@"
}

mostrar_diagnostico() {
  "${COMPOSE[@]}" ps || true
  "${COMPOSE[@]}" logs --tail=200 backend caddy frontend-build || true
}

if [[ ! -f .env ]]; then
  echo "Falta o arquivo .env. Rode: cp .env.example .env e preencha antes de continuar."
  exit 1
fi

# shellcheck disable=SC1091
source .env

for var in DOMAIN POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB JWT_SECRET; do
  valor="${!var:-}"
  if [[ -z "$valor" ]] || [[ "$valor" == troque-esta-senha* ]] || \
     [[ "$valor" == gere-com-* ]] || [[ "$valor" == *seudominio* ]]; then
    echo "A variável $var no .env está ausente ou mantém valor de exemplo."
    exit 1
  fi
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker não encontrado. Instale com: curl -fsSL https://get.docker.com | sh"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 não está disponível."
  exit 1
fi

COMMIT_ATUAL="$(git rev-parse --verify HEAD 2>/dev/null || printf 'desconhecido')"
log "Iniciando deploy do commit $COMMIT_ATUAL para $DOMAIN."

log "Verificando se o DNS aponta para este servidor."
IP_SERVIDOR="$(curl -fsS -4 --max-time 10 ifconfig.me 2>/dev/null || true)"
IP_DOMINIO="$(getent ahostsv4 "$DOMAIN" | awk 'NR == 1 {print $1}' || true)"
if [[ -n "$IP_SERVIDOR" && -n "$IP_DOMINIO" && "$IP_SERVIDOR" != "$IP_DOMINIO" ]]; then
  echo "Aviso: $DOMAIN resolve para $IP_DOMINIO, mas este servidor é $IP_SERVIDOR."
  echo "O Caddy só emitirá/renovará o certificado quando o DNS estiver correto."
  read -r -p "Continuar mesmo assim? [y/N] " resposta
  [[ "$resposta" == "y" ]] || exit 1
fi

# Antes de alterar imagens ou executar migrations, preserva o banco existente.
# No primeiro deploy ainda não existe serviço db; nesse caso o passo é omitido.
if "${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -Fxq db; then
  log "Criando backup pré-deploy do PostgreSQL."
  PROJETO="$PWD" ./infra/backup/backup.sh
else
  log "Banco ainda não está em execução; backup pré-deploy não se aplica ao primeiro deploy."
fi

log "Construindo e subindo serviços de produção."
"${COMPOSE[@]}" up -d --build --remove-orphans

log "Aguardando readiness do backend."
BACKEND_PRONTO=0
for _ in $(seq 1 60); do
  if backend_exec python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=3).read()" \
    >/dev/null 2>&1; then
    BACKEND_PRONTO=1
    break
  fi
  sleep 2
done

if [[ "$BACKEND_PRONTO" != "1" ]]; then
  echo "ERRO: backend não atingiu readiness; migrations e corpus não serão executados." >&2
  mostrar_diagnostico
  exit 1
fi

log "Confirmando migrations de forma idempotente."
backend_exec python -m app.commands.migrate

log "Reconciliando as 11 coleções e publicando somente conteúdo revisado."
# O comando sai com código diferente de zero se qualquer coleção permanecer
# abaixo do mínimo versionado. `set -e` impede declarar sucesso nesse cenário.
backend_exec python -m app.commands.reconcile_content --publish-reviewed

if [[ "${AI_ENABLED:-false}" == "true" ]]; then
  log "Indexando a base reconciliada para a IA clínica."
  backend_exec python -m app.services.indexar
fi

log "Confirmando readiness interno após a reconciliação."
backend_exec python -c \
  "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5).read()"

log "Aguardando o domínio HTTPS responder pela pilha publicada."
PUBLICO_PRONTO=0
for _ in $(seq 1 60); do
  if curl -fsS --max-time 5 "https://${DOMAIN}/api/ready" >/dev/null 2>&1; then
    PUBLICO_PRONTO=1
    break
  fi
  sleep 2
done

if [[ "$PUBLICO_PRONTO" != "1" ]]; then
  echo "ERRO: backend está pronto internamente, mas https://${DOMAIN}/api/ready não respondeu." >&2
  mostrar_diagnostico
  exit 1
fi

"${COMPOSE[@]}" ps
log "Deploy certificado concluído: commit $COMMIT_ATUAL, migrations aplicadas, corpus reconciliado e HTTPS pronto."
