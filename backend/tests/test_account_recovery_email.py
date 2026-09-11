"""Regressões do segundo canal de recuperação de acesso (14/08/2026)."""

import pytest

from app.core.config import settings
from app.models.account_recovery import AccountRecoveryEmail
from app.services import account_recovery


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_recovery_email_precisa_ser_diferente_do_login(criar_usuario, db):
    user, _ = criar_usuario(email="medico@corvia.med.br")
    with pytest.raises(ValueError, match="diferente"):
        account_recovery.definir_email_recuperacao(db, user, "medico@corvia.med.br")


def test_recovery_email_e_unico_e_nao_pode_ser_login_de_outra_conta(criar_usuario, db):
    user_a, _ = criar_usuario(email="a@corvia.med.br")
    user_b, _ = criar_usuario(email="b@corvia.med.br")

    account_recovery.definir_email_recuperacao(db, user_a, "externo.a@example.com")
    db.commit()

    with pytest.raises(ValueError, match="outra conta"):
        account_recovery.definir_email_recuperacao(db, user_b, "externo.a@example.com")
    with pytest.raises(ValueError, match="outra conta"):
        account_recovery.definir_email_recuperacao(db, user_b, "a@corvia.med.br")


def test_esqueci_senha_aceita_segundo_email_sem_transforma_lo_em_login(
    client, criar_usuario, db, monkeypatch
):
    user, _ = criar_usuario(email="interno@corvia.med.br")
    account_recovery.definir_email_recuperacao(db, user, "externo@example.com")
    db.commit()

    chamados: list[int] = []
    monkeypatch.setattr(account_recovery, "enviar_recuperacao_senha", lambda user_id: chamados.append(user_id) or True)

    resposta = client.post("/api/auth/esqueci-senha", json={"email": "externo@example.com"})
    assert resposta.status_code == 202
    assert chamados == [user.id]

    # O segundo endereço é só recuperação; nunca vira credencial normal de login.
    login = client.post(
        "/api/auth/login",
        data={"username": "externo@example.com", "password": "senha-teste-123"},
    )
    assert login.status_code == 401


def test_admin_consegue_definir_recuperacao_para_usuario_que_nao_consegue_entrar(
    client, criar_usuario, db, monkeypatch
):
    alvo, _ = criar_usuario(email="bloqueado@corvia.med.br")
    _, token_admin = criar_usuario(email="admin-recovery@teste.local", role="admin")
    confirmados: list[int] = []
    monkeypatch.setattr(
        account_recovery,
        "enviar_confirmacao_canal_recuperacao",
        lambda user_id: confirmados.append(user_id) or True,
    )

    resposta = client.put(
        f"/api/auth/admin/users/{alvo.id}/email-recuperacao",
        json={"recovery_email": "bloqueado.externo@example.com"},
        headers=_headers(token_admin),
    )
    assert resposta.status_code == 200, resposta.text
    registro = db.get(AccountRecoveryEmail, alvo.id)
    assert registro is not None
    assert registro.email == "bloqueado.externo@example.com"
    assert confirmados == [alvo.id]


def test_titular_precisa_confirmar_senha_atual_para_trocar_canal(client, criar_usuario):
    _, token = criar_usuario(email="titular@corvia.med.br")
    resposta = client.put(
        "/api/auth/email-recuperacao",
        json={"recovery_email": "titular.externo@example.com", "senha_atual": "senha-errada"},
        headers=_headers(token),
    )
    assert resposta.status_code == 400


def test_remetente_transacional_padrao_e_contato_corvia():
    assert "contato@corvia.med.br" in settings.smtp_from.lower()


