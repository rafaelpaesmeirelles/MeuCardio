#!/usr/bin/env bash
set -Eeuo pipefail
COMPOSE=(docker compose -f docker-compose.prod.yml)
source .env
export DEPLOY_COMMIT="$(git rev-parse --verify HEAD)"
"${COMPOSE[@]}" build frontend-build
"${COMPOSE[@]}" run --rm --no-deps frontend-build
"${COMPOSE[@]}" up -d --no-build --no-deps caddy
for _ in $(seq 1 45); do
  if curl -fsS --max-time 4 "https://${DOMAIN}/api/health" >/dev/null 2>&1; then
    echo "Emergency recovery stage online."
    exit 0
  fi
  sleep 2
done
echo "Emergency recovery stage did not restore public health." >&2
exit 1
