"""POST /api/agenda/integrations/apple — extensão do Trabalho 10: opt-in de
e-mail (mail/mail_consent_accepted) além de Calendário/Contatos, sem quebrar
o comportamento anterior (só Calendário/Contatos, que já funcionava).
"""
from app.models.agenda import CalendarIntegration
from app.models.subscription import Subscription
from app.services import apple_mail


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _payload(**overrides) -> dict:
    base = {
        "apple_id": "titular@icloud.com",
        "app_specific_password": "abcd-efgh-ijkl-mnop",
        "consent_accepted": True,
    }
    base.update(overrides)
    return base


def test_conectar_apple_sem_mail_mantem_comportamento_anterior(client, db, criar_usuario, monkeypatch):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    monkeypatch.setattr(
        "app.services.agenda_integrada.connectors.AppleICloudCalendarConnector.diagnose",
        lambda self: {"ok": True},
    )
    resposta = client.post("/api/agenda/integrations/apple", json=_payload(), headers=_headers(token))
    assert resposta.status_code == 201, resposta.text
    integracao = db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == user.id).first()
    assert integracao.capabilities["read_mail"] is False
    assert integracao.capabilities["send_mail"] is False


def test_conectar_apple_com_mail_sem_consentimento_de_mail_e_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/agenda/integrations/apple", json=_payload(mail=True), headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_conectar_apple_com_mail_confirma_via_imap_antes_de_liberar(client, db, criar_usuario, monkeypatch):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    monkeypatch.setattr(
        "app.services.agenda_integrada.connectors.AppleICloudCalendarConnector.diagnose",
        lambda self: {"ok": True},
    )
    chamadas = []
    monkeypatch.setattr(
        apple_mail, "diagnose",
        lambda credentials: chamadas.append(credentials["username"]) or {"ok": True, "provider": "apple_mail"},
    )
    resposta = client.post(
        "/api/agenda/integrations/apple",
        json=_payload(mail=True, mail_consent_accepted=True),
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    assert chamadas == ["titular@icloud.com"]
    integracao = db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == user.id).first()
    assert integracao.capabilities["read_mail"] is True
    assert integracao.capabilities["send_mail"] is True


def test_conectar_apple_mail_diagnose_falha_nao_salva_integracao(client, db, criar_usuario, monkeypatch):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    monkeypatch.setattr(
        "app.services.agenda_integrada.connectors.AppleICloudCalendarConnector.diagnose",
        lambda self: {"ok": True},
    )

    def _falha(credentials):
        from app.services.apple_mail import AppleMailError
        raise AppleMailError("Login IMAP recusado.", status_code=401)

    monkeypatch.setattr(apple_mail, "diagnose", _falha)
    resposta = client.post(
        "/api/agenda/integrations/apple",
        json=_payload(mail=True, mail_consent_accepted=True),
        headers=_headers(token),
    )
    assert resposta.status_code == 401
    assert db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == user.id).count() == 0


def test_email_contas_lista_apple_quando_mail_ativado(client, db, criar_usuario, monkeypatch, monkeypatch_mail360):
    from app.core.security import create_access_token
    from app.models.email_account import EmailAccount
    from app.models.subscription import TIPO_EMAIL

    user, token = criar_usuario()
    _subscribe(db, user.id)
    db.add(Subscription(user_id=user.id, kind=TIPO_EMAIL, status="ativo"))
    db.commit()

    monkeypatch.setattr(
        "app.services.agenda_integrada.connectors.AppleICloudCalendarConnector.diagnose",
        lambda self: {"ok": True},
    )
    monkeypatch.setattr(apple_mail, "diagnose", lambda credentials: {"ok": True})
    conectar = client.post(
        "/api/agenda/integrations/apple",
        json=_payload(mail=True, mail_consent_accepted=True),
        headers=_headers(token),
    )
    assert conectar.status_code == 201, conectar.text

    token_app = create_access_token(user.email, scope="app")
    sugestao = client.get("/api/email/sugestao-endereco", headers=_headers(token_app))
    ativar = client.post(
        "/api/email/conta",
        json={"senha": "senha-caixa-123", "aceite_lgpd": True, "local_part": sugestao.json()["local_part"]},
        headers=_headers(token_app),
    )
    assert ativar.status_code == 201, ativar.text
    endereco = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first().email_address
    login = client.post("/api/email/entrar", json={"endereco": endereco, "senha": "senha-caixa-123"})
    token_email = login.json()["access_token"]

    contas = client.get("/api/email/contas", headers=_headers(token_email))
    assert contas.status_code == 200
    apple_na_lista = next(c for c in contas.json() if c["provider"] == "apple")
    assert apple_na_lista["send_mail"] is True
