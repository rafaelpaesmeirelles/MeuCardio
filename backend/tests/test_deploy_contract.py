"""Gates operacionais do deploy, backup e restauração de produção."""

from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOY = REPO_ROOT / "deploy.sh"
BACKUP = REPO_ROOT / "infra/backup/backup.sh"
RESTORE = REPO_ROOT / "infra/backup/restaurar.sh"
COMPOSE = REPO_ROOT / "docker-compose.prod.yml"
HEALTH = REPO_ROOT / "backend/app/api/health.py"
FRONTEND_DOCKERIGNORE = REPO_ROOT / "frontend/.dockerignore"
BACKEND_DOCKERIGNORE = REPO_ROOT / "backend/.dockerignore"
FRONTEND_DOCKERFILE = REPO_ROOT / "frontend/Dockerfile.prod"


def _fonte(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def _linhas_ativas(caminho: Path) -> list[str]:
    return [
        linha.strip()
        for linha in _fonte(caminho).splitlines()
        if linha.strip() and not linha.lstrip().startswith("#")
    ]


def test_scripts_operacionais_possuem_sintaxe_bash_valida():
    resultado = subprocess.run(
        ["bash", "-n", str(DEPLOY), str(BACKUP), str(RESTORE)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    assert resultado.returncode == 0, resultado.stderr


def test_deploy_exige_readiness_antes_de_migrar_e_reconciliar():
    fonte = _fonte(DEPLOY)
    assert "BACKEND_PRONTO=0" in fonte
    assert "http://localhost:8000/api/ready" in fonte
    assert "tráfego permanecerá fechado" in fonte
    assert fonte.index("BACKEND_PRONTO=0") < fonte.index("python -m app.commands.migrate")
    assert fonte.index("python -m app.commands.migrate") < fonte.index(
        "python -m app.commands.reconcile_content --publish-reviewed"
    )


def test_deploy_constroi_antes_da_indisponibilidade_e_abre_proxy_por_ultimo():
    fonte = _fonte(DEPLOY)
    indice_build = fonte.index('"${COMPOSE[@]}" build backend frontend-build')
    indice_stop_caddy = fonte.index("parar_servico_se_existir caddy", indice_build)
    indice_up_privado = fonte.index(
        '"${COMPOSE[@]}" up -d --no-build --remove-orphans db redis backend frontend-build'
    )
    indice_reconcile = fonte.index("python -m app.commands.reconcile_content --publish-reviewed")
    indice_up_caddy = fonte.index('"${COMPOSE[@]}" up -d --no-build caddy')

    assert indice_build < indice_stop_caddy < indice_up_privado < indice_reconcile < indice_up_caddy
    assert 'up -d --build --remove-orphans' not in fonte
    assert "Abrindo o proxy somente após banco, corpus e build estarem certificados" in fonte


def test_deploy_diagnostica_falhas_inesperadas_apos_subir_servicos():
    fonte = _fonte(DEPLOY)
    linhas = [linha.strip() for linha in fonte.splitlines()]
    linha_up = linhas.index(
        '"${COMPOSE[@]}" up -d --no-build --remove-orphans db redis backend frontend-build'
    )
    inicios = [i for i, linha in enumerate(linhas) if linha == "SERVICOS_INICIADOS=1"]
    assert "diagnosticar_erro()" in fonte
    assert "trap diagnosticar_erro ERR" in fonte
    assert 'if [[ "$SERVICOS_INICIADOS" == "1" ]]' in fonte
    assert any(inicio < linha_up for inicio in inicios)


def test_deploy_restaura_dump_se_fase_mutavel_falhar():
    fonte = _fonte(DEPLOY)
    indice_rollback_on = fonte.index("ROLLBACK_NECESSARIO=1")
    indice_migrate = fonte.index("python -m app.commands.migrate")
    indice_reconcile = fonte.index("python -m app.commands.reconcile_content --publish-reviewed")
    indice_rollback_off = fonte.index("ROLLBACK_NECESSARIO=0", indice_reconcile)

    assert indice_rollback_on < indice_migrate < indice_reconcile < indice_rollback_off
    assert "restaurar_backup_pre_deploy()" in fonte
    assert "RESTAURACAO_AUTOMATICA=1" in fonte
    assert "RESTAURACAO_SEM_RELIGAR=1" in fonte
    assert 'CONFIRM_RESTORE_TARGET="$POSTGRES_DB"' in fonte
    assert 'bash ./infra/backup/restaurar.sh "$BACKUP_PRE_DEPLOY"' in fonte
    assert "aplicação permanecerá parada; não há dump para restaurar" in fonte
    assert "rollback automático também falhou" in fonte


def test_deploy_preserva_banco_persistente_mesmo_parado_e_sem_labels():
    fonte = _fonte(DEPLOY)
    linhas_ativas = "\n".join(_linhas_ativas(DEPLOY))
    assert "BANCO_PERSISTENTE=0" in fonte
    assert "detectar_banco_persistente()" in fonte
    assert 'container_id="$("${COMPOSE[@]}" ps -a -q db)"' in fonte
    assert 'ps -a -q db 2>/dev/null || true' not in linhas_ativas
    assert "label=com.docker.compose.volume=pgdata" in fonte
    assert 'volume_deterministico="${projeto}_pgdata"' in fonte
    assert 'grep -Fxq "$volume_deterministico"' in fonte
    assert '"${COMPOSE[@]}" up -d --no-deps db' in fonte
    assert 'PROJETO="$PWD" bash ./infra/backup/backup.sh' in fonte
    assert 'BACKUP_PRE_DEPLOY="$(tail -n 1 "$BACKUP_LOG")"' in fonte


def test_deploy_nao_volta_ao_importador_parcial():
    fonte = _fonte(DEPLOY)
    assert "app.services.importer" not in fonte
    assert "--allow-partial" not in fonte
    assert "python -m app.commands.reconcile_content --publish-reviewed" in fonte


def test_deploy_exige_https_publico_e_fecha_proxy_se_certificacao_falhar():
    fonte = _fonte(DEPLOY)
    assert 'https://${DOMAIN}/api/ready' in fonte
    assert "PUBLICO_PRONTO=0" in fonte
    assert "TRAFEGO_ABERTO=1" in fonte
    assert "Falha durante a certificação pública; fechando o proxy" in fonte
    assert 'https://${DOMAIN}/api/version' in fonte


def test_deploy_bloqueia_concorrencia_e_revalida_checkout():
    fonte = _fonte(DEPLOY)
    assert "git status --porcelain --untracked-files=normal" in fonte
    assert 'exec 9>"${GIT_DIR}/corvia-deploy.lock"' in fonte
    assert "flock -n 9" in fonte
    assert "Outro deploy já está em execução" in fonte
    assert "ARVORE_ATUAL" in fonte
    assert "O checkout mudou durante o deploy" in fonte
    assert fonte.count("validar_checkout_imutavel") >= 5
    assert "for comando in git curl getent sha256sum flock mktemp tail tee grep" in fonte


def test_contextos_docker_excluem_artefatos_ignorados_locais():
    frontend = set(_linhas_ativas(FRONTEND_DOCKERIGNORE))
    backend = set(_linhas_ativas(BACKEND_DOCKERIGNORE))
    assert {"node_modules/", "dist/", ".env", ".env.*"}.issubset(frontend)
    assert {"__pycache__/", ".pytest_cache/", ".venv/", "venv/", ".env", ".env.*"}.issubset(backend)


def test_frontend_instala_dependencias_deterministicamente_pelo_lockfile():
    fonte = _fonte(FRONTEND_DOCKERFILE)
    assert "COPY package.json package-lock.json ./" in fonte
    assert "RUN npm ci" in fonte
    assert "RUN npm install" not in fonte
    assert fonte.index("COPY package.json package-lock.json ./") < fonte.index("RUN npm ci")
    assert fonte.index("RUN npm ci") < fonte.index("COPY . .")


def test_deploy_injeta_e_confirma_commit_publico():
    deploy = _fonte(DEPLOY)
    compose = _fonte(COMPOSE)
    health = _fonte(HEALTH)
    assert 'export DEPLOY_COMMIT="$COMMIT_ATUAL"' in deploy
    assert 'https://${DOMAIN}/api/version' in deploy
    assert "DEPLOY_COMMIT: ${DEPLOY_COMMIT:-unknown}" in compose
    assert '@router.get("/version")' in health


def test_backup_e_portavel_atomico_restauravel_e_verificado():
    fonte = _fonte(BACKUP)
    linhas_ativas = "\n".join(_linhas_ativas(BACKUP))
    assert 'PROJETO="${PROJETO:-' in fonte
    assert "/opt/meucardio" not in linhas_ativas
    assert 'TEMPORARIO="${ARQUIVO}.tmp"' in fonte
    assert "--format=custom" in fonte
    assert "pg_restore --list" in fonte
    assert 'sha256sum "$(basename "$ARQUIVO")"' in fonte
    assert "--no-owner" in fonte and "--no-privileges" in fonte


def test_restaurador_valida_antes_de_apagar_e_usa_pg_restore():
    fonte = _fonte(RESTORE)
    indice_hash = fonte.index('hash_calculado="$(sha256sum "$arquivo"')
    indice_catalogo = fonte.index("pg_restore --list")
    indice_drop = fonte.index("dropdb")
    assert indice_hash < indice_drop
    assert indice_catalogo < indice_drop
    assert "--exit-on-error" in fonte
    assert "Checksum não corresponde ao dump selecionado" in fonte
    assert 'nome_registrado" != "$(basename "$arquivo")"' in fonte
    assert '[[ "$banco_confirmado" == "$POSTGRES_DB" ]]' in fonte


def test_restaurador_so_apaga_depois_de_parar_backend_existente():
    linhas = _linhas_ativas(RESTORE)
    indice_container = next(
        i for i, linha in enumerate(linhas) if linha.startswith('BACKEND_CONTAINER="$(')
    )
    indice_stop = next(
        i
        for i, linha in enumerate(linhas[indice_container + 1 :], indice_container + 1)
        if linha == '"${COMPOSE[@]}" stop backend'
    )
    indice_drop = next(
        i
        for i, linha in enumerate(linhas[indice_stop + 1 :], indice_stop + 1)
        if " exec -T db dropdb " in f" {linha} "
    )
    assert indice_container < indice_stop < indice_drop
    fonte = _fonte(RESTORE)
    assert 'ps -a -q backend 2>/dev/null || true' not in fonte
    assert 'stop backend >/dev/null 2>&1 || true' not in fonte


def test_restaurador_suporta_rollback_automatico_sem_reabrir_backend():
    fonte = _fonte(RESTORE)
    assert 'MODO_AUTOMATICO="${RESTAURACAO_AUTOMATICA:-0}"' in fonte
    assert 'SEM_RELIGAR="${RESTAURACAO_SEM_RELIGAR:-0}"' in fonte
    assert 'CONFIRM_RESTORE_TARGET' in fonte
    assert "Confirmação automática divergente" in fonte
    assert 'if [[ "$SEM_RELIGAR" == "1" ]]' in fonte
    assert "Backend e tráfego permanecem parados" in fonte
    assert fonte.index('if [[ "$SEM_RELIGAR" == "1" ]]') < fonte.index("BACKEND_RELIGADO=1")


def test_restaurador_para_backend_novamente_se_readiness_final_falhar():
    fonte = _fonte(RESTORE)
    assert "BACKEND_RELIGADO=0" in fonte
    assert 'if [[ "$BACKEND_RELIGADO" == "1" ]]' in fonte
    assert "Falha após tentar religar o backend" in fonte
    assert "BACKEND_RELIGADO=1" in fonte
    assert fonte.index("BACKEND_RELIGADO=1") < fonte.index('"${COMPOSE[@]}" up -d backend')
    assert "CRÍTICO: não foi possível confirmar a parada do backend" in fonte


def test_restaurador_mantem_compatibilidade_com_backup_sql_gzip_legado():
    fonte = _fonte(RESTORE)
    assert "*.sql.gz" in fonte
    assert 'FORMATO="sql-gzip-legado"' in fonte
    assert 'gzip -t "$ARQUIVO"' in fonte
    assert 'gunzip -c "$ARQUIVO"' in fonte
    assert "ON_ERROR_STOP=1" in fonte
