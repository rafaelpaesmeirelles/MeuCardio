#!/usr/bin/env bash
# Forced command for the GitHub Actions deploy key. This key cannot open a
# shell, forward ports, or execute any command other than `deploy <main SHA>`.
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export GIT_TERMINAL_PROMPT=0
umask 027

readonly PROJECT_DIR="/opt/meucardio"
readonly ORIGINAL_COMMAND="${SSH_ORIGINAL_COMMAND:-}"
readonly RECOVERY_BASE_SHA="c06e2dcb28de8c3ffea75fa50fe5279280d4ddf1"

deny() {
  printf 'Deploy request denied: %s\n' "$1" >&2
  exit 64
}

if [[ ! "$ORIGINAL_COMMAND" =~ ^deploy[[:space:]]([0-9a-f]{40})$ ]]; then
  deny "expected exactly: deploy <40-character main SHA>"
fi
readonly EXPECTED_SHA="${BASH_REMATCH[1]}"

[[ -d "$PROJECT_DIR/.git" ]] || deny "production checkout not found"
cd "$PROJECT_DIR"

changes="$(git status --porcelain --untracked-files=normal)"
if [[ -n "$changes" ]]; then
  printf 'Production checkout is dirty; refusing to overwrite it:\n%s\n' "$changes" >&2
  exit 65
fi

git fetch --prune origin main
remote_main="$(git rev-parse --verify origin/main)"
if [[ "$remote_main" != "$EXPECTED_SHA" ]]; then
  printf 'Requested SHA %s is not current origin/main %s.\n' "$EXPECTED_SHA" "$remote_main" >&2
  exit 65
fi

git checkout main
git merge --ff-only "$EXPECTED_SHA"

[[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || deny "checkout SHA mismatch"
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] || deny "checkout changed during update"

# Recuperação controlada do incidente de 28/08/2026: o rollback automático
# restaura o banco e deliberadamente deixa backend/caddy parados. O deploy.sh
# precisa do backend anterior vivo apenas para ler DEPLOY_COMMIT na guarda de
# migrations. Se ele estiver parado, religamos SOMENTE o backend privado e
# apenas quando pudermos provar que nenhuma migration mudou desde o release
# que estava ativo antes do incidente. Assim o entrypoint do backend não pode
# aplicar schema novo antes do backup do deploy.
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
