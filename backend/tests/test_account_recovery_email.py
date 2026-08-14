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
