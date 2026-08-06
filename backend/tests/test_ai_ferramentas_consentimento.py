"""Consentimento do médico para o assistente usar tools de agenda/e-mail —
rota HTTP real (PUT /api/ai/ferramentas/consentimento) e reflexo em
GET /api/ai/status. Isolamento entre usuários incluído: consentir não pode
vazar para outra conta.
"""


from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def test_status_comeca_sem_consentimento(client, criar_usuario, db):
    user, token = criar_usuario(email="ia.consent.status@teste.local")
    _subscribe(db, user.id)
    resposta = client.get("/api/ai/status", headers=_headers(token))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["ferramentas_consentidas"] is False
    assert "ferramentas_disponiveis_instalacao" in corpo


def test_conceder_e_revogar_consentimento(client, criar_usuario, db):
    user, token = criar_usuario(email="ia.consent.toggle@teste.local")
    _subscribe(db, user.id)

    concedido = client.put(
        "/api/ai/ferramentas/consentimento", headers=_headers(token), json={"ativar": True}
    )
    assert concedido.status_code == 200, concedido.text
    assert concedido.json()["ferramentas_consentidas"] is True
    assert concedido.json()["consent_em"] is not None

    status_depois = client.get("/api/ai/status", headers=_headers(token))
    assert status_depois.json()["ferramentas_consentidas"] is True

    db.refresh(user)
    assert user.ia_ferramentas_consent_em is not None
    assert user.ia_ferramentas_consent_versao

    revogado = client.put(
        "/api/ai/ferramentas/consentimento", headers=_headers(token), json={"ativar": False}
    )
    assert revogado.status_code == 200
    assert revogado.json()["ferramentas_consentidas"] is False
    assert revogado.json()["consent_em"] is None

    status_final = client.get("/api/ai/status", headers=_headers(token))
    assert status_final.json()["ferramentas_consentidas"] is False


def test_consentimento_e_isolado_por_usuario(client, criar_usuario, db):
    user_a, token_a = criar_usuario(email="ia.consent.a@teste.local")
    user_b, token_b = criar_usuario(email="ia.consent.b@teste.local")
    _subscribe(db, user_a.id)
    _subscribe(db, user_b.id)

    client.put("/api/ai/ferramentas/consentimento", headers=_headers(token_a), json={"ativar": True})

    status_a = client.get("/api/ai/status", headers=_headers(token_a))
    status_b = client.get("/api/ai/status", headers=_headers(token_b))
    assert status_a.json()["ferramentas_consentidas"] is True
    assert status_b.json()["ferramentas_consentidas"] is False


def test_consentimento_exige_autenticacao():
    from fastapi.testclient import TestClient
    from app.main import app

    resposta = TestClient(app).put("/api/ai/ferramentas/consentimento", json={"ativar": True})
    assert resposta.status_code in (401, 403)
