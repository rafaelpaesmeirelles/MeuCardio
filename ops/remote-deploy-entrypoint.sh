#!/usr/bin/env bash
# Forced command for the production deploy key. No shell or port forwarding.
# Release protocol:
#   windows-stage <current-main SHA> <Windows SHA-256> (binary on stdin)
#   deploy-release <current-main SHA> <Windows SHA-256> <Android cert SHA-256>
#   deploy-web-android <current-main SHA> <Android cert SHA-256>
#   verify-release <current-main SHA> <Android cert SHA-256>
# Operational maintenance remains limited to intelligence/intelligence-force
# for the exact already-deployed SHA. Web/APK release bypasses are not accepted.
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export GIT_TERMINAL_PROMPT=0
umask 027
readonly PROJECT_DIR="/opt/meucardio"
readonly ORIGINAL_COMMAND="${SSH_ORIGINAL_COMMAND:-}"
readonly RECOVERY_BASE_SHA="59566e1196e0fa7f465df93516790ef454e1f565"
readonly ANDROID_NAME="corvia-cardiology-spaces-android-1.2.0.apk"
readonly WINDOWS_NAME="corvia-cardiology-spaces-windows-1.2.0.exe"
readonly MAX_WINDOWS_BYTES=367001600
readonly STABLE_ENTRYPOINT="/usr/local/libexec/corvia-remote-deploy-entrypoint"
readonly DOWNLOAD_DIR="$PROJECT_DIR/downloads"
readonly RELEASE_LOCK_FILE="$DOWNLOAD_DIR/.corvia-release.lock"

deny() { printf 'Production request denied: %s\n' "$1" >&2; exit 64; }
REQUEST_KIND=""; EXPECTED_SHA=""; EXPECTED_WINDOWS_SHA=""; EXPECTED_ANDROID_CERT_SHA=""; INTELLIGENCE_FORCE="0"
if [[ "$ORIGINAL_COMMAND" =~ ^deploy-release[[:space:]]([0-9a-f]{40})[[:space:]]([0-9a-f]{64})[[:space:]]([0-9a-f]{64})$ ]]; then
  REQUEST_KIND="deploy-release"; EXPECTED_SHA="${BASH_REMATCH[1]}"; EXPECTED_WINDOWS_SHA="${BASH_REMATCH[2]}"; EXPECTED_ANDROID_CERT_SHA="${BASH_REMATCH[3]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^deploy-web-android[[:space:]]([0-9a-f]{40})[[:space:]]([0-9a-f]{64})$ ]]; then
  REQUEST_KIND="deploy-web-android"; EXPECTED_SHA="${BASH_REMATCH[1]}"; EXPECTED_ANDROID_CERT_SHA="${BASH_REMATCH[2]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^verify-release[[:space:]]([0-9a-f]{40})[[:space:]]([0-9a-f]{64})$ ]]; then
  REQUEST_KIND="verify-release"; EXPECTED_SHA="${BASH_REMATCH[1]}"; EXPECTED_ANDROID_CERT_SHA="${BASH_REMATCH[2]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^windows-stage[[:space:]]([0-9a-f]{40})[[:space:]]([0-9a-f]{64})$ ]]; then
  REQUEST_KIND="windows-stage"; EXPECTED_SHA="${BASH_REMATCH[1]}"; EXPECTED_WINDOWS_SHA="${BASH_REMATCH[2]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^intelligence[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="intelligence"; EXPECTED_SHA="${BASH_REMATCH[1]}"
elif [[ "$ORIGINAL_COMMAND" =~ ^intelligence-force[[:space:]]([0-9a-f]{40})$ ]]; then
  REQUEST_KIND="intelligence"; EXPECTED_SHA="${BASH_REMATCH[1]}"; INTELLIGENCE_FORCE="1"
else deny "command is not on the production allow-list"; fi
readonly REQUEST_KIND EXPECTED_SHA EXPECTED_WINDOWS_SHA EXPECTED_ANDROID_CERT_SHA INTELLIGENCE_FORCE
readonly RELEASE_RECEIPT="$DOWNLOAD_DIR/.corvia-release-${EXPECTED_SHA}.json"

