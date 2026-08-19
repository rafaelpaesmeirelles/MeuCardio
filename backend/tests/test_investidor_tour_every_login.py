from app.core.security import create_access_token


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_investidor_tour_reabre_em_cada_nova_sessao(client, db, criar_usuario):
    user, token_1 = criar_usuario(email="investidor@corvia.med.br", full_name="Investidor CorVIA", role="leitor")
    user.investidor = True
    user.onboarding_visto = True  # estado legado não pode pular o tour de um novo login
    db.commit()

    primeiro_me = client.get("/api/auth/me", headers=_headers(token_1))
    assert primeiro_me.status_code == 200
    assert primeiro_me.json()["investidor"] is True
    assert primeiro_me.json()["onboarding_pendente"] is True

    pulou = client.post("/api/auth/me/onboarding-concluido", json={}, headers=_headers(token_1))
    assert pulou.status_code == 200
    assert pulou.json()["onboarding_pendente"] is False

    mesma_sessao = client.get("/api/auth/me", headers=_headers(token_1))
    assert mesma_sessao.status_code == 200
    assert mesma_sessao.json()["onboarding_pendente"] is False

    # Novo login = novo token. O cookie efêmero da sessão anterior não vale
    # para este token, então a primeira tela volta a ser obrigatoriamente o tour.
    token_2 = create_access_token(user.email, scope="app")
    assert token_2 != token_1

    novo_login = client.get("/api/auth/me", headers=_headers(token_2))
    assert novo_login.status_code == 200
    assert novo_login.json()["onboarding_pendente"] is True
