"""Gateway de e-mail externo para a caixa unificada do CorvIA Mail.

As mensagens permanecem no Google/Microsoft. O CorvIA faz proxy autenticado
pelas APIs oficiais e não persiste corpo ou anexos no banco local.
"""

from __future__ import annotations

import base64
from email.message import EmailMessage
from email.utils import getaddresses
from html import escape
from typing import Any
from urllib.parse import quote

import httpx
from sqlalchemy.orm import Session

from app.models.agenda import CalendarIntegration
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.external_accounts import ensure_fresh_credentials


class ExternalMailError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


_GMAIL = "https://gmail.googleapis.com/gmail/v1/users/me"
_GRAPH = "https://graph.microsoft.com/v1.0/me"


def _request(
    db: Session,
    integration: CalendarIntegration,
    method: str,
    url: str,
    **kwargs: Any,
) -> httpx.Response:
    try:
        credentials = ensure_fresh_credentials(db, integration)
    except ConnectorError as exc:
        raise ExternalMailError(str(exc), status_code=exc.status_code) from exc
    headers = dict(kwargs.pop("headers", {}))
    headers["Authorization"] = f"Bearer {credentials['access_token']}"
    try:
        response = httpx.request(method, url, headers=headers, timeout=30.0, **kwargs)
    except httpx.HTTPError as exc:
        raise ExternalMailError("O provedor de e-mail não respondeu. Tente novamente.") from exc
    if response.status_code == 401:
        raise ExternalMailError("A autorização da conta expirou. Reconecte-a na Agenda.", status_code=409)
    if response.status_code == 403:
        raise ExternalMailError(
            "A conta não autorizou acesso ao e-mail. Reconecte-a e aceite as permissões solicitadas.",
            status_code=403,
        )
    if response.status_code >= 400:
        raise ExternalMailError(f"O provedor recusou a operação (HTTP {response.status_code}).")
    return response


def _b64url_decode(value: str) -> str:
    padding = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(value + padding).decode("utf-8", errors="replace")
    except (ValueError, TypeError):
        return ""


def _gmail_headers(payload: dict[str, Any]) -> dict[str, str]:
    return {
        str(item.get("name", "")).lower(): str(item.get("value", ""))
        for item in payload.get("headers", [])
    }


def _gmail_body(payload: dict[str, Any]) -> tuple[str, str]:
    html = ""
    text = ""
    stack = [payload]
    while stack:
        part = stack.pop()
        mime = str(part.get("mimeType") or "")
        data = str((part.get("body") or {}).get("data") or "")
        if data and mime == "text/html" and not html:
            html = _b64url_decode(data)
        elif data and mime == "text/plain" and not text:
            text = _b64url_decode(data)
        stack.extend(reversed(part.get("parts") or []))
    return html, text


def _gmail_message(raw: dict[str, Any], *, full: bool = False) -> dict[str, Any]:
    payload = raw.get("payload") or {}
    headers = _gmail_headers(payload)
    labels = set(raw.get("labelIds") or [])
    result: dict[str, Any] = {
        "messageId": str(raw.get("id") or ""),
        "id": str(raw.get("id") or ""),
        "subject": headers.get("subject") or "(sem assunto)",
        "fromAddress": headers.get("from") or "",
        "toAddress": headers.get("to") or "",
        "ccAddress": headers.get("cc") or "",
        "receivedTime": str(raw.get("internalDate") or ""),
        "summary": str(raw.get("snippet") or ""),
        "status": "0" if "UNREAD" in labels else "1",
        "hasAttachment": int(any((part.get("filename") for part in payload.get("parts") or []))),
        "folderId": next((label for label in ("INBOX", "SENT", "DRAFT", "SPAM", "TRASH") if label in labels), ""),
        "provider": "google",
    }
    if full:
        html, text = _gmail_body(payload)
        result["htmlContent"] = html or None
        result["content"] = html or escape(text).replace("\n", "<br>")
    return result


def _address(value: Any) -> str:
    if isinstance(value, dict):
        item = value.get("emailAddress") or value
        return str(item.get("address") or item.get("name") or "")
    return ""


def _addresses(values: Any) -> str:
    return ", ".join(filter(None, (_address(value) for value in (values or []))))


def _graph_message(raw: dict[str, Any], *, full: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "messageId": str(raw.get("id") or ""),
        "id": str(raw.get("id") or ""),
        "subject": str(raw.get("subject") or "(sem assunto)"),
        "fromAddress": _address(raw.get("from") or raw.get("sender")),
        "toAddress": _addresses(raw.get("toRecipients")),
        "ccAddress": _addresses(raw.get("ccRecipients")),
        "receivedTime": str(raw.get("receivedDateTime") or raw.get("sentDateTime") or ""),
        "summary": str(raw.get("bodyPreview") or ""),
        "status": "1" if raw.get("isRead") else "0",
        "hasAttachment": int(bool(raw.get("hasAttachments"))),
        "provider": "microsoft",
    }
    if full:
        body = raw.get("body") or {}
        content = str(body.get("content") or "")
        result["htmlContent"] = content if str(body.get("contentType", "")).lower() == "html" else None
        result["content"] = content
    return result


def list_folders(db: Session, integration: CalendarIntegration) -> list[dict[str, Any]]:
    if integration.provider == "google_calendar":
        body = _request(db, integration, "GET", f"{_GMAIL}/labels").json()
        visible = {"INBOX", "DRAFT", "SENT", "SPAM", "TRASH", "IMPORTANT", "STARRED"}
        return [
            {"folderId": item["id"], "id": item["id"], "folderName": item.get("name", item["id"]), "folderType": item["id"]}
            for item in body.get("labels", []) if item.get("id") in visible or item.get("type") == "user"
        ]
    body = _request(
        db, integration, "GET", f"{_GRAPH}/mailFolders",
        params={"$top": "100", "$select": "id,displayName,wellKnownName"},
    ).json()
    return [
        {"folderId": item["id"], "id": item["id"], "folderName": item.get("displayName", "Pasta"), "folderType": item.get("wellKnownName") or item.get("displayName")}
        for item in body.get("value", [])
    ]


