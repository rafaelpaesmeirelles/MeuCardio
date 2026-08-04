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
    assert 'if [[ "$BACKEND_PRONTO" != "1" ]]' in fonte
    assert "mostrar_diagnostico" in fonte
    assert fonte.index("BACKEND_PRONTO=0") < fonte.index("python -m app.commands.migrate")
    assert fonte.index("python -m app.commands.migrate") < fonte.index(
        "python -m app.commands.reconcile_content --publish-reviewed"
    )


def test_deploy_diagnostica_falhas_inesperadas_apos_subir_servicos():
    fonte = _fonte(DEPLOY)
    linhas = [linha.strip() for linha in fonte.splitlines()]
    linha_up = linhas.index('"${COMPOSE[@]}" up -d --build --remove-orphans')
    inicios = [i for i, linha in enumerate(linhas) if linha == "SERVICOS_INICIADOS=1"]
    assert "diagnosticar_erro()" in fonte
    assert "trap diagnosticar_erro ERR" in fonte
    assert 'if [[ "$SERVICOS_INICIADOS" == "1" ]]' in fonte
    assert any(inicio < linha_up for inicio in inicios)


def test_deploy_preserva_banco_persistente_mesmo_parado_e_falha_fechado():
    fonte = _fonte(DEPLOY)
    linhas_ativas = "\n".join(_linhas_ativas(DEPLOY))
    assert "BANCO_PERSISTENTE=0" in fonte
    assert "detectar_banco_persistente()" in fonte
    assert 'container_id="$("${COMPOSE[@]}" ps -a -q db)"' in fonte
    assert 'ps -a -q db 2>/dev/null || true' not in linhas_ativas
    assert "label=com.docker.compose.volume=pgdata" in fonte
    assert "detectar_banco_persistente\nif [[ \"$BANCO_PERSISTENTE\" == \"1\" ]]" in fonte
    assert '"${COMPOSE[@]}" up -d --no-deps db' in fonte
    assert 'PROJETO="$PWD" bash ./infra/backup/backup.sh' in fonte


def test_deploy_nao_volta_ao_importador_parcial():
    fonte = _fonte(DEPLOY)
    assert "app.services.importer" not in fonte
    assert "--allow-partial" not in fonte
    assert "python -m app.commands.reconcile_content --publish-reviewed" in fonte


def test_deploy_faz_backup_e_exige_https_publico():
    fonte = _fonte(DEPLOY)
    assert 'https://${DOMAIN}/api/ready' in fonte
    assert "PUBLICO_PRONTO=0" in fonte
    assert "--build --remove-orphans" in fonte
    assert "git rev-parse --verify HEAD" in fonte


def test_deploy_exige_checkout_limpo_e_ferramentas_do_host():
    fonte = _fonte(DEPLOY)
    assert "git status --porcelain --untracked-files=normal" in fonte
    assert "checkout contém alterações não versionadas" in fonte
    assert "for comando in git curl getent sha256sum" in fonte


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
    fonte = _fonte(RESTORE)
    indice_container = fonte.index('BACKEND_CONTAINER="$(')
    indice_stop = fonte.index('"${COMPOSE[@]}" stop backend')
    indice_drop = fonte.index("dropdb")
    assert indice_container < indice_stop < indice_drop
    assert 'ps -a -q backend 2>/dev/null || true' not in fonte
    assert 'stop backend >/dev/null 2>&1 || true' not in fonte


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
