#!/usr/bin/env bash
# One-time, non-deploying bootstrap from an already fetched, reviewed main SHA.
# Must be run in an authenticated administrative session on production.
set -Eeuo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
umask 077

readonly PROJECT_DIR="/opt/meucardio"
readonly EXPECTED_SHA="${1:-}"
readonly AUTHORIZED_KEYS="/root/.ssh/authorized_keys"
readonly KEY_MARKER="corvia-github-actions-deploy"
readonly STABLE_ENTRYPOINT="/usr/local/libexec/corvia-remote-deploy-entrypoint"

[[ "$(id -u)" == "0" ]] || { echo "Run as root." >&2; exit 1; }
[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "Expected a full SHA." >&2; exit 64; }
[[ -d "$PROJECT_DIR/.git" && -f "$AUTHORIZED_KEYS" ]] || { echo "Production checkout/key file missing." >&2; exit 65; }
cd "$PROJECT_DIR"
git fetch --prune origin main
[[ "$(git rev-parse origin/main)" == "$EXPECTED_SHA" ]] || { echo "SHA is not current origin/main." >&2; exit 65; }

tmpdir="$(mktemp -d)"
cleanup() { rm -rf "$tmpdir"; }
trap cleanup EXIT
git show "$EXPECTED_SHA:ops/remote-deploy-entrypoint.sh" > "$tmpdir/entrypoint"
bash -n "$tmpdir/entrypoint"
grep -Fq 'windows-stage' "$tmpdir/entrypoint"
grep -Fq 'deploy-release' "$tmpdir/entrypoint"
install -d -o root -g root -m 0755 "$(dirname "$STABLE_ENTRYPOINT")"
install -o root -g root -m 0755 "$tmpdir/entrypoint" "$tmpdir/entrypoint.installed"

python3 - "$AUTHORIZED_KEYS" "$KEY_MARKER" "$STABLE_ENTRYPOINT" "$tmpdir/authorized_keys.new" <<'PY'
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
marker_text = sys.argv[2]
command = sys.argv[3]
output = Path(sys.argv[4])
lines = source.read_text(encoding="utf-8").splitlines()
indexes = [i for i, line in enumerate(lines) if line.endswith(f" {marker_text}")]
if len(indexes) != 1:
    raise SystemExit(f"expected exactly one {marker_text!r} authorized key, found {len(indexes)}")
i = indexes[0]
match = re.fullmatch(r'restrict,command="[^"]+" (ssh-[^ ]+ [^ ]+ .+)', lines[i])
if not match:
    raise SystemExit("marked authorized key does not have the expected restricted format")
lines[i] = f'restrict,command="{command}" {match.group(1)}'
output.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

cp -a "$AUTHORIZED_KEYS" "$tmpdir/authorized_keys.backup"
install -o root -g root -m 0755 "$tmpdir/entrypoint.installed" "$STABLE_ENTRYPOINT"
if ! install -o root -g root -m 0600 "$tmpdir/authorized_keys.new" "$AUTHORIZED_KEYS"; then
  install -o root -g root -m 0600 "$tmpdir/authorized_keys.backup" "$AUTHORIZED_KEYS"
  exit 1
fi
printf 'Forced command bootstrapped from %s without checkout or deploy. SHA256=%s\n' \
  "$EXPECTED_SHA" "$(sha256sum "$STABLE_ENTRYPOINT" | cut -d' ' -f1)"
