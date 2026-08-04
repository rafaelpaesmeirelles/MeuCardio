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
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr


def test_deploy_exige_readiness_antes_de_migrar_e_reconciliar():
    fonte = _fonte(DEPLOY)

    assert "BACKEND_PRONTO=0" in fonte
    assert "http://localhost:8000/api/ready" in fonte
    assert 'if [[ "$BACKEND_PRONTO" != "1" ]]' in fonte
    assert "mostrar_diagnostico" in fonte
    assert "python -m app.commands.migrate" in fonte
    assert "python -m app.commands.reconcile_content --publish-reviewed" in fonte
    assert fonte.index("BACKEND_PRONTO=0") < fonte.index("python -m app.commands.migrate")
    assert fonte.index("python -m app.commands.migrate") < fonte.index(
        "python -m app.commands.reconcile_content --publish-reviewed"
    )


def test_deploy_diagnostica_falhas_inesperadas_apos_subir_servicos():
    fonte = _fonte(DEPLOY)
    linhas = [linha.strip() for linha in fonte.splitlines()]
    linha_up = linhas.index('"${COMPOSE[@]}" up -d --build --remove-orphans')
    inicios = [i for i, linha in enumerate(linhas) if linha == "SERVICOS_INICIADOS=1"]

    assert "SERVICOS_INICIADOS=0" in fonte
    assert "diagnosticar_erro()" in fonte
    assert "trap diagnosticar_erro ERR" in fonte
    assert "trap - ERR" in fonte
    assert 'if [[ "$SERVICOS_INICIADOS" == "1" ]]' in fonte
    assert any(inicio < linha_up for inicio in inicios)
    assert fonte.index("trap diagnosticar_erro ERR") < fonte.index(
        "python -m app.commands.reconcile_content --publish-reviewed"
    )


def test_deploy_preserva_banco_persistente_mesmo_parado():
    fonte = _fonte(DEPLOY)

    assert "banco_persistente_existe()" in fonte
    assert 'ps -a -q db' in fonte
    assert "label=com.docker.compose.project=" in fonte
    assert "label=com.docker.compose.volume=pgdata" in fonte
    assert '"${COMPOSE[@]}" up -d --no-deps db' in fonte
    assert "aguardar_postgres" in fonte
    assert 'PROJETO="$PWD" bash ./infra/backup/backup.sh' in fonte
    assert "--status running" not in "\n".join(_linhas_ativas(DEPLOY))


def test_deploy_nao_volta_ao_importador_parcial():
    fonte = _fonte(DEPLOY)

    assert "app.services.importer" not in fonte
    assert "--allow-partial" not in fonte
    assert "as 11 coleções" in fonte
    assert "algum arquivo for ignorado" in fonte


def test_deploy_faz_backup_e_exige_https_publico():
    fonte = _fonte(DEPLOY)

    assert 'https://${DOMAIN}/api/ready' in fonte
    assert "PUBLICO_PRONTO=0" in fonte
    assert 'if [[ "$PUBLICO_PRONTO" != "1" ]]' in fonte
    assert "--build --remove-orphans" in fonte
    assert "git rev-parse --verify HEAD" in fonte


def test_deploy_exige_checkout_limpo_e_ferramentas_do_host():
    fonte = _fonte(DEPLOY)

    assert "git status --porcelain --untracked-files=normal" in fonte
    assert "ALTERACOES_LOCAIS" in fonte
    assert "checkout contém alterações não versionadas" in fonte
    assert "for comando in git curl getent sha256sum" in fonte


def test_contextos_docker_excluem_artefatos_ignorados_locais():
    frontend = set(_linhas_ativas(FRONTEND_DOCKERIGNORE))
    backend = set(_linhas_ativas(BACKEND_DOCKERIGNORE))

    assert {"node_modules/", "dist/", ".env", ".env.*"}.issubset(frontend)
    assert {"__pycache__/", ".pytest_cache/", ".venv/", "venv/", ".env", ".env.*"}.issubset(backend)


def test_deploy_injeta_e_confirma_commit_publico():
    deploy = _fonte(DEPLOY)
    compose = _fonte(COMPOSE)
    health = _fonte(HEALTH)

    assert 'export DEPLOY_COMMIT="$COMMIT_ATUAL"' in deploy
    assert 'https://${DOMAIN}/api/version' in deploy
    assert "VERSAO_PUBLICA" in deploy
    assert "COMMIT_ATUAL" in deploy
    assert "DEPLOY_COMMIT: ${DEPLOY_COMMIT:-unknown}" in compose
    assert '@router.get("/version")' in health
    assert 'os.getenv("DEPLOY_COMMIT", "unknown")' in health


def test_backup_e_portavel_atomico_restauravel_e_verificado():
    fonte = _fonte(BACKUP)
    linhas_ativas = "\n".join(_linhas_ativas(BACKUP))

    assert 'PROJETO="${PROJETO:-' in fonte
    assert "/opt/meucardio" not in linhas_ativas
    assert 'TEMPORARIO="${ARQUIVO}.tmp"' in fonte
    assert 'trap \'rm -f "$TEMPORARIO"\' EXIT' in fonte
    assert "--format=custom" in fonte
    assert "--compress=9" in fonte
    assert "pg_restore --list" in fonte
    assert 'sha256sum "$(basename "$ARQUIVO")"' in fonte
    assert "--no-owner" in fonte
    assert "--no-privileges" in fonte
    assert "meucardio_*.dump" in fonte


def test_restaurador_valida_antes_de_apagar_e_usa_pg_restore():
    fonte = _fonte(RESTORE)
    linhas_ativas = "\n".join(_linhas_ativas(RESTORE))
    indice_hash = fonte.index('hash_calculado="$(sha256sum "$arquivo"')
    indice_catalogo = fonte.index("pg_restore --list")
    indice_drop = fonte.index("dropdb")

    assert 'PROJETO="${PROJETO:-' in fonte
    assert "/opt/meucardio" not in linhas_ativas
    assert indice_hash < indice_drop
    assert indice_catalogo < indice_drop
    assert "--if-exists --force" in fonte
    assert "--exit-on-error" in fonte
    assert "--no-owner" in fonte
    assert "--no-privileges" in fonte
    assert "Checksum obrigatório não encontrado" in fonte
    assert "Checksum não corresponde ao dump selecionado" in fonte
    assert 'nome_registrado" != "$(basename "$arquivo")"' in fonte
    assert '[[ "$banco_confirmado" == "$POSTGRES_DB" ]]' in fonte
    assert "O backend permanece parado" in fonte
    assert "BACKEND_PRONTO=0" in fonte


def test_restaurador_so_apaga_depois_de_parar_backend_existente():
    fonte = _fonte(RESTORE)
    indice_container = fonte.index('BACKEND_CONTAINER="$(')
    indice_stop = fonte.index('"${COMPOSE[@]}" stop backend')
    indice_drop = fonte.index("dropdb")

    assert indice_container < indice_stop < indice_drop
    assert 'ps -a -q backend' in fonte
    assert 'stop backend >/dev/null 2>&1 || true' not in fonte
    assert "Uma falha aqui é bloqueante" in fonte


def test_restaurador_mantem_compatibilidade_com_backup_sql_gzip_legado():
    fonte = _fonte(RESTORE)

    assert "*.sql.gz" in fonte
    assert 'FORMATO="sql-gzip-legado"' in fonte
    assert 'gzip -t "$ARQUIVO"' in fonte
    assert 'gunzip -c "$ARQUIVO"' in fonte
    assert "ON_ERROR_STOP=1" in fonte
