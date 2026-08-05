"""Sincronização de contatos externos com persistência cifrada por tenant."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.models.agenda import CalendarIntegration, ExternalContact
from app.services.agenda_integrada.connectors import (
    ConnectorError,
    _raise_provider,
    _safe_json,
)
from app.services.cofre import cifrar_campo, decifrar_campo


@dataclass(frozen=True)
class ContactData:
    external_id: str
    display_name: str
    emails: list[str]
    phones: list[str]
    organization: str
    version: str | None = None
    updated_at: str | None = None
    deleted: bool = False


@dataclass(frozen=True)
class ContactPull:
    contacts: list[ContactData]
    cursor: str | None
    full_snapshot: bool
    full_resync_required: bool = False


class _OAuthContacts:
    def __init__(self, token: str, *, transport=None):
        if not token:
            raise ConnectorError("reauth_required", "Token OAuth ausente.", status_code=409)
        self.client = httpx.Client(timeout=30.0, transport=transport, follow_redirects=False)
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}


class GoogleContacts(_OAuthContacts):
    url = "https://people.googleapis.com/v1/people/me/connections"

    def pull(self, cursor: str | None) -> ContactPull:
        params: dict[str, Any] = {
            "personFields": "names,emailAddresses,phoneNumbers,organizations,metadata",
            "pageSize": 1000,
            "requestSyncToken": "true",
            "sources": "READ_SOURCE_TYPE_CONTACT",
        }
        if cursor:
            params["syncToken"] = cursor
        contacts: list[ContactData] = []
        while True:
            response = self.client.get(self.url, headers=self.headers, params=params)
            if response.status_code == 400 and cursor:
                return ContactPull([], None, False, full_resync_required=True)
            _raise_provider(response)
            body = _safe_json(response)
            for person in body.get("connections", []):
                if not isinstance(person, dict) or not person.get("resourceName"):
                    continue
                meta = person.get("metadata") or {}
                names = person.get("names") or []
                orgs = person.get("organizations") or []
                contacts.append(ContactData(
                    external_id=str(person["resourceName"]),
                    display_name=str((names[0] if names else {}).get("displayName") or ""),
                    emails=[str(x.get("value")) for x in person.get("emailAddresses", []) if x.get("value")],
                    phones=[str(x.get("value")) for x in person.get("phoneNumbers", []) if x.get("value")],
                    organization=str((orgs[0] if orgs else {}).get("name") or ""),
                    version=str(person.get("etag") or "") or None,
                    deleted=bool(meta.get("deleted")),
                ))
            page = body.get("nextPageToken")
            if page:
                params["pageToken"] = page
                continue
            return ContactPull(contacts, body.get("nextSyncToken") or cursor, not bool(cursor))


class MicrosoftContacts(_OAuthContacts):
    base = "https://graph.microsoft.com/v1.0"
    url = (
        f"{base}/me/contacts?$select=id,displayName,emailAddresses,businessPhones,homePhones,"
        "mobilePhone,companyName,lastModifiedDateTime&$top=999"
    )

    def pull(self, _cursor: str | None) -> ContactPull:
        url: str | None = self.url
        contacts: list[ContactData] = []
        while url:
            if not url.startswith(f"{self.base}/"):
                raise ConnectorError("invalid_contacts_cursor", "Paginação Microsoft inválida.", status_code=502)
            response = self.client.get(url, headers=self.headers)
            _raise_provider(response)
            body = _safe_json(response)
            for item in body.get("value", []):
                if not isinstance(item, dict) or not item.get("id"):
                    continue
                contacts.append(ContactData(
                    external_id=str(item["id"]), display_name=str(item.get("displayName") or ""),
                    emails=[str(x.get("address")) for x in item.get("emailAddresses", []) if x.get("address")],
                    phones=[str(x) for x in [*(item.get("businessPhones") or []), *(item.get("homePhones") or []), item.get("mobilePhone")] if x],
                    organization=str(item.get("companyName") or ""),
                    version=str(item.get("@odata.etag") or "") or None,
                    updated_at=item.get("lastModifiedDateTime"),
                ))
            url = body.get("@odata.nextLink")
        return ContactPull(contacts, None, True)


class AppleContacts:
    def __init__(self, username: str, password: str, *, transport=None):
        from app.services.agenda_integrada.apple_dav import AppleDavClient

        self.dav = AppleDavClient(username, password, transport=transport)

    def pull(self, _cursor: str | None) -> ContactPull:
        from app.services.agenda_integrada.apple_dav import parse_vcard

        contacts: list[ContactData] = []
        for addressbook in self.dav.addressbooks():
            for resource in self.dav.addressbook_resources(addressbook):
                item = parse_vcard(resource.data, resource.href)
                contacts.append(ContactData(
                    external_id=str(item["id"]), display_name=item["display_name"],
                    emails=item["emails"], phones=item["phones"], organization=item["organization"],
                    version=resource.etag, updated_at=item["updated_at"],
                ))
        return ContactPull(contacts, None, True)


def _cursor(integration: CalendarIntegration) -> str | None:
    return decifrar_campo(integration.contacts_cursor_cipher, integration.id) if integration.contacts_cursor_cipher else None


def _connector(integration: CalendarIntegration, credentials: dict, *, transport=None):
    if integration.provider == "google_calendar":
        return GoogleContacts(str(credentials.get("access_token") or ""), transport=transport)
    if integration.provider == "microsoft_365":
        return MicrosoftContacts(str(credentials.get("access_token") or ""), transport=transport)
    if integration.provider == "apple_icloud":
        return AppleContacts(str(credentials.get("username") or ""), str(credentials.get("app_specific_password") or ""), transport=transport)
    raise ConnectorError("contacts_not_supported", "Este provedor não oferece sincronização de contatos.", status_code=409)


def _encrypted(value: Any, contact_id: int) -> bytes:
    raw = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return cifrar_campo(raw, contact_id)


def sync_contacts(db: Session, integration: CalendarIntegration, *, full: bool = False, transport=None) -> dict:
    if not integration.enabled or not integration.contacts_enabled:
        raise ConnectorError("contacts_disabled", "Sincronização de contatos desativada.", status_code=409)
    from app.services.agenda_integrada.external_accounts import ensure_fresh_credentials

    credentials = ensure_fresh_credentials(db, integration)
    connector = _connector(integration, credentials, transport=transport)
    cursor = None if full else _cursor(integration)
    result = connector.pull(cursor)
    if result.full_resync_required:
        result = connector.pull(None)
    seen: set[str] = set()
    created = updated = deleted = 0
    for source in result.contacts:
        seen.add(source.external_id)
        item = db.query(ExternalContact).filter(
            ExternalContact.integration_id == integration.id,
            ExternalContact.external_id == source.external_id,
        ).first()
        if not item:
            item = ExternalContact(owner_id=integration.owner_id, integration_id=integration.id, external_id=source.external_id)
            db.add(item); db.flush(); created += 1
        else:
            updated += 1
        item.external_version = source.version
        item.display_name_cipher = _encrypted(source.display_name[:500], item.id)
        item.emails_cipher = _encrypted([x.strip().lower()[:320] for x in source.emails if x.strip()][:20], item.id)
        item.phones_cipher = _encrypted([x.strip()[:80] for x in source.phones if x.strip()][:20], item.id)
        item.organization_cipher = _encrypted(source.organization[:500], item.id)
        item.external_updated_at = source.updated_at
        item.deleted = source.deleted
        deleted += int(source.deleted)
    if result.full_snapshot:
        query = db.query(ExternalContact).filter(
            ExternalContact.integration_id == integration.id,
            ExternalContact.deleted.is_(False),
        )
        if seen:
            query = query.filter(ExternalContact.external_id.notin_(seen))
        for item in query.all():
            item.deleted = True; deleted += 1
    integration.contacts_cursor_cipher = cifrar_campo(result.cursor, integration.id) if result.cursor else None
    db.commit()
    return {"created": created, "updated": updated, "deleted": deleted, "total_received": len(result.contacts)}


def list_contacts(db: Session, owner_id: int, *, query: str = "", limit: int = 50) -> list[dict]:
    rows = db.query(ExternalContact, CalendarIntegration).join(
        CalendarIntegration, CalendarIntegration.id == ExternalContact.integration_id,
    ).filter(
        ExternalContact.owner_id == owner_id, ExternalContact.deleted.is_(False),
        CalendarIntegration.enabled.is_(True), CalendarIntegration.contacts_enabled.is_(True),
    ).order_by(ExternalContact.updated_at.desc()).limit(2500).all()
    needle = query.strip().casefold()
    result: list[dict] = []
    seen_emails: set[str] = set()
    for item, integration in rows:
        name = decifrar_campo(item.display_name_cipher, item.id) if item.display_name_cipher else ""
        emails = json.loads(decifrar_campo(item.emails_cipher, item.id)) if item.emails_cipher else []
        phones = json.loads(decifrar_campo(item.phones_cipher, item.id)) if item.phones_cipher else []
        organization = decifrar_campo(item.organization_cipher, item.id) if item.organization_cipher else ""
        haystack = " ".join([name, organization, *emails, *phones]).casefold()
        if needle and needle not in haystack:
            continue
        unique_emails = [email for email in emails if email not in seen_emails]
        if not unique_emails:
            continue
        seen_emails.update(unique_emails)
        result.append({
            "id": item.id, "name": name or unique_emails[0], "emails": unique_emails,
            "phones": phones, "organization": organization, "provider": integration.provider,
            "integration_id": integration.id,
        })
        if len(result) >= limit:
            break
    return result
