"""Opinião rápida de ECG sem cadastro de paciente ou persistência clínica.

O arquivo validado existe apenas em memória durante a chamada ao provedor.
Nenhum nome de arquivo, traçado ou conteúdo da resposta é gravado no banco;
somente metadados operacionais sem PHI entram no log de auditoria.
"""
from __future__ import annotations

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
from app.services.ia import ecg_assist

router = APIRouter(prefix="/api/ecg-ia", tags=["ecg-ia"])
logger = logging.getLogger(__name__)
MAX_ECG_BYTES = 20 * 1024 * 1024


def _availability() -> tuple[bool, str | None]:
    """Expõe o bloqueio operacional sem revelar credenciais ou segredos."""
    if not settings.ai_enabled:
        return False, "ai_disabled"
    if not settings.ai_clinical_multimodal_enabled:
        return False, "multimodal_disabled"
    if not ecg_assist.supported_media_types():
        return False, "provider_unsupported"
    if not ecg_assist.provider_configured():
        return False, "provider_not_configured"
    return True, None


def _operational_day_utc_bounds(now_utc: datetime | None = None) -> tuple[datetime, datetime]:
    current = now_utc or datetime.now(timezone.utc)
    zone = ZoneInfo(settings.fuso_operacao)
    local_day = current.astimezone(zone).date()
    start_local = datetime.combine(local_day, time.min, tzinfo=zone)
    end_local = datetime.combine(local_day + timedelta(days=1), time.min, tzinfo=zone)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _ensure_available() -> None:
    enabled, _ = _availability()
    if not enabled:
        raise HTTPException(
            status_code=503,
            detail="A assistência multimodal clínica está desligada nesta instalação.",
        )


@router.get("/status")
def status_ia_ecg():
    enabled, unavailable_reason = _availability()
    return {
        "enabled": enabled,
        "unavailable_reason": unavailable_reason,
        "supported_media_types": list(ecg_assist.supported_media_types()),
        "max_size_bytes": MAX_ECG_BYTES,
        "stores_file": False,
    }


@router.post("/analisar")
async def analisar_ecg_rapido(
    arquivo: UploadFile = File(...),
    confirm_external_processing: bool = Form(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    if not confirm_external_processing:
        raise HTTPException(
            status_code=422,
            detail="Confirme o processamento externo para solicitar a opinião da IA.",
        )
    _ensure_available()
    content = await arquivo.read(MAX_ECG_BYTES + 1)
    if len(content) > MAX_ECG_BYTES:
        raise HTTPException(status_code=413, detail="O ECG precisa ter no máximo 20 MB.")
    try:
        original_name = safe_filename(arquivo.filename, "ecg")
        media_type = validate_file(content, original_name, "exam")
    except UploadRejected as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    if media_type not in ecg_assist.supported_media_types():
        raise HTTPException(
            status_code=422,
            detail="O provedor configurado não analisa este formato de ECG. Envie um formato aceito.",
        )

    # A reserva usa a mesma ação do fluxo longitudinal: a cota diária é única
    # por médico, independentemente de a opinião ser rápida ou de prontuário.
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
        action="ai_ecg_transfer_attempt",
        entity="ecg_quick_opinion",
        entity_id=str(user.id),
        detail={
            "mode": "quick_opinion",
            "provider": settings.ai_provider,
            "external_processing_confirmed": confirm_external_processing,
            "media_type": media_type,
            "size_bytes": len(content),
            "stores_file": False,
            "status": "reserved",
        },
    )
    db.add(attempt)
    db.commit()
    attempt_id = attempt.id

    def record_outcome(status: str, **detail: object) -> None:
        db.add(AuditLog(
            user_id=user.id,
            action="ai_ecg_transfer_outcome",
            entity="ecg_quick_opinion",
            entity_id=str(user.id),
            detail={
                "mode": "quick_opinion",
                "transfer_attempt_id": attempt_id,
                "provider": settings.ai_provider,
                "status": status,
                **detail,
            },
        ))
        db.commit()

    try:
        # Os SDKs multimodais usados aqui são síncronos. Executá-los direto
        # nesta rota async bloqueava o event loop do worker enquanto a IA
        # processava a imagem, fazendo a tela parecer travada sob concorrência.
        analysis = await run_in_threadpool(ecg_assist.analyze_ecg, content, media_type)
    except ValueError as error:
        db.rollback()
        record_outcome("invalid_response")
        if "exige ECG" in str(error) or "Formato" in str(error):
            raise HTTPException(status_code=422, detail=str(error)) from error
        raise HTTPException(
            status_code=502,
            detail="O provedor devolveu uma sugestão clínica inválida. Nada foi armazenado.",
        ) from error
    except Exception as error:
        db.rollback()
        # Não inclui nome, bytes ou conteúdo do ECG. Mantém no log operacional
        # apenas a pilha e a mensagem técnica devolvida pelo SDK/provedor.
        logger.exception(
            "Falha na análise multimodal rápida de ECG (provider=%s, error_type=%s)",
            settings.ai_provider,
            type(error).__name__,
        )
        record_outcome("provider_error", error_type=type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail=f"O provedor multimodal não respondeu ({type(error).__name__}). Nada foi armazenado.",
        ) from error

    analysis["payload"]["disclaimer"] = (
        "Sugestão gerada por IA. Não é laudo, não é salva no prontuário e exige revisão médica."
    )
    record_outcome(
        "success",
        provider=analysis["provider"],
        model=analysis["model"],
        prompt_version=analysis["prompt_version"],
        tokens_input=analysis["tokens_input"],
        tokens_output=analysis["tokens_output"],
    )
    return {
        "payload": analysis["payload"],
        "provider": analysis["provider"],
        "model": analysis["model"],
        "prompt_version": analysis["prompt_version"],
        "stored": False,
    }
