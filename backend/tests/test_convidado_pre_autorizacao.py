"""Pré-autorização de convidado por e-mail.

Um admin cadastra o e-mail de login ANTES da pessoa se registrar. Quando o
cadastro canônico, já com segundo e-mail externo, casa com essa linha, o User
nasce aprovado e convidado sem revisão manual posterior.
"""
from datetime import datetime, timezone

from app.models.audit import AuditLog
from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado
from app.models.user import User


CADASTRO = "/api/auth/solicitar-acesso-com-recuperacao"


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


def test_cadastro_com_email_pre_autorizado_nasce_aprovado_e_convidado(client, db):
    db.add(ConvidadoPreAutorizado(
        email="drmarciopeixoto@corvia.med.br", observacao="Convidado previamente autorizado.",
    ))
    db.commit()

    resp = client.post(CADASTRO, json=_payload())
    assert resp.status_code == 201, resp.text
    assert resp.json().get("acesso_imediato") is True

    user = db.query(User).filter(User.email == "drmarciopeixoto@corvia.med.br").first()
    assert user is not None
    assert user.convidado is True
    assert user.status == "aprovado"
    assert user.is_active is True
    assert user.role == "medico"

    login = client.post("/api/auth/login", data={"username": user.email, "password": "senha-forte-123"})
    assert login.status_code == 200, login.text


def test_pre_autorizacao_e_consumida_uma_unica_vez(client, db):
    db.add(ConvidadoPreAutorizado(email="drmarciopeixoto@corvia.med.br"))
    db.commit()

    resp = client.post(CADASTRO, json=_payload())
    assert resp.status_code == 201

    pre_auth = db.query(ConvidadoPreAutorizado).filter(
        ConvidadoPreAutorizado.email == "drmarciopeixoto@corvia.med.br"
    ).first()
    assert pre_auth.usado_em is not None
    assert pre_auth.usado_por_user_id is not None


def test_audit_log_registrado_na_aprovacao_automatica(client, db):
    db.add(ConvidadoPreAutorizado(email="drmarciopeixoto@corvia.med.br"))
    db.commit()

    client.post(CADASTRO, json=_payload())

    log = db.query(AuditLog).filter(AuditLog.action == "convidado_via_pre_autorizacao").first()
    assert log is not None
    assert log.detail["email"] == "drmarciopeixoto@corvia.med.br"


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
