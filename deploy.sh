#!/usr/bin/env bash
# Dispatcher temporário e seguro para hotfix visual web.
# Se o commit não for exclusivamente de UI aprovada, delega ao deploy
# certificado original, preservado pelo blob imutável abaixo.
set -Eeuo pipefail

readonly ORIGINAL_DEPLOY_BLOB="3547e3c0678df10bad1cd473d59e0fe6fc438dc9"
readonly LAST_KNOWN_PRODUCTION_BASE="0909b006f591a615a4957d6b7e178f414f4ceeeb"
COMPOSE=(docker compose -f docker-compose.prod.yml)

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

run_full_certified_deploy() {
  log "Hotfix visual não aplicável; delegando ao deploy certificado original."
  git cat-file blob "$ORIGINAL_DEPLOY_BLOB" | bash -s
}

[[ -f .env ]] || { echo "Falta .env" >&2; exit 1; }
# shellcheck disable=SC1091
source .env

for cmd in git docker curl flock python3; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "$cmd ausente" >&2; exit 1; }
done
docker compose version >/dev/null 2>&1 || { echo "Docker Compose v2 indisponível" >&2; exit 1; }

GIT_DIR="$(git rev-parse --git-dir)"
exec 9>"${GIT_DIR}/corvia-deploy.lock"
flock -n 9 || { echo "Outro deploy já está em execução neste repositório." >&2; exit 1; }

CURRENT_SHA="$(git rev-parse --verify HEAD)"
[[ "$CURRENT_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "SHA atual inválido" >&2; exit 1; }

if ! git log -1 --pretty=%B | grep -Fq '[login-emergency-deploy]'; then
  run_full_certified_deploy
  exit $?
fi

# Descobre a última release em execução sem escrever em nada. Se backend e API
# estiverem indisponíveis, usa o último checkout publicamente observado antes
# dos hotfixes; essa base é usada apenas para validar a allow-list de arquivos.
RUNNING_SHA="$("${COMPOSE[@]}" exec -T backend printenv DEPLOY_COMMIT 2>/dev/null | tr -d '[:space:]' || true)"
if [[ ! "$RUNNING_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  RUNNING_SHA="$(curl --fail --silent --show-error --max-time 5 "https://${DOMAIN}/api/version" 2>/dev/null \
    | python3 -c 'import json,sys; p=json.load(sys.stdin); print(p.get("commit") or p.get("version") or p.get("sha") or "")' 2>/dev/null \
    | tr -d '[:space:]' || true)"
fi
if [[ ! "$RUNNING_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  RUNNING_SHA="$LAST_KNOWN_PRODUCTION_BASE"
  log "API indisponível; validando o hotfix contra a última base de produção conhecida: $RUNNING_SHA."
fi
git cat-file -e "${RUNNING_SHA}^{commit}" 2>/dev/null || { echo "Base de produção não existe no checkout local." >&2; exit 65; }

CHANGED="$(git diff --name-only "$RUNNING_SHA" "$CURRENT_SHA")"
[[ -n "$CHANGED" ]] || { echo "Nenhuma mudança para publicar." >&2; exit 65; }
INVALID="$(printf '%s\n' "$CHANGED" | grep -Ev '^(frontend/|\.github/workflows/deploy-login-emergency\.yml$|deploy\.sh$)' || true)"
if [[ -n "$INVALID" ]]; then
  printf 'Hotfix visual contém arquivos fora da allow-list:\n%s\n' "$INVALID" >&2
  run_full_certified_deploy
  exit $?
fi

log "Hotfix exclusivamente visual confirmado entre $RUNNING_SHA e $CURRENT_SHA."
log "Banco, migrations e workers não serão tocados."

# Build e publicação somente dos arquivos estáticos.
DEPLOY_COMMIT="$CURRENT_SHA" "${COMPOSE[@]}" build frontend-build
DEPLOY_COMMIT="$CURRENT_SHA" "${COMPOSE[@]}" run --rm --no-deps frontend-build
DEPLOY_COMMIT="$CURRENT_SHA" "${COMPOSE[@]}" run --rm --no-deps --entrypoint sh frontend-build -c \
  "grep -R -F '$CURRENT_SHA' /site >/dev/null"

# Se o Caddy estiver parado, religa somente o proxy estático, sem dependências.
if ! "${COMPOSE[@]}" ps --status running --services | grep -Fxq caddy; then
  log "Caddy não está em execução; religando somente o proxy, sem tocar backend/banco."
  "${COMPOSE[@]}" up -d --no-build --no-deps caddy
fi

WEB_OK=0
for _ in $(seq 1 20); do
  if curl --fail --silent --show-error --max-time 5 "https://${DOMAIN}/" >/dev/null 2>&1 \
    && curl --fail --silent --show-error --max-time 5 "https://${DOMAIN}/entrar" >/dev/null 2>&1; then
    WEB_OK=1; break
  fi
  sleep 2
done
[[ "$WEB_OK" == "1" ]] || { echo "Frontend não respondeu publicamente após o hotfix." >&2; exit 1; }

# Health/ready são informativos aqui: o objetivo do hotfix é exclusivamente UI.
if curl --fail --silent --show-error --max-time 5 "https://${DOMAIN}/api/health" >/dev/null 2>&1; then
  log "API health OK."
else
  log "AVISO: API health segue indisponível; nenhum serviço clínico foi alterado por este hotfix."
fi
if curl --fail --silent --show-error --max-time 5 "https://${DOMAIN}/api/ready" >/dev/null 2>&1; then
  log "API ready OK."
else
  log "AVISO: API ready segue indisponível; nenhum serviço clínico foi alterado por este hotfix."
fi

printf 'UI_SHA=%s\n' "$CURRENT_SHA"
log "Hotfix visual web concluído sem tocar banco ou migrations."
