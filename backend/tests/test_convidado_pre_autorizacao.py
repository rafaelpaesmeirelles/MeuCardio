"""Pré-autorização de convidado por e-mail.

O cadastro que encontra um convite permanece pendente. Somente a posse do
link enviado ao endereço convidado permite ativar a conta e consumir o convite.
"""
from datetime import datetime, timezone

import pytest

from app.models.audit import AuditLog
from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.services import emails


CADASTRO = "/api/auth/solicitar-acesso-com-recuperacao"


@pytest.fixture(autouse=True)
def _emails_locais(monkeypatch):
    enviados = []
    def enviar(_db, **dados):
        enviados.append(dados)
        return True
    monkeypatch.setattr(emails, "_enviar", enviar)
    return enviados


def _confirmar(client, db):
    token = db.query(PasswordResetToken).filter_by(alvo="convite").one()
    dados = {"token": token.token, "nova_senha": "senha-confirmada-123",
             "recovery_email": "canal-confirmado@externo.test"}
    resposta = client.post("/api/auth/redefinir-senha", json=dados)
    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    return dados


def _payload(**overrides):
    base = dict(
        full_name="Márcio Peixoto", birth_date="1978-05-10", cpf="390.533.447-05",
        profession="Médico", council_name="CRM", council_number="99999", council_state="SP",
        email="drmarciopeixoto@corvia.med.br",
        recovery_email="marcio.recuperacao@externo.test",
        password="senha-forte-123",
    )
    base.update(overrides)
    return base


def test_cadastro_convidado_so_e_aprovado_apos_confirmar_posse_do_email(client, db, _emails_locais):
    db.add(ConvidadoPreAutorizado(
        email="drmarciopeixoto@corvia.med.br", observacao="Convidado previamente autorizado.",
    ))
    db.commit()

    resp = client.post(CADASTRO, json=_payload())
    assert resp.status_code == 201, resp.text
    assert resp.json().get("acesso_imediato") is False

    user = db.query(User).filter(User.email == "drmarciopeixoto@corvia.med.br").first()
    assert user is not None
    assert (user.convidado, user.status, user.is_active, user.role) == (False, "pendente", False, "leitor")
    login = client.post("/api/auth/login", data={"username": user.email, "password": "senha-forte-123"})
    assert login.status_code == 403, login.text
    assert len(_emails_locais) == 1
    assert _emails_locais[0]["tipo"] == "confirmar_convite"
    assert _emails_locais[0]["destinatario"] == user.email

    _confirmar(client, db)
    assert user.convidado is True
    assert user.status == "aprovado"
    assert user.is_active is True
    assert user.role == "medico"

    login = client.post("/api/auth/login", data={"username": user.email, "password": "senha-confirmada-123"})
    assert login.status_code == 200, login.text


def test_pre_autorizacao_e_consumida_uma_unica_vez(client, db):
    db.add(ConvidadoPreAutorizado(email="drmarciopeixoto@corvia.med.br"))
    db.commit()

    resp = client.post(CADASTRO, json=_payload())
    assert resp.status_code == 201

    pre_auth = db.query(ConvidadoPreAutorizado).filter(
        ConvidadoPreAutorizado.email == "drmarciopeixoto@corvia.med.br"
    ).first()
    assert pre_auth.usado_em is None and pre_auth.usado_por_user_id is None
    dados = _confirmar(client, db)
    assert pre_auth.usado_em is not None
    assert pre_auth.usado_por_user_id is not None
    usado_em = pre_auth.usado_em
    repetida = client.post("/api/auth/redefinir-senha", json=dados)
    assert repetida.status_code == 400, repetida.text
    db.refresh(pre_auth)
    assert pre_auth.usado_em == usado_em


def test_audit_log_registrado_somente_apos_confirmacao_do_convite(client, db):
    db.add(ConvidadoPreAutorizado(email="drmarciopeixoto@corvia.med.br"))
    db.commit()

    client.post(CADASTRO, json=_payload())

    assert db.query(AuditLog).filter(AuditLog.action.in_(
        ["convidado_via_pre_autorizacao", "convidado_email_confirmado"])).count() == 0
    _confirmar(client, db)
    log = db.query(AuditLog).filter(AuditLog.action == "convidado_email_confirmado").one()
    assert log is not None
    convite = db.query(ConvidadoPreAutorizado).one()
    assert log.detail == {"pre_autorizacao_id": convite.id, "incluir_corvia_mail": True}
    assert log.user_id == convite.usado_por_user_id


def test_cadastro_sem_pre_autorizacao_segue_fluxo_normal_pendente(client, db):
    resp = client.post(CADASTRO, json=_payload(
        email="outro.medico@teste.local",
        recovery_email="outro.medico.recuperacao@externo.test",
    ))
    assert resp.status_code == 201, resp.text
    assert "acesso_imediato" not in resp.json()

    user = db.query(User).filter(User.email == "outro.medico@teste.local").first()
    assert user is not None
    assert user.convidado is False
    assert user.status == "pendente"
    assert user.is_active is False
    assert user.role == "leitor"


def test_pre_autorizacao_ja_usada_nao_se_aplica_a_novo_cadastro_do_mesmo_email(client, db):
    pre_auth = ConvidadoPreAutorizado(
        email="ja-usado@corvia.med.br",
        usado_em=datetime.now(timezone.utc),
    )
    db.add(pre_auth)
    db.commit()

    resp = client.post(CADASTRO, json=_payload(
        email="ja-usado@corvia.med.br", cpf="529.982.247-25",
        recovery_email="ja-usado.recuperacao@externo.test",
    ))
    assert resp.status_code == 201
    user = db.query(User).filter(User.email == "ja-usado@corvia.med.br").first()
    assert user.convidado is False
    assert user.status == "pendente"
