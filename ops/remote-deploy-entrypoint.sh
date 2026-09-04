#!/usr/bin/env bash
# Forced command for the production deploy key. No shell or port forwarding.
# Release protocol:
#   deploy-web <current-main SHA>
# Operational maintenance remains limited to intelligence/intelligence-force
# and cfm-sync for the exact already-deployed SHA.
# Android and Windows release commands are intentionally not accepted.
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export GIT_TERMINAL_PROMPT=0
umask 027
readonly PROJECT_DIR="/opt/meucardio"
readonly ORIGINAL_COMMAND="${SSH_ORIGINAL_COMMAND:-}"
readonly STABLE_ENTRYPOINT="/usr/local/libexec/corvia-remote-deploy-entrypoint"

deny() { printf 'Production request denied: %s\n' "$1" >&2; exit 64; }
REQUEST_KIND=""; EXPECTED_SHA=""; INTELLIGENCE_FORCE="0"
if [[ "$ORIGINAL_COMMAND" =~ ^deploy-web[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="deploy-web"; EXPECTED_SHA="${BASH_REMATCH[1]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^intelligence[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="intelligence"; EXPECTED_SHA="${BASH_REMATCH[1]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^intelligence-force[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="intelligence"; EXPECTED_SHA="${BASH_REMATCH[1]}"; INTELLIGENCE_FORCE="1"
elif [[ "$ORIGINAL_COMMAND" =~ ^cfm-sync[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="cfm-sync"; EXPECTED_SHA="${BASH_REMATCH[1]}"
else
  deny "command is not on the production allow-list"
fi
readonly REQUEST_KIND EXPECTED_SHA INTELLIGENCE_FORCE

[[ -d "$PROJECT_DIR/.git" ]] || deny "production checkout not found"
cd "$PROJECT_DIR"
changes="$(git status --porcelain --untracked-files=normal -- . ':(exclude)downloads')"
[[ -z "$changes" ]] || { printf 'Production checkout is dirty:\n%s\n' "$changes" >&2; exit 65; }
git fetch --prune origin main
remote_main="$(git rev-parse --verify origin/main)"
[[ "$remote_main" == "$EXPECTED_SHA" ]] || { printf 'Requested SHA is not current origin/main.\n' >&2; exit 65; }

require_deployed_sha() {
  [[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || deny "production SHA differs"
}

if [[ "$REQUEST_KIND" == "intelligence" ]]; then
  require_deployed_sha
  docker compose -f docker-compose.prod.yml exec -T backend true >/dev/null 2>&1 || deny "backend not running"
  if [[ "$INTELLIGENCE_FORCE" == "1" ]]; then
    exec docker compose -f docker-compose.prod.yml exec -T -e CORVIA_INTELLIGENCE_FORCE=1 backend python -m app.services.guideline_discovery_cli
  fi
  exec docker compose -f docker-compose.prod.yml exec -T backend python -m app.services.guideline_discovery_cli
fi

if [[ "$REQUEST_KIND" == "cfm-sync" ]]; then
  require_deployed_sha
  docker compose -f docker-compose.prod.yml exec -T backend true >/dev/null 2>&1 || deny "backend not running"
  exec docker compose -f docker-compose.prod.yml exec -T backend python -m app.commands.sync_cfm_registry --download
fi

# Web-only deploy. No native build, signing, staging, promotion or validation.
git checkout main
git merge --ff-only "$EXPECTED_SHA"
[[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || deny "checkout SHA mismatch"
changes="$(git status --porcelain --untracked-files=normal -- . ':(exclude)downloads')"
[[ -z "$changes" ]] || deny "checkout changed during update"

# deploy.sh already owns the certified production transaction: immutable build,
# DB snapshot, migrations, backend readiness, corpus reconciliation, frontend,
# HTTPS certification and rollback. Do not add a second migration/recovery path
# here; that was the source of the previous recovery deadlock.
bash ./deploy.sh

# Self-refresh the stable forced command after a successful web deploy so future
# executions use the exact entrypoint from the deployed SHA.
if [[ -e "$STABLE_ENTRYPOINT" ]]; then
  next_entrypoint="$(mktemp "$(dirname "$STABLE_ENTRYPOINT")/.corvia-entrypoint.XXXXXX")"
  install -o root -g root -m 0755 "$PROJECT_DIR/ops/remote-deploy-entrypoint.sh" "$next_entrypoint"
  bash -n "$next_entrypoint"
  mv -f "$next_entrypoint" "$STABLE_ENTRYPOINT"
fi

printf 'WEB_SHA=%s\n' "$EXPECTED_SHA"
printf 'Release %s deployed web-only. Android and Windows remain disabled.\n' "$EXPECTED_SHA"
