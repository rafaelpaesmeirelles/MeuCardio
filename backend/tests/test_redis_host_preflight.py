import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ops" / "check-redis-host.sh"


def executar(caminho: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["OVERCOMMIT_MEMORY_PATH"] = str(caminho)
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def resposta(resultado: subprocess.CompletedProcess[str]) -> dict[str, str]:
    assert resultado.stdout.strip(), resultado.stderr
    return json.loads(resultado.stdout)


def test_host_redis_pronto_quando_overcommit_esta_habilitado(tmp_path: Path):
    valor = tmp_path / "overcommit_memory"
    valor.write_text("1\n", encoding="utf-8")

    resultado = executar(valor)

    assert resultado.returncode == 0
    assert resposta(resultado) == {
        "status": "ok",
        "code": "REDIS_HOST_READY",
        "overcommit_memory": "1",
        "message": "Host apto para operações de background do Redis.",
    }


def test_host_redis_bloqueia_deploy_quando_overcommit_esta_desabilitado(tmp_path: Path):
    valor = tmp_path / "overcommit_memory"
    valor.write_text("0\n", encoding="utf-8")

    resultado = executar(valor)
    corpo = resposta(resultado)

    assert resultado.returncode == 2
    assert corpo["status"] == "blocked"
    assert corpo["code"] == "OVERCOMMIT_NOT_ENABLED"
    assert corpo["overcommit_memory"] == "0"
    assert "vm.overcommit_memory=1" in corpo["message"]


def test_host_redis_recusa_valor_invalido(tmp_path: Path):
    valor = tmp_path / "overcommit_memory"
    valor.write_text("invalido\n", encoding="utf-8")

    resultado = executar(valor)
    corpo = resposta(resultado)

    assert resultado.returncode == 3
    assert corpo["code"] == "OVERCOMMIT_INVALID"
    assert corpo["overcommit_memory"] == "invalido"


def test_host_redis_exige_execucao_no_host_linux(tmp_path: Path):
    resultado = executar(tmp_path / "ausente")
    corpo = resposta(resultado)

    assert resultado.returncode == 3
    assert corpo["code"] == "OVERCOMMIT_UNREADABLE"
    assert corpo["overcommit_memory"] == ""
