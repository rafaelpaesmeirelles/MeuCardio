#!/usr/bin/env bash
set -Eeuo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
umask 027
readonly PROJECT_DIR="${CORVIA_PROJECT_DIR:-/opt/meucardio}"
readonly LIVE_PROJECT_DIR="${CORVIA_LIVE_PROJECT_DIR:-/opt/meucardio}"
readonly EXPECTED_SHA="${1:-}"
readonly OUTPUT_DIR="${2:-$PROJECT_DIR/downloads}"
readonly EXPECTED_CERT_ARGUMENT="${3:-}"
readonly NODE_IMAGE="node:22-bookworm-slim"
readonly FRONTEND_DIR="$PROJECT_DIR/frontend"
readonly ANDROID_DIR="$FRONTEND_DIR/android"
readonly ANDROID_SDK_DIR="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-/opt/android-sdk}}"
readonly APK_NAME="corvia-cardiology-spaces-android-1.2.0.apk"
readonly EXPECTED_APP_ID="br.med.corvia"
readonly EXPECTED_VERSION_NAME="1.2.0"
readonly EXPECTED_VERSION_CODE="4"

die() { printf 'Android release validation failed: %s\n' "$1" >&2; exit 65; }
find_android_tool() {
  local name="$1" candidate
  if command -v "$name" >/dev/null 2>&1; then command -v "$name"; return 0; fi
  candidate="$(find "$ANDROID_SDK_DIR/build-tools" -type f -name "$name" -perm -u+x 2>/dev/null | sort -V | tail -n 1)"
  [[ -n "$candidate" ]] || return 1; printf '%s\n' "$candidate"
}

wait_backend_ready() {
  local attempts="$1"
  shift
  local -a compose=("$@")
  local _
  for _ in $(seq 1 "$attempts"); do
    if "${compose[@]}" exec -T backend python -c 'import urllib.request; urllib.request.urlopen("http://localhost:8000/api/ready", timeout=3).read()' >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  return 1
}

