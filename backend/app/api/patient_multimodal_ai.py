from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.core.uploads import UploadRejected, safe_filename, validate_file
from app.models.audit import AuditLog
from app.models.patient_multimodal import PatientMultimodalAISuggestion, PatientMultimodalExamRecord
from app.models.prontuario import ClinicalEncounter, PatientClinicalItem, PatientExamResult
from app.models.user import User
from app.services import cofre
from app.services.clinical_ownership import encounter_for_user, patient_profile_for_user
from app.services.ia import cardiovascular_exam_assist
from app.services.ia.cardiovascular_exam_assist import ClinicalFile
from app.services.ia.clinical_file_sanitizer import UnsafeClinicalFile, contains_identifier, sanitize_clinical_file

router = APIRouter(prefix="/api/pacientes", tags=["prontuario-multimodal"])
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_CONTEXT_CHARS = 28_000


class SuggestionRequest(BaseModel):
    confirm_external_processing: Literal[True]
    clinical_question: str = ""


class SuggestionReview(BaseModel):
    decision: Literal["accept", "reject"]
    final_interpretation: str | None = None
    review_note: str | None = None


def _operational_day_utc_bounds(now_utc: datetime | None = None) -> tuple[datetime, datetime]:
    current = now_utc or datetime.now(timezone.utc)
    zone = ZoneInfo(settings.fuso_operacao)
    local_day = current.astimezone(zone).date()
    start_local = datetime.combine(local_day, time.min, tzinfo=zone)
    end_local = datetime.combine(local_day + timedelta(days=1), time.min, tzinfo=zone)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _exam_for_user(pid: int, exam_id: int, db: Session, user) -> PatientMultimodalExamRecord:
    patient_profile_for_user(pid, db, user)
    row = db.get(PatientMultimodalExamRecord, exam_id)
    if not row or row.owner_id != user.id or row.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Exame multimodal não encontrado.")
    return row


def _suggestion_for_user(pid: int, exam_id: int, suggestion_id: int, db: Session, user) -> PatientMultimodalAISuggestion:
    _exam_for_user(pid, exam_id, db, user)
    row = db.get(PatientMultimodalAISuggestion, suggestion_id)
    if (
        not row
        or row.owner_id != user.id
        or row.patient_profile_id != pid
        or row.exam_record_id != exam_id
    ):
        raise HTTPException(status_code=404, detail="Sugestão multimodal não encontrada.")
    return row


def _name(row: PatientMultimodalExamRecord) -> str:
    return cofre.decifrar_campo(row.original_name_cifrado, row.id)


def _notes(row: PatientMultimodalExamRecord) -> str | None:
    return cofre.decifrar_campo(row.notes_cifrado, row.id) if row.notes_cifrado else None


def _suggestion_payload(row: PatientMultimodalAISuggestion) -> dict:
    try:
        value = json.loads(cofre.decifrar_campo(row.payload_cifrado, row.id))
    except (ValueError, json.JSONDecodeError):
        value = {}
    return value if isinstance(value, dict) else {}


def _dump_suggestion(row: PatientMultimodalAISuggestion) -> dict:
    data = _suggestion_payload(row)
    return {
        "id": row.id,
        "exam_record_id": row.exam_record_id,
        "status": row.status,
        "payload": data.get("payload") or {},
        "web_sources": data.get("web_sources") or [],
        "provider": row.provider,
        "model": row.model,
        "prompt_version": row.prompt_version,
        "tokens_input": row.tokens_input,
        "tokens_output": row.tokens_output,
        "reviewed_by": row.reviewed_by,
        "reviewed_at": row.reviewed_at,
        "review_note": cofre.decifrar_campo(row.review_note_cifrado, row.id) if row.review_note_cifrado else None,
        "accepted_result_id": row.accepted_result_id,
        "created_at": row.created_at,
    }