[[ -d "$PROJECT_DIR/.git" ]] || deny "production checkout not found"
cd "$PROJECT_DIR"
install -d -m 0755 "$DOWNLOAD_DIR"
if [[ "$REQUEST_KIND" != "intelligence" ]]; then
  exec 9>"$RELEASE_LOCK_FILE"
  flock -w 30 9 || deny "another release operation holds the production lock"
fi
changes="$(git status --porcelain --untracked-files=normal -- . ':(exclude)downloads')"
[[ -z "$changes" ]] || { printf 'Production checkout is dirty:\n%s\n' "$changes" >&2; exit 65; }

require_current_remote_main() {
  local remote_main
  git fetch --prune origin main
  remote_main="$(git rev-parse --verify origin/main)"
  [[ "$remote_main" == "$EXPECTED_SHA" ]] \
    || { printf 'Requested SHA is not current origin/main.\n' >&2; exit 65; }
}
require_current_remote_main

readonly STAGING_ROOT="$PROJECT_DIR/downloads/.release-staging"
readonly RELEASE_STAGING_DIR="$STAGING_ROOT/$EXPECTED_SHA"

receive_windows_artifact() {
  local destination="$1" artifact size actual_sha
  install -d -m 0750 "$(dirname "$destination")"
  artifact="$(mktemp "$(dirname "$destination")/.windows-upload.XXXXXX")"
  trap 'rm -f "$artifact"' EXIT
  timeout 300s head -c "$((MAX_WINDOWS_BYTES + 1))" > "$artifact" || deny "Windows upload timed out"
  size="$(stat -c '%s' "$artifact")"
  [[ "$size" -ge 20000000 && "$size" -le "$MAX_WINDOWS_BYTES" ]] || deny "Windows artifact size invalid"
  [[ "$(od -An -tx1 -N2 "$artifact" | tr -d '[:space:]')" == "4d5a" ]] || deny "Windows PE signature invalid"
  actual_sha="$(sha256sum "$artifact" | cut -d' ' -f1)"
  [[ "$actual_sha" == "$EXPECTED_WINDOWS_SHA" ]] || deny "Windows SHA-256 mismatch"
  install -m 0644 "$artifact" "$destination"
  printf '%s  %s\n' "$actual_sha" "$WINDOWS_NAME" > "$destination.sha256"
  chmod 0644 "$destination.sha256"; rm -f "$artifact"; trap - EXIT
  printf 'WINDOWS_SHA256=%s\n' "$actual_sha"
}

validate_staged_artifact() {
  local artifact="$1" expected_sha="$2" expected_magic="$3" actual_sha magic_bytes
  [[ -s "$artifact" && -s "$artifact.sha256" ]] || deny "staged native artifact incomplete"
  magic_bytes="$(( ${#expected_magic} / 2 ))"
  [[ "$(od -An -tx1 -N"$magic_bytes" "$artifact" | tr -d '[:space:]')" == "$expected_magic" ]] || deny "staged signature invalid"
  actual_sha="$(sha256sum "$artifact" | cut -d' ' -f1)"
  [[ "$actual_sha" == "$expected_sha" ]] || deny "staged digest mismatch"
  grep -Eiq "^${actual_sha}([[:space:]]|$)" "$artifact.sha256" || deny "staged sidecar mismatch"
}

find_android_tool() {
  local name="$1" sdk_dir candidate
  if command -v "$name" >/dev/null 2>&1; then command -v "$name"; return 0; fi
  sdk_dir="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-/opt/android-sdk}}"
  candidate="$(find "$sdk_dir/build-tools" -type f -name "$name" -perm -u+x 2>/dev/null | sort -V | tail -n 1)"
  [[ -n "$candidate" ]] || return 1
  printf '%s\n' "$candidate"
}

