#!/usr/bin/env bash
# Forced command for the GitHub Actions production key. This key cannot open a
# shell, forward ports, or execute arbitrary commands. It accepts only:
#   deploy <40-character current main SHA>
#   apk <40-character current main SHA>
#   intelligence <40-character current main SHA>
#   intelligence-force <40-character current main SHA>
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export GIT_TERMINAL_PROMPT=0
umask 027

readonly PROJECT_DIR="/opt/meucardio"
readonly ORIGINAL_COMMAND="${SSH_ORIGINAL_COMMAND:-}"
# Último SHA de produção certificado antes do rollback emergencial de
# 29/08/2026. A recuperação privada abaixo ainda exige que nenhuma migration
# tenha mudado entre esta base e o SHA solicitado antes de religar o backend.
readonly RECOVERY_BASE_SHA="59566e1196e0fa7f465df93516790ef454e1f565"

deny() {
  printf 'Production request denied: %s\n' "$1" >&2
  exit 64
}

REQUEST_KIND=""
EXPECTED_SHA=""
INTELLIGENCE_FORCE="0"
if [[ "$ORIGINAL_COMMAND" =~ ^deploy[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="deploy"
  EXPECTED_SHA="${BASH_REMATCH[1]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^apk[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="apk"
  EXPECTED_SHA="${BASH_REMATCH[1]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^intelligence[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="intelligence"
  EXPECTED_SHA="${BASH_REMATCH[1]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^intelligence-force[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="intelligence"
  EXPECTED_SHA="${BASH_REMATCH[1]}"
  INTELLIGENCE_FORCE="1"
else
  deny "expected exactly: deploy <SHA>, apk <SHA>, intelligence <SHA>, or intelligence-force <SHA>"
fi
readonly REQUEST_KIND EXPECTED_SHA INTELLIGENCE_FORCE

[[ -d "$PROJECT_DIR/.git" ]] || deny "production checkout not found"
cd "$PROJECT_DIR"

changes="$(git status --porcelain --untracked-files=normal)"
if [[ -n "$changes" ]]; then
  printf 'Production checkout is dirty; refusing request:\n%s\n' "$changes" >&2
  exit 65
fi

git fetch --prune origin main
remote_main="$(git rev-parse --verify origin/main)"
if [[ "$remote_main" != "$EXPECTED_SHA" ]]; then
  printf 'Requested SHA %s is not current origin/main %s.\n' "$EXPECTED_SHA" "$remote_main" >&2
  exit 65
fi

if [[ "$REQUEST_KIND" == "intelligence" ]]; then
  deployed_sha="$(git rev-parse --verify HEAD)"
  if [[ "$deployed_sha" != "$EXPECTED_SHA" ]]; then
    printf 'CorVIA Intelligence refused: production is at %s but current main is %s. Deploy current main first.\n' \
      "$deployed_sha" "$EXPECTED_SHA" >&2
    exit 65
  fi

  docker compose -f docker-compose.prod.yml exec -T backend true >/dev/null 2>&1 \
    || deny "production backend is not running"

  if [[ "$INTELLIGENCE_FORCE" == "1" ]]; then
    exec docker compose -f docker-compose.prod.yml exec -T \
      -e CORVIA_INTELLIGENCE_FORCE=1 backend \
      python -m app.services.guideline_discovery_cli
  fi

  exec docker compose -f docker-compose.prod.yml exec -T backend \
    python -m app.services.guideline_discovery_cli
fi

if [[ "$REQUEST_KIND" == "apk" ]]; then
  deployed_sha="$(git rev-parse --verify HEAD)"
  if [[ "$deployed_sha" != "$EXPECTED_SHA" ]]; then
    printf 'APK build refused: production is at %s but current main is %s. Deploy current main first.\n' \
      "$deployed_sha" "$EXPECTED_SHA" >&2
    exit 65
  fi

  exec bash "$PROJECT_DIR/ops/build-android-apk.sh" "$EXPECTED_SHA"
fi

git checkout main
git merge --ff-only "$EXPECTED_SHA"

[[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || deny "checkout SHA mismatch"
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] || deny "checkout changed during update"

# Recuperação controlada após rollback automático: o rollback restaura o banco
# e deliberadamente deixa backend/caddy parados. O deploy.sh precisa do backend
# anterior vivo apenas para ler DEPLOY_COMMIT na guarda de migrations. Se ele
# estiver parado, religamos SOMENTE o backend privado e apenas quando pudermos
# provar que nenhuma migration mudou desde o último release certificado.
if ! docker compose -f docker-compose.prod.yml exec -T backend true >/dev/null 2>&1; then
  git merge-base --is-ancestor "$RECOVERY_BASE_SHA" "$EXPECTED_SHA" \
    || deny "recovery base is not an ancestor of requested main SHA"
  git diff --quiet "$RECOVERY_BASE_SHA" "$EXPECTED_SHA" -- backend/migrations/versions \
    || deny "backend is down and migrations changed since recovery base; manual recovery required"

  printf 'Backend stopped after rollback; bootstrapping private backend with no migration delta since %s.\n' "$RECOVERY_BASE_SHA" >&2
  DEPLOY_COMMIT="$RECOVERY_BASE_SHA" docker compose -f docker-compose.prod.yml up -d --no-deps backend

  ready=0
  for _ in $(seq 1 30); do
    if docker compose -f docker-compose.prod.yml exec -T backend \
      python -c 'import urllib.request; urllib.request.urlopen("http://localhost:8000/api/ready", timeout=2).read()' \
      >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 2
  done
  [[ "$ready" == "1" ]] || deny "recovery backend did not become ready"
fi

exec bash ./deploy.sh
