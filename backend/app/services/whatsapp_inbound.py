import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import HTTPException

from app.core.config import settings
from app.core.uploads import UploadRejected, validate_file
from app.models.user import User
from app.models.whatsapp import (
    WhatsAppCommand,
    WhatsAppLink,
    WhatsAppMessage,
    WhatsAppUsageMetric,
    WhatsAppWebhookEvent,
)
from app.services.cofre import cifrar_campo, decifrar_campo, guardar
from app.services.whatsapp_adapter import WhatsAppProviderError, get_adapter
from app.services.ia.clinical_file_sanitizer import UnsafeClinicalFile,contains_identifier,sanitize_clinical_file
from app.services.whatsapp_assistant import (
    complete_pairing,
    create_command,
    decrypt_payload,
    enforce_cost_headroom,
    require_positive_tariff,
    undo_command,
    _audit,
)
from app.services.whatsapp_outbox import deliver_once
from app.services.whatsapp_security import (
    allow_rate,
    canonical_json,
    detect_pii,
    payload_hash,
    phone_hash,
    trusted_interactive,
    utcnow,
)


def iter_meta_messages(payload):
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            for message in value.get("messages") or []:
                yield message


def _interactive_action(message):
    interactive = message.get("interactive") or {}
    reply = interactive.get("button_reply") or interactive.get("list_reply") or {}
    return trusted_interactive(reply.get("id"))


def _message_text(message):
    if message.get("type") == "text":
        return str((message.get("text") or {}).get("body") or "").strip()
    action = _interactive_action(message)
    return action.get("text", "") if action and action.get("action") == "text" else ""


def _media_filename(message_type, mime_type, media_id):
    suffixes = {
        "application/pdf": ".pdf", "image/jpeg": ".jpg", "image/png": ".png",
        "image/webp": ".webp", "text/plain": ".txt", "text/csv": ".csv",
        "audio/ogg": ".ogg", "audio/mpeg": ".mp3", "audio/mp4": ".m4a",
        "audio/aac": ".aac", "audio/amr": ".amr",
    }
    return f"whatsapp-{str(media_id)[:40]}{suffixes.get(mime_type, '.bin')}"


def _validate_media(message_type, media):
    if not media.content or len(media.content) > settings.whatsapp_max_media_bytes:
        raise UploadRejected(413, "Mídia vazia ou acima do limite.")
    filename = _media_filename(message_type, media.mime_type, media.filename)
    if message_type == "audio":
        signatures = {
            "audio/ogg": lambda data: data.startswith(b"OggS"),
            "audio/mpeg": lambda data: data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0),
            "audio/mp4": lambda data: len(data) >= 12 and data[4:8] == b"ftyp",
            "audio/aac": lambda data: len(data) >= 2 and data[0] == 0xFF and data[1] & 0xF0 == 0xF0,
            "audio/amr": lambda data: data.startswith((b"#!AMR\n", b"#!AMR-WB\n")),
        }
        validator = signatures.get(media.mime_type)
        if validator is None or not validator(media.content):
            raise UploadRejected(422, "Formato de áudio não permitido.")
        return media.mime_type, filename
    validated = validate_file(media.content, filename, "clinical_exam")
    if message_type == "image" and not validated.startswith("image/"):
        raise UploadRejected(422, "A mídia não é uma imagem válida.")
    if message_type == "document" and validated not in {"application/pdf", "text/plain", "text/csv"}:
        raise UploadRejected(422, "Documento não permitido.")
    return validated, filename


def _safe_reply(result):
    if result.get("undo_token") and result.get("command_id"):
        command_id, token = result["command_id"], result["undo_token"]
        return {"text": f"Ação concluída. Use o botão ou responda DESFAZER {command_id} {token}", "button_id": f"corvia:undo:{command_id}:{token}", "button_title": "Desfazer"}
    if result.get("requires_confirmation"):
        return {"text": "A ação exige confirmação explícita e PIN dentro do CorVIA.", "button_id": None, "button_title": None}
    return {"text": result.get("message") or "Comando recebido. Confira no CorVIA.", "button_id": None, "button_title": None}


def _deliver_reply(db, *, link, phone, source_id, result, adapter):
    if settings.whatsapp_provider != "meta":
        return None
    cost = require_positive_tariff(settings.whatsapp_meta_message_cost_microunits, "Meta")
    enforce_cost_headroom(db, link.user_id, cost)
    reply = _safe_reply(result)
    mode = "interactive" if reply.get("button_id") else "text"
    delivery = deliver_once(
        db, adapter=adapter, idempotency_key=f"inbound-reply:{source_id}", owner_id=link.user_id,
        link_id=link.id, phone=phone, text=reply["text"], mode=mode,
        button_id=reply.get("button_id") or "", button_title=reply.get("button_title") or "Desfazer",
        retention_days=link.retention_days, estimated_cost_microunits=cost,
    )
    if delivery.status == "sent" and delivery.result:
        if not db.query(WhatsAppMessage).filter(WhatsAppMessage.provider_message_id == delivery.result.message_id).first():
            db.add(WhatsAppMessage(
                link_id=link.id, owner_id=link.user_id, provider_message_id=delivery.result.message_id,
                direction="outbound", message_type=mode,
                payload_cipher=cifrar_campo(canonical_json({"reply_to": source_id, "mode": mode}), link.user_id),
                status="accepted", authorization_level=1, meta_billable=True,
                estimated_cost_microunits=cost, expires_at=utcnow()+timedelta(days=link.retention_days),
            ))
            outbox = db.query(__import__("app.models.whatsapp", fromlist=["WhatsAppOutboundOutbox"]).WhatsAppOutboundOutbox).filter_by(id=delivery.outbox_id).first()
            if outbox:
                outbox.estimated_cost_microunits = 0
    return delivery.status


