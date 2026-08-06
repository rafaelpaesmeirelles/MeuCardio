"""Conexão da Yahoo (POST /api/email/conectar-yahoo) e despacho das rotas
/externas/{id}/... para app/services/yahoo_mail.py quando a integração é
provider="yahoo_mail" — sem IMAP/SMTP real, yahoo_mail é mockado no nível do
módulo (mesmo padrão de test_email_mensagens_todas.py para external_mail).
"""
from app.core.security import create_access_token
from app.models.agenda import CalendarIntegration
from app.services import yahoo_mail


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _token_email(client, db, user, monkeypatch_mail360, senha="senha-caixa-123"):
    from app.models.email_account import EmailAccount
    from app.models.subscription import TIPO_EMAIL, Subscription

    db.add(Subscription(user_id=user.id, kind=TIPO_EMAIL, status="ativo"))
    db.commit()
    token_app = create_access_token(user.email, scope="app")
    sugestao = client.get("/api/email/sugestao-endereco", headers=_headers(token_app))
    local_part = sugestao.json()["local_part"]
    ativar = client.post(
        "/api/email/conta",
        json={"senha": senha, "aceite_lgpd": True, "local_part": local_part},
        headers=_headers(token_app),
    )
    assert ativar.status_code == 201, ativar.text
    endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": senha})
    return login.json()["access_token"]


def test_conectar_yahoo_sem_consentimento_e_422(client, criar_usuario):
    _, token = criar_usuario()
    resposta = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "titular@yahoo.com", "senha_de_app": "abcd1234", "consent_accepted": False},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_conectar_yahoo_email_invalido_e_422(client, criar_usuario):
    _, token = criar_usuario()
    resposta = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "nao-e-email", "senha_de_app": "abcd1234", "consent_accepted": True},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_conectar_yahoo_credencial_recusada_nao_persiste_integracao(client, db, criar_usuario, monkeypatch):
    user, token = criar_usuario()

    def _diagnose_falha(credentials):
        from app.services.yahoo_mail import YahooMailError
        raise YahooMailError("Login IMAP recusado.", status_code=401)

    monkeypatch.setattr(yahoo_mail, "diagnose", _diagnose_falha)
    resposta = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "titular@yahoo.com", "senha_de_app": "abcd1234", "consent_accepted": True},
        headers=_headers(token),
    )
    assert resposta.status_code == 401
    assert db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == user.id).count() == 0


def test_conectar_yahoo_com_sucesso_aparece_em_contas(client, db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, token = criar_usuario()
    monkeypatch.setattr(yahoo_mail, "diagnose", lambda credentials: {"ok": True, "provider": "yahoo_mail"})

    conectar = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "titular@yahoo.com", "senha_de_app": "abcd1234", "consent_accepted": True},
        headers=_headers(token),
    )
    assert conectar.status_code == 201, conectar.text
    assert conectar.json()["provider"] == "yahoo"

    integracao = db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == user.id).first()
    assert integracao.provider == "yahoo_mail"
    assert integracao.capabilities == {"read_mail": True, "send_mail": True}

    token_email = _token_email(client, db, user, monkeypatch_mail360)
    contas = client.get("/api/email/contas", headers=_headers(token_email))
    assert contas.status_code == 200
    yahoo_na_lista = next(c for c in contas.json() if c["provider"] == "yahoo")
    assert yahoo_na_lista["send_mail"] is True


def test_mensagens_externas_despacha_para_yahoo(client, db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, token = criar_usuario()
    monkeypatch.setattr(yahoo_mail, "diagnose", lambda credentials: {"ok": True})
    conectar = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "titular@yahoo.com", "senha_de_app": "abcd1234", "consent_accepted": True},
        headers=_headers(token),
    )
    integration_id = conectar.json()["id"]

    chamadas = []

    def _list_messages(credentials, *, folder, limit, start):
        chamadas.append((credentials["username"], folder, limit, start))
        return [{"messageId": "INBOX:1", "subject": "Da Yahoo", "receivedTime": "1000", "provider": "yahoo"}]

    monkeypatch.setattr(yahoo_mail, "list_messages", _list_messages)
    token_email = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.get(f"/api/email/externas/{integration_id}/mensagens", headers=_headers(token_email))
    assert resposta.status_code == 200
    assert resposta.json()[0]["subject"] == "Da Yahoo"
    assert chamadas == [("titular@yahoo.com", None, 50, 1)]


def test_mover_mensagem_yahoo_nao_e_suportado(client, db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, token = criar_usuario()
    monkeypatch.setattr(yahoo_mail, "diagnose", lambda credentials: {"ok": True})
    conectar = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "titular@yahoo.com", "senha_de_app": "abcd1234", "consent_accepted": True},
        headers=_headers(token),
    )
    integration_id = conectar.json()["id"]
    token_email = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.put(
        f"/api/email/externas/{integration_id}/mensagens/acoes",
        json={"message_ids": ["INBOX:1"], "acao": "mover", "pasta_destino": "Arquivo"},
        headers=_headers(token_email),
    )
    assert resposta.status_code == 422


def test_enviar_pela_yahoo_despacha_corretamente(client, db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, token = criar_usuario()
    monkeypatch.setattr(yahoo_mail, "diagnose", lambda credentials: {"ok": True})
    conectar = client.post(
        "/api/email/conectar-yahoo",
        json={"endereco": "titular@yahoo.com", "senha_de_app": "abcd1234", "consent_accepted": True},
        headers=_headers(token),
    )
    integration_id = conectar.json()["id"]

    enviados = []
    monkeypatch.setattr(
        yahoo_mail, "send_message",
        lambda credentials, *, to, subject, html, cc=None, bcc=None: enviados.append((to, subject, html)) or {"status": "sent"},
    )
    token_email = _token_email(client, db, user, monkeypatch_mail360)
    resposta = client.post(
        f"/api/email/externas/{integration_id}/mensagens",
        json={"para": "destino@example.com", "assunto": "Oi", "corpo_html": "Texto", "anexos": []},
        headers=_headers(token_email),
    )
    assert resposta.status_code == 201
    assert enviados == [("destino@example.com", "Oi", "Texto")]
