"""Auditoria AUTH/SESSION → OAUTH (issue #52, subfase 2): state/PKCE, troca de
código, account-linking, renovação e revogação, exercitando o fluxo real
(`begin_oauth`/`complete_oauth`/`ensure_fresh_credentials`/
`disconnect_integration`) contra o banco, não só a rota de callback mockada
(já coberta por `test_agenda_oauth_callback.py`).

Nenhum destes testes fala com Google/Microsoft de verdade — toda chamada
HTTP de troca/renovação/revogação de token é interceptada via
`monkeypatch` de `httpx.post`/`httpx.get` no módulo
`app.services.agenda_integrada.external_accounts`, nunca sai para a rede.
"""
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from app.core.config import settings
from app.models.agenda import CalendarIntegration, IntegrationOAuthState
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.domain import integration_credentials
from app.services.agenda_integrada.external_accounts import (
    begin_oauth,
    complete_oauth,
    disconnect_integration,
    ensure_fresh_credentials,
)


@pytest.fixture
def google_oauth_configured(monkeypatch):
    monkeypatch.setattr(settings, "google_oauth_client_id", "id-teste")
    monkeypatch.setattr(settings, "google_oauth_client_secret", "segredo-teste")


def _token_response(**overrides):
    body = {
        "access_token": "access-novo",
        "refresh_token": "refresh-novo",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "openid email profile",
    }
    body.update(overrides)
    return httpx.Response(200, json=body)


def _profile_response(email="medico@gmail.com", sub="google-sub-1"):
    return httpx.Response(200, json={"sub": sub, "email": email, "name": "Dr. Teste"})


def _mock_token_and_profile(monkeypatch, *, token_response=None, profile_response=None):
    """Substitui exatamente as duas chamadas de rede de `complete_oauth`:
    POST na troca de código por token, GET no userinfo do provedor."""
    calls: list[tuple[str, str]] = []

    def _post(url, data=None, headers=None, timeout=None):
        calls.append(("POST", url))
        if url.endswith("/revoke"):
            return httpx.Response(200)
        assert "code_verifier" in data  # PKCE sempre enviado na troca
        if token_response is not None:
            return token_response
        return _token_response()

    def _get(url, headers=None, timeout=None):
        calls.append(("GET", url))
        assert headers["Authorization"].startswith("Bearer ")
        if profile_response is not None:
            return profile_response
        return _profile_response()

    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post", _post
    )
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.get", _get
    )
    return calls


# --- state/PKCE ---------------------------------------------------------


