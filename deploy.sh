#!/usr/bin/env bash
# Deploy de produção certificado: backup, build, migrations, corpus e HTTPS.
# Rodar no servidor, dentro da pasta do projeto (/opt/meucardio).
set -Eeuo pipefail

COMPOSE=(docker compose -f docker-compose.prod.yml)
SERVICOS_INICIADOS=0
BANCO_PERSISTENTE=0
ROLLBACK_NECESSARIO=0
TRAFEGO_ABERTO=0
BACKUP_PRE_DEPLOY=""
COMMIT_ATUAL=""
ARVORE_ATUAL=""

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
backend_exec() { "${COMPOSE[@]}" exec -T backend "$@"; }
mostrar_diagnostico() {
  "${COMPOSE[@]}" ps || true
  "${COMPOSE[@]}" logs --tail=200 backend caddy frontend-build db || true
}

compose_project_name() {
  local nome="${COMPOSE_PROJECT_NAME:-$(basename "$PWD")}"
  printf '%s' "$nome" | tr '[:upper:]' '[:lower:]' | sed -E 's/^[^a-z0-9]+//; s/[^a-z0-9_-]+//g'
}

parar_servico_se_existir() {
  local servico="$1" container_id
  container_id="$("${COMPOSE[@]}" ps -a -q "$servico")"
  [[ -z "$container_id" ]] || "${COMPOSE[@]}" stop "$servico"
}

restaurar_backup_pre_deploy() {
  echo "Bloqueando tráfego e revertendo o banco após falha na fase mutável." >&2
  parar_servico_se_existir caddy
  parar_servico_se_existir backend
  TRAFEGO_ABERTO=0

  if [[ -z "$BACKUP_PRE_DEPLOY" ]]; then
    echo "Primeiro deploy sem banco anterior: aplicação permanecerá parada; não há dump para restaurar." >&2
    return 0
  fi
  if [[ ! -f "$BACKUP_PRE_DEPLOY" || ! -f "${BACKUP_PRE_DEPLOY}.sha256" ]]; then
    echo "CRÍTICO: dump pré-deploy ou checksum não encontrado: $BACKUP_PRE_DEPLOY" >&2
    return 1
  fi

  PROJETO="$PWD" \
  RESTAURACAO_AUTOMATICA=1 \
  RESTAURACAO_SEM_RELIGAR=1 \
  CONFIRM_RESTORE_TARGET="$POSTGRES_DB" \
    bash ./infra/backup/restaurar.sh "$BACKUP_PRE_DEPLOY"
}

diagnosticar_erro() {
  local status=$?
  local linha="${BASH_LINENO[0]:-desconhecida}"
  trap - ERR

  if [[ "$ROLLBACK_NECESSARIO" == "1" ]]; then
    if ! restaurar_backup_pre_deploy; then
      echo "CRÍTICO: o rollback automático também falhou. Mantenha o tráfego bloqueado e restaure manualmente o dump." >&2
    fi
    ROLLBACK_NECESSARIO=0
  elif [[ "$TRAFEGO_ABERTO" == "1" ]]; then
    echo "Falha durante a certificação pública; fechando o proxy para evitar falso sucesso." >&2
    if ! parar_servico_se_existir caddy; then
      echo "CRÍTICO: não foi possível confirmar a parada do Caddy." >&2
    fi
    TRAFEGO_ABERTO=0
  fi

  if [[ "$SERVICOS_INICIADOS" == "1" ]]; then
    echo "ERRO: deploy interrompido na linha $linha (status $status)." >&2
    mostrar_diagnostico
  fi
  exit "$status"
}

detectar_banco_persistente() {
  local container_id projeto volume_rotulado volume_deterministico volumes
  BANCO_PERSISTENTE=0
  container_id="$("${COMPOSE[@]}" ps -a -q db)"
  if [[ -n "$container_id" ]]; then BANCO_PERSISTENTE=1; return 0; fi

  projeto="$(compose_project_name)"
  volume_rotulado="$(docker volume ls -q \
    --filter "label=com.docker.compose.project=${projeto}" \
    --filter "label=com.docker.compose.volume=pgdata" | head -n 1)"
  if [[ -n "$volume_rotulado" ]]; then BANCO_PERSISTENTE=1; return 0; fi

  volume_deterministico="${projeto}_pgdata"
  volumes="$(docker volume ls -q)"
  if grep -Fxq "$volume_deterministico" <<< "$volumes"; then BANCO_PERSISTENTE=1; fi
}

