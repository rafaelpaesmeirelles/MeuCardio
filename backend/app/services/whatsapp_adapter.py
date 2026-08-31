from dataclasses import dataclass
from io import BytesIO

import httpx

from app.core.config import settings


class WhatsAppProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class SendResult:
    provider: str
    message_id: str
    billable: bool
    raw_status: str


@dataclass(frozen=True)
class MediaResult:
    content: bytes
    mime_type: str
    filename: str


class SandboxAdapter:
    def send_text(self, phone, text, *, idempotency_key):
        return SendResult("sandbox", f"sandbox-{idempotency_key[:40]}", False, "accepted")

    def send_template(self, phone, template_name, language, parameters, *, idempotency_key):
        return self.send_text(phone, template_name, idempotency_key=idempotency_key)

    def send_interactive(self, phone, body, button_id, button_title, *, idempotency_key):
        return self.send_text(phone, body, idempotency_key=idempotency_key)

    def download_media(self, media_id):
        raise WhatsAppProviderError("Mídia indisponível no sandbox.")

    def transcribe_audio(self, content, *, filename, mime_type):
        raise WhatsAppProviderError("Transcrição indisponível no sandbox.")


class MetaCloudAdapter:
    def __init__(self, client=None):
        if not settings.whatsapp_meta_configured:
            raise WhatsAppProviderError("Meta não configurada")
        self.client = client or httpx.Client(timeout=15)

    def _send(self, phone, payload, key):
        response = self.client.post(
            f"https://graph.facebook.com/{settings.whatsapp_meta_api_version}/{settings.whatsapp_phone_number_id}/messages",
            headers={"Authorization": f"Bearer {settings.whatsapp_meta_access_token}"},
            json={"messaging_product": "whatsapp", "to": phone, **payload},
        )
        try:
            data = response.json()
        except ValueError:
            data = {}
        if response.status_code >= 400:
            raise WhatsAppProviderError("Meta recusou mensagem")
        message_id = ((data.get("messages") or [{}])[0]).get("id")
        if not message_id:
            raise WhatsAppProviderError("Meta sem id")
        return SendResult("meta", message_id, True, "accepted")

    def send_text(self, phone, text, *, idempotency_key):
        return self._send(phone, {"type": "text", "text": {"body": text[:4096], "preview_url": False}}, idempotency_key)

    def send_template(self, phone, template_name, language, parameters, *, idempotency_key):
        if not template_name:
            raise WhatsAppProviderError("Template ausente")
        components = ([{"type": "body", "parameters": [{"type": "text", "text": str(value)[:1024]} for value in parameters]}] if parameters else [])
        return self._send(phone, {"type": "template", "template": {"name": template_name, "language": {"code": language}, "components": components}}, idempotency_key)

    def send_interactive(self, phone, body, button_id, button_title, *, idempotency_key):
        if not button_id.startswith("corvia:undo:"):
            raise WhatsAppProviderError("Botão não permitido")
        return self._send(phone, {"type": "interactive", "interactive": {"type": "button", "body": {"text": body[:1024]}, "action": {"buttons": [{"type": "reply", "reply": {"id": button_id[:256], "title": button_title[:20]}}]}}}, idempotency_key)

    def download_media(self, media_id):
        safe_id = str(media_id or "")
        if not safe_id or not safe_id.replace("-", "").replace("_", "").isalnum():
            raise WhatsAppProviderError("Identificador de mídia inválido")
        headers = {"Authorization": f"Bearer {settings.whatsapp_meta_access_token}"}
        metadata = self.client.get(f"https://graph.facebook.com/{settings.whatsapp_meta_api_version}/{safe_id}", headers=headers)
        if metadata.status_code >= 400:
            raise WhatsAppProviderError("Meta recusou consulta de mídia")
        try:
            info = metadata.json()
        except ValueError as exc:
            raise WhatsAppProviderError("Metadados de mídia inválidos") from exc
        url = info.get("url")
        size = int(info.get("file_size") or 0)
        if not url or size > settings.whatsapp_max_media_bytes:
            raise WhatsAppProviderError("Mídia ausente ou acima do limite")
        response = self.client.get(url, headers=headers)
        if response.status_code >= 400 or len(response.content) > settings.whatsapp_max_media_bytes:
            raise WhatsAppProviderError("Falha ou limite excedido no download")
        mime_type = (response.headers.get("content-type") or info.get("mime_type") or "application/octet-stream").split(";", 1)[0].lower()
        return MediaResult(response.content, mime_type, f"meta-{safe_id}")

    def transcribe_audio(self, content, *, filename, mime_type):
        if not settings.openai_api_key:
            raise WhatsAppProviderError("Provedor de transcrição não configurado")
        from openai import OpenAI
        stream = BytesIO(content)
        stream.name = filename or "audio.ogg"
        try:
            result = OpenAI(api_key=settings.openai_api_key).audio.transcriptions.create(
                model=settings.whatsapp_transcription_model,
                file=stream,
            )
        except Exception as exc:
            raise WhatsAppProviderError("Falha no provedor de transcrição") from exc
        text = (getattr(result, "text", None) or "").strip()
        if not text:
            raise WhatsAppProviderError("Transcrição vazia")
        return text


def get_adapter():
    return SandboxAdapter() if settings.whatsapp_provider == "sandbox" else MetaCloudAdapter()
