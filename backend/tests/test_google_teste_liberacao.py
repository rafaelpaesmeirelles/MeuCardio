"""Fila de liberação manual de testador do Google (app OAuth em modo
Testing) — GoogleTestUserRequest, POST/GET em app/api/agenda_integrada.py
e as duas rotas de admin em app/api/admin.py.
"""
from app.core.config import settings
from app.models.agenda import GoogleTestUserRequest
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def test_solicitar_teste_cria_pedido_pendente(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/agenda/google-teste/solicitar",
        json={"google_email": "rafael@gmail.com"},
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    assert resposta.json()["status"] == "pendente"
    item = db.query(GoogleTestUserRequest).filter(GoogleTestUserRequest.user_id == user.id).first()
    assert item.google_email == "rafael@gmail.com"


def test_solicitar_de_novo_atualiza_pedido_pendente_em_vez_de_duplicar(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    client.post("/api/agenda/google-teste/solicitar", json={"google_email": "rafael@gmail.com"}, headers=_headers(token))
    resposta = client.post(
        "/api/agenda/google-teste/solicitar",
        json={"google_email": "outro@gmail.com"},
        headers=_headers(token),
    )
    assert resposta.status_code == 201
    itens = db.query(GoogleTestUserRequest).filter(GoogleTestUserRequest.user_id == user.id).all()
    assert len(itens) == 1
    assert itens[0].google_email == "outro@gmail.com"


def test_solicitar_email_invalido_e_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/agenda/google-teste/solicitar",
        json={"google_email": "nao-e-email"},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_solicitar_fora_do_modo_teste_e_409(client, db, criar_usuario, monkeypatch):
    monkeypatch.setattr(settings, "google_oauth_modo_teste", False)
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/agenda/google-teste/solicitar",
        json={"google_email": "rafael@gmail.com"},
        headers=_headers(token),
    )
    assert resposta.status_code == 409


def test_status_devolve_none_sem_pedido(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/agenda/google-teste/status", headers=_headers(token))
    assert resposta.status_code == 200
    assert resposta.json()["status"] is None


def test_status_reflete_pedido_criado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    client.post("/api/agenda/google-teste/solicitar", json={"google_email": "rafael@gmail.com"}, headers=_headers(token))
    resposta = client.get("/api/agenda/google-teste/status", headers=_headers(token))
    assert resposta.json() == {
        "status": "pendente", "google_email": "rafael@gmail.com",
        "created_at": resposta.json()["created_at"],
    }


def test_capabilities_expoe_modo_teste(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.get("/api/agenda/capabilities", headers=_headers(token))
    assert resposta.json()["google_oauth_modo_teste"] is True


def test_admin_lista_pedidos_pendentes(client, db, criar_usuario):
    user, token_user = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
    client.post("/api/agenda/google-teste/solicitar", json={"google_email": "rafael@gmail.com"}, headers=_headers(token_user))
    resposta = client.get("/api/admin/google-teste", headers=_headers(token_admin))
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["google_email"] == "rafael@gmail.com"


def test_admin_lista_e_bloqueada_para_nao_admin(client, criar_usuario):
    _, token = criar_usuario()
    resposta = client.get("/api/admin/google-teste", headers=_headers(token))
    assert resposta.status_code == 403


def test_admin_libera_pedido_e_notifica(client, db, criar_usuario, monkeypatch):
    user, token_user = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
    client.post("/api/agenda/google-teste/solicitar", json={"google_email": "rafael@gmail.com"}, headers=_headers(token_user))
    item_id = db.query(GoogleTestUserRequest).filter(GoogleTestUserRequest.user_id == user.id).first().id

    chamadas = []
    monkeypatch.setattr(
        "app.services.emails.enviar_google_teste_liberado",
        lambda user_id, google_email: chamadas.append((user_id, google_email)) or True,
    )
    resposta = client.post(f"/api/admin/google-teste/{item_id}/liberar", headers=_headers(token_admin))
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "liberado"

    item = db.get(GoogleTestUserRequest, item_id)
    assert item.status == "liberado"
    assert item.liberado_em is not None
    assert item.notificado_em is not None
    assert chamadas == [(user.id, "rafael@gmail.com")]


def test_admin_liberar_pedido_inexistente_e_404(client, criar_usuario):
    _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
    resposta = client.post("/api/admin/google-teste/999999/liberar", headers=_headers(token_admin))
    assert resposta.status_code == 404


def test_admin_liberar_pedido_ja_liberado_e_409(client, db, criar_usuario, monkeypatch):
    user, token_user = criar_usuario()
    _subscribe(db, user.id)
    _, token_admin = criar_usuario(email="admin@teste.local", role="admin")
    client.post("/api/agenda/google-teste/solicitar", json={"google_email": "rafael@gmail.com"}, headers=_headers(token_user))
    item_id = db.query(GoogleTestUserRequest).filter(GoogleTestUserRequest.user_id == user.id).first().id
    monkeypatch.setattr("app.services.emails.enviar_google_teste_liberado", lambda *a, **k: True)
    client.post(f"/api/admin/google-teste/{item_id}/liberar", headers=_headers(token_admin))
    resposta = client.post(f"/api/admin/google-teste/{item_id}/liberar", headers=_headers(token_admin))
    assert resposta.status_code == 409