aguardar_postgres() {
  local pronto=0
  for _ in $(seq 1 30); do
    if "${COMPOSE[@]}" exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; then pronto=1; break; fi
    sleep 2
  done
  [[ "$pronto" == "1" ]]
}

criar_backup_pre_deploy() {
  local backup_log
  detectar_banco_persistente
  if [[ "$BANCO_PERSISTENTE" != "1" ]]; then
    log "Nenhum container ou volume pgdata existente; backup não se aplica ao primeiro deploy."
    return 0
  fi

  log "Banco persistente imobilizado; iniciando somente o PostgreSQL para o snapshot de rollback."
  "${COMPOSE[@]}" up -d --no-deps db
  aguardar_postgres || { echo "PostgreSQL não ficou pronto para backup." >&2; return 1; }

  backup_log="$(mktemp)"
  if PROJETO="$PWD" bash ./infra/backup/backup.sh | tee "$backup_log"; then
    BACKUP_PRE_DEPLOY="$(tail -n 1 "$backup_log")"
    rm -f "$backup_log"
  else
    rm -f "$backup_log"
    return 1
  fi
  [[ -f "$BACKUP_PRE_DEPLOY" && -f "${BACKUP_PRE_DEPLOY}.sha256" ]] || {
    echo "Backup pré-deploy não foi materializado com checksum." >&2
    return 1
  }
}

validar_checkout_imutavel() {
  local head tree alteracoes
  head="$(git rev-parse --verify HEAD)"
  tree="$(git rev-parse "${head}^{tree}")"
  alteracoes="$(git status --porcelain --untracked-files=normal)"
  if [[ "$head" != "$COMMIT_ATUAL" || "$tree" != "$ARVORE_ATUAL" || -n "$alteracoes" ]]; then
    echo "O checkout mudou durante o deploy; o build não pode ser certificado como $COMMIT_ATUAL." >&2
    [[ -z "$alteracoes" ]] || printf '%s\n' "$alteracoes" >&2
    return 1
  fi
}