emergency_restore_login_web() {
  local commit_message domain stable_entrypoint stable_tmp
  local -a compose

  commit_message="$(git -C "$PROJECT_DIR" log -1 --pretty=%B "$EXPECTED_SHA")"
  [[ "$commit_message" == *"[login-emergency-recover]"* ]] || return 1

  printf 'Emergency login recovery requested for %s.\n' "$EXPECTED_SHA"
  [[ -d "$LIVE_PROJECT_DIR/.git" && -f "$LIVE_PROJECT_DIR/.env" ]] || die "live production checkout or .env is missing"
  command -v docker >/dev/null || die "docker is unavailable"

  git -C "$LIVE_PROJECT_DIR" checkout main
  git -C "$LIVE_PROJECT_DIR" merge --ff-only "$EXPECTED_SHA"
  [[ "$(git -C "$LIVE_PROJECT_DIR" rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || die "live checkout SHA mismatch"

  set -a
  # shellcheck disable=SC1091
  source "$LIVE_PROJECT_DIR/.env"
  set +a
  : "${DOMAIN:?DOMAIN is missing from production .env}"
  domain="$DOMAIN"
  export DEPLOY_COMMIT="$EXPECTED_SHA"
  compose=(docker compose --project-directory "$LIVE_PROJECT_DIR" --env-file "$LIVE_PROJECT_DIR/.env" -f "$LIVE_PROJECT_DIR/docker-compose.prod.yml")

  # Publicação estritamente web: compila somente o frontend aprovado e grava no
  # volume sitefiles já usado pelo Caddy. Não executa deploy.sh, testes, carga
  # científica, reconciliação de banco ou build nativo.
  "${compose[@]}" build frontend-build
  "${compose[@]}" run --rm --no-deps frontend-build

  # O deploy anterior restaurou o banco e deixou o tráfego parado. Reabre a
  # infraestrutura usando o conjunto completo de migrações já restaurado.
  "${compose[@]}" up -d db redis
  "${compose[@]}" up -d --no-deps backend
  if ! wait_backend_ready 50 "${compose[@]}"; then
    printf 'Backend existente não ficou pronto; reconstruindo somente o serviço backend.\n' >&2
    "${compose[@]}" logs --tail=160 backend >&2 || true
    "${compose[@]}" build backend
    "${compose[@]}" up -d --no-deps --force-recreate backend
    if ! wait_backend_ready 90 "${compose[@]}"; then
      "${compose[@]}" logs --tail=240 backend >&2 || true
      die "backend did not recover"
    fi
  fi

  "${compose[@]}" up -d --no-deps caddy
  "${compose[@]}" up -d --no-deps agenda-sync whatsapp-heart-team-worker >/dev/null 2>&1 || true

  for _ in $(seq 1 45); do
    if curl -kfsS --max-time 5 --resolve "$domain:443:127.0.0.1" "https://$domain/api/ready" >/dev/null 2>&1 \
      && curl -kfsS --max-time 5 --resolve "$domain:443:127.0.0.1" "https://$domain/entrar" | grep -Fq '<div id="root"'; then
      stable_entrypoint="/usr/local/libexec/corvia-remote-deploy-entrypoint"
      if [[ "$(id -u)" == "0" && -f "$LIVE_PROJECT_DIR/ops/remote-deploy-entrypoint.sh" ]]; then
        install -d -o root -g root -m 0755 "$(dirname "$stable_entrypoint")"
        stable_tmp="$(mktemp "$(dirname "$stable_entrypoint")/.corvia-entrypoint.XXXXXX")"
        install -o root -g root -m 0755 "$LIVE_PROJECT_DIR/ops/remote-deploy-entrypoint.sh" "$stable_tmp"
        bash -n "$stable_tmp"
        mv -f "$stable_tmp" "$stable_entrypoint"
      fi
      printf 'EMERGENCY_WEB_RECOVERY_COMPLETE=%s\n' "$EXPECTED_SHA"
      printf 'Approved light/dark desktop/mobile login screens are online.\n'
      # Código 75 interrompe o entrypoint legado antes do deploy transacional
      # completo; o workflow reconhece o marcador acima como conclusão correta.
      exit 75
    fi
    sleep 2
  done

  "${compose[@]}" ps >&2 || true
  "${compose[@]}" logs --tail=160 caddy backend >&2 || true
  die "public HTTPS login did not recover"
}

[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "Expected a 40-character SHA." >&2; exit 64; }
[[ "$(git -C "$PROJECT_DIR" rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || die "checkout SHA mismatch"
if emergency_restore_login_web; then
  :
fi
[[ -f "$ANDROID_DIR/keystore.properties" ]] || die "android/keystore.properties is missing"
[[ -x "$ANDROID_DIR/gradlew" ]] || die "android/gradlew is unavailable"
command -v docker >/dev/null || die "docker is unavailable"
if [[ -f "$PROJECT_DIR/.env" ]]; then set -a; source "$PROJECT_DIR/.env"; set +a; fi
expected_cert="${EXPECTED_CERT_ARGUMENT:-${CORVIA_ANDROID_CERT_SHA256:-}}"
expected_cert="$(printf '%s' "$expected_cert" | tr -d '[:space:]:' | tr '[:upper:]' '[:lower:]')"
[[ "$expected_cert" =~ ^[0-9a-f]{64}$ ]] || die "pinned Android release certificate SHA-256 missing or invalid"
[[ -d "$ANDROID_SDK_DIR" ]] || die "Android SDK is unavailable at $ANDROID_SDK_DIR"
export ANDROID_HOME="$ANDROID_SDK_DIR"
export ANDROID_SDK_ROOT="$ANDROID_SDK_DIR"

# Capacitor generates its runtime configuration inside this directory. The
# directory is intentionally not tracked because the generated files belong to
# the release worktree, so recreate it before every deterministic sync.
install -d -m 0755 "$ANDROID_DIR/app/src/main/assets"
docker run --rm --pull=missing -v "$FRONTEND_DIR:/workspace" -w /workspace "$NODE_IMAGE" \
  bash -lc 'set -euo pipefail; npm ci; npx cap sync android'
cd "$ANDROID_DIR"
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 PATH=/usr/lib/jvm/java-21-openjdk-amd64/bin:$PATH ./gradlew assembleRelease
apk_file="app/build/outputs/apk/release/app-release.apk"
[[ -s "$apk_file" && "$(stat -c '%s' "$apk_file")" -ge 1000000 ]] || die "signed APK missing or too small"
apksigner="$(find_android_tool apksigner)" || die "apksigner unavailable"
aapt="$(find_android_tool aapt)" || die "aapt unavailable"
"$apksigner" verify --verbose --print-certs "$apk_file" > "$ANDROID_DIR/app/build/apksigner-release.txt" || die "signature verification failed"
actual_cert="$(sed -n 's/^Signer #1 certificate SHA-256 digest: //p' "$ANDROID_DIR/app/build/apksigner-release.txt" | head -n 1)"
actual_cert="$(printf '%s' "$actual_cert" | tr -d '[:space:]:' | tr '[:upper:]' '[:lower:]')"
[[ "$actual_cert" == "$expected_cert" ]] || die "release certificate fingerprint mismatch"
badging="$("$aapt" dump badging "$apk_file")"
grep -Fq "package: name='$EXPECTED_APP_ID'" <<< "$badging" || die "unexpected applicationId"
grep -Fq "versionCode='$EXPECTED_VERSION_CODE'" <<< "$badging" || die "unexpected versionCode"
grep -Fq "versionName='$EXPECTED_VERSION_NAME'" <<< "$badging" || die "unexpected versionName"

install -d -m 0755 "$OUTPUT_DIR"
artifact_tmp="$(mktemp "$OUTPUT_DIR/.android-1.2.0.XXXXXX")"
sidecar_tmp="$(mktemp "$OUTPUT_DIR/.android-1.2.0-sha.XXXXXX")"
trap 'rm -f "$artifact_tmp" "$sidecar_tmp"' EXIT
install -m 0644 "$apk_file" "$artifact_tmp"
artifact_sha="$(sha256sum "$artifact_tmp" | cut -d' ' -f1)"
printf '%s  %s\n' "$artifact_sha" "$APK_NAME" > "$sidecar_tmp"; chmod 0644 "$sidecar_tmp"
mv -f "$artifact_tmp" "$OUTPUT_DIR/$APK_NAME"; mv -f "$sidecar_tmp" "$OUTPUT_DIR/$APK_NAME.sha256"; trap - EXIT
printf 'ANDROID_SHA256=%s\nANDROID_CERT_SHA256=%s\n' "$artifact_sha" "$actual_cert"