def test_begin_oauth_generates_single_use_state_with_pkce_challenge(
    db, criar_usuario, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.begin@teste.local")
    url = begin_oauth(
        db, owner_id=user.id, provider="google_calendar",
        calendar_write=False, contacts=True,
    )
    assert "code_challenge=" in url
    assert "code_challenge_method=S256" in url
    assert "state=" in url

    record = db.query(IntegrationOAuthState).filter(
        IntegrationOAuthState.owner_id == user.id
    ).one()
    # O valor público do state nunca é persistido em claro — só o digest.
    assert record.state_digest != url.split("state=")[1].split("&")[0]
    assert len(record.state_digest) == 64  # sha256 hex
    assert record.used_at is None
    assert record.expires_at > datetime.now(timezone.utc)


def test_complete_oauth_rejects_state_reuse_after_successful_exchange(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    """O state é de uso único — replay do mesmo state (ex.: usuário aperta
    voltar/atualizar no navegador após o callback já ter sido processado)
    não pode trocar um segundo código nem reabrir a janela PKCE."""
    user, _ = criar_usuario(email="oauth.replay@teste.local")
    url = begin_oauth(
        db, owner_id=user.id, provider="google_calendar",
        calendar_write=False, contacts=False,
    )
    state = url.split("state=")[1].split("&")[0]
    _mock_token_and_profile(monkeypatch)

    complete_oauth(db, provider="google_calendar", code="codigo-1", state=state)

    with pytest.raises(ConnectorError) as exc:
        complete_oauth(db, provider="google_calendar", code="codigo-2", state=state)
    assert exc.value.code == "invalid_oauth_state"
    assert exc.value.status_code == 400


def test_complete_oauth_rejects_expired_state(db, criar_usuario, google_oauth_configured):
    user, _ = criar_usuario(email="oauth.expirado@teste.local")
    record = IntegrationOAuthState(
        owner_id=user.id, provider="google_calendar",
        state_digest="a" * 64, code_verifier_cipher=b"\x00",
        request_data={}, expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    db.add(record)
    db.commit()

    with pytest.raises(ConnectorError) as exc:
        complete_oauth(db, provider="google_calendar", code="codigo", state="a" * 64)
    assert exc.value.code == "invalid_oauth_state"


def test_complete_oauth_rejects_state_issued_for_a_different_provider(
    db, criar_usuario, google_oauth_configured
):
    """State válido de um provedor não pode ser reaproveitado no callback
    de outro — a consulta de consumo filtra por (provider, digest) juntos."""
    user, _ = criar_usuario(email="oauth.cross-provider@teste.local")
    url = begin_oauth(
        db, owner_id=user.id, provider="google_calendar",
        calendar_write=False, contacts=False,
    )
    state = url.split("state=")[1].split("&")[0]

    with pytest.raises(ConnectorError) as exc:
        complete_oauth(db, provider="microsoft_365", code="codigo", state=state)
    assert exc.value.code == "invalid_oauth_state"


def test_complete_oauth_rejects_unknown_state(db, google_oauth_configured):
    with pytest.raises(ConnectorError) as exc:
        complete_oauth(db, provider="google_calendar", code="codigo", state="nao-existe")
    assert exc.value.code == "invalid_oauth_state"


# --- account-linking -----------------------------------------------------


def test_complete_oauth_creates_new_integration_on_first_connection(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.novo@teste.local")
    url = begin_oauth(
        db, owner_id=user.id, provider="google_calendar",
        calendar_write=False, contacts=False,
    )
    state = url.split("state=")[1].split("&")[0]
    _mock_token_and_profile(monkeypatch, profile_response=_profile_response(
        email="conta@gmail.com", sub="sub-fixo-1",
    ))

    integration = complete_oauth(db, provider="google_calendar", code="codigo", state=state)

    assert integration.owner_id == user.id
    assert integration.external_account_id == "sub-fixo-1"
    assert integration.status == "connected"
    assert integration.enabled is True
    total = db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == user.id
    ).count()
    assert total == 1


def test_complete_oauth_relinks_same_external_account_without_duplicating(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    """Reconectar a MESMA conta Google (mesmo `sub`) — ex.: token revogado e
    o médico autoriza de novo — atualiza a integração existente em vez de
    criar uma segunda linha duplicada para o mesmo owner+provider+conta."""
    user, _ = criar_usuario(email="oauth.relink@teste.local")

    def _fluxo_completo(code):
        url = begin_oauth(
            db, owner_id=user.id, provider="google_calendar",
            calendar_write=False, contacts=False,
        )
        state = url.split("state=")[1].split("&")[0]
        return complete_oauth(db, provider="google_calendar", code=code, state=state)

    _mock_token_and_profile(monkeypatch, profile_response=_profile_response(
        email="conta@gmail.com", sub="sub-estavel",
    ))
    primeira = _fluxo_completo("codigo-1")
    primeiro_id = primeira.id

    disconnect_integration(db, primeira)
    assert primeira.status == "disconnected"

    _mock_token_and_profile(monkeypatch, profile_response=_profile_response(
        email="conta@gmail.com", sub="sub-estavel",
    ))
    segunda = _fluxo_completo("codigo-2")

    assert segunda.id == primeiro_id  # mesma linha, não duplicada
    assert segunda.status == "connected"
    assert segunda.enabled is True
    total = db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == user.id,
        CalendarIntegration.provider == "google_calendar",
    ).count()
    assert total == 1


def test_complete_oauth_does_not_link_different_owners_to_same_row(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    """A mesma conta Google conectada por dois médicos diferentes (cenário
    real: consultório compartilhado) gera DUAS integrações isoladas, uma
    por owner — nunca uma sobrescreve o dono da outra."""
    user_a, _ = criar_usuario(email="oauth.owner-a@teste.local")
    user_b, _ = criar_usuario(email="oauth.owner-b@teste.local")

    def _conectar(user, code):
        url = begin_oauth(
            db, owner_id=user.id, provider="google_calendar",
            calendar_write=False, contacts=False,
        )
        state = url.split("state=")[1].split("&")[0]
        return complete_oauth(db, provider="google_calendar", code=code, state=state)

    _mock_token_and_profile(monkeypatch, profile_response=_profile_response(
        email="compartilhada@gmail.com", sub="sub-compartilhado",
    ))
    integ_a = _conectar(user_a, "codigo-a")
    _mock_token_and_profile(monkeypatch, profile_response=_profile_response(
        email="compartilhada@gmail.com", sub="sub-compartilhado",
    ))
    integ_b = _conectar(user_b, "codigo-b")

    assert integ_a.id != integ_b.id
    assert integ_a.owner_id == user_a.id
    assert integ_b.owner_id == user_b.id


# --- erros na troca de código --------------------------------------------


def test_complete_oauth_surfaces_provider_rejection_without_crashing(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.rejeitado@teste.local")
    url = begin_oauth(
        db, owner_id=user.id, provider="google_calendar",
        calendar_write=False, contacts=False,
    )
    state = url.split("state=")[1].split("&")[0]
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: httpx.Response(400, json={"error": "invalid_grant"}),
    )

    with pytest.raises(ConnectorError) as exc:
        complete_oauth(db, provider="google_calendar", code="codigo-invalido", state=state)
    assert exc.value.code == "oauth_exchange_error"

    # O state já foi consumido mesmo com a falha subsequente — não pode ser
    # reaproveitado numa segunda tentativa (evita reenvio silencioso do
    # mesmo code_verifier após um code já invalidado pelo provedor).
    with pytest.raises(ConnectorError) as exc2:
        complete_oauth(db, provider="google_calendar", code="codigo-novo", state=state)
    assert exc2.value.code == "invalid_oauth_state"


def test_complete_oauth_requires_offline_access_refresh_token(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    """Google só concede refresh_token com access_type=offline; se o
    provedor devolver token sem ele (ex.: reconsentimento incompleto), a
    conta não pode ficar 'conectada' sem forma de renovar depois."""
    user, _ = criar_usuario(email="oauth.sem-refresh@teste.local")
    url = begin_oauth(
        db, owner_id=user.id, provider="google_calendar",
        calendar_write=False, contacts=False,
    )
    state = url.split("state=")[1].split("&")[0]
    _mock_token_and_profile(
        monkeypatch,
        token_response=_token_response(refresh_token=""),
    )

    with pytest.raises(ConnectorError) as exc:
        complete_oauth(db, provider="google_calendar", code="codigo", state=state)
    assert exc.value.code == "oauth_refresh_token_missing"


# --- renovação (refresh token) -------------------------------------------


def _integracao_conectada(db, user, *, expira_em, refresh_token="refresh-atual"):
    integration = CalendarIntegration(
        owner_id=user.id, provider="google_calendar", display_name="conta@gmail.com",
        external_account_id="sub-refresh", sync_strategy="external_authoritative",
        enabled=True, status="connected", contacts_enabled=False,
        configuration={"calendar_id": "primary"},
        capabilities={"read_appointments": True},
    )
    db.add(integration)
    db.flush()
    from app.services.agenda_integrada.domain import store_integration_credentials
    store_integration_credentials(integration, {
        "access_token": "access-atual", "refresh_token": refresh_token,
        "expires_at": expira_em.isoformat(), "token_type": "Bearer", "scope": "",
    })
    db.commit()
    return integration


def test_ensure_fresh_credentials_skips_network_when_token_still_valid(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.token-valido@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    chamou_rede = []
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: chamou_rede.append(1) or pytest.fail("não deveria chamar a rede"),
    )

    creds = ensure_fresh_credentials(db, integration)
    assert creds["access_token"] == "access-atual"
    assert not chamou_rede


def test_ensure_fresh_credentials_renews_when_close_to_expiry(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.renovar@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: _token_response(access_token="access-renovado"),
    )

    creds = ensure_fresh_credentials(db, integration)
    assert creds["access_token"] == "access-renovado"
    assert integration.status == "connected"
    persistido = integration_credentials(integration)
    assert persistido["access_token"] == "access-renovado"


def test_ensure_fresh_credentials_marks_reauth_required_on_invalid_grant(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    """Refresh token revogado pelo usuário direto no provedor (ou expirado
    por inatividade) — o CorvIA não deve tentar de novo sozinho, tem que
    marcar para reconexão manual, sem derrubar a integração em silêncio."""
    user, _ = criar_usuario(email="oauth.reauth@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: httpx.Response(400, json={"error": "invalid_grant"}),
    )

    with pytest.raises(ConnectorError) as exc:
        ensure_fresh_credentials(db, integration)
    assert exc.value.code == "reauth_required"
    assert integration.status == "reauth_required"
    assert integration.last_error_code == "reauth_required"
    # Credencial antiga (ainda que expirada) não é apagada — dá para
    # auditar depois, e uma reconexão bem-sucedida sobrescreve normalmente.
    assert integration_credentials(integration)["access_token"] == "access-atual"


def test_ensure_fresh_credentials_treats_provider_5xx_as_retryable(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.5xx@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: httpx.Response(503, json={}),
    )

    with pytest.raises(ConnectorError) as exc:
        ensure_fresh_credentials(db, integration)
    assert exc.value.code == "oauth_refresh_provider_error"
    assert exc.value.retryable is True
    # 5xx não é falha de autorização — não marca reauth_required.
    assert integration.status == "connected"


def test_ensure_fresh_credentials_without_refresh_token_requires_reauth(
    db, criar_usuario, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.sem-refresh-armazenado@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) - timedelta(minutes=5),
        refresh_token="",
    )
    with pytest.raises(ConnectorError) as exc:
        ensure_fresh_credentials(db, integration)
    assert exc.value.code == "reauth_required"


def test_ensure_fresh_credentials_never_leaks_tokens_via_exception_message(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.sem-vazamento@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) - timedelta(minutes=5),
        refresh_token="refresh-secreto-nao-pode-vazar",
    )
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: httpx.Response(400, json={"error": "invalid_grant"}),
    )
    with pytest.raises(ConnectorError) as exc:
        ensure_fresh_credentials(db, integration)
    assert "refresh-secreto-nao-pode-vazar" not in str(exc.value)
    assert integration.last_error_message is not None
    assert "refresh-secreto-nao-pode-vazar" not in integration.last_error_message


# --- revogação -------------------------------------------------------------


def test_disconnect_integration_revokes_token_at_provider_and_clears_credentials(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    user, _ = criar_usuario(email="oauth.desconectar@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    chamadas = []

    def _post(url, data=None, headers=None, timeout=None):
        chamadas.append((url, data))
        return httpx.Response(200)

    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post", _post
    )

    disconnect_integration(db, integration)

    assert len(chamadas) == 1
    assert chamadas[0][0] == "https://oauth2.googleapis.com/revoke"
    assert chamadas[0][1]["token"] == "access-atual"
    assert integration.status == "disconnected"
    assert integration.enabled is False
    assert integration.credentials_cipher is None
    assert integration_credentials(integration) == {}


def test_disconnect_integration_succeeds_even_if_provider_revoke_call_fails(
    db, criar_usuario, monkeypatch, google_oauth_configured
):
    """Se o Google estiver fora do ar no momento da desconexão, o CorvIA
    ainda assim limpa a credencial local — não deixa a conta 'presa'
    conectada só porque a chamada de revogação (best-effort) falhou."""
    user, _ = criar_usuario(email="oauth.desconectar-falha@teste.local")
    integration = _integracao_conectada(
        db, user, expira_em=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    monkeypatch.setattr(
        "app.services.agenda_integrada.external_accounts.httpx.post",
        lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("recusado")),
    )

    disconnect_integration(db, integration)

    assert integration.status == "disconnected"
    assert integration.credentials_cipher is None


def test_begin_oauth_rejects_unconfigured_provider(db, criar_usuario, monkeypatch):
    monkeypatch.setattr(settings, "google_oauth_client_id", "")
    monkeypatch.setattr(settings, "google_oauth_client_secret", "")
    user, _ = criar_usuario(email="oauth.nao-configurado@teste.local")
    with pytest.raises(ConnectorError) as exc:
        begin_oauth(
            db, owner_id=user.id, provider="google_calendar",
            calendar_write=False, contacts=False,
        )
    assert exc.value.code == "oauth_not_configured"
    assert exc.value.status_code == 503