# Guarda contra o incidente de deploy de 11/08/2026 (issue #52): uma migration
# foi aplicada manualmente contra o backend antigo, ainda em execução, ANTES
# deste script começar — possível porque `migrations/` é bind mount, e o
# comando de migração (`app.commands.migrate`, o mesmo que o entrypoint do
# container roda) sempre aplica de verdade (não existe modo
# dry-run). O backup pré-deploy tirado depois já saiu contaminado: não
# representava mais o estado real anterior à mudança, e o rollback automático
# do próprio script restaurou um snapshot que já tinha o schema novo.
#
# Correção de design pós-revisão adversarial: a primeira versão comparava o
# `alembic_version` do banco contra o head ABSOLUTO das migrations deste RC —
# e por isso abortaria (falso positivo) todo deploy cujo commit não trouxesse
# migration nova, que é a maioria; e deixaria passar (falso negativo) o caso
# de só PARTE das migrations novas terem sido aplicadas fora de ordem. A
# referência correta não é "o head deste RC" — é "o head que o COMMIT
# ATUALMENTE EM EXECUÇÃO esperava, antes deste deploy tocar em qualquer
# coisa". `DEPLOY_COMMIT` é lido do ambiente do próprio container backend
# ainda rodando (injetado pelo `docker-compose.prod.yml` na hora em que ELE
# foi iniciado, no deploy anterior) — não depende do checkout do host, que
# já está no commit novo neste ponto do script.
#
# Por isso: chamar SÓ depois do build e SEMPRE antes de parar
# caddy/backend — a checagem exige o backend ANTIGO ainda vivo para ler o seu
# próprio `DEPLOY_COMMIT`, e não escreve em `db` (nunca faz `up -d`), evitando
# qualquer recriação de container sob tráfego real.
validar_migrations_nao_adiantadas() {
  local commit_anterior head_esperado versao_atual resultado
  detectar_banco_persistente
  if [[ "$BANCO_PERSISTENTE" != "1" ]]; then
    return 0  # primeiro deploy, sem banco anterior para comparar
  fi

  # A função inteira governa os próprios erros (graceful-skip em qualquer
  # falha de leitura, nunca hard-fail por indisponibilidade de diagnóstico) —
  # `set +e` local evita que `set -Eeuo pipefail` do script aborte no meio de
  # uma checagem que é defensiva, não obrigatória. Restaurado antes de sair,
  # em todo caminho de retorno.
  set +e

  commit_anterior="$("${COMPOSE[@]}" exec -T backend printenv DEPLOY_COMMIT 2>&1)"
  if [[ $? -ne 0 ]]; then
    log "Não foi possível ler DEPLOY_COMMIT do backend em execução (${commit_anterior}); pulando checagem de migration adiantada."
    set -e; return 0
  fi
  commit_anterior="$(tr -d '[:space:]' <<< "$commit_anterior")"
  if [[ -z "$commit_anterior" || "$commit_anterior" == "unknown" ]]; then
    log "DEPLOY_COMMIT do backend em execução indisponível; pulando checagem de migration adiantada (não é motivo para abortar um deploy legítimo)."
    set -e; return 0
  fi

  # Head esperado das migrations NO COMMIT ANTERIOR — via AST do próprio
  # Python (stdlib, sem alembic, sem tocar em nenhum container): lê
  # `revision`/`down_revision` de cada arquivo corretamente, INCLUSIVE
  # merge migrations (`down_revision` como tupla) e anotação de tipo
  # multi-linha — uma extração por regex ingênua aqui já se mostrou
  # ambígua contra o histórico real deste projeto (5 candidatas a head em
  # vez de 1) antes desta versão ser adotada. Head é a única revisão que
  # nenhuma outra, naquele commit, lista como seu(s) `down_revision`.
  resultado="$(
    { git show "${commit_anterior}:backend/migrations/versions" 2>/dev/null \
        | while IFS= read -r nome; do
            [[ "$nome" == *.py ]] || continue
            printf '===ARQUIVO:%s===\n' "$nome"
            git show "${commit_anterior}:backend/migrations/versions/${nome}" 2>/dev/null
          done
    } | python3 -c '
import ast, re, sys

texto = sys.stdin.read()
blocos = re.split(r"^===ARQUIVO:(.+?)===\n", texto, flags=re.M)[1:]

def extrair(no):
    if no is None:
        return []
    if isinstance(no, ast.Constant):
        return [] if no.value is None else [no.value]
    if isinstance(no, (ast.Tuple, ast.List)):
        out = []
        for el in no.elts:
            out.extend(extrair(el))
        return out
    return []

revisoes, downs = set(), set()
for i in range(0, len(blocos), 2):
    nome, conteudo = blocos[i], blocos[i + 1]
    try:
        arvore = ast.parse(conteudo, filename=nome)
    except SyntaxError:
        print("", end="")
        raise SystemExit(0)
    rev = down = None
    for node in ast.walk(arvore):
        alvo = None
        if isinstance(node, ast.Assign):
            alvo = node.targets[0]
        elif isinstance(node, ast.AnnAssign):
            alvo = node.target
        if isinstance(alvo, ast.Name) and alvo.id == "revision":
            rev = extrair(node.value)
        elif isinstance(alvo, ast.Name) and alvo.id == "down_revision":
            down = extrair(node.value)
    if rev:
        revisoes.update(rev)
    if down:
        downs.update(down)

cabecas = revisoes - downs
print(cabecas.pop() if len(cabecas) == 1 else "", end="")
'
  )"
  head_esperado="$resultado"
  if [[ -z "$head_esperado" ]]; then
    log "Não foi possível calcular o head de migrations do commit anterior ($commit_anterior); pulando checagem de migration adiantada."
    set -e; return 0
  fi

  versao_atual="$("${COMPOSE[@]}" exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    -tAc "SELECT version_num FROM alembic_version" 2>&1)"
  if [[ $? -ne 0 ]]; then
    log "Não foi possível ler alembic_version do banco em produção (${versao_atual}); pulando checagem de migration adiantada."
    set -e; return 0
  fi
  versao_atual="$(tr -d '[:space:]' <<< "$versao_atual")"
  if [[ -z "$versao_atual" ]]; then
    log "alembic_version veio vazio; pulando checagem de migration adiantada."
    set -e; return 0
  fi

  set -e
  if [[ "$versao_atual" != "$head_esperado" ]]; then
    cat >&2 <<EOF
ABORTANDO: o banco de produção está em "$versao_atual", mas o commit
ATUALMENTE em execução ($commit_anterior) esperava "$head_esperado" — antes
deste deploy ter feito qualquer mudança.