def test_admin_invitation_rolls_back_account_when_recovery_channel_conflicts(
    client, criar_usuario, db, monkeypatch,
):
    from app.models.audit import AuditLog
    from app.models.user import User

    _, token_admin = criar_usuario(email="admin-atomic@example.com", role="admin")
    email = "novo-atomic@example.com"
    dispatched = []

    def conflito(_db, _user, _email):
        raise ValueError("Este e-mail já está vinculado a outra conta CorVIA.")

    monkeypatch.setattr(account_recovery, "definir_email_recuperacao", conflito)
    monkeypatch.setattr(account_recovery, "enviar_primeiro_acesso", lambda uid: dispatched.append(uid))
    before = db.query(AuditLog).filter(AuditLog.action == "criar_usuario").count()
    response = client.post(
        "/api/auth/admin/criar-usuario-com-recuperacao",
        json={"email": email, "full_name": "Conta fictícia", "password": "senha-teste-123", "recovery_email": "canal-atomic@example.com"},
        headers=_headers(token_admin),
    )
    assert response.status_code == 409, response.text
    db.expire_all()
    assert db.query(User).filter(User.email == email).first() is None
    assert db.query(AuditLog).filter(AuditLog.action == "criar_usuario").count() == before
    assert dispatched == []


def test_admin_invitation_persists_account_and_channel_before_dispatch(
    client, criar_usuario, db, monkeypatch,
):
    from app.models.user import User

    _, token_admin = criar_usuario(email="admin-atomic-ok@example.com", role="admin")
    dispatched = []

    def conferir_convite(user_id):
        db.expire_all()
        assert db.get(User, user_id) is not None
        assert db.get(AccountRecoveryEmail, user_id).email == "canal-atomic-ok@example.com"
        dispatched.append(user_id)
        return True

    monkeypatch.setattr(account_recovery, "enviar_primeiro_acesso", conferir_convite)
    response = client.post(
        "/api/auth/admin/criar-usuario-com-recuperacao",
        json={"email": "novo-atomic-ok@example.com", "full_name": "Conta fictícia", "password": "senha-teste-123", "recovery_email": "canal-atomic-ok@example.com"},
        headers=_headers(token_admin),
    )
    assert response.status_code == 201, response.text
    assert response.json()["recovery_email"] == "canal-atomic-ok@example.com"
    assert dispatched == [response.json()["id"]]


@pytest.mark.parametrize("route", ["/api/admin/users", "/api/auth/admin/criar-usuario-com-recuperacao"])
def test_admin_new_login_cannot_occupy_another_recovery_channel(
    route, client, criar_usuario, db, monkeypatch,
):
    from app.models.user import User

    owner, _ = criar_usuario(email="channel-owner@example.com")
    _, token_admin = criar_usuario(email="admin-channel-owner@example.com", role="admin")
    account_recovery.definir_email_recuperacao(db, owner, "occupied-channel@example.com")
    db.commit()
    dispatched = []
    monkeypatch.setattr(account_recovery, "enviar_primeiro_acesso", lambda uid: dispatched.append(uid))
    payload = {"email": "occupied-channel@example.com", "full_name": "Conta fictícia", "password": "senha-teste-123"}
    if route.endswith("criar-usuario-com-recuperacao"):
        payload["recovery_email"] = "new-independent-channel@example.com"
    response = client.post(route, json=payload, headers=_headers(token_admin))
    assert response.status_code == 409, response.text
    db.expire_all()
    assert db.query(User).filter(User.email == payload["email"]).first() is None
    assert db.get(AccountRecoveryEmail, owner.id).email == payload["email"]
    assert dispatched == []


def test_admin_cannot_create_or_convert_administrative_demo_account(
    client, criar_usuario, db,
):
    from app.models.user import User

    admin, token_admin = criar_usuario(email="admin-no-demo@example.com", role="admin")
    response = client.post(
        "/api/admin/users",
        json={"email": "forbidden-demo@example.com", "full_name": "Conta fictícia", "password": "senha-teste-123", "role": "admin", "tipo_acesso": "investidor"},
        headers=_headers(token_admin),
    )
    assert response.status_code == 422, response.text
    assert db.query(User).filter(User.email == "forbidden-demo@example.com").first() is None
    response = client.patch(
        f"/api/admin/users/{admin.id}/investidor?investidor=true",
        headers=_headers(token_admin),
    )
    assert response.status_code == 409, response.text
    db.expire_all()
    assert db.get(User, admin.id).investidor is False
