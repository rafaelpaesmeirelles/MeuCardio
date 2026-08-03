#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
MAX_BACKUP_AGE_SECONDS="${MAX_BACKUP_AGE_SECONDS:-93600}"

if ! [[ "$MAX_BACKUP_AGE_SECONDS" =~ ^[0-9]+$ ]] || [[ "$MAX_BACKUP_AGE_SECONDS" -le 0 ]]; then
  printf '{"status":"invalid_configuration","field":"MAX_BACKUP_AGE_SECONDS"}\n' >&2
  exit 3
fi

if [[ ! -d "$BACKUP_DIR" ]]; then
  printf '{"status":"missing","reason":"backup_directory_not_found"}\n' >&2
  exit 2
fi

latest_record="$({
  find "$BACKUP_DIR" -maxdepth 1 -type f \
    \( -name 'corvia-*.dump' -o -name 'corvia-*.dump.age' \) \
    -printf '%T@ %p\n'
} | sort -nr | sed -n '1p')"

if [[ -z "$latest_record" ]]; then
  printf '{"status":"missing","reason":"backup_file_not_found"}\n' >&2
  exit 2
fi

modified_raw="${latest_record%% *}"
backup_file="${latest_record#* }"
modified_epoch="${modified_raw%%.*}"
now_epoch="$(date +%s)"
age_seconds="$((now_epoch - modified_epoch))"
checksum_file="${backup_file}.sha256"

if [[ ! -f "$checksum_file" ]]; then
  printf '{"status":"invalid","reason":"checksum_missing","age_seconds":%s}\n' "$age_seconds" >&2
  exit 2
fi

if ! (
  cd "$(dirname "$backup_file")"
  sha256sum --check --status "$(basename "$checksum_file")"
); then
  printf '{"status":"invalid","reason":"checksum_failed","age_seconds":%s}\n' "$age_seconds" >&2
  exit 2
fi

if [[ "$age_seconds" -gt "$MAX_BACKUP_AGE_SECONDS" ]]; then
  printf '{"status":"stale","age_seconds":%s,"max_age_seconds":%s}\n' \
    "$age_seconds" "$MAX_BACKUP_AGE_SECONDS" >&2
  exit 2
fi

printf '{"status":"ok","age_seconds":%s,"max_age_seconds":%s}\n' \
  "$age_seconds" "$MAX_BACKUP_AGE_SECONDS"
