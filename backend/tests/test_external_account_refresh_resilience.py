from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.services import external_mail
from app.services.agenda_integrada import external_accounts
from app.services.agenda_integrada.connectors import ConnectorError


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {}
    def json(self):
        return self._body


class FakeDb:
    def __init__(self):
        self.commits = 0
    def commit(self):
        self.commits += 1


def oauth_credentials(*, expires_in_seconds=3600):
    return {
        "access_token": "old-access",
        "refresh_token": "refresh-token",
        "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).isoformat(),
        "token_type": "Bearer",
        "scope": "Mail.ReadWrite Mail.Send offline_access",
    }


def test_force_refresh_renews_even_when_access_token_not_expiring(monkeypatch):
    integration = SimpleNamespace(provider="microsoft_365", status="connected", last_error_code=None, last_error_message=None)
    db = FakeDb()
    stored = []
    monkeypatch.setattr(external_accounts, "integration_credentials", lambda _: oauth_credentials(expires_in_seconds=3600))
    monkeypatch.setattr(external_accounts, "store_integration_credentials", lambda _, credentials: stored.append(credentials))
    monkeypatch.setattr(external_accounts.httpx, "post", lambda *a, **k: FakeResponse(200, {
        "access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600,
        "scope": "Mail.ReadWrite Mail.Send offline_access",
    }))
    monkeypatch.setattr(external_accounts.settings, "microsoft_oauth_client_id", "client")
    monkeypatch.setattr(external_accounts.settings, "microsoft_oauth_client_secret", "secret")

    result = external_accounts.ensure_fresh_credentials(db, integration, force=True)

    assert result["access_token"] == "new-access"
    assert stored and stored[0]["refresh_token"] == "new-refresh"
    assert integration.status == "connected"
    assert integration.last_error_code is None


def test_transient_refresh_failure_does_not_mark_reauth_required(monkeypatch):
    integration = SimpleNamespace(provider="google_calendar", status="connected", last_error_code=None, last_error_message=None)
    db = FakeDb()
    monkeypatch.setattr(external_accounts, "integration_credentials", lambda _: oauth_credentials(expires_in_seconds=-10))
    monkeypatch.setattr(external_accounts.httpx, "post", lambda *a, **k: FakeResponse(503, {"error": "temporarily_unavailable"}))
    monkeypatch.setattr(external_accounts.settings, "google_oauth_client_id", "client")
    monkeypatch.setattr(external_accounts.settings, "google_oauth_client_secret", "secret")

    with pytest.raises(ConnectorError) as exc:
        external_accounts.ensure_fresh_credentials(db, integration)

    assert exc.value.status_code == 503
    assert integration.status == "connected"
    assert integration.last_error_code is None


def test_invalid_grant_marks_true_reauthentication_required(monkeypatch):
    integration = SimpleNamespace(provider="google_calendar", status="connected", last_error_code=None, last_error_message=None)
    db = FakeDb()
    monkeypatch.setattr(external_accounts, "integration_credentials", lambda _: oauth_credentials(expires_in_seconds=-10))
    monkeypatch.setattr(external_accounts.httpx, "post", lambda *a, **k: FakeResponse(400, {"error": "invalid_grant"}))
    monkeypatch.setattr(external_accounts.settings, "google_oauth_client_id", "client")
    monkeypatch.setattr(external_accounts.settings, "google_oauth_client_secret", "secret")

    with pytest.raises(ConnectorError) as exc:
        external_accounts.ensure_fresh_credentials(db, integration)

    assert exc.value.status_code == 409
    assert integration.status == "reauth_required"
    assert integration.last_error_code == "reauth_required"
    assert db.commits == 1


def test_mail_request_retries_once_after_early_401(monkeypatch):
    integration = SimpleNamespace(provider="google_calendar")
    refresh_calls = []

    def credentials(_db, _integration, *, force=False):
        refresh_calls.append(force)
        return {"access_token": "new" if force else "old"}

    responses = [FakeResponse(401), FakeResponse(200)]
    seen_auth = []

    def request(method, url, headers, timeout, **kwargs):
        seen_auth.append(headers["Authorization"])
        return responses.pop(0)

    monkeypatch.setattr(external_mail, "ensure_fresh_credentials", credentials)
    monkeypatch.setattr(external_mail.httpx, "request", request)

    result = external_mail._request(None, integration, "GET", "https://example.test/messages")

    assert result.status_code == 200
    assert refresh_calls == [False, True]
    assert seen_auth == ["Bearer old", "Bearer new"]


def test_mail_request_second_401_requires_reconnection(monkeypatch):
    integration = SimpleNamespace(provider="microsoft_365")
    monkeypatch.setattr(
        external_mail,
        "ensure_fresh_credentials",
        lambda _db, _integration, *, force=False: {"access_token": "refreshed" if force else "old"},
    )
    monkeypatch.setattr(external_mail.httpx, "request", lambda *a, **k: FakeResponse(401))

    with pytest.raises(external_mail.ExternalMailError) as exc:
        external_mail._request(None, integration, "GET", "https://example.test/messages")

    assert exc.value.status_code == 409
