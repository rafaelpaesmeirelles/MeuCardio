#!/usr/bin/env bash
# Deploy de produção certificado: backup, build, migrations, corpus e HTTPS.
# Rodar no servidor, dentro da pasta do projeto (/opt/meucardio).
set -Eeuo pipefail

COMPOSE=(docker compose -f docker-compose.prod.yml)
SERVICOS_INICIADOS=0
BANCO_PERSISTENTE=0
ROLLBACK_NECESSARIO=0
TRAFEGO_ABERTO=0
BACKUP_PRE_DEPLOY=""
COMMIT_ATUAL=""
ARVORE_ATUAL=""

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

backend_exec() {
  "${COMPOSE[@]}" exec -T backend "$@"
}

mostrar_diagnostico() {
  "${COMPOSE[@]}" ps || true
  "${COMPOSE[@]}" logs --tail=200 backend caddy frontend-build db || true
}

compose_project_name() {
  local nome="${COMPOSE_PROJECT_NAME:-$(basename "$PWD")}"
  printf '%s' "$nome" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/^[^a-z0-9]+//; s/[^a-z0-9_-]+//g'
}

parar_servico_se_existir() {
  local servico="$1" container_id
  container_id="$("${COMPOSE[@]}" ps -a -q "$servico")"
  if [[ -n "$container_id" ]]; then
    "${COMPOSE[@]}" stop "$servico"
  fi
}

restaurar_backup_pre_deploy() {
  echo "Bloqueando tráfego e revertendo o banco após falha na fase mutável." >&2
  parar_servico_se_existir caddy
  parar_servico_se_existir backend
  TRAFEGO_ABERTO=0

  if [[ -z "$BACKUP_PRE_DEPLOY" ]]; then
    echo "Primeiro deploy sem banco anterior: aplicação permanecerá parada; não há dump para restaurar." >&2
    return 0
  fi
  if [[ ! -f "$BACKUP_PRE_DEPLOY" || ! -f "${BACKUP_PRE_DEPLOY}.sha256" ]]; then
    echo "CRÍTICO: dump pré-deploy ou checksum não encontrado: $BACKUP_PRE_DEPLOY" >&2
    return 1
  fi

  PROJETO="$PWD" \
  RESTAURACAO_AUTOMATICA=1 \
  RESTAURACAO_SEM_RELIGAR=1 \
  CONFIRM_RESTORE_TARGET="$POSTGRES_DB" \
    bash ./infra/backup/restaurar.sh "$BACKUP_PRE_DEPLOY"
}

diagnosticar_erro() {
  local status=$?
  local linha="${BASH_LINENO[0]:-desconhecida}"
  trap - ERR

  if [[ "$ROLLBACK_NECESSARIO" == "1" ]]; then
    if ! restaurar_backup_pre_deploy; then
      echo "CRÍTICO: o rollback automático também falhou. Mantenha o tráfego bloqueado e restaure manualmente o dump." >&2
    fi
    ROLLBACK_NECESSARIO=0
  elif [[ "$TRAFEGO_ABERTO" == "1" ]]; then
    echo "Falha durante a certificação pública; fechando o proxy para evitar falso sucesso." >&2
    if ! parar_servico_se_existir caddy; then
      echo "CRÍTICO: não foi possível confirmar a parada do Caddy." >&2
    fi
    TRAFEGO_ABERTO=0
  fi

  if [[ "$SERVICOS_INICIADOS" == "1" ]]; then
    echo "ERRO: deploy interrompido na linha $linha (status $status)." >&2
    mostrar_diagnostico
  fi
  exit "$status"
}

detectar_banco_persistente() {
  local container_id projeto volume_rotulado volume_deterministico volumes

  # A chamada é intencionalmente fail-closed: erro do Docker/Compose não pode
  # ser reinterpretado como "primeiro deploy" e permitir migrations sem backup.
  container_id="$("${COMPOSE[@]}" ps -a -q db)"
  if [[ -n "$container_id" ]]; then
    BANCO_PERSISTENTE=1
    return 0
  fi

  projeto="$(compose_project_name)"
  volume_rotulado="$(docker volume ls -q \
    --filter "label=com.docker.compose.project=${projeto}" \
    --filter "label=com.docker.compose.volume=pgdata" \
    | head -n 1)"
  if [[ -n "$volume_rotulado" ]]; then
    BANCO_PERSISTENTE=1
    return 0
  fi

  # Cobre volume criado ou migrado manualmente sem labels do Compose. O nome
  # determinístico é o mesmo que o Compose reutilizará para o volume `pgdata`.
  volume_deterministico="${projeto}_pgdata"
  volumes="$(docker volume ls -q)"
  if grep -Fxq "$volume_deterministico" <<< "$volumes"; then
    BANCO_PERSISTENTE=1
  fi
}

aguardar_postgres() {
  local pronto=0
  for _ in $(seq 1 30); do
    if "${COMPOSE[@]}" exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; then
      pronto=1
      break
    fi
    sleep 2
  done
  [[ "$pronto" == "1" ]]
}

validar_checkout_imutavel() {
  local head tree alteracoes
  head="$(git rev-parse --verify HEAD)"
  tree="$(git rev-parse "${head}^{tree}")"
  alteracoes="$(git status --porcelain --untracked-files=normal)"

  if [[ "$head" != "$COMMIT_ATUAL" || "$tree" != "$ARVORE_ATUAL" || -n "$alteracoes" ]]; then
    echo "O checkout mudou durante o deploy; o build não pode ser certificado como $COMMIT_ATUAL." >&2
    [[ -n "$alteracoes" ]] && printf '%s\n' "$alteracoes" >&2
    return 1
  fi
}

