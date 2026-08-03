from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models.password_reset import PasswordResetToken


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login(client, email: str, password: str):
    return client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )


def test_revoke_all_sessions_invalidates_current_token_and_allows_fresh_login(
    client, criar_usuario
):
    user, token = criar_usuario(email="sessoes@teste.local", role="admin")

    before = client.get("/api/auth/me", headers=_headers(token))
    assert before.status_code == 200

    revoked = client.post(
        "/api/auth/encerrar-todas-sessoes",
        headers=_headers(token),
    )
    assert revoked.status_code == 200
    assert revoked.json() == {"nota": "Todas as sessões da conta foram encerradas."}

    after = client.get("/api/auth/me", headers=_headers(token))
    assert after.status_code == 401

    fresh_login = _login(client, user.email, "senha-conta-123")
    assert fresh_login.status_code == 200, fresh_login.text
    fresh_token = fresh_login.json()["access_token"]
    assert client.get("/api/auth/me", headers=_headers(fresh_token)).status_code == 200


def test_authenticated_password_change_revokes_previous_tokens(
    client, criar_usuario, monkeypatch
):
    from app.services import emails

    monkeypatch.setattr(emails, "enviar_senha_alterada", lambda user_id: None)
    user, token = criar_usuario(email="troca.senha@teste.local", role="admin")

    changed = client.post(
        "/api/auth/alterar-senha",
        headers=_headers(token),
        json={
            "senha_atual": "senha-conta-123",
            "nova_senha": "nova-senha-segura-456",
        },
    )
    assert changed.status_code == 200, changed.text

    assert client.get("/api/auth/me", headers=_headers(token)).status_code == 401
    assert _login(client, user.email, "senha-conta-123").status_code == 401

    fresh_login = _login(client, user.email, "nova-senha-segura-456")
    assert fresh_login.status_code == 200, fresh_login.text
    assert client.get(
        "/api/auth/me",
        headers=_headers(fresh_login.json()["access_token"]),
    ).status_code == 200


def test_password_reset_revokes_tokens_issued_before_reset(
    client, criar_usuario, db, monkeypatch
):
    from app.services import emails

    monkeypatch.setattr(emails, "enviar_senha_alterada", lambda user_id: None)
    user, old_token = criar_usuario(email="reset.sessao@teste.local", role="admin")
    reset = PasswordResetToken(
        user_id=user.id,
        alvo="conta",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()
    db.refresh(reset)

    response = client.post(
        "/api/auth/redefinir-senha",
        json={"token": reset.token, "nova_senha": "senha-pos-reset-789"},
    )
    assert response.status_code == 200, response.text
    assert client.get("/api/auth/me", headers=_headers(old_token)).status_code == 401

    fresh_login = _login(client, user.email, "senha-pos-reset-789")
    assert fresh_login.status_code == 200, fresh_login.text


def test_legacy_token_is_accepted_only_until_first_revocation_marker(
    client, criar_usuario, db
):
    user, _ = criar_usuario(email="token.legado@teste.local", role="admin")
    legacy_token = jwt.encode(
        {
            "sub": user.email,
            "scope": "app",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    assert client.get("/api/auth/me", headers=_headers(legacy_token)).status_code == 200

    user.sessions_valid_after = datetime.now(timezone.utc)
    db.commit()
    assert client.get("/api/auth/me", headers=_headers(legacy_token)).status_code == 401

    precise_token = create_access_token(user.email)
    assert client.get("/api/auth/me", headers=_headers(precise_token)).status_code == 200


def test_password_hash_listener_sets_revocation_marker_only_on_rotation(
    criar_usuario, db
):
    user, _ = criar_usuario(email="listener.sessao@teste.local", role="admin")
    assert user.sessions_valid_after is None

    user.password_hash = hash_password("senha-rotacionada-123")
    db.commit()
    db.refresh(user)

    assert user.sessions_valid_after is not None
