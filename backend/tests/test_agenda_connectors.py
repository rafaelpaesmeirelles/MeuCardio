from datetime import datetime, timedelta, timezone

import httpx
import pytest
from app.models.agenda import CalendarIntegration, CalendarOutboxEvent
from app.services.agenda_integrada.apple_dav import AppleDavClient, parse_icalendar, parse_vcard
from app.services.agenda_integrada.connectors import (
    ConnectorError,
    GoogleCalendarConnector,
    HomologationRequiredConnector,
    Microsoft365CalendarConnector,
    connector_catalog,
)
from app.services.agenda_integrada.contacts import GoogleContacts, MicrosoftContacts
from app.services.agenda_integrada.domain import (
    process_outbox_event,
    store_integration_credentials,
    sync_integration,
)


def test_catalog_does_not_claim_unverified_clinical_connectors():
    catalog = {item["provider"]: item for item in connector_catalog()}
    assert catalog["google_calendar"]["status"] == "adapter_available"
    assert catalog["microsoft_365"]["status"] == "adapter_available"
    assert catalog["apple_icloud"]["status"] == "adapter_available"
    assert catalog["apple_icloud"]["capabilities"]["create_appointment"] is False
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


def test_sync_preserves_mail_capability_granted_by_oauth_scope(db, criar_usuario):
    """Regressão: `sync_integration` sobrescrevia `capabilities` inteiro com o
    `ConnectorCapabilities` do conector de calendário — que não tem (e não deve
    ganhar) campo de e-mail — apagando `read_mail`/`send_mail` concedidos pelo
    escopo OAuth a cada sincronização. Achado ao vivo: conta Google conectada
    com Gmail sumia da caixa de e-mail unificada depois do 1º sync."""
    user, _ = criar_usuario(email="agenda.sync.mail-capability@teste.local")
    integration = CalendarIntegration(
        owner_id=user.id, provider="google_calendar", display_name="teste@gmail.com",
        external_account_id="ext-1", sync_strategy="external_authoritative",
        enabled=True, status="connected", contacts_enabled=True,
        configuration={"calendar_id": "primary"},
        # Estado pós-OAuth: complete_oauth() grava isto com base no escopo
        # concedido — mail=True foi pedido e o Google concedeu.
        capabilities={"read_appointments": True, "read_mail": True, "send_mail": True},
    )
    db.add(integration)
    db.flush()
    store_integration_credentials(integration, {
        "access_token": "token", "refresh_token": "refresh",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
    })
    db.commit()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": [], "nextSyncToken": "cursor-1"})

    sync_integration(db, integration, transport=httpx.MockTransport(handler))

    assert integration.capabilities["read_mail"] is True
    assert integration.capabilities["send_mail"] is True
    # As capacidades de calendário do conector continuam vindo do conector,
    # não congeladas do valor inicial que o teste montou.
    assert integration.capabilities["read_appointments"] is True
    assert integration.capabilities["create_appointment"] is True  # do conector, não do teste


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


def test_google_contacts_maps_people_and_preserves_sync_token():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "people.googleapis.com"
        return httpx.Response(200, json={
            "connections": [{
                "resourceName": "people/1", "etag": "v1",
                "names": [{"displayName": "Dra. Ana"}],
                "emailAddresses": [{"value": "ana@example.com"}],
                "phoneNumbers": [{"value": "+5511999999999"}],
                "organizations": [{"name": "Clínica"}],
            }],
            "nextSyncToken": "contacts-cursor-2",
        })

    result = GoogleContacts("token", transport=httpx.MockTransport(handler)).pull(None)
    assert result.cursor == "contacts-cursor-2"
    assert result.contacts[0].display_name == "Dra. Ana"
    assert result.contacts[0].emails == ["ana@example.com"]


def test_microsoft_contacts_rejects_pagination_outside_graph():
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"value": [], "@odata.nextLink": "https://example.invalid/token"})

    connector = MicrosoftContacts("token", transport=httpx.MockTransport(handler))
    with pytest.raises(ConnectorError, match="Paginação Microsoft inválida"):
        connector.pull(None)
    assert calls == 1


