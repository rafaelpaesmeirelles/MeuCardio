"""Pré-autorização de convidado por e-mail (08/08/2026, pedido do Rafael).

Um admin cadastra o e-mail em `ConvidadoPreAutorizado` ANTES da pessoa se
registrar. Quando esse e-mail passa por `POST /auth/solicitar-acesso`, o
`User` novo já nasce aprovado e marcado `convidado`, sem precisar de nenhuma
ação manual depois (nem aprovar a solicitação, nem marcar convidado no
painel Admin).
"""
from datetime import datetime, timezone

from app.models.audit import AuditLog
from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado
from app.models.user import User


def _payload(**overrides):
    base = dict(
        full_name="Márcio Peixoto", birth_date="1978-05-10", cpf="390.533.447-05",
        profession="Médico", council_name="CRM", council_number="99999", council_state="SP",
        email="drmarciopeixoto@corvia.med.br", password="senha-forte-123",
    )
    base.update(overrides)
    return base


def test_cadastro_com_email_pre_autorizado_nasce_aprovado_e_convidado(client, db):
    db.add(ConvidadoPreAutorizado(
        email="drmarciopeixoto@corvia.med.br", observacao="Amigo do Rafael, vai trabalhar com a Corvia.",
    ))
    db.commit()

    resp = client.post("/api/auth/solicitar-acesso", json=_payload())
    assert resp.status_code == 201, resp.text
    corpo = resp.json()
    assert corpo.get("acesso_imediato") is True

    user = db.query(User).filter(User.email == "drmarciopeixoto@corvia.med.br").first()
    assert user is not None
    assert user.convidado is True
    assert user.status == "aprovado"
    assert user.is_active is True
    assert user.role == "medico"

    # Login já funciona na hora, sem esperar aprovação de admin.
    login = client.post("/api/auth/login", data={"username": user.email, "password": "senha-forte-123"})
    assert login.status_code == 200, login.text


def test_pre_autorizacao_e_consumida_uma_unica_vez(client, db):
    db.add(ConvidadoPreAutorizado(email="drmarciopeixoto@corvia.med.br"))
    db.commit()

    resp = client.post("/api/auth/solicitar-acesso", json=_payload())
    assert resp.status_code == 201

    pre_auth = db.query(ConvidadoPreAutorizado).filter(
        ConvidadoPreAutorizado.email == "drmarciopeixoto@corvia.med.br"
    ).first()
    assert pre_auth.usado_em is not None
    assert pre_auth.usado_por_user_id is not None


def test_audit_log_registrado_na_aprovacao_automatica(client, db):
    db.add(ConvidadoPreAutorizado(email="drmarciopeixoto@corvia.med.br"))
    db.commit()

    client.post("/api/auth/solicitar-acesso", json=_payload())

    log = db.query(AuditLog).filter(AuditLog.action == "convidado_via_pre_autorizacao").first()
    assert log is not None
    assert log.detail["email"] == "drmarciopeixoto@corvia.med.br"


def test_cadastro_sem_pre_autorizacao_segue_fluxo_normal_pendente(client, db):
    """Sem pré-autorização — nenhuma mudança de comportamento."""
    resp = client.post("/api/auth/solicitar-acesso", json=_payload(email="outro.medico@teste.local"))
    assert resp.status_code == 201, resp.text
    corpo = resp.json()
    assert "acesso_imediato" not in corpo

    user = db.query(User).filter(User.email == "outro.medico@teste.local").first()
    assert user is not None
    assert user.convidado is False
    assert user.status == "pendente"
    assert user.is_active is False
    assert user.role == "leitor"


def test_pre_autorizacao_ja_usada_nao_se_aplica_a_novo_cadastro_do_mesmo_email(client, db):
    """Depois de consumida, mesmo que alguém apague a conta (não suportado
    aqui, mas simulando a regra), a pré-autorização usada não volta a
    valer — ela já está marcada `usado_em`, e a query em `solicitar_acesso`
    filtra `usado_em IS NULL`."""
    pre_auth = ConvidadoPreAutorizado(
        email="ja-usado@corvia.med.br",
        usado_em=datetime.now(timezone.utc),
    )
    db.add(pre_auth)
    db.commit()

    resp = client.post("/api/auth/solicitar-acesso", json=_payload(
        email="ja-usado@corvia.med.br", cpf="529.982.247-25",
    ))
    assert resp.status_code == 201
    user = db.query(User).filter(User.email == "ja-usado@corvia.med.br").first()
    assert user.convidado is False
    assert user.status == "pendente"
