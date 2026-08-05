"""Cliente DAV restrito aos serviços oficiais do iCloud.

O cliente não aceita URLs fornecidas pela interface. Endereços descobertos via
WebDAV só são seguidos quando usam HTTPS e pertencem ao domínio icloud.com,
evitando transformar a integração em um proxy SSRF.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

from app.services.agenda_integrada.connectors import ConnectorError

DAV = "DAV:"
CALDAV = "urn:ietf:params:xml:ns:caldav"
CARDDAV = "urn:ietf:params:xml:ns:carddav"


def _safe_icloud_url(base: str, href: str) -> str:
    url = urljoin(base, href)
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (hostname == "icloud.com" or hostname.endswith(".icloud.com")):
        raise ConnectorError("invalid_dav_discovery", "O iCloud devolveu um endereço DAV não permitido.", status_code=502)
    return url


def _unfold(value: str) -> list[str]:
    lines = value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    result: list[str] = []
    for line in lines:
        if line.startswith((" ", "\t")) and result:
            result[-1] += line[1:]
        else:
            result.append(line)
    return result


def _ical_value(line: str) -> tuple[str, str]:
    left, _, value = line.partition(":")
    return left.split(";", 1)[0].upper(), value.replace("\\n", "\n").replace("\\,", ",")


def _iso_ical(value: str, tzid: str | None = None) -> str | None:
    raw = value.strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%dT%H%M%S", "%Y%m%d"):
        try:
            parsed = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            if not fmt.endswith("Z") and tzid:
                try:
                    parsed = parsed.replace(tzinfo=ZoneInfo(tzid))
                except ZoneInfoNotFoundError:
                    return None
            return parsed.isoformat()
        except ValueError:
            continue
    return None


def parse_vcard(value: str, fallback_id: str) -> dict:
    fields: dict[str, list[str]] = {}
    for line in _unfold(value):
        key, val = _ical_value(line)
        if key in {"UID", "FN", "EMAIL", "TEL", "ORG", "REV"} and val:
            fields.setdefault(key, []).append(val.strip())
    return {
        "id": (fields.get("UID") or [fallback_id])[0],
        "display_name": (fields.get("FN") or [""])[0],
        "emails": fields.get("EMAIL", []),
        "phones": fields.get("TEL", []),
        "organization": (fields.get("ORG") or [""])[0].replace(";", " · "),
        "updated_at": (fields.get("REV") or [None])[0],
    }


def parse_icalendar(value: str, fallback_id: str) -> list[dict]:
    events: list[dict] = []
    current: dict[str, str] | None = None
    for line in _unfold(value):
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT" and current is not None:
            events.append({
                "id": current.get("UID") or fallback_id,
                "starts_at": _iso_ical(current.get("DTSTART", ""), current.get("DTSTART_TZID")),
                "ends_at": _iso_ical(current.get("DTEND", ""), current.get("DTEND_TZID")),
                "status": "cancelled" if current.get("STATUS", "").upper() == "CANCELLED" else "confirmed",
                "title": current.get("SUMMARY"),
                "description": current.get("DESCRIPTION"),
                "location": current.get("LOCATION"),
                "updated_at": _iso_ical(current.get("LAST-MODIFIED", "")),
            })
            current = None
            continue
        if current is not None:
            key, val = _ical_value(line)
            if key in {"UID", "DTSTART", "DTEND", "STATUS", "SUMMARY", "DESCRIPTION", "LOCATION", "LAST-MODIFIED"}:
                current[key] = val
                if key in {"DTSTART", "DTEND"}:
                    left = line.partition(":")[0]
                    for parameter in left.split(";")[1:]:
                        name, _, parameter_value = parameter.partition("=")
                        if name.upper() == "TZID" and parameter_value:
                            current[f"{key}_TZID"] = parameter_value
    return events


@dataclass(frozen=True)
class DavResource:
    href: str
    etag: str | None
    data: str


class AppleDavClient:
    calendar_root = "https://caldav.icloud.com/.well-known/caldav"
    contacts_root = "https://contacts.icloud.com/.well-known/carddav"

    def __init__(self, username: str, app_specific_password: str, *, transport=None):
        if not username or not app_specific_password:
            raise ConnectorError("apple_credentials_missing", "Informe o ID Apple e uma senha específica de app.", status_code=409)
        self.client = httpx.Client(
            auth=(username, app_specific_password), timeout=httpx.Timeout(30.0, connect=8.0),
            follow_redirects=False, transport=transport,
        )

    def _xml(self, method: str, url: str, body: str, *, depth: str = "0") -> ET.Element:
        current_url = _safe_icloud_url(url, url)
        response = None
        for _ in range(4):
            response = self.client.request(
                method, current_url, content=body.encode(),
                headers={"Depth": depth, "Content-Type": "application/xml; charset=utf-8"},
            )
            if response.status_code not in {301, 302, 307, 308}:
                break
            location = response.headers.get("location")
            if not location:
                break
            current_url = _safe_icloud_url(current_url, location)
        if response is None:  # pragma: no cover - o laço sempre executa
            raise ConnectorError("apple_dav_error", "O iCloud não respondeu.")
        if response.status_code == 401:
            raise ConnectorError("reauth_required", "ID Apple ou senha específica de app inválidos.", status_code=409)
        if response.status_code not in {200, 207}:
            raise ConnectorError("apple_dav_error", f"iCloud DAV respondeu HTTP {response.status_code}.", status_code=502)
        if len(response.content) > 25 * 1024 * 1024:
            raise ConnectorError("apple_dav_response_too_large", "Resposta DAV do iCloud acima do limite.")
        prefix = response.content[:4096].upper()
        if b"<!DOCTYPE" in prefix or b"<!ENTITY" in prefix:
            raise ConnectorError("apple_dav_unsafe_xml", "Resposta DAV insegura recusada.")
        try:
            return ET.fromstring(response.content)  # noqa: S314 - DTD/entidades recusados acima
        except ET.ParseError as exc:
            raise ConnectorError("apple_dav_invalid_xml", "Resposta DAV inválida do iCloud.", status_code=502) from exc

    def _discover_home(self, root: str, namespace: str, property_name: str) -> str:
        principal_xml = self._xml("PROPFIND", root, '<d:propfind xmlns:d="DAV:"><d:prop><d:current-user-principal/></d:prop></d:propfind>')
        href = principal_xml.findtext(f".//{{{DAV}}}current-user-principal/{{{DAV}}}href")
        if not href:
            raise ConnectorError("apple_dav_discovery_failed", "O iCloud não informou o usuário DAV.")
        principal = _safe_icloud_url(root, href)
        home_xml = self._xml(
            "PROPFIND", principal,
            f'<d:propfind xmlns:d="DAV:" xmlns:x="{namespace}"><d:prop><x:{property_name}/></d:prop></d:propfind>',
        )
        home_href = home_xml.findtext(f".//{{{namespace}}}{property_name}/{{{DAV}}}href")
        if not home_href:
            raise ConnectorError("apple_dav_discovery_failed", "O iCloud não informou a coleção DAV.")
        return _safe_icloud_url(principal, home_href)

    def _collections(self, home: str, namespace: str, resource_name: str) -> list[str]:
        xml = self._xml(
            "PROPFIND", home,
            '<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/><d:displayname/></d:prop></d:propfind>', depth="1",
        )
        result: list[str] = []
        for response in xml.findall(f".//{{{DAV}}}response"):
            if response.find(f".//{{{namespace}}}{resource_name}") is None:
                continue
            href = response.findtext(f"{{{DAV}}}href")
            if href:
                result.append(_safe_icloud_url(home, href))
        return list(dict.fromkeys(result))

    def addressbooks(self) -> list[str]:
        home = self._discover_home(self.contacts_root, CARDDAV, "addressbook-home-set")
        return self._collections(home, CARDDAV, "addressbook")

    def calendars(self) -> list[str]:
        home = self._discover_home(self.calendar_root, CALDAV, "calendar-home-set")
        return self._collections(home, CALDAV, "calendar")

    def addressbook_resources(self, addressbook: str) -> list[DavResource]:
        xml = self._xml(
            "REPORT", addressbook,
            '<c:addressbook-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:carddav"><d:prop><d:getetag/><c:address-data/></d:prop></c:addressbook-query>',
            depth="1",
        )
        return self._resources(xml, addressbook, CARDDAV, "address-data")

    def calendar_resources(self, calendar: str, start: datetime, end: datetime) -> list[DavResource]:
        start_utc = start.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        end_utc = end.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        body = (
            '<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop><d:getetag/>'
            '<c:calendar-data/></d:prop><c:filter><c:comp-filter name="VCALENDAR"><c:comp-filter name="VEVENT">'
            f'<c:time-range start="{start_utc}" end="{end_utc}"/></c:comp-filter></c:comp-filter></c:filter></c:calendar-query>'
        )
        xml = self._xml("REPORT", calendar, body, depth="1")
        return self._resources(xml, calendar, CALDAV, "calendar-data")

    @staticmethod
    def _resources(xml: ET.Element, base: str, namespace: str, data_tag: str) -> list[DavResource]:
        result: list[DavResource] = []
        for response in xml.findall(f".//{{{DAV}}}response"):
            href = response.findtext(f"{{{DAV}}}href")
            data = response.findtext(f".//{{{namespace}}}{data_tag}")
            if not href or not data:
                continue
            result.append(DavResource(
                href=_safe_icloud_url(base, href),
                etag=response.findtext(f".//{{{DAV}}}getetag"),
                data=data,
            ))
        return result
