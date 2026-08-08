"""Tarefa #42 do backlog: e-mail de "solicitação de acesso recebida",
disparado por `POST /api/auth/solicitar-acesso` (backend/app/api/auth.py),
ANTES de qualquer aprovação de admin. Mesmo padrão dos outros 13 e-mails
transacionais de `app/services/emails.py`: Jinja2 (HTML + texto puro),
`EmailLog` para idempotência, envio via `BackgroundTasks` com sessão própria
do banco.
"""
import smtplib

from app.models.email_log import EmailLog
from app.models.user import User
from app.services import emails


def _payload(**overrides):
    base = dict(
        full_name="João da Silva", birth_date="1980-01-01", cpf="529.982.247-25",
        profession="Médico", council_name="CRM", council_number="123456",
        council_state="SP", email="joao@teste.local", password="senha-forte-123",
    )
    base.update(overrides)
    return base


class _SMTPFalso:
    """Mesmo dublê de `test_apple_mail.py`/`test_yahoo_mail.py`, adaptado
    para `emails.smtplib.SMTP` (que usa `with ... as servidor`, não a versão
    já em contexto das outras duas)."""

    def __init__(self, enviados: list, *, falhar: bool = False):
        self._enviados = enviados
        self._falhar = falhar

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, usuario, senha):
        pass

    def send_message(self, mensagem):
        if self._falhar:
            raise smtplib.SMTPServerDisconnected("falha simulada")
        self._enviados.append(mensagem)


def _configurar_smtp(monkeypatch, enviados: list, *, falhar: bool = False):
    monkeypatch.setattr(emails.settings, "smtp_host", "smtp.teste.local")
    monkeypatch.setattr(emails.settings, "smtp_user", "contato@corvia.med.br")
    monkeypatch.setattr(emails.settings, "smtp_password", "segredo-de-teste")
    monkeypatch.setattr(
        emails.smtplib, "SMTP",
        lambda host, port, timeout=None: _SMTPFalso(enviados, falhar=falhar),
    )


def test_solicitar_acesso_dispara_email_e_grava_log_sem_smtp(client, db):
    """Ambiente de teste não configura SMTP (conftest.py não define
    smtp_host/user/password) — o envio real não é tentado, mas o `EmailLog`
    é gravado do mesmo jeito, mesmo comportamento das outras 13 funções."""
    resposta = client.post("/api/auth/solicitar-acesso", json=_payload())
    assert resposta.status_code == 201, resposta.text

    user = db.query(User).filter(User.email == "joao@teste.local").first()
    assert user is not None
    assert user.status == "pendente"
    assert user.is_active is False

    log = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user.id, EmailLog.tipo == "solicitacao_recebida")
        .first()
    )
    assert log is not None
    assert log.destinatario == "joao@teste.local"
    assert log.sucesso is False
    assert log.erro == "SMTP não configurado"


def test_solicitar_acesso_dispara_email_com_sucesso_quando_smtp_configurado(client, db, monkeypatch):
    enviados: list = []
    _configurar_smtp(monkeypatch, enviados)

    resposta = client.post(
        "/api/auth/solicitar-acesso",
        json=_payload(full_name="Maria Oliveira", email="maria@teste.local"),
    )
    assert resposta.status_code == 201, resposta.text

    user = db.query(User).filter(User.email == "maria@teste.local").first()
    assert user is not None

    log = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user.id, EmailLog.tipo == "solicitacao_recebida")
        .first()
    )
    assert log is not None
    assert log.sucesso is True
    assert log.erro is None

    assert len(enviados) == 1
    mensagem = enviados[0]
    assert mensagem["To"] == "maria@teste.local"
    assert mensagem["Subject"] == "Corvia — solicitação de acesso recebida"

    corpo = mensagem.get_body(preferencelist=("plain",)).get_content()
    assert "Maria" in corpo
    assert "CRM" in corpo
    assert "123456" in corpo
    assert "SP" in corpo
    assert "administrador" in corpo.lower()

    corpo_html = mensagem.get_body(preferencelist=("html",)).get_content()
    assert "CRM" in corpo_html


def test_solicitacao_recebida_com_conselho_outro_mostra_texto_livre(client, monkeypatch, db):
    """Conselho "Outro" tem que aparecer com o texto livre digitado no
    cadastro na EXIBIÇÃO do e-mail (mesma regra de `council_display`,
    08/08/2026) — nunca o literal "OUTRO" que fica gravado no banco."""
    enviados: list = []
    _configurar_smtp(monkeypatch, enviados)

    resposta = client.post(
        "/api/auth/solicitar-acesso",
        json=dict(
            full_name="Ana Souza", birth_date="1985-05-05", cpf="345.987.621-28",
            profession="Farmacêutica", council_name="Outro", council_number="99",
            council_name_other="Ordem dos Farmacêuticos", council_state_other="Lisboa",
            email="ana@teste.local", password="senha-forte-123",
        ),
    )
    assert resposta.status_code == 201, resposta.text

    user = db.query(User).filter(User.email == "ana@teste.local").first()
    assert user.council_name == "OUTRO"  # gravado literal, decide o escopo de prescrição

    assert len(enviados) == 1
    corpo = enviados[0].get_body(preferencelist=("plain",)).get_content()
    assert "Ordem dos Farmacêuticos" in corpo
    assert "Lisboa" in corpo
    assert "OUTRO" not in corpo


def test_enviar_solicitacao_recebida_e_idempotente(db, monkeypatch):
    """Segunda chamada com a mesma `chave_idempotencia` não reenvia nem
    duplica o `EmailLog` — mesmo mecanismo das outras 13 funções."""
    enviados: list = []
    _configurar_smtp(monkeypatch, enviados)

    user = User(
        email="pedro@teste.local", full_name="Pedro Lima",
        password_hash="hash-fake", role="leitor", status="pendente", is_active=False,
        council_name="CRM", council_number="1", council_state="SP",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert emails.enviar_solicitacao_recebida(user.id) is True
    assert emails.enviar_solicitacao_recebida(user.id) is True
    assert len(enviados) == 1

    logs = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user.id, EmailLog.tipo == "solicitacao_recebida")
        .all()
    )
    assert len(logs) == 1
    assert logs[0].chave_idempotencia == f"solicitacao_recebida:{user.id}"


def test_enviar_solicitacao_recebida_usuario_inexistente_nao_quebra(db):
    assert emails.enviar_solicitacao_recebida(999999) is False


def test_enviar_solicitacao_recebida_falha_de_smtp_nao_propaga(db, monkeypatch):
    """O envio nunca deve bloquear/derrubar quem chamou, mesmo com o SMTP
    configurado e a tentativa falhando de verdade (não só "não configurado")."""
    enviados: list = []
    _configurar_smtp(monkeypatch, enviados, falhar=True)

    user = User(
        email="carla@teste.local", full_name="Carla Nunes",
        password_hash="hash-fake", role="leitor", status="pendente", is_active=False,
        council_name="CRM", council_number="2", council_state="RJ",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert emails.enviar_solicitacao_recebida(user.id) is False
    assert enviados == []

    log = (
        db.query(EmailLog)
        .filter(EmailLog.user_id == user.id, EmailLog.tipo == "solicitacao_recebida")
        .first()
    )
    assert log is not None
    assert log.sucesso is False
    assert log.erro is not None
