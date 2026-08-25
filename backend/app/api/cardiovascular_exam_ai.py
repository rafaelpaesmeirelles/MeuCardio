"""Central transitória de IA para exames cardiovasculares.

O CorVIA não incorpora arquivos, textos ou respostas ao prontuário. O processador
externo recebe somente uma cópia sanitizada após consentimento versionado.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.core.uploads import UploadRejected, safe_filename, validate_file
from app.models.audit import AuditLog
from app.models.user import User
from app.services.ia import cardiovascular_exam_assist
from app.services.ia.cardiovascular_exam_assist import ClinicalFile
from app.services.ia.clinical_file_sanitizer import (
    UnsafeClinicalFile,
    contains_identifier,
    sanitize_clinical_file,
)

router = APIRouter(prefix="/api/exames-ia", tags=["exames-ia"])
logger = logging.getLogger(__name__)
MAX_FILES = 5
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_BYTES = 40 * 1024 * 1024
MAX_TEXT_CHARS = 16_000
CONSENT_VERSION = "clinical-ai-external-processing-v2-2026-08-25"


def _availability() -> tuple[bool, str | None]:
    if not settings.ai_enabled:
        return False, "ai_disabled"
    if not settings.ai_clinical_multimodal_enabled:
        return False, "multimodal_disabled"
    if not settings.ai_clinical_data_controls_approved:
        return False, "data_controls_not_approved"
    if settings.ai_provider != "openai":
        return False, "provider_unsupported"
    if not cardiovascular_exam_assist.provider_configured():
        return False, "provider_not_configured"
    return True, None


def _operational_day_utc_bounds(now_utc: datetime | None = None) -> tuple[datetime, datetime]:
    current = now_utc or datetime.now(timezone.utc)
    zone = ZoneInfo(settings.fuso_operacao)
    local_day = current.astimezone(zone).date()
    start_local = datetime.combine(local_day, time.min, tzinfo=zone)
    end_local = datetime.combine(local_day + timedelta(days=1), time.min, tzinfo=zone)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _clean_text(value: str, field: str) -> str:
    cleaned = value.strip()
    if len(cleaned) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=422, detail=f"{field} precisa ter no máximo {MAX_TEXT_CHARS} caracteres.")
    if contains_identifier(cleaned):
        raise HTTPException(
            status_code=422,
            detail=f"Remova identificadores diretos de {field} antes de enviar à IA.",
        )
    return cleaned


@router.get("/status")
def status_ia_exames():
    enabled, unavailable_reason = _availability()
    return {
        "enabled": enabled,
        "unavailable_reason": unavailable_reason,
        "supported_media_types": list(cardiovascular_exam_assist.supported_media_types()),
        "exam_types": cardiovascular_exam_assist.EXAM_TYPES,
        "max_files": MAX_FILES,
        "max_file_bytes": MAX_FILE_BYTES,
        "max_total_bytes": MAX_TOTAL_BYTES,
        "persists_files_in_corvia": False,
        "provider_response_storage_requested": False,
        "external_processor": "openai",
        "consent_version": CONSENT_VERSION,
        "searches_current_guidelines": True,
        "raw_dicom_supported": False,
        "video_supported": False,
    }


@router.post("/analisar")
async def analisar_exame_cardiovascular(
    arquivos: list[UploadFile] = File(default=[]),
    exam_type: str = Form(...),
    clinical_question: str = Form(default=""),
    report_text: str = Form(default=""),
    clinical_context: str = Form(default=""),
    file_notes: str = Form(default="[]"),
    confirm_external_processing: bool = Form(...),
    confirm_deidentified: bool = Form(...),
    confirm_same_case: bool = Form(default=False),
    consent_version: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    if not confirm_external_processing or not confirm_deidentified or consent_version != CONSENT_VERSION:
        raise HTTPException(
            status_code=422,
            detail="Confirme o termo atual de processamento externo e a remoção de identificadores.",
        )
    enabled, _ = _availability()
    if not enabled:
        raise HTTPException(status_code=503, detail="A central multimodal de exames está indisponível nesta instalação.")
    if exam_type not in cardiovascular_exam_assist.EXAM_TYPES:
        raise HTTPException(status_code=422, detail="Selecione um tipo de exame cardiovascular válido.")
    if len(arquivos) > MAX_FILES:
        raise HTTPException(status_code=422, detail=f"Envie no máximo {MAX_FILES} arquivos.")
    if len(arquivos) > 1 and not confirm_same_case:
        raise HTTPException(status_code=422, detail="Confirme que todos os arquivos pertencem ao mesmo caso clínico.")

    try:
        notes_value = json.loads(file_notes)
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=422, detail="Legendas dos arquivos inválidas.") from error
    if not isinstance(notes_value, list) or len(notes_value) > MAX_FILES:
        raise HTTPException(status_code=422, detail="Legendas dos arquivos inválidas.")
    notes = [_clean_text(str(item), "legenda do arquivo")[:300] for item in notes_value]

    question = _clean_text(clinical_question, "pergunta clínica")
    report = _clean_text(report_text, "laudo/resultados")
    context = _clean_text(clinical_context, "contexto clínico")
    clinical_files: list[ClinicalFile] = []
    payload_hasher = hashlib.sha256()
    for value in (exam_type, question, report, context, *notes):
        payload_hasher.update(value.encode("utf-8"))
        payload_hasher.update(b"\x00")
    total_bytes = 0
    sanitized_total_bytes = 0
    pdf_count = 0
    for index, upload in enumerate(arquivos, start=1):
        try:
            content = await upload.read(MAX_FILE_BYTES + 1)
        finally:
            await upload.close()
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(status_code=413, detail=f"O arquivo {index} excede 20 MB.")
        total_bytes += len(content)
        if total_bytes > MAX_TOTAL_BYTES:
            raise HTTPException(status_code=413, detail="Os arquivos excedem o limite total de 40 MB.")
        try:
            filename = safe_filename(upload.filename, f"exame-{index}")
            media_type = validate_file(content, filename, "clinical_exam")
        except UploadRejected as error:
            raise HTTPException(status_code=error.status_code, detail=error.detail) from error
        if media_type not in cardiovascular_exam_assist.supported_media_types():
            raise HTTPException(status_code=422, detail=f"O formato do arquivo {index} não é analisado pelo provedor atual.")
        if media_type == "application/pdf":
            pdf_count += 1
            if pdf_count > 1:
                raise HTTPException(status_code=422, detail="Envie no máximo um PDF por análise; use as demais posições para imagens.")
        try:
            sanitized, sanitized_type = await run_in_threadpool(sanitize_clinical_file, content, media_type)
        except UnsafeClinicalFile as error:
            raise HTTPException(status_code=422, detail=f"Arquivo {index}: {error}") from error
        sanitized_total_bytes += len(sanitized)
        if sanitized_total_bytes > MAX_TOTAL_BYTES:
            raise HTTPException(status_code=413, detail="As cópias sanitizadas excedem o limite total de 40 MB.")
        payload_hasher.update(sanitized)
        clinical_files.append(ClinicalFile(
            content=sanitized,
            media_type=sanitized_type,
            file_id=f"arquivo-{index}",
            label=notes[index - 1] if index <= len(notes) else "",
        ))
    if not clinical_files and not report and not context:
        raise HTTPException(status_code=422, detail="Envie ao menos um arquivo, laudo/resultados ou contexto clínico.")

    # Uma cota única impede contornar o limite alternando entre ECG legado e
    # a central ampla de exames. O lock serializa reservas simultâneas.
    db.query(User.id).filter(User.id == user.id).with_for_update().one()
    start, end = _operational_day_utc_bounds()
    used = db.query(AuditLog.id).filter(
        AuditLog.user_id == user.id,
        AuditLog.action.in_(("ai_ecg_transfer_attempt", "ai_clinical_exam_transfer_attempt")),
        AuditLog.created_at >= start,
        AuditLog.created_at < end,
    ).count()
    if used >= settings.ai_daily_limit:
        db.rollback()
        raise HTTPException(
            status_code=429,
            detail=f"Limite diário de {settings.ai_daily_limit} análises atingido. Recomeça amanhã.",
        )

    attempt = AuditLog(
        user_id=user.id,
        action="ai_clinical_exam_transfer_attempt",
        entity="cardiovascular_exam_quick_analysis",
        entity_id=str(user.id),
        detail={
            "mode": "transient_cardiovascular_exam",
            "provider": settings.ai_provider,
            "exam_type": exam_type,
            "external_processing_confirmed": True,
            "deidentified_confirmed": True,
            "same_case_confirmed": len(clinical_files) < 2 or confirm_same_case,
            "consent_version": CONSENT_VERSION,
            "consent_payload_sha256": payload_hasher.hexdigest(),
            "file_count": len(clinical_files),
            "media_types": [item.media_type for item in clinical_files],
            "total_size_bytes": total_bytes,
            "sanitized_total_size_bytes": sanitized_total_bytes,
            "has_report_text": bool(report),
            "has_clinical_context": bool(context),
            "persists_files_in_corvia": False,
            "provider_response_storage_requested": False,
            "status": "reserved",
        },
    )
    db.add(attempt)
    db.commit()
    attempt_id = attempt.id

    def record_outcome(status: str, **detail: object) -> None:
        db.add(AuditLog(
            user_id=user.id,
            action="ai_clinical_exam_transfer_outcome",
            entity="cardiovascular_exam_quick_analysis",
            entity_id=str(user.id),
            detail={
                "mode": "transient_cardiovascular_exam",
                "transfer_attempt_id": attempt_id,
                "provider": settings.ai_provider,
                "status": status,
                **detail,
            },
        ))
        db.commit()

    try:
        analysis = await run_in_threadpool(
            cardiovascular_exam_assist.analyze_exam,
            clinical_files,
            exam_type,
            question,
            report,
            context,
        )
    except ValueError as error:
        db.rollback()
        record_outcome("invalid_response")
        logger.warning("Resposta clínica multimodal recusada: %s", type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail="A IA não devolveu uma análise clínica íntegra e atualizada. O CorVIA não persistiu o conteúdo.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.exception(
            "Falha na central multimodal cardiovascular (provider=%s, error_type=%s)",
            settings.ai_provider,
            type(error).__name__,
        )
        record_outcome("provider_error", error_type=type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail=f"O provedor multimodal não respondeu ({type(error).__name__}). O CorVIA não persistiu o conteúdo.",
        ) from error

    record_outcome(
        "success",
        model=analysis["model"],
        prompt_version=analysis["prompt_version"],
        tokens_input=analysis["tokens_input"],
        tokens_output=analysis["tokens_output"],
        source_count=len(analysis["web_sources"]),
    )
    return {
        "payload": analysis["payload"],
        "web_sources": analysis["web_sources"],
        "provider": analysis["provider"],
        "model": analysis["model"],
        "prompt_version": analysis["prompt_version"],
        "persisted_in_corvia": False,
        "provider_response_storage_requested": False,
    }
