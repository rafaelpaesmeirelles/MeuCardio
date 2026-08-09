"""OAuth, renovação de tokens e identificação de contas externas.

Tokens nunca são devolvidos à interface. O estado OAuth é de uso único, tem
expiração curta e só é persistido como SHA-256; o verificador PKCE é cifrado.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agenda import CalendarIntegration, IntegrationOAuthState
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.domain import integration_credentials, store_integration_credentials
from app.services.cofre import cifrar_campo, decifrar_campo

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_PROFILE_URL = "https://openidconnect.googleapis.com/v1/userinfo"
MICROSOFT_GRAPH = "https://graph.microsoft.com/v1.0"
APP_PASSWORD_PROVIDERS = {"apple_icloud", "yahoo_mail"}


def _microsoft_authority() -> str:
    tenant = settings.microsoft_oauth_tenant.strip() or "common"
    if not all(ch.isalnum() or ch in {"-", "."} for ch in tenant):
        raise ConnectorError("oauth_configuration", "Tenant Microsoft inválido.", status_code=503)
    return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0"


def oauth_configured(provider: str) -> bool:
    if provider == "google_calendar": return bool(settings.google_oauth_client_id and settings.google_oauth_client_secret)
    if provider == "microsoft_365": return bool(settings.microsoft_oauth_client_id and settings.microsoft_oauth_client_secret)
    return False


def redirect_uri(provider: str) -> str:
    slug = "google" if provider == "google_calendar" else "microsoft"
    return f"{settings.public_url.rstrip('/')}/api/agenda/oauth/{slug}/callback"


def oauth_scopes(provider: str, *, calendar_write: bool, contacts: bool, mail: bool = False) -> list[str]:
    if provider == "google_calendar":
        scopes = ["openid", "email", "profile"]
        scopes.append("https://www.googleapis.com/auth/calendar.events" if calendar_write else "https://www.googleapis.com/auth/calendar.events.readonly")
        if contacts: scopes.append("https://www.googleapis.com/auth/contacts.readonly")
        if mail: scopes.extend(["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/gmail.send"])
        return scopes
    if provider == "microsoft_365":
        scopes = ["openid", "profile", "email", "offline_access", "User.Read"]
        scopes.append("Calendars.ReadWrite" if calendar_write else "Calendars.Read")
        if contacts: scopes.append("Contacts.Read")
        if mail: scopes.extend(["Mail.ReadWrite", "Mail.Send"])
        return scopes
    raise ConnectorError("unsupported_provider", "OAuth não suportado para este provedor.", status_code=422)


def begin_oauth(db: Session, *, owner_id: int, provider: str, calendar_write: bool, contacts: bool, mail: bool = False) -> str:
    if not oauth_configured(provider):
        raise ConnectorError("oauth_not_configured", "O administrador ainda precisa cadastrar o cliente OAuth deste provedor.", status_code=503)
    state = secrets.token_urlsafe(32); verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    record = IntegrationOAuthState(owner_id=owner_id, provider=provider, state_digest=hashlib.sha256(state.encode()).hexdigest(), code_verifier_cipher=cifrar_campo(verifier, owner_id), request_data={"calendar_write": calendar_write, "contacts": contacts, "mail": mail}, expires_at=datetime.now(timezone.utc) + timedelta(minutes=10))
    db.add(record); db.commit()
    scopes = oauth_scopes(provider, calendar_write=calendar_write, contacts=contacts, mail=mail)
    common = {"response_type": "code", "redirect_uri": redirect_uri(provider), "scope": " ".join(scopes), "state": state, "code_challenge": challenge, "code_challenge_method": "S256"}
    if provider == "google_calendar":
        query = {**common, "client_id": settings.google_oauth_client_id, "access_type": "offline", "include_granted_scopes": "true", "prompt": "consent"}
        return f"{GOOGLE_AUTH_URL}?{urlencode(query)}"
    query = {**common, "client_id": settings.microsoft_oauth_client_id, "response_mode": "query"}
    return f"{_microsoft_authority()}/authorize?{urlencode(query)}"


def _consume_state(db: Session, provider: str, state: str) -> tuple[IntegrationOAuthState, str]:
    digest = hashlib.sha256(state.encode()).hexdigest()
    record = db.query(IntegrationOAuthState).filter(IntegrationOAuthState.provider == provider, IntegrationOAuthState.state_digest == digest).with_for_update().first()
    now = datetime.now(timezone.utc); expires_at = record.expires_at if record else None
    if expires_at and expires_at.tzinfo is None: expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not record or record.used_at or not expires_at or expires_at <= now: raise ConnectorError("invalid_oauth_state", "Autorização expirada ou já utilizada.", status_code=400)
    verifier = decifrar_campo(record.code_verifier_cipher, record.owner_id); record.used_at = now; db.commit(); return record, verifier


def _token_payload(provider: str, code: str, verifier: str) -> tuple[str, dict[str, str]]:
    common = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri(provider), "code_verifier": verifier}
    if provider == "google_calendar": return GOOGLE_TOKEN_URL, {**common, "client_id": settings.google_oauth_client_id, "client_secret": settings.google_oauth_client_secret}
    return f"{_microsoft_authority()}/token", {**common, "client_id": settings.microsoft_oauth_client_id, "client_secret": settings.microsoft_oauth_client_secret}


def _normalize_token(body: dict[str, Any], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    if not body.get("access_token"): raise ConnectorError("oauth_token_error", "O provedor não devolveu token de acesso.", status_code=502)
    expires_in = max(60, int(body.get("expires_in") or 3600))
    result = {"access_token": str(body["access_token"]), "refresh_token": str(body.get("refresh_token") or (previous or {}).get("refresh_token") or ""), "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(), "token_type": str(body.get("token_type") or "Bearer"), "scope": str(body.get("scope") or (previous or {}).get("scope") or "")}
    if not result["refresh_token"]: raise ConnectorError("oauth_refresh_token_missing", "O provedor não concedeu acesso offline. Remova a autorização anterior e conecte novamente.", status_code=409)
    return result


def _provider_profile(provider: str, token: str) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if provider == "google_calendar":
        response = httpx.get(GOOGLE_PROFILE_URL, headers=headers, timeout=20.0)
        if response.status_code >= 400: raise ConnectorError("oauth_profile_error", f"Google profile HTTP {response.status_code}.")
        body = response.json(); return {"id": str(body.get("sub") or body.get("email") or ""), "name": str(body.get("name") or body.get("email") or "Conta Google"), "email": str(body.get("email") or "")}
    response = httpx.get(f"{MICROSOFT_GRAPH}/me?$select=id,displayName,mail,userPrincipalName", headers=headers, timeout=20.0)
    if response.status_code >= 400: raise ConnectorError("oauth_profile_error", f"Microsoft Graph HTTP {response.status_code}.")
    body = response.json(); email = body.get("mail") or body.get("userPrincipalName") or ""; return {"id": str(body.get("id") or email), "name": str(body.get("displayName") or email or "Conta Microsoft"), "email": str(email)}


def complete_oauth(db: Session, *, provider: str, code: str, state: str) -> CalendarIntegration:
    record, verifier = _consume_state(db, provider, state); token_url, payload = _token_payload(provider, code, verifier)
    try: response = httpx.post(token_url, data=payload, timeout=30.0)
    except httpx.HTTPError as exc: raise ConnectorError("oauth_network_error", "Falha de rede ao concluir a autorização.", retryable=True) from exc
    if response.status_code >= 400: raise ConnectorError("oauth_exchange_error", f"O provedor recusou a autorização (HTTP {response.status_code}).", status_code=400)
    token = _normalize_token(response.json()); profile = _provider_profile(provider, token["access_token"])
    integration = db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == record.owner_id, CalendarIntegration.provider == provider, CalendarIntegration.external_account_id == profile["id"]).first()
    capabilities = {"read_appointments": True, "incremental_sync": True, "create_appointment": bool(record.request_data.get("calendar_write")), "reschedule_appointment": bool(record.request_data.get("calendar_write")), "cancel_appointment": bool(record.request_data.get("calendar_write")), "read_contacts": bool(record.request_data.get("contacts")), "read_mail": bool(record.request_data.get("mail")), "send_mail": bool(record.request_data.get("mail"))}
    if not integration:
        integration = CalendarIntegration(owner_id=record.owner_id, provider=provider, display_name=profile["email"] or profile["name"], external_account_id=profile["id"], sync_strategy="bidirectional" if record.request_data.get("calendar_write") else "external_authoritative", configuration={"calendar_id": "primary"} if provider == "google_calendar" else {})
        db.add(integration); db.flush()
    integration.status = "connected"; integration.enabled = True; integration.write_enabled = bool(record.request_data.get("calendar_write")); integration.contacts_enabled = bool(record.request_data.get("contacts")); integration.capabilities = capabilities; integration.consent_version = "external-accounts-v2-2026-08-06"; integration.consent_at = datetime.now(timezone.utc); integration.revoked_at = None; integration.last_error_code = None; integration.last_error_message = None
    store_integration_credentials(integration, token); db.commit(); db.refresh(integration); return integration


def _refresh_payload(integration: CalendarIntegration, credentials: dict[str, Any]) -> tuple[str, dict[str, str]]:
    refresh_token = str(credentials.get("refresh_token") or "")
    if not refresh_token: raise ConnectorError("reauth_required", "A conta precisa ser conectada novamente.", status_code=409)
    if integration.provider == "google_calendar":
        return GOOGLE_TOKEN_URL, {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": settings.google_oauth_client_id, "client_secret": settings.google_oauth_client_secret}
    if integration.provider == "microsoft_365":
        return f"{_microsoft_authority()}/token", {"grant_type": "refresh_token", "refresh_token": refresh_token, "client_id": settings.microsoft_oauth_client_id, "client_secret": settings.microsoft_oauth_client_secret, "scope": str(credentials.get("scope") or "")}
    raise ConnectorError("unsupported_provider", "Provedor não suporta renovação OAuth.", status_code=422)


def ensure_fresh_credentials(db: Session, integration: CalendarIntegration, *, force: bool = False) -> dict[str, Any]:
    """Devolve credenciais válidas e renova OAuth automaticamente.

    ``force=True`` é usado quando a API do provedor responde 401 antes do
    ``expires_at`` local. Assim o CorvIA tenta recuperar a sessão com o refresh
    token antes de pedir ao médico uma reconexão interativa.
    """
    credentials = integration_credentials(integration)
    if integration.provider in APP_PASSWORD_PROVIDERS: return credentials
    expires_raw = credentials.get("expires_at")
    try: expires_at = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))
    except (TypeError, ValueError): expires_at = datetime.min.replace(tzinfo=timezone.utc)
    if not force and expires_at > datetime.now(timezone.utc) + timedelta(seconds=90): return credentials

    url, payload = _refresh_payload(integration, credentials)
    try: response = httpx.post(url, data=payload, timeout=30.0)
    except httpx.HTTPError as exc: raise ConnectorError("oauth_refresh_network_error", "Falha de rede ao renovar a autorização.", retryable=True, status_code=503) from exc

    if response.status_code >= 400:
        try: body = response.json()
        except ValueError: body = {}
        provider_error = str(body.get("error") or "").lower()
        if provider_error in {"invalid_grant", "interaction_required", "consent_required"}:
            integration.status = "reauth_required"; integration.last_error_code = "reauth_required"; integration.last_error_message = "A autorização externa expirou ou foi revogada."; db.commit()
            raise ConnectorError("reauth_required", "A autorização externa expirou ou foi revogada.", status_code=409)
        if provider_error in {"invalid_client", "unauthorized_client"}:
            integration.last_error_code = "oauth_configuration"; integration.last_error_message = "O cliente OAuth do CorvIA foi recusado pelo provedor."; db.commit()
            raise ConnectorError("oauth_configuration", "A configuração OAuth do CorvIA foi recusada pelo provedor.", status_code=503)
        if response.status_code == 429 or response.status_code >= 500:
            raise ConnectorError("oauth_refresh_provider_error", "O provedor está temporariamente indisponível para renovar a autorização.", retryable=True, status_code=503)
        raise ConnectorError("oauth_refresh_error", f"O provedor recusou a renovação (HTTP {response.status_code}).", retryable=False, status_code=502)

    updated = _normalize_token(response.json(), credentials)
    store_integration_credentials(integration, updated)
    integration.status = "connected"; integration.last_error_code = None; integration.last_error_message = None
    db.commit()
    return updated


def disconnect_integration(db: Session, integration: CalendarIntegration) -> None:
    credentials = integration_credentials(integration)
    if integration.provider == "google_calendar" and credentials.get("access_token"):
        try: httpx.post("https://oauth2.googleapis.com/revoke", data={"token": credentials["access_token"]}, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15.0)
        except httpx.HTTPError: pass
    integration.credentials_cipher = None; integration.cursor_cipher = None; integration.contacts_cursor_cipher = None; integration.enabled = False; integration.write_enabled = False; integration.contacts_enabled = False; integration.status = "disconnected"; integration.revoked_at = datetime.now(timezone.utc); db.commit()
