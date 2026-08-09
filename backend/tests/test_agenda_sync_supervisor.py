from types import SimpleNamespace

from app.services import agenda_sync_cli
from app.services.agenda_integrada.connectors import ConnectorError


class FakeDb:
    def __init__(self, item):
        self.item = item
        self.commits = 0
    def get(self, _model, _id):
        return self.item
    def commit(self):
        self.commits += 1


def integration(**overrides):
    data = dict(
        id=1,
        provider="google_calendar",
        display_name="titular@gmail.com",
        status="error",
        last_error_code="sync_failed",
        last_error_message="falhou",
        sync_mail=True,
        sync_calendar=True,
        contacts_enabled=False,
        capabilities={"read_mail": True},
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def test_transient_connector_error_remains_eligible_for_next_round():
    item = integration(status="error")
    db = FakeDb(item)
    exc = ConnectorError("oauth_refresh_provider_error", "Google temporariamente indisponível", retryable=True, status_code=503)

    agenda_sync_cli._registrar_falha(db, item.id, exc)

    assert item.status == "connected"
    assert item.last_error_code == "oauth_refresh_provider_error"
    assert db.commits == 1


def test_true_reauth_error_is_not_masked_as_transient():
    item = integration(status="connected")
    db = FakeDb(item)
    exc = ConnectorError("reauth_required", "Consentimento revogado", status_code=409)

    agenda_sync_cli._registrar_falha(db, item.id, exc)

    assert item.status == "reauth_required"
    assert item.last_error_code == "reauth_required"


def test_recoverable_statuses_include_previous_error_state():
    assert "connected" in agenda_sync_cli.ESTADOS_RECUPERAVEIS
    assert "error" in agenda_sync_cli.ESTADOS_RECUPERAVEIS
    assert "reauth_required" not in agenda_sync_cli.ESTADOS_RECUPERAVEIS


def test_mail_only_oauth_account_is_recognized_as_mail_capable():
    item = integration(sync_calendar=False, contacts_enabled=False, sync_mail=True)
    mail_aplicavel = bool(item.sync_mail and (item.capabilities or {}).get("read_mail"))
    calendario_aplicavel = bool(item.sync_calendar and item.status != "reauth_required")

    assert mail_aplicavel is True
    assert calendario_aplicavel is False