def list_messages(
    db: Session, integration: CalendarIntegration, *, folder: str | None, limit: int, start: int,
) -> list[dict[str, Any]]:
    limit = min(max(limit, 1), 100)
    start = max(start, 1)
    if integration.provider == "google_calendar":
        params: dict[str, str] = {"maxResults": str(min(start - 1 + limit, 500))}
        if folder:
            params["labelIds"] = folder
        listing = _request(db, integration, "GET", f"{_GMAIL}/messages", params=params).json()
        result = []
        for item in (listing.get("messages") or [])[start - 1 : start - 1 + limit]:
            raw = _request(
                db, integration, "GET", f"{_GMAIL}/messages/{quote(str(item['id']), safe='')}",
                params={"format": "metadata", "metadataHeaders": ["Subject", "From", "To", "Cc", "Date"]},
            ).json()
            result.append(_gmail_message(raw))
        return result
    folder_id = quote(folder or "inbox", safe="")
    fields = "id,subject,from,sender,toRecipients,ccRecipients,receivedDateTime,sentDateTime,bodyPreview,isRead,hasAttachments"
    body = _request(
        db, integration, "GET", f"{_GRAPH}/mailFolders/{folder_id}/messages",
        params={"$top": str(limit), "$skip": str(start - 1), "$orderby": "receivedDateTime desc", "$select": fields},
    ).json()
    return [_graph_message(item) for item in body.get("value", [])]


def get_message(db: Session, integration: CalendarIntegration, message_id: str) -> dict[str, Any]:
    encoded = quote(message_id, safe="")
    if integration.provider == "google_calendar":
        raw = _request(db, integration, "GET", f"{_GMAIL}/messages/{encoded}", params={"format": "full"}).json()
        _request(db, integration, "POST", f"{_GMAIL}/messages/{encoded}/modify", json={"removeLabelIds": ["UNREAD"]})
        return _gmail_message(raw, full=True)
    fields = "id,subject,from,sender,toRecipients,ccRecipients,receivedDateTime,sentDateTime,body,bodyPreview,isRead,hasAttachments"
    raw = _request(db, integration, "GET", f"{_GRAPH}/messages/{encoded}", params={"$select": fields}).json()
    if not raw.get("isRead"):
        _request(db, integration, "PATCH", f"{_GRAPH}/messages/{encoded}", json={"isRead": True})
    return _graph_message(raw, full=True)


def act_on_messages(
    db: Session,
    integration: CalendarIntegration,
    message_ids: list[str],
    action: str,
    *,
    destination: str | None = None,
) -> None:
    for message_id in message_ids:
        encoded = quote(message_id, safe="")
        if integration.provider == "google_calendar":
            add: list[str] = []
            remove: list[str] = []
            if action == "lida": remove = ["UNREAD"]
            elif action == "nao_lida": add = ["UNREAD"]
            elif action == "mover" and destination:
                add, remove = [destination], ["INBOX"]
            else:
                continue
            _request(db, integration, "POST", f"{_GMAIL}/messages/{encoded}/modify", json={"addLabelIds": add, "removeLabelIds": remove})
        elif action in {"lida", "nao_lida"}:
            _request(db, integration, "PATCH", f"{_GRAPH}/messages/{encoded}", json={"isRead": action == "lida"})
        elif action == "mover" and destination:
            _request(db, integration, "POST", f"{_GRAPH}/messages/{encoded}/move", json={"destinationId": destination})


def send_message(
    db: Session,
    integration: CalendarIntegration,
    *,
    to: str,
    subject: str,
    html: str,
    cc: str | None = None,
    bcc: str | None = None,
) -> dict[str, Any]:
    recipients = [address for _, address in getaddresses([to]) if address]
    cc_list = [address for _, address in getaddresses([cc or ""]) if address]
    bcc_list = [address for _, address in getaddresses([bcc or ""]) if address]
    if not recipients:
        raise ExternalMailError("Informe ao menos um destinatário válido.", status_code=422)
    if integration.provider == "google_calendar":
        message = EmailMessage()
        message["To"] = ", ".join(recipients)
        if cc_list: message["Cc"] = ", ".join(cc_list)
        if bcc_list: message["Bcc"] = ", ".join(bcc_list)
        message["Subject"] = subject
        message.set_content("Esta mensagem contém conteúdo HTML.")
        message.add_alternative(html, subtype="html")
        raw = base64.urlsafe_b64encode(message.as_bytes()).rstrip(b"=").decode()
        return _request(db, integration, "POST", f"{_GMAIL}/messages/send", json={"raw": raw}).json()
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": [{"emailAddress": {"address": item}} for item in recipients],
            "ccRecipients": [{"emailAddress": {"address": item}} for item in cc_list],
            "bccRecipients": [{"emailAddress": {"address": item}} for item in bcc_list],
        },
        "saveToSentItems": True,
    }
    _request(db, integration, "POST", f"{_GRAPH}/sendMail", json=payload)
    return {"sent": True}


def delete_message(db: Session, integration: CalendarIntegration, message_id: str) -> None:
    encoded = quote(message_id, safe="")
    if integration.provider == "google_calendar":
        _request(db, integration, "POST", f"{_GMAIL}/messages/{encoded}/trash")
    else:
        _request(db, integration, "DELETE", f"{_GRAPH}/messages/{encoded}")