def _dump_exam(row: PatientMultimodalExamRecord, db: Session) -> dict:
    latest = (
        db.query(PatientMultimodalAISuggestion)
        .filter(
            PatientMultimodalAISuggestion.owner_id == row.owner_id,
            PatientMultimodalAISuggestion.patient_profile_id == row.patient_profile_id,
            PatientMultimodalAISuggestion.exam_record_id == row.id,
        )
        .order_by(PatientMultimodalAISuggestion.created_at.desc(), PatientMultimodalAISuggestion.id.desc())
        .first()
    )
    return {
        "id": row.id,
        "patient_profile_id": row.patient_profile_id,
        "author_id": row.author_id,
        "source_encounter_id": row.source_encounter_id,
        "performed_at": row.performed_at,
        "exam_type": row.exam_type,
        "exam_type_label": cardiovascular_exam_assist.EXAM_TYPES.get(row.exam_type, row.exam_type),
        "original_name": _name(row),
        "media_type": row.media_type,
        "size_bytes": row.size_bytes,
        "notes": _notes(row),
        "created_at": row.created_at,
        "latest_suggestion": _dump_suggestion(latest) if latest else None,
    }


def _safe_fragment(value: str | None, *, limit: int = 2400) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    # Um trecho com possível identificador não é enviado ao processador externo.
    # A omissão é explícita para a IA não inferir ausência clínica.
    if contains_identifier(text):
        return "[trecho clínico omitido pelo CorVIA por possível identificador direto]"
    return text[:limit]


def _decrypt_field(value: bytes | None, row_id: int) -> str | None:
    return cofre.decifrar_campo(value, row_id) if value is not None else None


def _chart_context(pid: int, db: Session, user) -> str:
    profile = patient_profile_for_user(pid, db, user)
    sections: list[str] = [
        "CONTEXTO LONGITUDINAL DESIDENTIFICADO DO PRONTUÁRIO",
    ]
    if profile.birth_date:
        today = date.today()
        age = today.year - profile.birth_date.year - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))
        sections.append(f"Idade aproximada: {max(age, 0)} anos")
    if profile.sex:
        sections.append(f"Sexo cadastrado: {profile.sex}")

    items = (
        db.query(PatientClinicalItem)
        .filter(
            PatientClinicalItem.owner_id == user.id,
            PatientClinicalItem.patient_profile_id == pid,
            PatientClinicalItem.is_active.is_(True),
        )
        .order_by(PatientClinicalItem.created_at.desc())
        .limit(80)
        .all()
    )
    if items:
        lines: list[str] = []
        for item in items:
            try:
                payload = json.loads(cofre.decifrar_campo(item.payload_cifrado, item.id))
            except (ValueError, json.JSONDecodeError):
                continue
            name = _safe_fragment(str(payload.get("name") or ""), limit=300)
            details = _safe_fragment(str(payload.get("details") or ""), limit=700)
            text = " — ".join(x for x in (name, details) if x)
            if text:
                lines.append(f"- {item.kind}: {text}")
        if lines:
            sections.append("PROBLEMAS / ALERGIAS / MEDICAÇÕES ATIVAS\n" + "\n".join(lines))

    results = (
        db.query(PatientExamResult)
        .filter(PatientExamResult.owner_id == user.id, PatientExamResult.patient_profile_id == pid)
        .order_by(PatientExamResult.performed_at.desc())
        .limit(60)
        .all()
    )
    if results:
        lines = []
        for result in results:
            try:
                payload = json.loads(cofre.decifrar_campo(result.payload_cifrado, result.id))
            except (ValueError, json.JSONDecodeError):
                continue
            name = _safe_fragment(str(payload.get("exam_name") or ""), limit=300)
            value = _safe_fragment(str(payload.get("structured_result") or payload.get("result") or ""), limit=800)
            report = _safe_fragment(str(payload.get("report_text") or ""), limit=1200)
            content = " | ".join(x for x in (name, value, report) if x)
            if content:
                lines.append(f"- {result.performed_at.date().isoformat()}: {content}")
        if lines:
            sections.append("EXAMES E RESULTADOS ANTERIORES\n" + "\n".join(lines))

    encounters = (
        db.query(ClinicalEncounter)
        .filter(ClinicalEncounter.owner_id == user.id, ClinicalEncounter.patient_profile_id == pid)
        .order_by(ClinicalEncounter.created_at.desc())
        .limit(16)
        .all()
    )
    if encounters:
        lines = []
        for encounter in encounters:
            parts = []
            for label, field in (
                ("queixa", encounter.chief_complaint_cifrado),
                ("anamnese", encounter.anamnesis_cifrado),
                ("exame físico", encounter.physical_exam_cifrado),
                ("avaliação", encounter.assessment_cifrado),
                ("plano", encounter.plan_cifrado),
            ):
                fragment = _safe_fragment(_decrypt_field(field, encounter.id), limit=1400)
                if fragment:
                    parts.append(f"{label}: {fragment}")
            if parts:
                when = (encounter.started_at or encounter.created_at).date().isoformat()
                lines.append(f"- {when}: " + " | ".join(parts))
        if lines:
            sections.append("ATENDIMENTOS RECENTES\n" + "\n".join(lines))

    context = "\n\n".join(sections)
    return context[:MAX_CONTEXT_CHARS]