Isso é o sintoma exato do incidente de 11/08/2026 (issue #52): alguém rodou
o comando de migração (ou 'alembic upgrade head') manualmente
contra o backend em execução, fora deste script — o bind mount de
migrations/ deixa a migration nova visível e APLICÁVEL DE VERDADE mesmo
antes do deploy oficial começar, mesmo que só parcialmente. O backup que
este script tiraria agora não representaria o estado real anterior à
mudança, e um rollback automático restauraria um banco que já tem schema
adiantado.

NUNCA rode comando de migration diretamente contra produção fora deste
script (ver DEPLOY.md). Se a migration já foi aplicada de propósito e você
sabe que o backup pré-deploy correto já existe separadamente, resolva
manualmente antes de tentar de novo — este script não segue sozinho.
EOF
    return 1
  fi
}

trap diagnosticar_erro ERR

if [[ ! -f .env ]]; then
  echo "Falta o arquivo .env. Rode: cp .env.example .env e preencha antes de continuar."
  exit 1
fi
# shellcheck disable=SC1091
source .env

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY está ausente; a central cardiovascular não pode ser habilitada." >&2
  exit 1
fi
# O compose de produção fixa OpenAI para esta release. Sobrescrever aqui evita
# que um AI_PROVIDER legado do .env governe o canário ou a indexação do deploy.
export AI_ENABLED=true
export AI_PROVIDER=openai
export AI_CLINICAL_MULTIMODAL_ENABLED=true
export AI_CLINICAL_DATA_CONTROLS_APPROVED=true

for var in DOMAIN POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB JWT_SECRET; do
  valor="${!var:-}"
  if [[ -z "$valor" ]] || [[ "$valor" == troque-esta-senha* ]] || \
     [[ "$valor" == gere-com-* ]] || [[ "$valor" == *seudominio* ]]; then
    echo "A variável $var no .env está ausente ou mantém valor de exemplo."
    exit 1
  fi
done

for comando in git curl getent sha256sum flock mktemp tail tee grep; do
  command -v "$comando" >/dev/null 2>&1 || { echo "Comando obrigatório ausente no host: $comando" >&2; exit 1; }
done
command -v docker >/dev/null 2>&1 || { echo "Docker não encontrado." >&2; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "Docker Compose v2 não está disponível." >&2; exit 1; }

GIT_DIR="$(git rev-parse --git-dir)"
exec 9>"${GIT_DIR}/corvia-deploy.lock"
flock -n 9 || { echo "Outro deploy já está em execução neste repositório." >&2; exit 1; }

COMMIT_ATUAL="$(git rev-parse --verify HEAD 2>/dev/null || true)"
[[ "$COMMIT_ATUAL" =~ ^[0-9a-f]{40}$ ]] || { echo "Não foi possível identificar um commit Git completo." >&2; exit 1; }
ARVORE_ATUAL="$(git rev-parse "${COMMIT_ATUAL}^{tree}")"
validar_checkout_imutavel
export DEPLOY_COMMIT="$COMMIT_ATUAL"
log "Iniciando deploy do commit $COMMIT_ATUAL para $DOMAIN."

IP_SERVIDOR="$(curl -fsS -4 --max-time 10 ifconfig.me 2>/dev/null || true)"
IP_DOMINIO="$(getent ahostsv4 "$DOMAIN" | awk 'NR == 1 {print $1}' || true)"
if [[ -n "$IP_SERVIDOR" && -n "$IP_DOMINIO" && "$IP_SERVIDOR" != "$IP_DOMINIO" ]]; then
  echo "Aviso: $DOMAIN resolve para $IP_DOMINIO, mas este servidor é $IP_SERVIDOR."
  read -r -p "Continuar mesmo assim? [y/N] " resposta
  [[ "$resposta" == "y" ]] || exit 1
fi

log "Construindo imagens a partir do checkout imutável, sem interromper o tráfego atual."
validar_checkout_imutavel
"${COMPOSE[@]}" build backend frontend-build
validar_checkout_imutavel

log "Validando provedor multimodal sem enviar dados clínicos."
"${COMPOSE[@]}" run --rm --no-deps backend python - <<'PY'
from app.core.config import settings
from app.services.ia.cardiovascular_exam_assist import DEFAULT_MODEL, _post

model = settings.ai_cardiovascular_exam_model.strip() or DEFAULT_MODEL
_, text, _, _ = _post({
    "model": model,
    "input": "Responda somente com a palavra OK.",
    "max_output_tokens": 64,
    "store": False,
})
if not text.strip():
    raise SystemExit("O provedor respondeu sem conteúdo ao canário não clínico.")