# Desde a tentativa de iniciar serviços, comandos não tratados passam pelo
# diagnóstico e, durante migrations/reconciliação, pelo rollback automático.
trap diagnosticar_erro ERR

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

for comando in git curl getent sha256sum flock mktemp tail tee grep; do
  if ! command -v "$comando" >/dev/null 2>&1; then
    echo "Comando obrigatório ausente no host: $comando" >&2
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

# Impede dois deploys simultâneos no mesmo checkout. A validação repetida de
# HEAD/árvore também detecta git pull/checkout executado por outro processo.
GIT_DIR="$(git rev-parse --git-dir)"
exec 9>"${GIT_DIR}/corvia-deploy.lock"
if ! flock -n 9; then
  echo "Outro deploy já está em execução neste repositório." >&2
  exit 1
fi

COMMIT_ATUAL="$(git rev-parse --verify HEAD 2>/dev/null || true)"
if [[ ! "$COMMIT_ATUAL" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Não foi possível identificar um commit Git completo; deploy não pode ser certificado." >&2
  exit 1
fi
ARVORE_ATUAL="$(git rev-parse "${COMMIT_ATUAL}^{tree}")"
validar_checkout_imutavel

# Docker Compose interpola variáveis exportadas antes de ler o arquivo. O mesmo
# SHA fica disponível em /api/version para conferência externa.
export DEPLOY_COMMIT="$COMMIT_ATUAL"
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

detectar_banco_persistente
if [[ "$BANCO_PERSISTENTE" == "1" ]]; then
  log "Banco persistente detectado; iniciando somente o PostgreSQL para backup pré-deploy."
  SERVICOS_INICIADOS=1
  "${COMPOSE[@]}" up -d --no-deps db
  if ! aguardar_postgres; then
    echo "PostgreSQL persistente não ficou pronto para o backup pré-deploy." >&2
    false
  fi

  BACKUP_LOG="$(mktemp)"
  if PROJETO="$PWD" bash ./infra/backup/backup.sh | tee "$BACKUP_LOG"; then
    BACKUP_PRE_DEPLOY="$(tail -n 1 "$BACKUP_LOG")"
    rm -f "$BACKUP_LOG"
  else
    rm -f "$BACKUP_LOG"
    false
  fi
  if [[ ! -f "$BACKUP_PRE_DEPLOY" || ! -f "${BACKUP_PRE_DEPLOY}.sha256" ]]; then
    echo "Backup pré-deploy não foi materializado com checksum." >&2
    false
  fi
else
  log "Nenhum container ou volume pgdata existente; backup não se aplica ao primeiro deploy."
fi

log "Construindo imagens a partir do checkout imutável, sem interromper o tráfego atual."
validar_checkout_imutavel
"${COMPOSE[@]}" build backend frontend-build
validar_checkout_imutavel

log "Fechando o proxy antes de substituir backend, frontend e banco lógico."
parar_servico_se_existir caddy
TRAFEGO_ABERTO=0
SERVICOS_INICIADOS=1
"${COMPOSE[@]}" up -d --no-build --remove-orphans db redis backend frontend-build

log "Aguardando readiness do backend sem tráfego público."
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
  echo "Backend não atingiu readiness; tráfego permanecerá fechado." >&2
  false
fi

# A partir daqui o banco pode mudar. Qualquer erro até o fim da indexação restaura
# automaticamente o dump pré-deploy e deixa backend/Caddy parados.
ROLLBACK_NECESSARIO=1
log "Confirmando migrations de forma idempotente."
backend_exec python -m app.commands.migrate

log "Reconciliando as 11 coleções e publicando somente conteúdo revisado."
backend_exec python -m app.commands.reconcile_content --publish-reviewed

if [[ "${AI_ENABLED:-false}" == "true" ]]; then
  log "Indexando a base reconciliada para a IA clínica."
  backend_exec python -m app.services.indexar
fi
ROLLBACK_NECESSARIO=0

log "Confirmando readiness interno após a fase mutável."
backend_exec python -c \
  "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5).read()"
validar_checkout_imutavel

log "Abrindo o proxy somente após banco, corpus e build estarem certificados."
"${COMPOSE[@]}" up -d --no-build caddy
TRAFEGO_ABERTO=1

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
  echo "Backend está pronto internamente, mas https://${DOMAIN}/api/ready não respondeu." >&2
  false
fi

log "Confirmando que o domínio público serve o commit solicitado."
VERSAO_PUBLICA="$(curl -fsS --max-time 10 "https://${DOMAIN}/api/version")"
if [[ "$VERSAO_PUBLICA" != *"\"commit\":\"${COMMIT_ATUAL}\""* ]]; then
  echo "ERRO: /api/version não confirmou o commit $COMMIT_ATUAL: $VERSAO_PUBLICA" >&2
  false
fi
validar_checkout_imutavel

"${COMPOSE[@]}" ps
TRAFEGO_ABERTO=0
log "Deploy certificado concluído: commit $COMMIT_ATUAL, migrations aplicadas, corpus reconciliado e HTTPS pronto."
