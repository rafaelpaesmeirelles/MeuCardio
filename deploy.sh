#!/usr/bin/env bash
# Recuperação emergencial web-only autorizada em 04/09/2026.
# Publica o frontend já aprovado e religa a infraestrutura existente com backup
# prévio. Não executa testes, não altera conteúdo científico e não toca apps nativos.
set -Eeuo pipefail

COMPOSE=(docker compose -f docker-compose.prod.yml)
log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

[[ -f .env ]] || { echo "Falta .env" >&2; exit 1; }
# shellcheck disable=SC1091
source .env
for var in DOMAIN POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB; do
  [[ -n "${!var:-}" ]] || { echo "$var ausente" >&2; exit 1; }
done
for cmd in git docker curl grep; do command -v "$cmd" >/dev/null || { echo "$cmd ausente" >&2; exit 1; }; done
docker compose version >/dev/null 2>&1 || { echo "Docker Compose v2 indisponível" >&2; exit 1; }

CURRENT_SHA="$(git rev-parse --verify HEAD)"
[[ "$CURRENT_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "SHA inválido" >&2; exit 1; }
export DEPLOY_COMMIT="$CURRENT_SHA"

log "RECUPERAÇÃO EMERGENCIAL: $CURRENT_SHA"
log "Subindo somente PostgreSQL e Redis existentes."
"${COMPOSE[@]}" up -d db redis

DB_OK=0
for _ in $(seq 1 45); do
  if "${COMPOSE[@]}" exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; then DB_OK=1; break; fi
  sleep 2
done
[[ "$DB_OK" == "1" ]] || { echo "PostgreSQL não ficou pronto" >&2; "${COMPOSE[@]}" logs --tail=120 db >&2 || true; exit 1; }

# Impede recuperação acidental sobre um volume novo/vazio.
SCHEMA_PROBE="$("${COMPOSE[@]}" exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT (to_regclass('public.users') IS NOT NULL)::int || ':' || (to_regclass('public.alembic_version') IS NOT NULL)::int" | tr -d '[:space:]')"
[[ "$SCHEMA_PROBE" == "1:1" ]] || {
  echo "ABORTANDO: o volume conectado não contém o schema de produção esperado (users + alembic_version)." >&2
  "${COMPOSE[@]}" ps >&2 || true
  docker volume ls >&2 || true
  exit 65
}
log "Volume de produção reconhecido pelo schema existente."

log "Criando backup pré-recuperação antes de qualquer migration do backend."
BACKUP_LOG="$(mktemp)"
if PROJETO="$PWD" bash ./infra/backup/backup.sh | tee "$BACKUP_LOG"; then
  BACKUP_PRE="$(tail -n 1 "$BACKUP_LOG")"
  rm -f "$BACKUP_LOG"
else
  rm -f "$BACKUP_LOG"
  exit 1
fi
[[ -f "$BACKUP_PRE" && -f "${BACKUP_PRE}.sha256" ]] || { echo "Backup/checksum não encontrado" >&2; exit 1; }
log "Backup pré-recuperação confirmado: $BACKUP_PRE"

log "Construindo frontend aprovado e backend da mesma revisão."
"${COMPOSE[@]}" build frontend-build backend agenda-sync whatsapp-heart-team-worker

log "Publicando arquivos estáticos aprovados no volume do site."
"${COMPOSE[@]}" run --rm --no-deps frontend-build
"${COMPOSE[@]}" run --rm --no-deps --entrypoint sh frontend-build -c "grep -R -F '$CURRENT_SHA' /site >/dev/null"
"${COMPOSE[@]}" run --rm --no-deps --entrypoint sh frontend-build -c "grep -R -F 'corvia-login-galaxy-disc-cloud-rotate' /site >/dev/null"
log "Build contém a cinemática de rotação da galáxia aprovada."

log "Religando backend. O próprio entrypoint aplica somente as migrations pendentes desta revisão."
"${COMPOSE[@]}" up -d --no-deps --force-recreate backend
BACKEND_OK=0
for _ in $(seq 1 100); do
  if "${COMPOSE[@]}" exec -T backend python -c 'import urllib.request; urllib.request.urlopen("http://localhost:8000/api/ready", timeout=3).read()' >/dev/null 2>&1; then BACKEND_OK=1; break; fi
  sleep 2
done

if [[ "$BACKEND_OK" != "1" ]]; then
  echo "Backend não ficou pronto; restaurando automaticamente o backup pré-recuperação." >&2
  "${COMPOSE[@]}" logs --tail=240 backend >&2 || true
  "${COMPOSE[@]}" stop backend agenda-sync whatsapp-heart-team-worker >/dev/null 2>&1 || true
  PROJETO="$PWD" RESTAURACAO_AUTOMATICA=1 RESTAURACAO_SEM_RELIGAR=1 CONFIRM_RESTORE_TARGET="$POSTGRES_DB" \
    bash ./infra/backup/restaurar.sh "$BACKUP_PRE"
  exit 1
fi
log "Backend pronto."

log "Religando proxy e workers sem novo ciclo de migrations."
"${COMPOSE[@]}" up -d --no-deps caddy
"${COMPOSE[@]}" up -d --no-deps agenda-sync whatsapp-heart-team-worker >/dev/null 2>&1 || true

PUBLIC_OK=0
for _ in $(seq 1 45); do
  if curl -kfsS --max-time 5 --resolve "$DOMAIN:443:127.0.0.1" "https://$DOMAIN/entrar" | grep -Fq '<div id="root"' \
    && curl -kfsS --max-time 5 --resolve "$DOMAIN:443:127.0.0.1" "https://$DOMAIN/api/health" >/dev/null \
    && curl -kfsS --max-time 5 --resolve "$DOMAIN:443:127.0.0.1" "https://$DOMAIN/api/ready" >/dev/null; then
    PUBLIC_OK=1; break
  fi
  sleep 2
done
[[ "$PUBLIC_OK" == "1" ]] || {
  echo "HTTPS local não confirmou frontend + backend após recuperação." >&2
  "${COMPOSE[@]}" ps >&2 || true
  "${COMPOSE[@]}" logs --tail=180 caddy backend >&2 || true
  exit 1
}

log "RECUPERAÇÃO CONCLUÍDA: frontend aprovado publicado, galáxias animadas e backend pronto."
printf 'WEB_SHA=%s\n' "$CURRENT_SHA"
printf 'BACKEND_SHA=%s\n' "$CURRENT_SHA"