def _ensure_ai_available() -> None:
    if not settings.ai_enabled or not settings.ai_clinical_multimodal_enabled or not settings.ai_clinical_data_controls_approved:
        raise HTTPException(status_code=503, detail="A assistência multimodal clínica está indisponível nesta instalação.")
    if not cardiovascular_exam_assist.provider_configured():
        raise HTTPException(status_code=503, detail="O provedor multimodal não está configurado.")


def _reserve_quota(db: Session, user, *, exam_id: int) -> int:
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
        raise HTTPException(status_code=429, detail=f"Limite diário de {settings.ai_daily_limit} análises atingido. Recomeça amanhã.")
    attempt = AuditLog(
        user_id=user.id,
        action="ai_clinical_exam_transfer_attempt",
        entity="patient_multimodal_exam_record",
        entity_id=str(exam_id),
        detail={"mode": "longitudinal_patient_record", "provider": settings.ai_provider, "status": "reserved"},
    )
    db.add(attempt)
    db.commit()
    return attempt.id


@router.get("/{pid}/exames-multimodais/status")
def multimodal_status(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    patient_profile_for_user(pid, db, user)
    return {
        "enabled": bool(
            settings.ai_enabled
            and settings.ai_clinical_multimodal_enabled
            and settings.ai_clinical_data_controls_approved
            and cardiovascular_exam_assist.provider_configured()
        ),
        "exam_types": cardiovascular_exam_assist.EXAM_TYPES,
        "supported_media_types": list(cardiovascular_exam_assist.supported_media_types()),
        "stores_original_in_patient_record": True,
        "stores_ai_suggestion_in_patient_record": True,
        "medical_review_required": True,
        "decision_support_only": True,
    }


@router.get("/{pid}/exames-multimodais")
def list_multimodal_exams(
    pid: int,
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    rows = (
        db.query(PatientMultimodalExamRecord)
        .filter(PatientMultimodalExamRecord.owner_id == user.id, PatientMultimodalExamRecord.patient_profile_id == pid)
        .order_by(PatientMultimodalExamRecord.performed_at.desc(), PatientMultimodalExamRecord.id.desc())
        .limit(limit)
        .all()
    )
    db.add(AuditLog(user_id=user.id, action="list_patient_multimodal_exams", entity="patient_profile", entity_id=str(pid), detail={"count": len(rows)}))
    result = [_dump_exam(row, db) for row in rows]
    db.commit()
    return result


@router.post("/{pid}/exames-multimodais", status_code=201)
async def upload_multimodal_exam(
    pid: int,
    arquivo: UploadFile = File(...),
    exam_type: str = Form(...),
    performed_at: datetime = Form(...),
    notes: str = Form(default=""),
    source_encounter_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    if exam_type not in cardiovascular_exam_assist.EXAM_TYPES:
        raise HTTPException(status_code=422, detail="Selecione um tipo de exame válido.")
    if performed_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="A data clínica deve informar o fuso horário.")
    if source_encounter_id is not None:
        encounter = encounter_for_user(source_encounter_id, db, user)
        if encounter.patient_profile_id != pid:
            raise HTTPException(status_code=404, detail="Atendimento de origem não encontrado.")
    if len(notes) > 5000:
        raise HTTPException(status_code=422, detail="Observações excedem 5000 caracteres.")

    try:
        content = await arquivo.read(MAX_FILE_BYTES + 1)
    finally:
        await arquivo.close()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="O exame precisa ter no máximo 20 MB.")
    try:
        original_name = safe_filename(arquivo.filename, "exame")
        media_type = validate_file(content, original_name, "clinical_exam")
    except UploadRejected as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    row = PatientMultimodalExamRecord(
        owner_id=user.id,
        patient_profile_id=pid,
        author_id=user.id,
        source_encounter_id=source_encounter_id,
        performed_at=performed_at,
        exam_type=exam_type,
        storage_key="",
        original_name_cifrado=b"",
        media_type=media_type,
        size_bytes=len(content),
        notes_cifrado=None,
    )
    storage_key: str | None = None
    try:
        db.add(row)
        db.flush()
        storage_key = cofre.guardar(content, row.id)
        row.storage_key = storage_key
        row.original_name_cifrado = cofre.cifrar_campo(original_name, row.id)
        row.notes_cifrado = cofre.cifrar_campo(notes.strip(), row.id) if notes.strip() else None
        db.add(AuditLog(
            user_id=user.id,
            action="upload_patient_multimodal_exam",
            entity="patient_multimodal_exam_record",
            entity_id=str(row.id),
            detail={"patient_profile_id": pid, "exam_type": exam_type, "media_type": media_type, "size_bytes": len(content), "source_encounter_id": source_encounter_id},
        ))
        db.commit()
    except cofre.CofreIndisponivel as error:
        db.rollback()
        if storage_key:
            cofre.apagar(storage_key)
        raise HTTPException(status_code=503, detail="Armazenamento seguro do prontuário indisponível.") from error
    except Exception:
        db.rollback()
        if storage_key:
            cofre.apagar(storage_key)
        raise
    db.refresh(row)
    return _dump_exam(row, db)


@router.get("/{pid}/exames-multimodais/{exam_id}/arquivo")
def open_multimodal_exam(
    pid: int,
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _exam_for_user(pid, exam_id, db, user)
    try:
        content = cofre.ler(row.storage_key, row.id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Arquivo do exame não encontrado.") from error
    except cofre.CofreIndisponivel as error:
        raise HTTPException(status_code=503, detail="Arquivo do exame indisponível.") from error
    db.add(AuditLog(user_id=user.id, action="read_patient_multimodal_exam", entity="patient_multimodal_exam_record", entity_id=str(row.id), detail={"patient_profile_id": pid}))
    db.commit()
    return Response(content=content, media_type=row.media_type, headers={"Content-Disposition": f'inline; filename="exame-{row.id}"', "Cache-Control": "no-store, private", "X-Content-Type-Options": "nosniff"})


@router.get("/{pid}/exames-multimodais/{exam_id}/sugestoes")
def list_multimodal_suggestions(
    pid: int,
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _exam_for_user(pid, exam_id, db, user)
    rows = (
        db.query(PatientMultimodalAISuggestion)
        .filter(
            PatientMultimodalAISuggestion.owner_id == user.id,
            PatientMultimodalAISuggestion.patient_profile_id == pid,
            PatientMultimodalAISuggestion.exam_record_id == exam_id,
        )
        .order_by(PatientMultimodalAISuggestion.created_at.desc(), PatientMultimodalAISuggestion.id.desc())
        .all()
    )
    db.add(AuditLog(user_id=user.id, action="list_patient_multimodal_ai_suggestions", entity="patient_multimodal_exam_record", entity_id=str(exam_id), detail={"count": len(rows)}))
    result = [_dump_suggestion(row) for row in rows]
    db.commit()
    return result


@router.post("/{pid}/exames-multimodais/{exam_id}/sugestoes", status_code=201)
async def generate_multimodal_suggestion(
    pid: int,
    exam_id: int,
    request: SuggestionRequest,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _ensure_ai_available()
    row = _exam_for_user(pid, exam_id, db, user)
    question = request.clinical_question.strip()
    if len(question) > 4000 or contains_identifier(question):
        raise HTTPException(status_code=422, detail="A pergunta clínica deve ser desidentificada e ter no máximo 4000 caracteres.")

    try:
        original = cofre.ler(row.storage_key, row.id)
        sanitized, sanitized_type = await run_in_threadpool(sanitize_clinical_file, original, row.media_type)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Arquivo do exame não encontrado.") from error
    except (cofre.CofreIndisponivel, UnsafeClinicalFile) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    context = _chart_context(pid, db, user)
    attempt_id = _reserve_quota(db, user, exam_id=row.id)
    # A observação livre permanece cifrada e local no prontuário. A legenda
    # externa usa apenas o tipo canônico do exame para não transferir texto
    # potencialmente identificável que não passou pelo sanitizador clínico.
    clinical_file = ClinicalFile(
        content=sanitized,
        media_type=sanitized_type,
        file_id=f"exame-{row.id}",
        label=cardiovascular_exam_assist.EXAM_TYPES[row.exam_type],
    )
    try:
        analysis = await run_in_threadpool(
            cardiovascular_exam_assist.analyze_exam,
            [clinical_file], row.exam_type, question, "", context,
        )
    except Exception as error:
        db.rollback()
        db.add(AuditLog(
            user_id=user.id,
            action="ai_clinical_exam_transfer_outcome",
            entity="patient_multimodal_exam_record",
            entity_id=str(row.id),
            detail={"mode": "longitudinal_patient_record", "transfer_attempt_id": attempt_id, "status": "provider_error", "error_type": type(error).__name__},
        ))
        db.commit()
        raise HTTPException(status_code=502, detail=f"A análise multimodal não foi concluída ({type(error).__name__}). O exame original permanece preservado.") from error

    payload = dict(analysis["payload"])
    payload["disclaimer"] = (
        "Sugestão assistiva gerada por IA com base no exame e no contexto longitudinal desidentificado. "
        "Não é laudo, diagnóstico ou prescrição; não substitui julgamento, conduta nem decisão médica. "
        "Qualquer incorporação ao prontuário exige revisão e aceitação explícita do médico responsável."
    )
    suggestion = PatientMultimodalAISuggestion(
        owner_id=user.id,
        patient_profile_id=pid,
        exam_record_id=row.id,
        requested_by=user.id,
        status="generated",
        payload_cifrado=b"",
        provider=analysis["provider"],
        model=analysis["model"],
        prompt_version=analysis["prompt_version"],
        tokens_input=analysis["tokens_input"],
        tokens_output=analysis["tokens_output"],
    )
    db.add(suggestion)
    db.flush()
    suggestion.payload_cifrado = cofre.cifrar_campo(json.dumps({"payload": payload, "web_sources": analysis["web_sources"]}, ensure_ascii=False), suggestion.id)
    db.add(AuditLog(
        user_id=user.id,
        action="generate_patient_multimodal_ai_suggestion",
        entity="patient_multimodal_ai_suggestion",
        entity_id=str(suggestion.id),
        detail={"patient_profile_id": pid, "exam_record_id": row.id, "exam_type": row.exam_type, "source_count": len(analysis["web_sources"]), "transfer_attempt_id": attempt_id},
    ))
    db.add(AuditLog(
        user_id=user.id,
        action="ai_clinical_exam_transfer_outcome",
        entity="patient_multimodal_exam_record",
        entity_id=str(row.id),
        detail={"mode": "longitudinal_patient_record", "transfer_attempt_id": attempt_id, "status": "success", "model": analysis["model"], "source_count": len(analysis["web_sources"])},
    ))
    db.commit()
    db.refresh(suggestion)
    return _dump_suggestion(suggestion)


@router.post("/{pid}/exames-multimodais/{exam_id}/sugestoes/{suggestion_id}/revisao")
def review_multimodal_suggestion(
    pid: int,
    exam_id: int,
    suggestion_id: int,
    review: SuggestionReview,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    exam = _exam_for_user(pid, exam_id, db, user)
    suggestion = _suggestion_for_user(pid, exam_id, suggestion_id, db, user)
    if suggestion.status != "generated":
        raise HTTPException(status_code=409, detail="Esta sugestão já foi revisada.")
    note = (review.review_note or "").strip()
    if len(note) > 5000:
        raise HTTPException(status_code=422, detail="Nota de revisão excede 5000 caracteres.")
    now = datetime.now(timezone.utc)
    suggestion.reviewed_by = user.id
    suggestion.reviewed_at = now
    suggestion.review_note_cifrado = cofre.cifrar_campo(note, suggestion.id) if note else None

    if review.decision == "reject":
        suggestion.status = "rejected"
    else:
        final = (review.final_interpretation or "").strip()
        if not final:
            raise HTTPException(status_code=422, detail="Para aceitar, registre sua interpretação médica final do exame.")
        if len(final) > 20_000:
            raise HTTPException(status_code=422, detail="Interpretação final excede 20.000 caracteres.")
        exam_kind = "laboratorial" if exam.exam_type == "laboratory" else (
            "metodo_grafico" if exam.exam_type in {"ecg", "holter", "mapa", "exercise_test", "cardiopulmonary_test", "electrophysiology", "device_interrogation"}
            else "imagem" if exam.exam_type in {"echocardiogram", "vascular_ultrasound", "chest_xray", "coronary_ct", "cardiac_ct", "cardiac_mri", "nuclear_cardiology", "angiography", "hemodynamics"}
            else "outro"
        )
        result = PatientExamResult(
            owner_id=user.id,
            patient_profile_id=pid,
            author_id=user.id,
            source_encounter_id=exam.source_encounter_id,
            lab_test_id=None,
            correction_of_id=None,
            exam_kind=exam_kind,
            performed_at=exam.performed_at,
            payload_cifrado=b"",
            correction_reason_cifrado=None,
        )
        db.add(result)
        db.flush()
        result.payload_cifrado = cofre.cifrar_campo(json.dumps({
            "exam_name": cardiovascular_exam_assist.EXAM_TYPES.get(exam.exam_type, exam.exam_type),
            "structured_result": None,
            "report_text": final,
            "unit": None,
            "reference_range": None,
            "notes": note or None,
            "source": "Interpretação médica após assistência multimodal CorVIA IA",
            "multimodal_exam_record_id": exam.id,
            "ai_suggestion_id": suggestion.id,
        }, ensure_ascii=False), result.id)
        suggestion.status = "accepted"
        suggestion.accepted_result_id = result.id

    db.add(AuditLog(
        user_id=user.id,
        action="review_patient_multimodal_ai_suggestion",
        entity="patient_multimodal_ai_suggestion",
        entity_id=str(suggestion.id),
        detail={"patient_profile_id": pid, "exam_record_id": exam.id, "decision": review.decision, "accepted_result_id": suggestion.accepted_result_id},
    ))
    db.commit()
    db.refresh(suggestion)
    return _dump_suggestion(suggestion)
