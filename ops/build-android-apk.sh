#!/usr/bin/env bash
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
umask 027

readonly PROJECT_DIR="/opt/meucardio"
readonly EXPECTED_SHA="${1:-}"
readonly NODE_IMAGE="node:22-bookworm-slim"
readonly FRONTEND_DIR="$PROJECT_DIR/frontend"
readonly ANDROID_DIR="$FRONTEND_DIR/android"
readonly DOWNLOAD_DIR="$PROJECT_DIR/downloads"

[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "Expected a 40-character SHA." >&2; exit 64; }
[[ "$(git -C "$PROJECT_DIR" rev-parse --verify HEAD)" == "$EXPECTED_SHA" ]] || {
  echo "Checkout SHA mismatch while building Android APK." >&2
  exit 65
}
[[ -f "$ANDROID_DIR/keystore.properties" ]] || { echo "android/keystore.properties is missing." >&2; exit 65; }
[[ -x "$ANDROID_DIR/gradlew" ]] || { echo "android/gradlew is unavailable." >&2; exit 65; }
command -v docker >/dev/null || { echo "docker is unavailable." >&2; exit 65; }

printf 'Synchronizing Capacitor with isolated Node 22 image %s.\n' "$NODE_IMAGE"
docker run --rm --pull=missing \
  -v "$FRONTEND_DIR:/workspace" \
  -w /workspace \
  "$NODE_IMAGE" \
  bash -lc 'set -euo pipefail; node --version; npm --version; npm ci; npx cap sync android'

cd "$ANDROID_DIR"
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
  PATH=/usr/lib/jvm/java-21-openjdk-amd64/bin:$PATH \
  ./gradlew assembleRelease

apk_file="app/build/outputs/apk/release/app-release.apk"
[[ -s "$apk_file" ]] || { echo "Signed release APK was not generated." >&2; exit 65; }

install -d -m 0755 "$DOWNLOAD_DIR"
install -m 0644 "$apk_file" "$DOWNLOAD_DIR/corvia-os-android-1.0.1.apk"
cp "$DOWNLOAD_DIR/corvia-os-android-1.0.1.apk" "$DOWNLOAD_DIR/corvia-os-android.apk"
cd "$DOWNLOAD_DIR"
sha256sum corvia-os-android-1.0.1.apk > corvia-os-android-1.0.1.apk.sha256
sha256sum corvia-os-android.apk > corvia-os-android.apk.sha256

printf 'Android APK published for %s.\n' "$EXPECTED_SHA"
