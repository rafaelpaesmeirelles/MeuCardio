def test_session_status_sem_sessao_nao_gera_401(client):
    response = client.get("/api/auth/session-status")
    assert response.status_code == 200
    assert response.json() == {"authenticated": False}


def test_session_status_reconhece_bearer_valido(client, criar_usuario):
    _user, token = criar_usuario()
    response = client.get(
        "/api/auth/session-status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}
