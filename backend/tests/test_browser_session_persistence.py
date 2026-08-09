def test_browser_session_persistent_cookie_lasts_30_days(client, criar_usuario):
    user, _ = criar_usuario(email="persistente@teste.local")
    response = client.post(
        "/api/auth/sessao",
        data={
            "username": user.email,
            "password": "senha-conta-123",
            "permanecer_conectado": "true",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["persistent"] is True
    cookie = response.headers.get("set-cookie", "")
    assert "corvia_session=" in cookie
    assert "Max-Age=2592000" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == user.email


def test_browser_session_without_persistence_keeps_normal_expiry(client, criar_usuario):
    user, _ = criar_usuario(email="curta@teste.local")
    response = client.post(
        "/api/auth/sessao",
        data={
            "username": user.email,
            "password": "senha-conta-123",
            "permanecer_conectado": "false",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["persistent"] is False
    cookie = response.headers.get("set-cookie", "")
    assert "corvia_session=" in cookie
    assert "Max-Age=43200" in cookie


def test_logout_removes_even_persistent_cookie(client, criar_usuario):
    user, _ = criar_usuario(email="logout-persistente@teste.local")
    login = client.post(
        "/api/auth/sessao",
        data={
            "username": user.email,
            "password": "senha-conta-123",
            "permanecer_conectado": "true",
        },
    )
    assert login.status_code == 200
    assert client.get("/api/auth/me").status_code == 200

    logout = client.post("/api/auth/sair")
    assert logout.status_code == 200
    assert client.get("/api/auth/me").status_code == 401
