#!/usr/bin/env bash
# Forced command for the GitHub Actions deploy key. This key cannot open a
# shell, forward ports, or execute any command other than `deploy <main SHA>`.
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export GIT_TERMINAL_PROMPT=0
umask 027

readonly PROJECT_DIR="/opt/meucardio"
readonly ORIGINAL_COMMAND="${SSH_ORIGINAL_COMMAND:-}"

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

exec bash ./deploy.sh
