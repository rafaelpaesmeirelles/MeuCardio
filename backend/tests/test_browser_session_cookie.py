import pytest
from starlette.responses import Response
from starlette.websockets import WebSocketDisconnect

from app.core.security import AUTH_COOKIE_NAME, gravar_cookie_sessao
from app.main import app


def _login_cookie(client, email: str, password: str = "senha-conta-123"):
    return client.post(
        "/api/auth/sessao",
        data={"username": email, "password": password},
    )


def test_browser_login_sets_httponly_lax_cookie_and_authenticates_without_bearer(
    client, criar_usuario
):
    user, _ = criar_usuario(email="cookie.web@teste.local", role="admin")

    response = _login_cookie(client, user.email)
    assert response.status_code == 200, response.text
    # `persistent` (09/08/2026, "permanecer conectado") passou a vir na
    # resposta depois que este teste foi escrito — assert por chave em vez
    # de igualdade estrita de dict, para não travar a cada campo novo que a
    # rota passe a devolver.
    assert response.json()["authenticated"] is True

    set_cookie = response.headers["set-cookie"].lower()
    assert f"{AUTH_COOKIE_NAME}=" in set_cookie
    assert "httponly" in set_cookie
    # "lax", não "strict" (09/08/2026) -- "strict" derrubava a sessão sempre
    # que o retorno de um OAuth (Google/Microsoft) pousava de volta em
    # /agenda, porque o navegador não reenvia cookie Strict numa navegação de
    # topo cuja cadeia começou em outro site. Ver gravar_cookie_sessao().
    assert "samesite=lax" in set_cookie
    assert "path=/" in set_cookie
    assert "secure" not in set_cookie

    me = client.get("/api/auth/me")
    assert me.status_code == 200, me.text
    assert me.json()["email"] == user.email


def test_browser_logout_clears_cookie_even_without_authenticated_dependency(
    client, criar_usuario
):
    user, _ = criar_usuario(email="logout.cookie@teste.local", role="admin")
    assert _login_cookie(client, user.email).status_code == 200
    assert client.get("/api/auth/me").status_code == 200

    logout = client.post("/api/auth/sair")
    assert logout.status_code == 200
    assert logout.json() == {"authenticated": False}
    cleared = logout.headers["set-cookie"].lower()
    assert f"{AUTH_COOKIE_NAME}=" in cleared
    assert "max-age=0" in cleared or "expires=" in cleared

    assert client.get("/api/auth/me").status_code == 401


def test_bearer_clients_remain_supported(client, criar_usuario):
    user, token = criar_usuario(email="integracao.bearer@teste.local", role="admin")
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_production_cookie_is_secure(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    response = Response()

    gravar_cookie_sessao(response, "jwt-de-teste")

    set_cookie = response.headers["set-cookie"].lower()
    assert "secure" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie


def test_chat_websocket_uses_browser_cookie_not_query_secret(client, criar_usuario):
    user, _ = criar_usuario(email="chat.cookie@teste.local", role="admin")
    assert _login_cookie(client, user.email).status_code == 200

    # A query contém somente um marcador não secreto mantido por compatibilidade
    # com o componente atual. O backend prioriza o cookie HttpOnly no handshake.
    with client.websocket_connect("/api/chat/ws?token=cookie-session") as websocket:
        websocket.send_text("ping")


def test_chat_websocket_rejects_invalid_session_without_cookie():
    from fastapi.testclient import TestClient

    isolated_client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc:
        with isolated_client.websocket_connect("/api/chat/ws?token=invalid"):
            pass
    assert exc.value.code == 4401