print("Provedor multimodal e modelo confirmados por canário não clínico.")
PY
validar_checkout_imutavel

log "Confirmando que nenhuma migration deste RC já foi aplicada fora deste script."
validar_migrations_nao_adiantadas
validar_checkout_imutavel

log "Fechando o proxy e o backend antigo antes do snapshot usado no rollback."
parar_servico_se_existir caddy
TRAFEGO_ABERTO=0
parar_servico_se_existir backend
SERVICOS_INICIADOS=1
# Todas as requisições aceitas antes da indisponibilidade já terminaram; o dump
# feito agora não perde gravações durante o build se houver rollback posterior.
criar_backup_pre_deploy
validar_checkout_imutavel

# O backend executa migrations no próprio comando de entrada. O rollback precisa
# estar armado antes deste `up`, não apenas antes da confirmação idempotente.
ROLLBACK_NECESSARIO=1
"${COMPOSE[@]}" up -d --no-build --remove-orphans db redis backend frontend-build

log "Aguardando readiness do backend sem tráfego público."
BACKEND_PRONTO=0
for _ in $(seq 1 60); do
  if backend_exec python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=3).read()" \
    >/dev/null 2>&1; then BACKEND_PRONTO=1; break; fi
  sleep 2
done
[[ "$BACKEND_PRONTO" == "1" ]] || { echo "Backend não atingiu readiness; tráfego permanecerá fechado." >&2; false; }

log "Confirmando migrations de forma idempotente."
backend_exec python -m app.commands.migrate
log "Reconciliando as 11 coleções e publicando somente conteúdo revisado."
backend_exec python -m app.commands.reconcile_content --publish-reviewed
log "Publicando somente conteúdo atual que já está revisado."
backend_exec python -m app.commands.publish_preserved_content
if [[ "${AI_ENABLED:-false}" == "true" ]]; then
  log "Indexando a base reconciliada para a IA clínica."
  backend_exec python -m app.services.indexar
fi

log "Certificando flags e controles transitórios da central cardiovascular."
backend_exec python - <<'PY'
from app.api.cardiovascular_exam_ai import status_ia_exames

status = status_ia_exames()
expected = {
    "enabled": True,
    "unavailable_reason": None,
    "external_processor": "openai",
    "persists_files_in_corvia": False,
    "provider_response_storage_requested": False,
    "searches_current_guidelines": True,
}
for key, value in expected.items():
    actual = status.get(key)
    if type(actual) is not type(value) or actual != value:
        raise SystemExit(f"Controle multimodal inválido: {key}.")
required_media = {"image/jpeg", "image/png", "application/pdf"}
if not required_media.issubset(set(status.get("supported_media_types", []))):
    raise SystemExit("Os formatos clínicos mínimos não estão habilitados.")
if status.get("max_files", 0) < 5:
    raise SystemExit("A captura de cinco arquivos não está habilitada.")
print("Central cardiovascular habilitada com controles transitórios confirmados.")
PY

# Ainda dentro da janela de rollback: readiness e checkout imutável precisam
# passar antes que o dump deixe de ser a recuperação automática do deploy.
backend_exec python -c \
  "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5).read()"
validar_checkout_imutavel
ROLLBACK_NECESSARIO=0

log "Abrindo o proxy somente após banco, corpus e build estarem certificados."
"${COMPOSE[@]}" up -d --no-build caddy
TRAFEGO_ABERTO=1

PUBLICO_PRONTO=0
for _ in $(seq 1 60); do
  if curl -fsS --max-time 5 "https://${DOMAIN}/api/ready" >/dev/null 2>&1; then PUBLICO_PRONTO=1; break; fi
  sleep 2
done
[[ "$PUBLICO_PRONTO" == "1" ]] || { echo "HTTPS público não respondeu." >&2; false; }

VERSAO_PUBLICA="$(curl -fsS --max-time 10 "https://${DOMAIN}/api/version")"
[[ "$VERSAO_PUBLICA" == *"\"commit\":\"${COMMIT_ATUAL}\""* ]] || {
  echo "ERRO: /api/version não confirmou o commit $COMMIT_ATUAL: $VERSAO_PUBLICA" >&2; false;
}
validar_checkout_imutavel

"${COMPOSE[@]}" ps
TRAFEGO_ABERTO=0
log "Deploy certificado concluído: commit $COMMIT_ATUAL, migrations aplicadas, corpus reconciliado e HTTPS pronto."
