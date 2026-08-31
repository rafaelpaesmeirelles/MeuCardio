#!/usr/bin/env bash
# One-time production setup. Run as root from /opt/meucardio after this file is
# present on main. It creates a restricted key and stores its private half in
# GitHub Actions without printing it.
set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
umask 077

readonly REPOSITORY="${CORVIA_GITHUB_REPOSITORY:-rafaelpaesmeirelles/MeuCardio}"
readonly SSH_HOST="${1:-169.58.78.100}"
readonly SSH_PORT="${2:-22}"
readonly SSH_USER="root"
readonly PROJECT_DIR="/opt/meucardio"
readonly SOURCE_ENTRYPOINT="$PROJECT_DIR/ops/remote-deploy-entrypoint.sh"
readonly ENTRYPOINT="/usr/local/libexec/corvia-remote-deploy-entrypoint"
readonly AUTHORIZED_KEYS="/root/.ssh/authorized_keys"
readonly KEY_MARKER="corvia-github-actions-deploy"

[[ "$(id -u)" == "0" ]] || { echo "Run this installer as root." >&2; exit 1; }
[[ "$SSH_HOST" =~ ^[A-Za-z0-9.-]+$ ]] || { echo "Invalid SSH host." >&2; exit 64; }
[[ "$SSH_PORT" =~ ^[0-9]{1,5}$ ]] || { echo "Invalid SSH port." >&2; exit 64; }
(( SSH_PORT >= 1 && SSH_PORT <= 65535 )) || { echo "SSH port is out of range." >&2; exit 64; }
[[ -f "$SOURCE_ENTRYPOINT" ]] || { echo "$SOURCE_ENTRYPOINT must exist." >&2; exit 1; }
bash -n "$SOURCE_ENTRYPOINT"
install -d -o root -g root -m 0755 "$(dirname "$ENTRYPOINT")"
install -o root -g root -m 0755 "$SOURCE_ENTRYPOINT" "$ENTRYPOINT"

for command in gh git ssh-keygen; do
  command -v "$command" >/dev/null || { echo "Missing required command: $command" >&2; exit 1; }
done
gh auth status >/dev/null

tmpdir="$(mktemp -d)"
authorization_installed=0
cleanup() {
  status=$?
  trap - EXIT
  if [[ "$status" -ne 0 && "$authorization_installed" == "1" ]]; then
    cp "$tmpdir/authorized_keys.backup" "$AUTHORIZED_KEYS"
    echo "Setup failed; authorized_keys was restored." >&2
  fi
  rm -rf "$tmpdir"
  exit "$status"
}
trap cleanup EXIT
key_file="$tmpdir/deploy_key"
ssh-keygen -q -t ed25519 -N '' -C "$KEY_MARKER" -f "$key_file"
read -r key_type key_data _ < "$key_file.pub"

install -m 0700 -d /root/.ssh
touch "$AUTHORIZED_KEYS"
chmod 0600 "$AUTHORIZED_KEYS"
cp -a "$AUTHORIZED_KEYS" "$tmpdir/authorized_keys.backup"

python3 - "$AUTHORIZED_KEYS" "$KEY_MARKER" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
marker = sys.argv[2]
lines = [line for line in path.read_text(encoding="utf-8").splitlines() if not line.endswith(f" {marker}")]
path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
PY
printf 'restrict,command="%s" %s %s %s\n' \
  "$ENTRYPOINT" "$key_type" "$key_data" "$KEY_MARKER" >> "$AUTHORIZED_KEYS"
authorization_installed=1

if [[ ! -r /etc/ssh/ssh_host_ed25519_key.pub ]]; then
  echo "Missing /etc/ssh/ssh_host_ed25519_key.pub." >&2
  exit 1
fi
read -r host_key_type host_key_data _ < /etc/ssh/ssh_host_ed25519_key.pub
known_host="$SSH_HOST"
if [[ "$SSH_PORT" != "22" ]]; then
  known_host="[$SSH_HOST]:$SSH_PORT"
fi
printf '%s %s %s\n' "$known_host" "$host_key_type" "$host_key_data" > "$tmpdir/known_hosts"

gh secret set PRODUCTION_SSH_PRIVATE_KEY --repo "$REPOSITORY" < "$key_file"
printf '%s' "$SSH_HOST" | gh secret set PRODUCTION_SSH_HOST --repo "$REPOSITORY"
printf '%s' "$SSH_PORT" | gh secret set PRODUCTION_SSH_PORT --repo "$REPOSITORY"
printf '%s' "$SSH_USER" | gh secret set PRODUCTION_SSH_USER --repo "$REPOSITORY"
gh secret set PRODUCTION_SSH_KNOWN_HOSTS --repo "$REPOSITORY" < "$tmpdir/known_hosts"

authorization_installed=0
echo "Restricted production deploy key installed and GitHub secrets configured."
echo "The key accepts only the forced entrypoint allow-list; release commands require exact current origin/main SHA."
