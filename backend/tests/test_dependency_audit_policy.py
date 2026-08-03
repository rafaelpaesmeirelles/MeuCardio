from types import SimpleNamespace

from packaging.version import Version

from app.commands import audit_dependencies


class _Response:
    def __init__(self, version: str):
        self.version = version

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return ('{"info":{"version":"' + self.version + '"}}').encode()


def test_residual_exception_runs_audit_while_fix_is_unavailable(monkeypatch):
    monkeypatch.setattr(audit_dependencies, "latest_pypi_version", lambda: Version("49.0.0"))
    observed = {}

    def fake_run(command, check):
        observed["command"] = command
        observed["check"] = check
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(audit_dependencies.subprocess, "run", fake_run)

    assert audit_dependencies.main() == 0
    assert observed["check"] is False
    assert observed["command"][-2:] == ["--ignore-vuln", "CVE-2026-69247"]


def test_residual_exception_expires_when_fixed_release_exists(monkeypatch):
    monkeypatch.setattr(audit_dependencies, "latest_pypi_version", lambda: Version("50.0.0"))

    def forbidden_run(*args, **kwargs):
        raise AssertionError("pip-audit não deve executar com exceção expirada")

    monkeypatch.setattr(audit_dependencies.subprocess, "run", forbidden_run)

    assert audit_dependencies.main() == 1
