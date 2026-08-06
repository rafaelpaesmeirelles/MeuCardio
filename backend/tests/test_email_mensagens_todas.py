"""GET /api/email/mensagens/todas — caixa combinada (CorvIA Mail nativo +
contas Google/Microsoft conectadas com e-mail autorizado), mesclada por data.
"""
from app.models.agenda import CalendarIntegration
from app.models.email_account import EmailAccount
from app.services import external_mail, mail360


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


def _integracao_google_com_mail(db, user_id, *, read_mail=True) -> CalendarIntegration:
    integracao = CalendarIntegration(
        owner_id=user_id, provider="google_calendar", display_name="titular@gmail.com",
        external_account_id="ext-google-1", sync_strategy="external_authoritative",
        enabled=True, status="connected", contacts_enabled=True,
        capabilities={"read_appointments": True, "read_mail": read_mail, "send_mail": read_mail},
    )
    db.add(integracao)
    db.commit()
    db.refresh(integracao)
    return integracao


def test_mescla_nativa_e_externa_ordenada_por_data_mais_recente_primeiro(
    client, db, criar_usuario, monkeypatch_mail360, monkeypatch,
):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    _integracao_google_com_mail(db, user.id)

    monkeypatch.setattr(
        mail360, "listar_mensagens",
        lambda *a, **k: [{"messageId": "nativa-1", "subject": "Da caixa nativa", "receivedTime": "1000000"}],
    )
    monkeypatch.setattr(
        external_mail, "list_messages",
        lambda *a, **k: [{
            "messageId": "gmail-1", "id": "gmail-1", "subject": "Do Gmail",
            "receivedTime": "9999999", "provider": "google",
        }],
    )

    resposta = client.get("/api/email/mensagens/todas", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["fontes_com_erro"] == []
    assert [m["messageId"] for m in corpo["mensagens"]] == ["gmail-1", "nativa-1"]
    assert corpo["mensagens"][0]["origem"] != "corvia"
    assert corpo["mensagens"][1]["origem"] == "corvia"


def test_ignora_integracao_sem_read_mail(client, db, criar_usuario, monkeypatch_mail360, monkeypatch):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    _integracao_google_com_mail(db, user.id, read_mail=False)

    monkeypatch.setattr(mail360, "listar_mensagens", lambda *a, **k: [])
    chamou_externa = []
    monkeypatch.setattr(
        external_mail, "list_messages",
        lambda *a, **k: chamou_externa.append(True) or [],
    )

    resposta = client.get("/api/email/mensagens/todas", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    assert resposta.json()["mensagens"] == []
    assert chamou_externa == []  # nunca chegou a chamar a API externa


def test_falha_em_uma_fonte_nao_derruba_as_outras(client, db, criar_usuario, monkeypatch_mail360, monkeypatch):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    _integracao_google_com_mail(db, user.id)

    monkeypatch.setattr(
        mail360, "listar_mensagens",
        lambda *a, **k: [{"messageId": "nativa-1", "subject": "Sobrevive", "receivedTime": "1000"}],
    )

    def _falha(*a, **k):
        raise external_mail.ExternalMailError("token expirado", status_code=409)

    monkeypatch.setattr(external_mail, "list_messages", _falha)

    resposta = client.get("/api/email/mensagens/todas", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert [m["messageId"] for m in corpo["mensagens"]] == ["nativa-1"]
    assert len(corpo["fontes_com_erro"]) == 1
    assert corpo["fontes_com_erro"][0]["provider"] == "google"
    assert "token expirado" in corpo["fontes_com_erro"][0]["erro"]


def test_limite_fora_do_intervalo_devolve_422(client, db, criar_usuario, monkeypatch_mail360):
    user, _ = criar_usuario()
    token = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.get("/api/email/mensagens/todas?limite=0", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 422
    resposta = client.get("/api/email/mensagens/todas?limite=51", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 422


def test_isolamento_entre_usuarios(client, db, criar_usuario, monkeypatch_mail360, monkeypatch):
    dono, _ = criar_usuario(email="mensagens.todas.dono@teste.local")
    outro, _ = criar_usuario(email="mensagens.todas.outro@teste.local")
    _integracao_google_com_mail(db, dono.id)
    token_outro = _token_email(client, db, outro, monkeypatch_mail360, senha="senha-outro-123")

    monkeypatch.setattr(mail360, "listar_mensagens", lambda *a, **k: [])
    chamou_externa = []
    monkeypatch.setattr(external_mail, "list_messages", lambda *a, **k: chamou_externa.append(True) or [])

    resposta = client.get("/api/email/mensagens/todas", headers={"Authorization": f"Bearer {token_outro}"})
    assert resposta.status_code == 200
    assert chamou_externa == []  # a integração do dono não foi consultada pelo token do outro


def test_sem_token_devolve_401(client):
    assert client.get("/api/email/mensagens/todas").status_code == 401
