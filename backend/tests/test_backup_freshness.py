import hashlib
import json
import os
import subprocess
import time
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "ops" / "check-backup-freshness.sh"


def _backup(tmp_path: Path, content: bytes = b"backup-valido") -> Path:
    backup = tmp_path / "corvia-teste-20260803T000000Z.dump"
    backup.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    backup.with_name(f"{backup.name}.sha256").write_text(
        f"{digest}  {backup.name}\n", encoding="utf-8"
    )
    return backup


def _run(tmp_path: Path, max_age: int = 3600) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "BACKUP_DIR": str(tmp_path),
        "MAX_BACKUP_AGE_SECONDS": str(max_age),
    }
    return subprocess.run(
        ["bash", str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_backup_recente_com_checksum_valido_e_aprovado(tmp_path):
    _backup(tmp_path)
    result = _run(tmp_path)

    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "ok"


def test_backup_antigo_e_sinalizado_com_saida_nao_zero(tmp_path):
    backup = _backup(tmp_path)
    old = time.time() - 7200
    os.utime(backup, (old, old))

    result = _run(tmp_path, max_age=3600)

    assert result.returncode == 2
    assert json.loads(result.stderr)["status"] == "stale"


def test_backup_corrompido_falha_na_validacao_de_checksum(tmp_path):
    backup = _backup(tmp_path)
    backup.write_bytes(b"conteudo-alterado-depois-do-checksum")

    result = _run(tmp_path)

    assert result.returncode == 2
    assert json.loads(result.stderr)["reason"] == "checksum_failed"


def test_backup_name_prefix_e_configuravel_para_o_backup_real_de_producao(tmp_path):
    """Achado de auditoria (issue #52, fase de hardening): o backup real de
    produção (infra/backup/backup.sh, o que de fato roda no cron
    documentado em DEPLOY.md) grava como 'meucardio_<data>.dump', não
    'corvia-*' — sem BACKUP_NAME_PREFIX configurável, apontar este script
    para o diretório real de produção sempre acusaria backup ausente,
    mesmo com backups válidos sendo criados todo dia."""
    conteudo = b"backup-producao-real"
    backup = tmp_path / "meucardio_20260810T030000Z.dump"
    backup.write_bytes(conteudo)
    digest = hashlib.sha256(conteudo).hexdigest()
    backup.with_name(f"{backup.name}.sha256").write_text(
        f"{digest}  {backup.name}\n", encoding="utf-8"
    )

    env = {**os.environ, "BACKUP_DIR": str(tmp_path), "MAX_BACKUP_AGE_SECONDS": "3600",
           "BACKUP_NAME_PREFIX": "meucardio_"}
    result = subprocess.run(
        ["bash", str(SCRIPT)], check=False, capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "ok"
