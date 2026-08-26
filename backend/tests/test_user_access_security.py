from app.core.security import hash_password
from app.models.email_account import EmailAccount


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login(client, email: str, password: str = "senha-conta-123", **headers):
    return client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers=headers,
    )


def test_novo_login_invalida_imediatamente_a_sessao_anterior(client, criar_usuario):
    user, _ = criar_usuario(email="sessao-unica@teste.local")

    primeiro = _login(client, user.email)
    assert primeiro.status_code == 200, primeiro.text
    token_1 = primeiro.json()["access_token"]
    assert client.get("/api/auth/me", headers=_headers(token_1)).status_code == 200

    segundo = _login(client, user.email)
    assert segundo.status_code == 200, segundo.text
    token_2 = segundo.json()["access_token"]

    assert client.get("/api/auth/me", headers=_headers(token_1)).status_code == 401
    assert client.get("/api/auth/me", headers=_headers(token_2)).status_code == 200


def test_corvia_mail_tambem_aceita_apenas_a_sessao_mais_recente(client, db, criar_usuario):
    user, _ = criar_usuario(email="mail-sessao-unica@teste.local")
    conta = EmailAccount(
        user_id=user.id,
        email_address="sessao.unica@corvia.med.br",
        mail360_account_key="mail-session-key",
        password_hash=hash_password("senha-mail-123"),
        status="ativa",
    )
    db.add(conta)
    db.commit()

    first = client.post(
        "/api/email/entrar",
        json={"endereco": conta.email_address, "senha": "senha-mail-123"},
    )
    assert first.status_code == 200, first.text
    token_1 = first.json()["access_token"]

    second = client.post(
        "/api/email/entrar",
        json={"endereco": conta.email_address, "senha": "senha-mail-123"},
    )
    assert second.status_code == 200, second.text
    token_2 = second.json()["access_token"]

    assert client.get("/api/email/eu", headers=_headers(token_1)).status_code == 401
    assert client.get("/api/email/eu", headers=_headers(token_2)).status_code == 200


def test_historico_e_restrito_ao_proprietario_e_expoe_dados_de_seguranca(
    client, criar_usuario,
):
    owner, owner_token = criar_usuario(email="admin@teste.local", role="admin")
    _other_admin, other_admin_token = criar_usuario(email="outro-admin@teste.local", role="admin")
    target, _ = criar_usuario(email="auditado@teste.local")

    login = _login(
        client,
        target.email,
        **{
            "CF-Connecting-IP": "203.0.113.42",
            "CF-IPCity": "São Paulo",
            "CF-Region": "São Paulo",
            "CF-IPCountry": "BR",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/140.0 Safari/537.36",
        },
    )
    assert login.status_code == 200, login.text

    denied = client.get(
        f"/api/admin/user-management/{target.id}/accesses",
        headers=_headers(other_admin_token),
    )
    assert denied.status_code == 403

    allowed = client.get(
        f"/api/admin/user-management/{target.id}/accesses",
        headers=_headers(owner_token),
    )
    assert allowed.status_code == 200, allowed.text
    item = allowed.json()["items"][0]
    assert item["ip_address"] == "203.0.113.42"
    assert item["location"] == "São Paulo, São Paulo, BR"
    assert item["operating_system"] == "Windows"
    assert item["browser"] == "Google Chrome"
    assert item["active"] is True

    revoked = client.post(
        f"/api/admin/user-management/{target.id}/revoke-session",
        headers=_headers(owner_token),
    )
    assert revoked.status_code == 200, revoked.text
    assert client.get("/api/auth/me", headers=_headers(login.json()["access_token"])).status_code == 401


def test_tentativas_repetidas_e_mudanca_rapida_geram_alertas_explicaveis(
    client, db, criar_usuario,
):
    _owner, owner_token = criar_usuario(email="admin@teste.local", role="admin")
    target, _ = criar_usuario(email="risco@teste.local")

    for _ in range(3):
        resposta = _login(
            client, target.email, "senha-errada",
            **{"CF-Connecting-IP": "203.0.113.10", "CF-IPCity": "São Paulo", "CF-IPCountry": "BR"},
        )
        assert resposta.status_code == 401

    first = _login(
        client, target.email,
        **{
            "CF-Connecting-IP": "203.0.113.10", "CF-IPCity": "São Paulo",
            "CF-IPCountry": "BR", "User-Agent": "Mozilla/5.0 (Windows NT 10.0) Chrome/140.0",
        },
    )
    assert first.status_code == 200
    second = _login(
        client, target.email,
        **{
            "CF-Connecting-IP": "198.51.100.20", "CF-IPCity": "Lisboa",
            "CF-IPCountry": "PT", "User-Agent": "Mozilla/5.0 (iPhone) Safari/605.1",
        },
    )
    assert second.status_code == 200

    history = client.get(
        f"/api/admin/user-management/{target.id}/accesses",
        headers=_headers(owner_token),
    )
    assert history.status_code == 200, history.text
    codes = {
        reason["code"]
        for item in history.json()["items"]
        for reason in item["risk_reasons"]
    }
    assert "tentativas_repetidas" in codes
    assert "sessao_ativa_substituida" in codes
    assert "pais_diferente_em_curto_periodo" in codes
