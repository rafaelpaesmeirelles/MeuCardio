"""Regressões da sincronização contínua de contas externas.

Cobre os dois bugs reportados em produção: retorno do OAuth levando a /entrar
e Yahoo mail-only sem uma ação de sincronização funcional.
"""
from datetime import datetime, timezone
import hashlib

from app.api import agenda_integrada
from app.models.agenda import CalendarIntegration, IntegrationOAuthState
from app.models.subscription import Subscription
from app.services import account_sync
from app.services.agenda_integrada.domain import store_integration_credentials
from app.services.yahoo_mail import YahooMailError


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _yahoo(db, user) -> CalendarIntegration:
    item = CalendarIntegration(
        owner_id=user.id,
        provider="yahoo_mail",
        display_name="medico@yahoo.com",
        external_account_id="medico@yahoo.com",
        status="connected",
        enabled=True,
        sync_calendar=True,  # legado possível; não pode forçar calendar sync
        sync_mail=True,
        contacts_enabled=False,
        capabilities={"read_mail": True, "send_mail": True},
        sync_strategy="external_authoritative",
        configuration={},
    )
    db.add(item)
    db.flush()
    store_integration_credentials(item, {
        "username": "medico@yahoo.com",
        "app_specific_password": "senha-app",
    })
    db.commit()
    db.refresh(item)
    return item


def test_yahoo_mail_only_sync_uses_heartbeat_and_never_calendar(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.yahoo.runtime@teste.local")
    item = _yahoo(db, user)
    chamadas = []

    monkeypatch.setattr(
        account_sync.yahoo_mail,
        "diagnose",
        lambda credenciais: chamadas.append(("mail", credenciais["username"])) or {"ok": True},
    )
    monkeypatch.setattr(
        account_sync,
        "sync_integration",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("Yahoo não deve tentar sincronizar calendário")),
    )

    resultado = account_sync.sincronizar_conta(db, item, full=False)

    assert resultado["ok"] is True
    assert chamadas == [("mail", "medico@yahoo.com")]
    db.refresh(item)
    assert item.status == "connected"
    assert item.last_success_at is not None
    assert item.last_error_code is None


def test_yahoo_transient_provider_failure_keeps_connection_eligible(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.yahoo.transient@teste.local")
    item = _yahoo(db, user)
    monkeypatch.setattr(
        account_sync.yahoo_mail,
        "diagnose",
        lambda _cred: (_ for _ in ()).throw(YahooMailError("timeout do IMAP", status_code=503)),
    )

    resultado = account_sync.sincronizar_conta(db, item, full=False)

    assert resultado["ok"] is False
    assert resultado["reauth_required"] is False
    db.refresh(item)
    assert item.status == "connected"
    assert item.enabled is True
    assert item.last_error_code == "mail_provider_unavailable"


def test_yahoo_bad_app_password_marks_reauth_instead_of_silent_drop(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="sync.yahoo.reauth.runtime@teste.local")
    item = _yahoo(db, user)
    monkeypatch.setattr(
        account_sync.yahoo_mail,
        "diagnose",
        lambda _cred: (_ for _ in ()).throw(YahooMailError("senha recusada", status_code=401)),
    )

    resultado = account_sync.sincronizar_conta(db, item, full=False)

    assert resultado["reauth_required"] is True
    db.refresh(item)
    assert item.status == "reauth_required"
    assert item.enabled is True  # mantém a linha para Reconectar; não apaga/desliga em silêncio


def test_sync_live_route_works_for_mail_only_account(client, db, criar_usuario, monkeypatch):
    user, token = criar_usuario(email="sync.yahoo.route@teste.local")
    _subscribe(db, user.id)
    item = _yahoo(db, user)
    monkeypatch.setattr(account_sync.yahoo_mail, "diagnose", lambda _cred: {"ok": True})

    response = client.post(
        f"/api/agenda/integrations/{item.id}/sync-live?full=false",
        headers=_headers(token),
        json={},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert any(c["componente"] == "mail" and c["ok"] for c in payload["componentes"])


def test_sync_live_is_tenant_scoped(client, db, criar_usuario, monkeypatch):
    owner, _ = criar_usuario(email="sync.owner@teste.local")
    outro, token_outro = criar_usuario(email="sync.outro@teste.local")
    _subscribe(db, outro.id)
    item = _yahoo(db, owner)
    monkeypatch.setattr(account_sync.yahoo_mail, "diagnose", lambda _cred: {"ok": True})

    response = client.post(
        f"/api/agenda/integrations/{item.id}/sync-live",
        headers=_headers(token_outro),
        json={},
    )
    assert response.status_code == 404


def test_successful_oauth_callback_reissues_browser_session_cookie(
    client, db, criar_usuario, monkeypatch,
):
    """Mesmo se o cookie que iniciou o OAuth não voltar do provedor, o
    state de uso único permite restaurar SOMENTE a sessão do dono que iniciou
    o fluxo. O redirecionamento seguinte para o SPA não deve cair em /entrar."""
    user, _ = criar_usuario(email="oauth.session.recovery@teste.local")
    state = "state-oauth-seguro-teste"
    integration = CalendarIntegration(
        owner_id=user.id,
        provider="google_calendar",
        display_name="medico@gmail.com",
        external_account_id="google-sub-session",
        status="connected",
        enabled=True,
        contacts_enabled=False,
        capabilities={"read_appointments": True, "read_mail": True},
        sync_strategy="external_authoritative",
        configuration={"calendar_id": "primary"},
    )
    db.add(integration)
    db.flush()
    db.add(IntegrationOAuthState(
        owner_id=user.id,
        provider="google_calendar",
        state_digest=hashlib.sha256(state.encode()).hexdigest(),
        code_verifier_cipher=b"teste",
        request_data={},
        expires_at=datetime.now(timezone.utc),
        used_at=datetime.now(timezone.utc),
    ))
    db.commit()

    monkeypatch.setattr(agenda_integrada, "complete_oauth", lambda *_a, **_k: integration)
    monkeypatch.setattr(agenda_integrada, "sync_integration", lambda *_a, **_k: {})

    response = client.get(
        f"/api/agenda/oauth/google/callback?code=ok&state={state}",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "conta_conectada=google_calendar" in response.headers["location"]
    cookie = response.headers.get("set-cookie", "")
    assert "corvia_session=" in cookie
    assert "HttpOnly" in cookie


def test_failed_oauth_callback_never_becomes_session_recovery(client, db, criar_usuario):
    user, _ = criar_usuario(email="oauth.session.fail@teste.local")
    state = "state-falha-teste"
    db.add(IntegrationOAuthState(
        owner_id=user.id,
        provider="google_calendar",
        state_digest=hashlib.sha256(state.encode()).hexdigest(),
        code_verifier_cipher=b"teste",
        request_data={},
        expires_at=datetime.now(timezone.utc),
        used_at=datetime.now(timezone.utc),
    ))
    db.commit()

    response = client.get(
        f"/api/agenda/oauth/google/callback?error=access_denied&state={state}",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "conta_erro=" in response.headers["location"]
    assert "corvia_session=" not in response.headers.get("set-cookie", "")
