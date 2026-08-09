import jwt

from app.core.config import settings
from app.core.security import create_access_token
from app.models.email_account import EmailAccount


def test_email_session_can_be_renewed_while_still_valid(client, criar_usuario, db):
    user, _ = criar_usuario(email="mail-renew@teste.local")
    conta = EmailAccount(
        user_id=user.id,
        email_address="mail-renew@corvia.med.br",
        mail360_account_key="mail-renew-key",
        status="ativa",
    )
    db.add(conta)
    db.commit()

    token_antigo = create_access_token(conta.email_address, scope="email", expires_minutes=10)
    response = client.post(
        "/api/email/renovar-sessao",
        headers={"Authorization": f"Bearer {token_antigo}"},
    )
    assert response.status_code == 200, response.text
    token_novo = response.json()["access_token"]
    assert token_novo != token_antigo

    payload = jwt.decode(token_novo, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    assert payload["scope"] == "email"
    assert payload["sub"] == conta.email_address
    assert payload["exp"] - payload["iat"] >= 29 * 24 * 60 * 60


def test_app_token_cannot_renew_email_session(client, criar_usuario):
    _, token_app = criar_usuario(email="mail-scope@teste.local")
    response = client.post(
        "/api/email/renovar-sessao",
        headers={"Authorization": f"Bearer {token_app}"},
    )
    assert response.status_code == 401
