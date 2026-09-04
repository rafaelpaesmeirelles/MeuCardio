#!/usr/bin/env bash
# Estágio temporário de recuperação operacional: reabre apenas frontend/Caddy
# sobre o backend de recuperação já iniciado pelo entrypoint remoto.
set -Eeuo pipefail
COMPOSE=(docker compose -f docker-compose.prod.yml)
# shellcheck disable=SC1091
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
