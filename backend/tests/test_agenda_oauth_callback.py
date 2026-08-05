from urllib.parse import parse_qs, urlparse

from app.api import agenda_integrada
from app.services.agenda_integrada.connectors import ConnectorError


class _Integration:
    id = 91
    provider = "google_calendar"
    contacts_enabled = True
    last_error_code = None
    last_error_message = None


class _DB:
    def __init__(self, integration):
        self.integration = integration
        self.commits = 0

    def get(self, _model, _identifier):
        return self.integration

    def commit(self):
        self.commits += 1


def _query(response):
    return parse_qs(urlparse(response.headers["location"]).query)


def test_oauth_callback_runs_initial_calendar_and_contacts_sync(monkeypatch):
    integration = _Integration()
    db = _DB(integration)
    calls = []
    monkeypatch.setattr(agenda_integrada, "complete_oauth", lambda *_args, **_kwargs: integration)
    monkeypatch.setattr(
        agenda_integrada,
        "sync_integration",
        lambda _db, item, *, full: calls.append(("calendar", item.id, full)),
    )
    monkeypatch.setattr(
        agenda_integrada,
        "sync_contacts",
        lambda _db, item, *, full: calls.append(("contacts", item.id, full)),
    )

    response = agenda_integrada._oauth_callback("google_calendar", "code", "state", None, db)

    assert response.status_code == 303
    assert _query(response) == {"conta_conectada": ["google_calendar"], "sincronizacao": ["ok"]}
    assert calls == [("calendar", 91, True), ("contacts", 91, True)]


def test_oauth_callback_preserves_account_when_initial_sync_is_temporarily_unavailable(monkeypatch):
    integration = _Integration()
    db = _DB(integration)
    monkeypatch.setattr(agenda_integrada, "complete_oauth", lambda *_args, **_kwargs: integration)

    def fail_sync(*_args, **_kwargs):
        raise ConnectorError("provider_unavailable", "Provedor temporariamente indisponível.", retryable=True)

    monkeypatch.setattr(agenda_integrada, "sync_integration", fail_sync)

    response = agenda_integrada._oauth_callback("google_calendar", "code", "state", None, db)

    assert response.status_code == 303
    assert _query(response) == {"conta_conectada": ["google_calendar"], "sincronizacao": ["pendente"]}
    assert integration.last_error_code == "provider_unavailable"
    assert integration.last_error_message == "Provedor temporariamente indisponível."
    assert db.commits == 1
