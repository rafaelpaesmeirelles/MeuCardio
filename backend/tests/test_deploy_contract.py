"""Gates operacionais do deploy de produção e do backup pré-deploy."""

from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOY = REPO_ROOT / "deploy.sh"
BACKUP = REPO_ROOT / "infra/backup/backup.sh"
COMPOSE = REPO_ROOT / "docker-compose.prod.yml"
HEALTH = REPO_ROOT / "backend/app/api/health.py"


def _fonte(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def test_scripts_operacionais_possuem_sintaxe_bash_valida():
    resultado = subprocess.run(
        ["bash", "-n", str(DEPLOY), str(BACKUP)],
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


def test_deploy_nao_volta_ao_importador_parcial():
    fonte = _fonte(DEPLOY)

    assert "app.services.importer" not in fonte
    assert "--allow-partial" not in fonte
    assert "as 11 coleções" in fonte


def test_deploy_faz_backup_e_exige_https_publico():
    fonte = _fonte(DEPLOY)

    assert 'PROJETO="$PWD" ./infra/backup/backup.sh' in fonte
    assert 'https://${DOMAIN}/api/ready' in fonte
    assert "PUBLICO_PRONTO=0" in fonte
    assert 'if [[ "$PUBLICO_PRONTO" != "1" ]]' in fonte
    assert "--build --remove-orphans" in fonte
    assert "git rev-parse --verify HEAD" in fonte


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


def test_backup_e_portavel_atomico_e_verificado():
    fonte = _fonte(BACKUP)

    assert 'PROJETO="${PROJETO:-' in fonte
    assert "/opt/meucardio" not in fonte
    assert 'TEMPORARIO="${ARQUIVO}.tmp"' in fonte
    assert 'trap \'rm -f "$TEMPORARIO"\' EXIT' in fonte
    assert 'gzip -t "$TEMPORARIO"' in fonte
    assert 'sha256sum "$ARQUIVO"' in fonte
    assert "--no-owner --no-privileges" in fonte
