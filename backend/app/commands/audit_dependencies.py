"""Audita dependências Python com uma exceção residual autoexpirável.

`cryptography==49.0.0` é a versão mais recente disponível durante esta revisão,
mas o feed do PyPI já anuncia CVE-2026-69247 com correção em 50.0.0. A exceção
é deliberadamente estreita: a auditoria continua bloqueando todos os demais
findings e passa a falhar assim que a versão de correção for publicada.
"""

from __future__ import annotations

import json
import subprocess
import sys
from urllib.request import Request, urlopen

from packaging.version import Version

PACKAGE = "cryptography"
ADVISORY = "CVE-2026-69247"
FIX_VERSION = Version("50.0.0")
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE}/json"


def latest_pypi_version() -> Version:
    request = Request(PYPI_URL, headers={"User-Agent": "MeuCardio dependency audit"})
    with urlopen(request, timeout=15) as response:  # noqa: S310 - host fixo e confiável
        payload = json.load(response)
    return Version(payload["info"]["version"])


def audit_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "pip_audit",
        "-r",
        "requirements.txt",
        "--progress-spinner=off",
        "--strict",
        "--ignore-vuln",
        ADVISORY,
    ]


def main() -> int:
    latest = latest_pypi_version()
    if latest >= FIX_VERSION:
        print(
            f"A exceção {ADVISORY} expirou: {PACKAGE} {latest} está disponível; "
            f"atualize requirements.txt para >= {FIX_VERSION}.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Exceção residual ativa: {ADVISORY}; versão pública mais recente de "
        f"{PACKAGE}: {latest}; correção anunciada: {FIX_VERSION}."
    )
    return subprocess.run(audit_command(), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
