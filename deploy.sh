#!/usr/bin/env bash
# Dispatcher temporário e seguro para hotfix visual web.
# Se o commit não for exclusivamente de UI aprovada, delega ao deploy
# certificado original, preservado pelo blob imutável abaixo.
set -Eeuo pipefail

readonly ORIGINAL_DEPLOY_BLOB="3547e3c0678df10bad1cd473d59e0fe6fc438dc9"
COMPOSE=(docker compose -f docker-compose.prod.yml)

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

run_full_certified_deploy() {
  log "Hotfix visual não aplicável; delegando ao deploy certificado original."
  git cat-file blob "$ORIGINAL_DEPLOY_BLOB" | bash -s
}

[[ -f .env ]] || { echo "Falta .env" >&2; exit 1; }
# shellcheck disable=SC1091
source .env

command -v git >/dev/null 2>&1 || { echo "git ausente" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker ausente" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl ausente" >&2; exit 1; }
command -v flock >/dev/null 2>&1 || { echo "flock ausente" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 ausente" >&2; exit 1; }
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

# Primeiro tenta o SHA do backend em execução. Em versões antigas esse env pode
# estar ausente; nesse caso usa exclusivamente o /api/version público, que é
# leitura e não toca banco, migrations ou serviços.
RUNNING_SHA="$("${COMPOSE[@]}" exec -T backend printenv DEPLOY_COMMIT 2>/dev/null | tr -d '[:space:]' || true)"
if [[ ! "$RUNNING_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  RUNNING_SHA="$(curl --fail --silent --show-error --max-time 15 "https://${DOMAIN}/api/version" \
    | python3 -c 'import json,sys; p=json.load(sys.stdin); print(p.get("commit") or p.get("version") or p.get("sha") or "")' \
    | tr -d '[:space:]' || true)"
fi
[[ "$RUNNING_SHA" =~ ^[0-9a-f]{40}$ ]] || {
  echo "Não foi possível confirmar o SHA atualmente publicado; recusando hotfix isolado." >&2
  exit 65
}
git cat-file -e "${RUNNING_SHA}^{commit}" 2>/dev/null || {
  echo "Commit atualmente publicado não existe no checkout local." >&2
  exit 65
}

CHANGED="$(git diff --name-only "$RUNNING_SHA" "$CURRENT_SHA")"
[[ -n "$CHANGED" ]] || { echo "Nenhuma mudança para publicar." >&2; exit 65; }

INVALID="$(printf '%s\n' "$CHANGED" | grep -Ev '^(frontend/|\.github/workflows/deploy-login-emergency\.yml$|deploy\.sh$)' || true)"
if [[ -n "$INVALID" ]]; then
  printf 'Hotfix visual contém arquivos fora da allow-list:\n%s\n' "$INVALID" >&2
  run_full_certified_deploy
  exit $?
fi

log "Hotfix exclusivamente visual confirmado entre $RUNNING_SHA e $CURRENT_SHA."
log "Backend, banco, migrations, workers e Caddy permanecerão em execução e intocados."

DEPLOY_COMMIT="$CURRENT_SHA" "${COMPOSE[@]}" build frontend-build
DEPLOY_COMMIT="$CURRENT_SHA" "${COMPOSE[@]}" run --rm --no-deps frontend-build

DEPLOY_COMMIT="$CURRENT_SHA" "${COMPOSE[@]}" run --rm --no-deps --entrypoint sh frontend-build -c \
  "grep -R -F '$CURRENT_SHA' /site >/dev/null"

curl --fail --silent --show-error --max-time 15 "https://${DOMAIN}/" >/dev/null
curl --fail --silent --show-error --max-time 15 "https://${DOMAIN}/entrar" >/dev/null
curl --fail --silent --show-error --max-time 15 "https://${DOMAIN}/api/health" >/dev/null
curl --fail --silent --show-error --max-time 15 "https://${DOMAIN}/api/ready" >/dev/null

printf 'UI_SHA=%s\n' "$CURRENT_SHA"
log "Hotfix visual web concluído sem tocar backend, banco ou migrations."
