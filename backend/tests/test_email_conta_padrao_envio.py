"""GET /api/email/contas (campo `padrao`) e PUT /api/email/conta-padrao-envio
— Trabalho 9, painel "Administre suas contas": qual caixa abre por padrão ao
escrever uma mensagem nova no CorvIA Mail.
"""
from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount


def _dar_assinatura_email_ativa(db, user):
    from app.models.subscription import TIPO_EMAIL, Subscription

    db.add(Subscription(user_id=user.id, kind=TIPO_EMAIL, status="ativo"))
    db.commit()


def _token_email(client, db, user, monkeypatch_mail360, senha="senha-caixa-123"):
    from app.core.security import create_access_token

    _dar_assinatura_email_ativa(db, user)
    token_app = create_access_token(user.email, scope="app")
    sugestao = client.get("/api/email/sugestao-endereco", headers={"Authorization": f"Bearer {token_app}"})
    local_part = sugestao.json()["local_part"]
    ativar = client.post(
        "/api/email/conta",
        json={"senha": senha, "aceite_lgpd": True, "local_part": local_part},
        headers={"Authorization": f"Bearer {token_app}"},
    )
    assert ativar.status_code == 201, ativar.text
    endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": senha})
    return login.json()["access_token"]


def _integracao_google_com_mail(db, user_id, *, send_mail=True) -> CalendarIntegration:
    integracao = CalendarIntegration(
        owner_id=user_id, provider="google_calendar", display_name="titular@gmail.com",
        external_account_id="ext-google-1", sync_strategy="external_authoritative",
        enabled=True, status="connected", contacts_enabled=True,
        capabilities={"read_appointments": True, "read_mail": True, "send_mail": send_mail},
    )
    db.add(integracao)
    db.commit()
    db.refresh(integracao)
    return integracao


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_corvia_e_padrao_quando_nunca_configurado(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    contas = client.get("/api/email/contas", headers=_headers(token)).json()
    assert next(c for c in contas if c["id"] == "corvia")["padrao"] is True


def test_definir_conta_padrao_externa_e_refletido_em_contas(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    integracao = _integracao_google_com_mail(db, user.id)
    token = _token_email(client, db, user, monkeypatch_mail360)

    resposta = client.put(
        "/api/email/conta-padrao-envio", json={"conta_id": str(integracao.id)}, headers=_headers(token),
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["conta_padrao_envio"] == str(integracao.id)

    contas = client.get("/api/email/contas", headers=_headers(token)).json()
    assert next(c for c in contas if c["id"] == "corvia")["padrao"] is False
    assert next(c for c in contas if c["id"] == str(integracao.id))["padrao"] is True


def test_voltar_para_corvia_como_padrao(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    integracao = _integracao_google_com_mail(db, user.id)
    token = _token_email(client, db, user, monkeypatch_mail360)
    client.put("/api/email/conta-padrao-envio", json={"conta_id": str(integracao.id)}, headers=_headers(token))

    resposta = client.put("/api/email/conta-padrao-envio", json={"conta_id": "corvia"}, headers=_headers(token))
    assert resposta.status_code == 200
    contas = client.get("/api/email/contas", headers=_headers(token)).json()
    assert next(c for c in contas if c["id"] == "corvia")["padrao"] is True


def test_conta_inexistente_e_422(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.put("/api/email/conta-padrao-envio", json={"conta_id": "999999"}, headers=_headers(token))
    assert resposta.status_code == 422


def test_conta_sem_permissao_de_envio_e_422(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    integracao = _integracao_google_com_mail(db, user.id, send_mail=False)
    token = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.put(
        "/api/email/conta-padrao-envio", json={"conta_id": str(integracao.id)}, headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_conta_de_outro_usuario_nao_e_aceita(client, db, criar_usuario, monkeypatch_mail360):
    user1, _ = criar_usuario()
    user2, _ = criar_usuario(email="outro@teste.local")
    integracao_do_user2 = _integracao_google_com_mail(db, user2.id)
    token_user1 = _token_email(client, db, user1, monkeypatch_mail360, senha="senha-user1-123")

    resposta = client.put(
        "/api/email/conta-padrao-envio",
        json={"conta_id": str(integracao_do_user2.id)},
        headers=_headers(token_user1),
    )
    assert resposta.status_code == 422
