"""Contratos e adaptadores oficiais da Agenda Integrada.

Somente URLs documentadas e fixas podem ser chamadas. Feegow e os demais
PMS/PEP ficam no catálogo de homologação enquanto não houver documentação
oficial verificável; não existe endpoint configurável pelo usuário e, assim,
o módulo também não introduz SSRF.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Protocol
from urllib.parse import quote

import httpx


@dataclass(frozen=True)
class ConnectorCapabilities:
    read_appointments: bool = False
    incremental_sync: bool = False
    create_appointment: bool = False
    reschedule_appointment: bool = False
    cancel_appointment: bool = False
    read_availability: bool = False
    search_patient: bool = False
    create_patient: bool = False
    webhooks: bool = False
    read_contacts: bool = False


@dataclass(frozen=True)
class ExternalAppointment:
    external_id: str
    starts_at: str | None
    ends_at: str | None
    status: str
    title: str | None = None
    description: str | None = None
    location: str | None = None
    external_updated_at: str | None = None
    version: str | None = None
    practitioner_external_id: str = "default"
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class PullResult:
    appointments: list[ExternalAppointment]
    cursor: str | None
    full_resync_required: bool = False


class ConnectorError(RuntimeError):
    def __init__(self, code: str, message: str, *, retryable: bool = False, status_code: int = 502):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.status_code = status_code


class CalendarConnector(Protocol):
    provider: str
    capabilities: ConnectorCapabilities

    def diagnose(self) -> dict[str, Any]: ...
    def pull(self, *, cursor: str | None, start: datetime, end: datetime) -> PullResult: ...
    def create(self, payload: dict[str, Any], *, idempotency_key: str) -> dict[str, Any]: ...
    def reschedule(self, external_id: str, payload: dict[str, Any], *, version: str | None) -> dict[str, Any]: ...
    def cancel(self, external_id: str, *, reason: str | None, version: str | None) -> dict[str, Any]: ...


def _safe_json(response: httpx.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        body = {}
    return body if isinstance(body, dict) else {}


def _raise_provider(response: httpx.Response) -> None:
    if response.is_success:
        return
    body = _safe_json(response)
    retryable = response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}
    if response.status_code == 401:
        code = "reauth_required"
    elif response.status_code == 403:
        code = "permission_denied"
    elif response.status_code == 404:
        code = "external_not_found"
    elif response.status_code in {409, 412}:
        code = "external_conflict"
    elif response.status_code == 429:
        code = "rate_limited"
    else:
        code = "provider_error"
    detail = body.get("error") or body.get("message") or f"HTTP {response.status_code}"
    if isinstance(detail, dict):
        detail = detail.get("message") or detail.get("status") or code
    raise ConnectorError(code, str(detail)[:500], retryable=retryable, status_code=502)


class _HttpConnector:
    timeout = httpx.Timeout(15.0, connect=5.0)

    def __init__(self, credentials: dict[str, Any], configuration: dict[str, Any], transport=None):
        self.credentials = credentials
        self.configuration = configuration
        self.client = httpx.Client(timeout=self.timeout, transport=transport, follow_redirects=False)

    @property
    def token(self) -> str:
        token = str(self.credentials.get("access_token") or "").strip()
        if not token:
            raise ConnectorError("reauth_required", "Token OAuth ausente.", status_code=409)
        return token

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}


class GoogleCalendarConnector(_HttpConnector):
    provider = "google_calendar"
    capabilities = ConnectorCapabilities(
        read_appointments=True,
        incremental_sync=True,
        create_appointment=True,
        reschedule_appointment=True,
        cancel_appointment=True,
        webhooks=True,
        read_contacts=True,
    )
    base_url = "https://www.googleapis.com/calendar/v3"

    @property
    def calendar_id(self) -> str:
        return str(self.configuration.get("calendar_id") or "primary")

    def _calendar_url(self, suffix: str = "") -> str:
        cid = quote(self.calendar_id, safe="")
        return f"{self.base_url}/calendars/{cid}{suffix}"

    def diagnose(self) -> dict[str, Any]:
        response = self.client.get(self._calendar_url(), headers=self.headers)
        _raise_provider(response)
        body = _safe_json(response)
        return {
            "ok": True,
            "provider": self.provider,
            "calendar_id": body.get("id") or self.calendar_id,
            "timezone": body.get("timeZone"),
            "capabilities": asdict(self.capabilities),
        }

    def pull(self, *, cursor: str | None, start: datetime, end: datetime) -> PullResult:
        params: dict[str, Any] = {
            "maxResults": 250,
            "singleEvents": "true",
            "showDeleted": "true",
        }
        if cursor:
            params["syncToken"] = cursor
        else:
            params["timeMin"] = start.isoformat()
            params["timeMax"] = end.isoformat()

        events: list[ExternalAppointment] = []
        while True:
            response = self.client.get(self._calendar_url("/events"), headers=self.headers, params=params)
            if response.status_code == 410:
                return PullResult([], None, full_resync_required=True)
            _raise_provider(response)
            body = _safe_json(response)
            for item in body.get("items", []):
                if not isinstance(item, dict) or not item.get("id"):
                    continue
                events.append(ExternalAppointment(
                    external_id=str(item["id"]),
                    starts_at=(item.get("start") or {}).get("dateTime") or (item.get("start") or {}).get("date"),
                    ends_at=(item.get("end") or {}).get("dateTime") or (item.get("end") or {}).get("date"),
                    status=str(item.get("status") or "confirmed"),
                    title=item.get("summary"),
                    description=item.get("description"),
                    location=item.get("location"),
                    external_updated_at=item.get("updated"),
                    version=item.get("etag"),
                    raw={"recurringEventId": item.get("recurringEventId")},
                ))
            page = body.get("nextPageToken")
            if page:
                params["pageToken"] = page
                continue
            return PullResult(events, body.get("nextSyncToken") or cursor)

    def create(self, payload: dict[str, Any], *, idempotency_key: str) -> dict[str, Any]:
        event_id = hashlib.sha256(idempotency_key.encode()).hexdigest()[:32]
        body = self._event_body(payload)
        body["id"] = event_id
        response = self.client.post(
            self._calendar_url("/events"), headers={**self.headers, "Content-Type": "application/json"},
            params={"sendUpdates": "none"}, json=body,
        )
        if response.status_code == 409:
            existing = self.client.get(self._calendar_url(f"/events/{quote(event_id, safe='')}"), headers=self.headers)
            _raise_provider(existing)
            return _safe_json(existing)
        _raise_provider(response)
        return _safe_json(response)

    def reschedule(self, external_id: str, payload: dict[str, Any], *, version: str | None) -> dict[str, Any]:
        headers = {**self.headers, "Content-Type": "application/json"}
        if version:
            headers["If-Match"] = version
        response = self.client.patch(
            self._calendar_url(f"/events/{quote(external_id, safe='')}"),
            headers=headers, params={"sendUpdates": "none"}, json=self._event_body(payload),
        )
        _raise_provider(response)
        return _safe_json(response)

    def cancel(self, external_id: str, *, reason: str | None, version: str | None) -> dict[str, Any]:
        headers = self.headers
        if version:
            headers = {**headers, "If-Match": version}
        response = self.client.delete(
            self._calendar_url(f"/events/{quote(external_id, safe='')}"),
            headers=headers, params={"sendUpdates": "none"},
        )
        _raise_provider(response)
        return {"id": external_id, "status": "cancelled"}

    def _event_body(self, payload: dict[str, Any]) -> dict[str, Any]:
        timezone = payload.get("timezone") or "America/Sao_Paulo"
        expose_name = bool(self.configuration.get("expose_patient_name"))
        title = payload.get("patient_name") if expose_name else None
        summary = f"{payload.get('service_name') or 'Consulta'} — {title or 'Corvia'}"
        return {
            "summary": summary[:300],
            "description": str(payload.get("notes") or "")[:4000],
            "location": str(payload.get("location_name") or "")[:300],
            "start": {"dateTime": payload["starts_at"], "timeZone": timezone},
            "end": {"dateTime": payload["ends_at"], "timeZone": timezone},
            "visibility": "private",
            "extendedProperties": {"private": {"corviaAppointmentId": str(payload.get("appointment_id") or "")}},
        }


class Microsoft365CalendarConnector(_HttpConnector):
    provider = "microsoft_365"
    capabilities = ConnectorCapabilities(
        read_appointments=True,
        incremental_sync=True,
        create_appointment=True,
        reschedule_appointment=True,
        cancel_appointment=True,
        webhooks=True,
        read_contacts=True,
    )
    base_url = "https://graph.microsoft.com/v1.0"

    @property
    def calendar_id(self) -> str | None:
        value = self.configuration.get("calendar_id")
        return str(value) if value else None

    def _events_url(self) -> str:
        if self.calendar_id:
            return f"{self.base_url}/me/calendars/{quote(self.calendar_id, safe='')}/events"
        return f"{self.base_url}/me/events"

    def _calendar_view_delta_url(self, start: datetime, end: datetime) -> str:
        if self.calendar_id:
            root = f"{self.base_url}/me/calendars/{quote(self.calendar_id, safe='')}/calendarView/delta"
        else:
            root = f"{self.base_url}/me/calendarView/delta"
        return f"{root}?startDateTime={quote(start.isoformat(), safe='')}&endDateTime={quote(end.isoformat(), safe='')}"

    def diagnose(self) -> dict[str, Any]:
        url = f"{self.base_url}/me/calendars/{quote(self.calendar_id, safe='')}" if self.calendar_id else f"{self.base_url}/me/calendar"
        response = self.client.get(url, headers=self.headers)
        _raise_provider(response)
        body = _safe_json(response)
        return {
            "ok": True,
            "provider": self.provider,
            "calendar_id": body.get("id") or self.calendar_id,
            "name": body.get("name"),
            "capabilities": asdict(self.capabilities),
        }


    def pull(self, *, cursor: str | None, start: datetime, end: datetime) -> PullResult:
        url = cursor or self._calendar_view_delta_url(start, end)
        if cursor and not cursor.startswith(f"{self.base_url}/"):
            raise ConnectorError("invalid_cursor", "Cursor Microsoft inválido.", status_code=409)
        events: list[ExternalAppointment] = []
        while url:
            response = self.client.get(url, headers={**self.headers, "Prefer": 'outlook.timezone="UTC"'})
            if response.status_code in {404, 410} and cursor:
                return PullResult([], None, full_resync_required=True)
            _raise_provider(response)
            body = _safe_json(response)
            for item in body.get("value", []):
                if not isinstance(item, dict) or not item.get("id"):
                    continue
                removed = item.get("@removed")
                events.append(ExternalAppointment(
                    external_id=str(item["id"]),
                    starts_at=(item.get("start") or {}).get("dateTime"),
                    ends_at=(item.get("end") or {}).get("dateTime"),
                    status="cancelled" if removed or item.get("isCancelled") else "confirmed",
                    title=item.get("subject"),
                    description=(item.get("bodyPreview") or "")[:4000],
                    location=(item.get("location") or {}).get("displayName"),
                    external_updated_at=item.get("lastModifiedDateTime"),
                    version=item.get("changeKey") or item.get("@odata.etag"),
                    raw={"iCalUId": item.get("iCalUId")},
                ))
            url = body.get("@odata.nextLink")
            if not url:
                return PullResult(events, body.get("@odata.deltaLink") or cursor)
        return PullResult(events, cursor)

    def create(self, payload: dict[str, Any], *, idempotency_key: str) -> dict[str, Any]:
        body = self._event_body(payload)
        body["transactionId"] = idempotency_key[:255]
        response = self.client.post(
            self._events_url(), headers={**self.headers, "Content-Type": "application/json"}, json=body
        )
        _raise_provider(response)
        return _safe_json(response)

    def reschedule(self, external_id: str, payload: dict[str, Any], *, version: str | None) -> dict[str, Any]:
        headers = {**self.headers, "Content-Type": "application/json"}
        if version:
            headers["If-Match"] = version
        response = self.client.patch(
            f"{self._events_url()}/{quote(external_id, safe='')}", headers=headers, json=self._event_body(payload)
        )
        _raise_provider(response)
        return _safe_json(response)

    def cancel(self, external_id: str, *, reason: str | None, version: str | None) -> dict[str, Any]:
        headers = {**self.headers, "Content-Type": "application/json"}
        if version:
            headers["If-Match"] = version
        response = self.client.post(
            f"{self._events_url()}/{quote(external_id, safe='')}/cancel",
            headers=headers, json={"comment": (reason or "Cancelado no Corvia")[:500]},
        )
        _raise_provider(response)
        return {"id": external_id, "status": "cancelled"}

    def _event_body(self, payload: dict[str, Any]) -> dict[str, Any]:
        expose_name = bool(self.configuration.get("expose_patient_name"))
        title = payload.get("patient_name") if expose_name else None
        subject = f"{payload.get('service_name') or 'Consulta'} — {title or 'Corvia'}"
        return {
            "subject": subject[:255],
            "sensitivity": "private",
            "body": {"contentType": "text", "content": str(payload.get("notes") or "")[:4000]},
            "start": {"dateTime": payload["starts_at"], "timeZone": payload.get("timezone") or "UTC"},
            "end": {"dateTime": payload["ends_at"], "timeZone": payload.get("timezone") or "UTC"},
            "location": {"displayName": str(payload.get("location_name") or "")[:255]},
        }


class AppleICloudCalendarConnector:
    """Leitura oficial via CalDAV usando senha específica de app.

    A escrita permanece desativada até haver testes de interoperabilidade com
    recorrências e ETags do iCloud; isso evita sobrescrever eventos do usuário.
    """

    provider = "apple_icloud"
    capabilities = ConnectorCapabilities(read_appointments=True, read_contacts=True)

    def __init__(self, credentials: dict[str, Any], configuration: dict[str, Any], transport=None):
        from app.services.agenda_integrada.apple_dav import AppleDavClient

        self.configuration = configuration
        self.dav = AppleDavClient(
            str(credentials.get("username") or ""),
            str(credentials.get("app_specific_password") or ""),
            transport=transport,
        )

    def diagnose(self) -> dict[str, Any]:
        calendars = self.dav.calendars()
        # 08/08/2026: reproduzido com credencial real (Rafael) — a descoberta de
        # calendário (caldav.icloud.com) funciona normalmente, mas a de contatos
        # (contacts.icloud.com/.well-known/carddav) responde 207 com
        # current-user-principal vazio (status interno 404), sem nenhum
        # redirecionamento de partição, ao contrário do caldav. Causa exata do lado
        # da Apple não confirmada (log de diagnóstico não deu margem pra mais). Até
        # então, essa falha isolada de contatos derrubava a conexão inteira — quem só
        # queria sincronizar agenda ficava bloqueado por um serviço que nem usaria.
        # Agora a falha de contatos vira degradação, não impedimento: calendário (e
        # e-mail, diagnosticado à parte) conectam normalmente, e o retorno sinaliza
        # que contatos não ficou disponível, sem fingir que funcionou.
        addressbooks_count = 0
        addressbooks_disponivel = True
        try:
            addressbooks_count = len(self.dav.addressbooks())
        except ConnectorError as exc:
            if exc.code != "apple_dav_discovery_failed":
                raise
            addressbooks_disponivel = False
        return {
            "ok": True, "provider": self.provider, "calendars": len(calendars),
            "addressbooks": addressbooks_count, "addressbooks_disponivel": addressbooks_disponivel,
            "capabilities": asdict(self.capabilities),
        }

    def pull(self, *, cursor: str | None, start: datetime, end: datetime) -> PullResult:
        from app.services.agenda_integrada.apple_dav import parse_icalendar

        appointments: list[ExternalAppointment] = []
        for calendar in self.dav.calendars():
            for resource in self.dav.calendar_resources(calendar, start, end):
                for item in parse_icalendar(resource.data, resource.href):
                    appointments.append(ExternalAppointment(
                        external_id=str(item["id"]), starts_at=item.get("starts_at"),
                        ends_at=item.get("ends_at"), status=str(item.get("status") or "confirmed"),
                        title=item.get("title"), description=item.get("description"),
                        location=item.get("location"), external_updated_at=item.get("updated_at"),
                        version=resource.etag,
                    ))
        return PullResult(appointments, None)

    def create(self, *_args, **_kwargs) -> dict[str, Any]:
        raise ConnectorError("write_not_supported", "A escrita no calendário Apple ainda não está habilitada.", status_code=409)

    reschedule = create
    cancel = create


class HomologationRequiredConnector:
    capabilities = ConnectorCapabilities()

    def __init__(self, provider: str, *_args, **_kwargs):
        self.provider = provider

    def diagnose(self) -> dict[str, Any]:
        return {
            "ok": False,
            "provider": self.provider,
            "code": "homologation_required",
            "message": "Conector aguardando documentação oficial e homologação; nenhuma chamada externa foi realizada.",
            "capabilities": asdict(self.capabilities),
        }

    def pull(self, **_kwargs) -> PullResult:
        raise ConnectorError("homologation_required", "Leitura externa ainda não homologada.", status_code=409)

    def create(self, *_args, **_kwargs) -> dict[str, Any]:
        raise ConnectorError("homologation_required", "Escrita externa ainda não homologada.", status_code=409)

    reschedule = create
    cancel = create


_CATALOG = {
    "google_calendar": {
        "name": "Google Calendar", "status": "adapter_available", "official_api": True,
        "capabilities": asdict(GoogleCalendarConnector.capabilities),
    },
    "microsoft_365": {
        "name": "Microsoft 365 / Outlook", "status": "adapter_available", "official_api": True,
        "capabilities": asdict(Microsoft365CalendarConnector.capabilities),
    },
    "apple_icloud": {
        "name": "Apple iCloud (Calendário e Contatos)", "status": "adapter_available",
        "official_api": True, "capabilities": asdict(AppleICloudCalendarConnector.capabilities),
    },
    "feegow": {"name": "Feegow", "status": "homologation_required", "official_api": False, "capabilities": asdict(ConnectorCapabilities())},
    "amplimed": {"name": "Amplimed", "status": "coming_soon", "official_api": False, "capabilities": asdict(ConnectorCapabilities())},
    "iclinic": {"name": "iClinic", "status": "coming_soon", "official_api": False, "capabilities": asdict(ConnectorCapabilities())},
    "tasy": {"name": "Philips Tasy", "status": "coming_soon", "official_api": False, "capabilities": asdict(ConnectorCapabilities())},
    "mv": {"name": "MV", "status": "coming_soon", "official_api": False, "capabilities": asdict(ConnectorCapabilities())},
    "pixeon": {"name": "Pixeon", "status": "coming_soon", "official_api": False, "capabilities": asdict(ConnectorCapabilities())},
    "ics": {"name": "Arquivo ICS", "status": "coming_soon_read_only", "official_api": True, "capabilities": asdict(ConnectorCapabilities(read_appointments=True))},
    "csv": {"name": "Arquivo CSV", "status": "coming_soon_read_only", "official_api": False, "capabilities": asdict(ConnectorCapabilities(read_appointments=True))},
}


def connector_catalog() -> list[dict[str, Any]]:
    return [{"provider": key, **value} for key, value in _CATALOG.items()]


def get_connector(provider: str, credentials: dict[str, Any], configuration: dict[str, Any], transport=None) -> CalendarConnector:
    if provider == "google_calendar":
        return GoogleCalendarConnector(credentials, configuration, transport=transport)
    if provider == "microsoft_365":
        return Microsoft365CalendarConnector(credentials, configuration, transport=transport)
    if provider == "apple_icloud":
        return AppleICloudCalendarConnector(credentials, configuration, transport=transport)
    if provider in _CATALOG:
        return HomologationRequiredConnector(provider)
    raise ConnectorError("unsupported_provider", "Provedor de agenda não suportado.", status_code=422)