completed_release_digest() {
  local receipt="${1:-$RELEASE_RECEIPT}" apk sidecar windows windows_sidecar
  local receipt_digest apksigner cert_output actual_cert version_payload
  apk="$DOWNLOAD_DIR/$ANDROID_NAME"
  sidecar="$apk.sha256"
  windows="$DOWNLOAD_DIR/$WINDOWS_NAME"
  windows_sidecar="$windows.sha256"
  [[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || return 1
  [[ -s "$receipt" && -s "$apk" && -s "$sidecar" ]] || return 1

  receipt_digest="$(python3 scripts/ci_release_policy.py verify-release-receipt \
    --receipt "$receipt" \
    --apk "$apk" \
    --apk-sidecar "$sidecar" \
    --expected-sha "$EXPECTED_SHA" \
    --expected-cert "$EXPECTED_ANDROID_CERT_SHA" \
    --windows "$windows" \
    --windows-sidecar "$windows_sidecar")" || return 1

  apksigner="$(find_android_tool apksigner)" || return 1
  cert_output="$("$apksigner" verify --print-certs "$apk" 2>/dev/null)" || return 1
  actual_cert="$(sed -n 's/^Signer #1 certificate SHA-256 digest: //p' <<< "$cert_output" | head -n 1)"
  actual_cert="$(printf '%s' "$actual_cert" | tr -d '[:space:]:' | tr '[:upper:]' '[:lower:]')"
  [[ "$actual_cert" == "$EXPECTED_ANDROID_CERT_SHA" ]] || return 1

  version_payload="$(curl -fsS --max-time 10 -H 'Cache-Control: no-cache, no-store' \
    "https://corvia.med.br/api/version?release=$EXPECTED_SHA")" || return 1
  python3 - "$EXPECTED_SHA" "$version_payload" <<'PY' || return 1
import json
import sys

expected, raw = sys.argv[1:]
payload = json.loads(raw)
actual = payload.get("commit") or payload.get("version") or payload.get("sha")
if actual != expected:
    raise SystemExit(f"public release is {actual!r}, expected {expected!r}")
PY
  curl -fsS --max-time 10 -H 'Cache-Control: no-cache' \
    "https://corvia.med.br/api/health?release=$EXPECTED_SHA" >/dev/null || return 1
  curl -fsS --max-time 10 -H 'Cache-Control: no-cache' \
    "https://corvia.med.br/api/ready?release=$EXPECTED_SHA" >/dev/null || return 1
  printf '%s\n' "$receipt_digest"
}

require_deployed_sha() { [[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || deny "production SHA differs"; }

if [[ "$REQUEST_KIND" == "verify-release" ]]; then
  require_deployed_sha
  if existing_android_sha="$(completed_release_digest)"; then
    printf 'ANDROID_SHA256=%s\nALREADY_DEPLOYED=1\n' "$existing_android_sha"
    printf 'Release %s receipt and artifacts verified; production unchanged.\n' "$EXPECTED_SHA"
    exit 0
  fi
  deny "release receipt, digest, certificate or runtime state could not be verified"
fi

if [[ "$REQUEST_KIND" == "deploy-release" || "$REQUEST_KIND" == "deploy-web-android" ]] \
  && [[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]]; then
  if existing_android_sha="$(completed_release_digest)"; then
    printf 'ANDROID_SHA256=%s\nALREADY_DEPLOYED=1\n' "$existing_android_sha"
    printf 'Release %s was already complete; no deployment repeated.\n' "$EXPECTED_SHA"
    exit 0
  fi
  deny "release SHA is already checked out but its completion receipt or runtime state is incomplete"
fi

if [[ "$REQUEST_KIND" == "windows-stage" ]]; then
  receive_windows_artifact "$RELEASE_STAGING_DIR/$WINDOWS_NAME"
  printf 'Windows staged; production unchanged.\n'; exit 0
fi
if [[ "$REQUEST_KIND" == "intelligence" ]]; then
  require_deployed_sha
  docker compose -f docker-compose.prod.yml exec -T backend true >/dev/null 2>&1 || deny "backend not running"
  if [[ "$INTELLIGENCE_FORCE" == "1" ]]; then
    exec docker compose -f docker-compose.prod.yml exec -T -e CORVIA_INTELLIGENCE_FORCE=1 backend python -m app.services.guideline_discovery_cli
  fi
  exec docker compose -f docker-compose.prod.yml exec -T backend python -m app.services.guideline_discovery_cli
fi
if [[ "$REQUEST_KIND" == "deploy-release" || "$REQUEST_KIND" == "deploy-web-android" ]]; then
  if [[ "$REQUEST_KIND" == "deploy-release" ]]; then
    validate_staged_artifact "$RELEASE_STAGING_DIR/$WINDOWS_NAME" "$EXPECTED_WINDOWS_SHA" "4d5a"
  fi
  install -d -m 0750 "$RELEASE_STAGING_DIR"
  native_worktree="$(mktemp -d "$STAGING_ROOT/.native-source.XXXXXX")"
  rmdir "$native_worktree"
  git worktree add --detach "$native_worktree" "$EXPECTED_SHA" >/dev/null
  cleanup_native_worktree() { git worktree remove --force "$native_worktree" >/dev/null 2>&1 || true; }
  trap cleanup_native_worktree EXIT
  install -m 0600 "$PROJECT_DIR/frontend/android/keystore.properties" \
    "$native_worktree/frontend/android/keystore.properties"
  python3 - "$native_worktree/frontend/android/keystore.properties" \
    "$PROJECT_DIR/frontend/android/app" <<'PY'
from pathlib import Path
import re
import sys

properties = Path(sys.argv[1])
original_app = Path(sys.argv[2])
lines = properties.read_text(encoding="utf-8").splitlines()
found = False
for index, line in enumerate(lines):
    match = re.match(r"^(\s*storeFile\s*[=:]\s*)(.+?)\s*$", line)
    if not match:
        continue
    value = match.group(2).strip()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = (original_app / candidate).resolve()
    if not candidate.is_file():
        raise SystemExit("Android release keystore referenced by keystore.properties is missing")
    lines[index] = f"storeFile={candidate}"
    found = True
if not found:
    raise SystemExit("keystore.properties has no storeFile")
properties.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
  build_log="$(mktemp "$RELEASE_STAGING_DIR/.android-build.XXXXXX")"
  CORVIA_PROJECT_DIR="$native_worktree" bash "$native_worktree/ops/build-android-apk.sh" \
    "$EXPECTED_SHA" "$RELEASE_STAGING_DIR" "$EXPECTED_ANDROID_CERT_SHA" | tee "$build_log"
  expected_android_sha="$(sed -n 's/^ANDROID_SHA256=//p' "$build_log" | tail -n 1)"
  [[ "$expected_android_sha" =~ ^[0-9a-f]{64}$ ]] || deny "Android build returned no digest"
  validate_staged_artifact "$RELEASE_STAGING_DIR/$ANDROID_NAME" "$expected_android_sha" "504b0304"
  if [[ "$REQUEST_KIND" == "deploy-release" ]]; then
    validate_staged_artifact "$RELEASE_STAGING_DIR/$WINDOWS_NAME" "$EXPECTED_WINDOWS_SHA" "4d5a"
  fi
  cleanup_native_worktree
  trap - EXIT
fi

# Android compilation may take long enough for main to advance. Re-fetch at
# the last safe point before changing the production checkout.
require_current_remote_main
git checkout main
git merge --ff-only "$EXPECTED_SHA"
[[ "$(git rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || deny "checkout SHA mismatch"
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] || deny "checkout changed during update"

if ! docker compose -f docker-compose.prod.yml exec -T backend true >/dev/null 2>&1; then
  git merge-base --is-ancestor "$RECOVERY_BASE_SHA" "$EXPECTED_SHA" || deny "recovery base is not ancestor"
  git diff --quiet "$RECOVERY_BASE_SHA" "$EXPECTED_SHA" -- backend/migrations/versions || deny "backend down and migrations changed"
  DEPLOY_COMMIT="$RECOVERY_BASE_SHA" docker compose -f docker-compose.prod.yml up -d --no-deps backend
  ready=0
  for _ in $(seq 1 30); do
    if docker compose -f docker-compose.prod.yml exec -T backend python -c 'import urllib.request; urllib.request.urlopen("http://localhost:8000/api/ready", timeout=2).read()' >/dev/null 2>&1; then ready=1; break; fi
    sleep 2
  done
  [[ "$ready" == "1" ]] || deny "recovery backend not ready"
fi

bash ./deploy.sh
validate_staged_artifact "$RELEASE_STAGING_DIR/$ANDROID_NAME" "$expected_android_sha" "504b0304"
if [[ "$REQUEST_KIND" == "deploy-release" ]]; then
  validate_staged_artifact "$RELEASE_STAGING_DIR/$WINDOWS_NAME" "$EXPECTED_WINDOWS_SHA" "4d5a"
fi

download_dir="$PROJECT_DIR/downloads"; backup_dir="$RELEASE_STAGING_DIR/.previous"
install -d -m 0755 "$download_dir"; install -d -m 0750 "$backup_dir"
release_artifacts=("$ANDROID_NAME" "$ANDROID_NAME.sha256")
if [[ "$REQUEST_KIND" == "deploy-release" ]]; then
  release_artifacts+=("$WINDOWS_NAME" "$WINDOWS_NAME.sha256")
fi
promotion_failed=0
for name in "${release_artifacts[@]}"; do
  if [[ -e "$download_dir/$name" ]]; then mv "$download_dir/$name" "$backup_dir/$name" || promotion_failed=1; fi
done
if [[ "$promotion_failed" == "0" ]]; then
  for name in "${release_artifacts[@]}"; do
    mv "$RELEASE_STAGING_DIR/$name" "$download_dir/$name" || promotion_failed=1
  done
fi
if [[ "$promotion_failed" != "0" ]]; then
  for name in "${release_artifacts[@]}"; do rm -f "$download_dir/$name"; done
  for name in "${release_artifacts[@]}"; do
    [[ ! -e "$backup_dir/$name" ]] || mv "$backup_dir/$name" "$download_dir/$name"
  done
  deny "native promotion failed; prior clients restored"
fi
rm -rf "$backup_dir" "$RELEASE_STAGING_DIR"
if [[ -e "$STABLE_ENTRYPOINT" ]]; then
  next_entrypoint="$(mktemp "$(dirname "$STABLE_ENTRYPOINT")/.corvia-entrypoint.XXXXXX")"
  install -o root -g root -m 0755 "$PROJECT_DIR/ops/remote-deploy-entrypoint.sh" "$next_entrypoint"
  bash -n "$next_entrypoint"
  mv -f "$next_entrypoint" "$STABLE_ENTRYPOINT"
fi

# The receipt is written only after deploy, public readiness, native promotion
# and entrypoint rotation all succeeded. It turns a lost SSH response into a
# safe no-op on retry, while a partial same-SHA state remains fail-closed.
require_current_remote_main
receipt_candidate="$(mktemp "$DOWNLOAD_DIR/.corvia-release-receipt.XXXXXX")"
trap 'rm -f "$receipt_candidate"' EXIT
python3 - "$receipt_candidate" "$EXPECTED_SHA" "$expected_android_sha" \
  "$EXPECTED_ANDROID_CERT_SHA" "$EXPECTED_WINDOWS_SHA" <<'PY'
from __future__ import annotations

import json
from pathlib import Path
import sys

path, sha, android_sha, android_cert, windows_sha = sys.argv[1:]
payload = {
    "schema": 1,
    "sha": sha,
    "android_name": "corvia-cardiology-spaces-android-1.2.0.apk",
    "android_sha256": android_sha,
    "android_cert_sha256": android_cert,
    "windows_sha256": windows_sha or None,
}
Path(path).write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
chmod 0640 "$receipt_candidate"
certified_android_sha="$(completed_release_digest "$receipt_candidate")" \
  || deny "completed release could not be reconciled before receipt commit"
mv -f "$receipt_candidate" "$RELEASE_RECEIPT"
trap - EXIT

printf 'ANDROID_SHA256=%s\n' "$certified_android_sha"
if [[ "$REQUEST_KIND" == "deploy-release" ]]; then
  printf 'WINDOWS_SHA256=%s\n' "$EXPECTED_WINDOWS_SHA"
fi
printf 'Release %s deployed; certified clients promoted for %s.\n' "$EXPECTED_SHA" "$REQUEST_KIND"