def _process_text(db, *, user, link, row, text, message_id, interactive_action=None):
    if interactive_action and interactive_action.get("action") == "undo":
        command = db.query(WhatsAppCommand).filter(WhatsAppCommand.id == interactive_action["command_id"], WhatsAppCommand.owner_id == user.id).first()
        result = undo_command(db, user, command, token=interactive_action["token"])
        row.status = "processed"
        return {"command_id": command.id, "message": result.get("status", "Desfeito.")}
    undo_match = __import__("re").fullmatch(r"\s*DESFAZER\s+(\d+)\s+([A-Za-z0-9_-]{16,256})\s*", text or "", __import__("re").I)
    if undo_match:
        command = db.query(WhatsAppCommand).filter(WhatsAppCommand.id == int(undo_match.group(1)), WhatsAppCommand.owner_id == user.id).first()
        result = undo_command(db, user, command, token=undo_match.group(2)); row.status = "processed"
        return {"command_id": command.id, "message": result.get("status", "Desfeito.")}
    pii = detect_pii(text)
    if pii:
        row.pii_kinds = pii; row.status = "awaiting_anonymization_confirmation"
        return {"message": "Identificadores detectados. Revise e anonimize dentro do CorVIA."}
    command, result, confirm, undo = create_command(
        db, user, link, text=text, idempotency_key=f"wa:{message_id}", explicit_kind=None,
        arguments={}, message_id=row.id,
    )
    row.status = "processed" if command.status in {"completed", "awaiting_confirmation", "needs_clarification"} else command.status
    # O nonce retornado por create_command nunca sai do processo de ingestão.
    # Para comandos originados no WhatsApp ele é reemitido exclusivamente na
    # área autenticada do CorVIA.
    return {"command_id": command.id, "message": result.get("mensagem", "Comando recebido."), "requires_confirmation": bool(confirm), "undo_token": undo}