def test_apple_vcard_and_calendar_parsers_unfold_records():
    contact = parse_vcard(
        "BEGIN:VCARD\r\nUID:abc\r\nFN:Dra. Ana\r\nEMAIL:ana@icloud.com\r\nTEL:+5511\r\nORG:Corvia;Cardio\r\nEND:VCARD",
        "fallback",
    )
    events = parse_icalendar(
        "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:event-1\r\nDTSTART:20260805T130000Z\r\nDTEND:20260805T133000Z\r\nSUMMARY:Consulta\r\nEND:VEVENT\r\nEND:VCALENDAR",
        "fallback",
    )
    assert contact["emails"] == ["ana@icloud.com"]
    assert contact["organization"] == "Corvia · Cardio"
    assert events[0]["id"] == "event-1"
    assert events[0]["starts_at"] == "2026-08-05T13:00:00+00:00"


def test_apple_dav_follows_partition_redirect_correctly():
    """Bug real reportado pelo Rafael em 07/08/2026: conectar Apple falhava
    com HTTP 502 mesmo com credenciais corretas. Reproduzido sem credencial
    nenhuma, simulando o comportamento real do iCloud — `caldav.icloud.com`
    redireciona (301) para um servidor de partição do usuário
    (`pXX-caldav.icloud.com`), e as próximas descobertas (principal →
    calendar-home-set → coleções) precisam resolver os hrefs relativos
    contra ESSE host, não contra o host genérico original. O bug estava em
    `_discover_home`/`_collections` resolvendo sempre contra a URL de
    entrada, nunca contra a URL que de fato respondeu — quebra em qualquer
    conta real da Apple, não só com credencial errada."""

    def handler(request: httpx.Request) -> httpx.Response:
        host, path = request.url.host, request.url.path
        if host == "caldav.icloud.com" and path == "/.well-known/caldav":
            return httpx.Response(301, headers={"location": "https://p01-caldav.icloud.com/.well-known/caldav"})
        if host == "p01-caldav.icloud.com" and path == "/.well-known/caldav":
            return httpx.Response(207, content=(
                '<?xml version="1.0"?><d:multistatus xmlns:d="DAV:"><d:response>'
                '<d:href>/.well-known/caldav</d:href><d:propstat><d:prop>'
                '<d:current-user-principal><d:href>/123456/principal/</d:href></d:current-user-principal>'
                '</d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propstat></d:response></d:multistatus>'
            ).encode())
        if host == "p01-caldav.icloud.com" and path == "/123456/principal/":
            return httpx.Response(207, content=(
                '<?xml version="1.0"?><d:multistatus xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">'
                '<d:response><d:href>/123456/principal/</d:href><d:propstat><d:prop>'
                '<c:calendar-home-set><d:href>/123456/calendars/</d:href></c:calendar-home-set>'
                '</d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propstat></d:response></d:multistatus>'
            ).encode())
        if host == "p01-caldav.icloud.com" and path == "/123456/calendars/":
            return httpx.Response(207, content=(
                '<?xml version="1.0"?><d:multistatus xmlns:d="DAV:"><d:response>'
                '<d:href>/123456/calendars/home/</d:href><d:propstat><d:prop><d:resourcetype>'
                '<d:collection/><cal:calendar xmlns:cal="urn:ietf:params:xml:ns:caldav"/></d:resourcetype>'
                '<d:displayname>Home</d:displayname></d:prop><d:status>HTTP/1.1 200 OK</d:status>'
                '</d:propstat></d:response></d:multistatus>'
            ).encode())
        return httpx.Response(404)  # pragma: no cover - qualquer host/caminho fora do esperado é falha do teste

    client = AppleDavClient("teste@icloud.com", "abcd-efgh-ijkl-mnop", transport=httpx.MockTransport(handler))
    calendars = client.calendars()
    assert calendars == ["https://p01-caldav.icloud.com/123456/calendars/home/"]
