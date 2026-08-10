"""Auditoria AUTH/SESSION (issue #52, subfase 1) — fluxo de "esqueci minha
senha" da conta principal (`app/api/password_reset.py`).

O que já tinha cobertura antes desta subfase: o EFEITO de uma redefinição
bem-sucedida sobre sessões existentes (`test_session_revocation.py`) e o gap
de revogação da sessão de e-mail (`test_email_session_password_change_revocation.py`).
O que faltava — e este arquivo cobre — é o fluxo do próprio token de reset:
proteção contra enumeração de usuário, expiração, uso único e o RBAC do
painel `/reset-pendentes`.
"""
from datetime import datetime, timedelta, timezone

from app.models.password_reset import PasswordResetToken


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_esqueci_senha_responde_identico_para_email_existente_e_inexistente(
    client, criar_usuario, db
):
    """Anti-enumeração (comentário da rota): a resposta não pode variar
    conforme o e-mail existir ou não — nem no status, nem no corpo."""
    criar_usuario(email="existe@teste.local")

    existente = client.post("/api/auth/esqueci-senha", json={"email": "existe@teste.local"})
    inexistente = client.post("/api/auth/esqueci-senha", json={"email": "nao.existe@teste.local"})

    assert existente.status_code == 202 == inexistente.status_code
    assert existente.json() == inexistente.json()

    # Nível de dado, não só de resposta HTTP: só o e-mail existente gera
    # PasswordResetToken de fato (o inexistente não tem user_id para atrelar).
    tokens = db.query(PasswordResetToken).all()
    assert len(tokens) == 1
    assert tokens[0].alvo == "conta"


def test_esqueci_senha_nao_gera_token_para_conta_inativa(client, criar_usuario, db):
    """`esqueci_senha` filtra `User.is_active.is_(True))` — conta desativada
    (ex.: banida por admin) não deve permitir gerar um novo link de reset."""
    user, _ = criar_usuario(email="inativa@teste.local")
    user.is_active = False
    db.commit()

    resp = client.post("/api/auth/esqueci-senha", json={"email": "inativa@teste.local"})
    assert resp.status_code == 202
    assert db.query(PasswordResetToken).count() == 0


def test_redefinir_senha_com_token_expirado_e_rejeitado(client, criar_usuario, db):
    user, _ = criar_usuario(email="expirado@teste.local")
    token = PasswordResetToken(
        user_id=user.id, alvo="conta",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    resp = client.post(
        "/api/auth/redefinir-senha",
        json={"token": token.token, "nova_senha": "senha-pos-expiracao-1"},
    )
    assert resp.status_code == 400

    login_com_senha_nova = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": "senha-pos-expiracao-1"},
    )
    assert login_com_senha_nova.status_code == 401


def test_redefinir_senha_e_de_uso_unico(client, criar_usuario, db):
    user, _ = criar_usuario(email="usounico@teste.local")
    token = PasswordResetToken(
        user_id=user.id, alvo="conta",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    primeira = client.post(
        "/api/auth/redefinir-senha",
        json={"token": token.token, "nova_senha": "senha-primeira-vez-1"},
    )
    assert primeira.status_code == 200, primeira.text

    # Replay do MESMO token, tentando trocar de novo — tem que ser rejeitado,
    # mesmo dentro da janela de validade original.
    segunda = client.post(
        "/api/auth/redefinir-senha",
        json={"token": token.token, "nova_senha": "senha-segunda-vez-2"},
    )
    assert segunda.status_code == 400, segunda.text

    ainda_com_a_primeira = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": "senha-primeira-vez-1"},
    )
    assert ainda_com_a_primeira.status_code == 200


def test_reset_pendentes_exige_admin(client, criar_usuario):
    """Painel `/api/auth/reset-pendentes` lista tokens de reset de TODOS os
    usuários — RBAC estrito é o que impede virar um vazamento de tokens
    válidos de terceiros para qualquer conta autenticada."""
    _, token_medico = criar_usuario(email="medico.comum@teste.local", role="medico")

    sem_auth = client.get("/api/auth/reset-pendentes")
    assert sem_auth.status_code == 401

    nao_admin = client.get("/api/auth/reset-pendentes", headers=_headers(token_medico))
    assert nao_admin.status_code == 403

    _, token_admin = criar_usuario(email="admin.reset@teste.local", role="admin")
    como_admin = client.get("/api/auth/reset-pendentes", headers=_headers(token_admin))
    assert como_admin.status_code == 200
