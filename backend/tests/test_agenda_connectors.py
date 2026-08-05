from datetime import datetime, timezone

import httpx
import pytest

from app.models.agenda import CalendarOutboxEvent
from app.services.agenda_integrada.connectors import (
    ConnectorError,
    GoogleCalendarConnector,
    HomologationRequiredConnector,
    Microsoft365CalendarConnector,
    connector_catalog,
)
from app.services.agenda_integrada.domain import process_outbox_event


def test_catalog_does_not_claim_unverified_clinical_connectors():
    catalog = {item["provider"]: item for item in connector_catalog()}
    assert catalog["google_calendar"]["status"] == "adapter_available"
    assert catalog["microsoft_365"]["status"] == "adapter_available"
    assert catalog["feegow"]["status"] == "homologation_required"
    assert catalog["feegow"]["official_api"] is False
    assert catalog["feegow"]["capabilities"]["create_appointment"] is False


def test_feegow_diagnostic_performs_no_network_call():
    result = HomologationRequiredConnector("feegow").diagnose()
    assert result["ok"] is False
    assert result["code"] == "homologation_required"


def test_google_incremental_sync_maps_cancelled_and_preserves_sync_token():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "www.googleapis.com"
        assert request.url.params["syncToken"] == "cursor-1"
        return httpx.Response(200, json={
            "items": [
                {
                    "id": "evt-1", "status": "confirmed", "summary": "Consulta",
                    "start": {"dateTime": "2026-08-05T10:00:00-03:00"},
                    "end": {"dateTime": "2026-08-05T10:30:00-03:00"},
                    "updated": "2026-08-05T12:00:00Z", "etag": '"v1"',
                },
                {"id": "evt-2", "status": "cancelled"},
            ],
            "nextSyncToken": "cursor-2",
        })

    connector = GoogleCalendarConnector(
        {"access_token": "token"}, {"calendar_id": "primary"},
        transport=httpx.MockTransport(handler),
    )
    result = connector.pull(
        cursor="cursor-1",
        start=datetime(2026, 8, 1, tzinfo=timezone.utc),
        end=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )
    assert result.cursor == "cursor-2"
    assert [item.status for item in result.appointments] == ["confirmed", "cancelled"]


def test_google_create_uses_deterministic_provider_id_for_idempotency():
    seen_ids = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = __import__("json").loads(request.content)
        seen_ids.append(body["id"])
        return httpx.Response(200, json={"id": body["id"], "etag": '"v1"'})

    connector = GoogleCalendarConnector(
        {"access_token": "token"}, {}, transport=httpx.MockTransport(handler)
    )
    payload = {
        "appointment_id": 7,
        "starts_at": "2026-08-05T13:00:00+00:00",
        "ends_at": "2026-08-05T13:30:00+00:00",
        "timezone": "America/Sao_Paulo",
    }
    connector.create(payload, idempotency_key="same-operation")
    connector.create(payload, idempotency_key="same-operation")
    assert len(seen_ids[0]) == 32
    assert seen_ids[0] == seen_ids[1]


def test_microsoft_create_sends_transaction_id():
    def handler(request: httpx.Request) -> httpx.Response:
        body = __import__("json").loads(request.content)
        assert body["transactionId"] == "agenda:1:2:3:create"
        return httpx.Response(201, json={"id": "external-1", "changeKey": "v1"})

    connector = Microsoft365CalendarConnector(
        {"access_token": "token"}, {}, transport=httpx.MockTransport(handler)
    )
    result = connector.create({
        "starts_at": "2026-08-05T13:00:00+00:00",
        "ends_at": "2026-08-05T13:30:00+00:00",
        "timezone": "UTC",
    }, idempotency_key="agenda:1:2:3:create")
    assert result["id"] == "external-1"


def test_microsoft_rejects_cursor_outside_graph_host():
    connector = Microsoft365CalendarConnector({"access_token": "token"}, {})
    with pytest.raises(ConnectorError, match="Cursor Microsoft inválido"):
        connector.pull(
            cursor="https://example.invalid/steal-token",
            start=datetime.now(timezone.utc),
            end=datetime.now(timezone.utc),
        )


def test_processed_outbox_event_is_idempotent_without_calling_provider():
    event = CalendarOutboxEvent(id=91, appointment_id=17, status="processed")
    result = process_outbox_event(None, event)  # type: ignore[arg-type]
    assert result == {"id": 91, "status": "processed", "appointment_id": 17}