def process_meta_message(db, message, *, adapter=None):
    adapter = adapter or get_adapter()
    message_id = str(message.get("id") or "")
    phone = "".join(char for char in str(message.get("from") or "") if char.isdigit())
    if not message_id or not 8 <= len(phone) <= 15:
        return {"status": "invalid"}
    if db.query(WhatsAppWebhookEvent).filter(WhatsAppWebhookEvent.provider_event_id == message_id).first():
        return {"status": "duplicate"}
    if not allow_rate(f"inbound:{phone}"):
        return {"status": "rate_limited"}
    provider_created = datetime.fromtimestamp(int(message.get("timestamp") or 0), timezone.utc) if message.get("timestamp") else utcnow()
    if provider_created < utcnow() - timedelta(seconds=settings.whatsapp_replay_window_seconds):
        db.add(WhatsAppWebhookEvent(provider_event_id=message_id, payload_hash=payload_hash(canonical_json(message).encode()), provider_created_at=provider_created, status="rejected_replay", failure_code="stale_timestamp"))
        return {"status": "rejected_replay"}
    link = db.query(WhatsAppLink).filter(WhatsAppLink.phone_hash == phone_hash(phone), WhatsAppLink.status == "active").first()
    text = _message_text(message)
    paired_now = False
    if not link and text.upper().startswith("VINCULAR "):
        code = text.split(None, 1)[1].strip()
        pairing_keys=(f"pairing:{phone}",f"pairing-code:{token_hash(code,'pairing-attempt')}","pairing-global")
        limits=(settings.whatsapp_pairing_max_attempts,settings.whatsapp_pairing_max_attempts,max(100,settings.whatsapp_pairing_max_attempts*20))
        if not all(allow_rate(key,limit=limit,window_seconds=settings.whatsapp_pairing_ttl_seconds) for key,limit in zip(pairing_keys,limits)):
            return {"status": "pairing_rate_limited"}
        link = complete_pairing(db, code=code, phone=phone); paired_now = True
    event = WhatsAppWebhookEvent(provider_event_id=message_id, payload_hash=payload_hash(canonical_json(message).encode()), link_id=link.id if link else None, provider_created_at=provider_created, status="processing")
    db.add(event); db.flush()
    if not link:
        event.status = "unlinked"; event.processed_at = utcnow(); return {"status": "unlinked"}
    user = db.query(User).filter(User.id == link.user_id).first()
    message_type = str(message.get("type") or "unsupported")
    payload = {"provider_type": message_type, "text": text}
    row = WhatsAppMessage(
        link_id=link.id, owner_id=link.user_id, provider_message_id=message_id, direction="inbound",
        message_type=message_type, payload_cipher=cifrar_campo(canonical_json(payload), link.user_id),
        status="received", authorization_level=1, expires_at=utcnow()+timedelta(days=link.retention_days),
    )
    db.add(row); db.flush()
    _audit(db, user.id, "whatsapp_inbound_received", "whatsapp_message", row.id, detail={"type": message_type})
    try:
        if paired_now:
            row.status = "processed"; result = {"status": "paired", "message": "WhatsApp vinculado com segurança ao CorVIA."}
        elif message_type in {"text", "interactive"}:
            action = _interactive_action(message) if message_type == "interactive" else None
            if message_type == "interactive" and not action:
                row.status = "blocked_security"; result = {"status": row.status, "message": "Resposta interativa não reconhecida."}
            else:
                result = _process_text(db, user=user, link=link, row=row, text=text, message_id=message_id, interactive_action=action)
        elif message_type in {"audio", "image", "document"}:
            media_meta = message.get(message_type) or {}; media = adapter.download_media(media_meta.get("id")); mime_type, filename = _validate_media(message_type, media)
            if message_type == "audio":
                storage_key = guardar(media.content, link.user_id, raiz=Path(settings.whatsapp_media_dir));payload.update({"media_storage_key": storage_key, "mime_type": mime_type, "filename": filename, "sha256": __import__("hashlib").sha256(media.content).hexdigest(), "size_bytes": len(media.content)})
                cost = require_positive_tariff(settings.whatsapp_transcription_cost_microunits, "transcrição"); enforce_cost_headroom(db, user.id, cost)
                try:
                    transcript = adapter.transcribe_audio(media.content, filename=filename, mime_type=mime_type)
                    payload["transcript"] = transcript; row.status = "awaiting_transcript_review"
                    db.add(WhatsAppUsageMetric(owner_id=user.id, link_id=link.id, idempotency_key=f"transcription:{message_id}", operation="audio_transcription", provider="openai", model=settings.whatsapp_transcription_model, estimated_cost_microunits=cost, success=True))
                    result = {"status": row.status, "message": "Áudio transcrito. Confira a interpretação no CorVIA antes de qualquer ação."}
                except WhatsAppProviderError:
                    row.status = "transcription_unavailable"; result = {"status": row.status, "message": "Transcrição indisponível; nenhuma ação foi executada."}
            else:
                safe_extract=""
                if mime_type=="application/pdf":
                    import fitz
                    with fitz.open(stream=media.content,filetype="pdf") as document:safe_extract="\n".join(page.get_text("text") for page in document)[:30000]
                elif mime_type in {"text/plain","text/csv"}:safe_extract=media.content.decode("utf-8-sig")[:30000]
                try:sanitized,sanitized_type=sanitize_clinical_file(media.content,mime_type)
                except UnsafeClinicalFile:
                    payload.update({"mime_type":mime_type,"filename":filename,"rejected_before_storage":True});row.status="media_rejected_identifiers";result={"status":row.status,"message":"O arquivo parece conter identificadores visíveis ou não pôde ser verificado localmente. Envie uma cópia anonimizada."};row.payload_cipher=cifrar_campo(canonical_json(payload),link.user_id)
                else:
                    storage_key=guardar(sanitized,link.user_id,raiz=Path(settings.whatsapp_media_dir));payload.update({"media_storage_key":storage_key,"mime_type":sanitized_type,"filename":filename,"sha256":__import__("hashlib").sha256(sanitized).hexdigest(),"size_bytes":len(sanitized),"sanitized":True,"sanitized_extract":safe_extract if safe_extract and not contains_identifier(safe_extract) else ""});row.status="awaiting_media_review";result={"status":row.status,"message":"Arquivo sanitizado localmente e recebido. Aprove ou rejeite o uso dentro do CorVIA."};row.payload_cipher=cifrar_campo(canonical_json(payload),link.user_id)
            row.payload_cipher = cifrar_campo(canonical_json(payload), link.user_id)
        else:
            row.status = "unsupported"; result = {"status": row.status, "message": "Formato não suportado."}
        event.status = "processed"; event.processed_at = utcnow()
        try:
            result["reply_status"] = _deliver_reply(db, link=link, phone=phone, source_id=message_id, result=result, adapter=adapter)
        except (HTTPException, WhatsAppProviderError) as exc:
            event.failure_code = "reply_fail_closed"; result["reply_status"] = "blocked"
        public_result=dict(result);public_result.pop("confirmation_token",None);public_result.pop("undo_token",None)
        return public_result
    except (HTTPException, UploadRejected, WhatsAppProviderError,UnsafeClinicalFile) as exc:
        row.status = "failed"; event.status = "failed"; event.failure_code = type(exc).__name__; event.processed_at = utcnow()
        return {"status": "failed", "error": type(exc).__name__}
