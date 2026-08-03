from types import SimpleNamespace

import pytest

from app.core.runtime import validar_configuracao_de_execucao

CHAVE_FERNET_VALIDA = "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="


def _settings(**alteracoes):
    valores = {
        "jwt_secret": "a" * 64,
        "admin_password": "senha-administrativa-segura",
        "admin_email": "admin@corvia.med.br",
        "database_url": "postgresql+psycopg://corvia:senha-banco-segura@db:5432/corvia",
        "storage_encryption_key": CHAVE_FERNET_VALIDA,
    }
    valores.update(alteracoes)
    return SimpleNamespace(**valores)


def test_producao_recusa_defaults_inseguros(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    configuracao = _settings(
        jwt_secret="dev-only-change-me",
        admin_password="troque-esta-senha",
        admin_email="admin@meucardio.local",
        database_url="postgresql+psycopg://meucardio:meucardio@db:5432/meucardio",
        storage_encryption_key="",
    )

    with pytest.raises(RuntimeError) as exc:
        validar_configuracao_de_execucao(configuracao)

    mensagem = str(exc.value)
    assert "JWT_SECRET" in mensagem
    assert "ADMIN_PASSWORD" in mensagem
    assert "ADMIN_EMAIL" in mensagem
    assert "PostgreSQL" in mensagem
    assert "STORAGE_ENCRYPTION_KEY" in mensagem


def test_producao_aceita_configuracao_segura(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    validar_configuracao_de_execucao(_settings())


def test_desenvolvimento_mantem_defaults_locais(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    validar_configuracao_de_execucao(
        _settings(
            jwt_secret="dev-only-change-me",
            admin_password="troque-esta-senha",
            admin_email="admin@meucardio.local",
            database_url="postgresql+psycopg://meucardio:meucardio@db:5432/meucardio",
            storage_encryption_key="",
        )
    )
