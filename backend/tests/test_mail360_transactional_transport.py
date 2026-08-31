from types import SimpleNamespace

import pytest

from app.core.runtime import validar_configuracao_de_execucao
from app.models.email_log import EmailLog
from app.models.user import User
from app.services import emails
from app.services.mail360 import Mail360Error


CHAVE_FERNET_VALIDA = "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="


def _runtime_settings(**alteracoes):
    valores = {
        "jwt_secret": "a" * 64,
        "admin_password": "senha-administrativa-segura",
        "admin_email": "admin@corvia.med.br",
        "database_url": "postgresql+psycopg://corvia:senha-banco-segura@db:5432/corvia",
        "storage_encryption_key": CHAVE_FERNET_VALIDA,
        "email_transacional_provider": "mail360",
        "mail360_transacional_configurado": True,
        "smtp_configurado": False,
        "smtp_host": "",
        "smtp_user": "",
        "smtp_from": "CorVIA <contato@corvia.med.br>",
    }
    valores.update(alteracoes)
    return SimpleNamespace(**valores)


def _usar_mail360(monkeypatch):
    monkeypatch.setattr(emails.settings, "email_transacional_provider", "mail360")
    monkeypatch.setattr(emails.settings, "mail360_transactional_account_key", "account-key-transacional-teste")
    monkeypatch.setattr(emails.settings, "smtp_host", "")
    monkeypatch.setattr(emails.settings, "smtp_user", "")
    monkeypatch.setattr(emails.settings, "smtp_password", "")
    monkeypatch.setattr(emails.settings, "smtp_from", "CorVIA <contato@corvia.med.br>")


def _criar_pendente(db, email: str) -> User:
    user = User(
        email=email,
        full_name="Dra. Teste Mail360",
        password_hash="hash-fake",
        role="leitor",
        status="pendente",
        is_active=False,
        council_name="CRM",
        council_number="123",
        council_state="SP",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_runtime_aceita_mail360_transacional_sem_smtp(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    validar_configuracao_de_execucao(_runtime_settings())


def test_runtime_recusa_mail360_transacional_incompleto(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    with pytest.raises(RuntimeError) as exc:
        validar_configuracao_de_execucao(
            _runtime_settings(mail360_transacional_configurado=False)
        )
    mensagem = str(exc.value)
    assert "MAIL360_CLIENT_ID" in mensagem
    assert "MAIL360_TRANSACTIONAL_ACCOUNT_KEY" in mensagem


def test_email_transacional_usa_conta_native_mail360(db, monkeypatch):
    _usar_mail360(monkeypatch)
    enviados = []

    def _enviar(account_key, remetente, para, assunto, html, **kwargs):
        enviados.append((account_key, remetente, para, assunto, html, kwargs))
        return {"messageId": "teste"}

    monkeypatch.setattr(emails, "enviar_mensagem_mail360", _enviar)
    user = _criar_pendente(db, "mail360-ok@teste.local")

    assert emails.enviar_solicitacao_recebida(user.id) is True
    assert len(enviados) == 1
    account_key, remetente, para, assunto, html, kwargs = enviados[0]
    assert account_key == "account-key-transacional-teste"
    assert remetente == "contato@corvia.med.br"
    assert para == user.email
    assert assunto == "CorVIA — solicitação de acesso recebida"
    # PNG canônico é deliberado em e-mail: tem suporte mais consistente do
    # que SVG nos clientes Outlook/Gmail sem alterar a identidade CorVIA.
    assert "https://corvia.med.br/corvia-logo-canonical.png" in html
    assert "cid:corvia-logo" not in html
    assert kwargs["mail_format"] == "html"

    registro = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user.id, EmailLog.tipo == "solicitacao_recebida")
        .one()
    )
    assert registro.sucesso is True
    assert registro.erro is None


def test_falha_mail360_nao_vira_falso_sucesso(db, monkeypatch):
    _usar_mail360(monkeypatch)

    def _falhar(*args, **kwargs):
        raise Mail360Error("falha controlada do provedor")

    monkeypatch.setattr(emails, "enviar_mensagem_mail360", _falhar)
    user = _criar_pendente(db, "mail360-fail@teste.local")

    assert emails.enviar_solicitacao_recebida(user.id) is False
    registro = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user.id, EmailLog.tipo == "solicitacao_recebida")
        .one()
    )
    assert registro.sucesso is False
    assert registro.erro == "falha controlada do provedor"
