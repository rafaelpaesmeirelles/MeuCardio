from __future__ import annotations

import hashlib
import io
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.core.uploads import safe_filename, validate_file
from app.models.audit import AuditLog
from app.models.heart_team import (
    HeartTeamAttachment, HeartTeamAuditEvent, HeartTeamCase, HeartTeamFinalReview,
    HeartTeamOpinion, HeartTeamPatientRecord, HeartTeamSuggestion,
    HeartTeamSuggestionReview,
)
from app.schemas.heart_team import (
    AnalyzeRequest, FinalReviewRequest, HeartTeamCaseCreate, HeartTeamCasePatch,
    SuggestionReviewRequest,
)
from app.services.cofre import cifrar_campo, decifrar_campo, guardar, ler
from app.services.heart_team import (
    HeartTeamBudgetExceeded, HeartTeamDisabled, HeartTeamError, HeartTeamSafetyError,
    audit_event, audit_sensitive_read, content_hash,
    create_case_draft, purge_expired_cache, usage_summary, utcnow,
    is_heart_team_physician, enqueue_analysis_job,
)
from app.services.heart_team_agents import AGENTS
from app.services.ia.clinical_file_sanitizer import UnsafeClinicalFile, sanitize_clinical_file

router = APIRouter(prefix="/api/heart-team", tags=["heart-team"])
admin_router = APIRouter(prefix="/api/admin/heart-team", tags=["admin-heart-team"])


def _enabled():
    if not settings.heart_team_enabled:
        raise HTTPException(404, "Heart Team não está habilitado.")


def _physician(user=Depends(current_user)):
    if not is_heart_team_physician(user):
        raise HTTPException(403, "Heart Team é restrito a médico com CRM e perfil profissional aprovado.")
    return user


def _owned_case(db: Session, case_id: int, owner_id: int, *, lock: bool = False) -> HeartTeamCase:
    query = db.query(HeartTeamCase).filter(HeartTeamCase.id == case_id, HeartTeamCase.owner_id == owner_id)
    case = query.with_for_update().first() if lock else query.first()
    if not case:
        raise HTTPException(404, "Caso não encontrado.")
    return case


def _dump_opinion(row: HeartTeamOpinion | dict) -> dict:
    if isinstance(row, dict):
        return row
    return {"id": row.id, "agent_key": row.agent_key, "round_name": row.round_name, "round": row.round_name, "content": row.content, "source_ids": row.source_ids, "confidence": row.confidence, "model": row.model_name, "created_at": row.created_at}


def _dump_case(db: Session, case: HeartTeamCase, *, include_detail: bool = True) -> dict:
    visible = case.status in {"awaiting_review", "completed"}
    suggestions = db.query(HeartTeamSuggestion).filter(HeartTeamSuggestion.case_id == case.id).order_by(HeartTeamSuggestion.id).all() if visible else []
    reviews = {row.suggestion_id: row for row in db.query(HeartTeamSuggestionReview).join(HeartTeamSuggestion, HeartTeamSuggestion.id == HeartTeamSuggestionReview.suggestion_id).filter(HeartTeamSuggestion.case_id == case.id).all()} if visible else {}
    data = {"id": case.id, "status": case.status, "question": case.question, "analysis_scope": case.analysis_scope, "selected_agents": case.selected_agents, "risk_classification": case.risk_classification, "missing_data": case.missing_data, "created_at": case.created_at, "updated_at": case.updated_at, "started_at": case.started_at, "finished_at": case.finished_at, "tokens_input": case.tokens_input, "tokens_output": case.tokens_output, "estimated_cost_micros": case.estimated_cost_micros, "pipeline_version": case.pipeline_version}
    if include_detail:
        data.update({"input_data": case.input_data, "result": case.result if visible else {}, "opinions": [_dump_opinion(row) for row in db.query(HeartTeamOpinion).filter(HeartTeamOpinion.case_id == case.id).order_by(HeartTeamOpinion.id).all()] if visible else [], "suggestions": [{"id": row.id, "category": row.category, "original_text": row.original_text, "original_hash": row.original_hash, "review": None if row.id not in reviews else {"decision": reviews[row.id].decision, "final_text": reviews[row.id].final_text, "final_hash": reviews[row.id].final_hash, "note": reviews[row.id].note}} for row in suggestions]})
    final = db.query(HeartTeamFinalReview).filter(HeartTeamFinalReview.case_id == case.id).first()
    data["final_review"] = None if not final else {"decision": final.decision, "final_hash": final.final_hash, "note": final.note, "created_at": final.created_at}
    return data


@router.get("/agents", dependencies=[Depends(_enabled), Depends(_physician)])
def list_agents():
    return [{"key": agent.key, "name": agent.name, "remit": agent.remit, "mandatory": agent.mandatory, "model_tier": agent.model_tier} for agent in AGENTS.values()]


@router.get("/usage", dependencies=[Depends(_enabled), Depends(_physician)])
def usage(user=Depends(current_user), db: Session = Depends(get_db)):
    db.add(AuditLog(user_id=user.id, action="heart_team.usage_read", entity="heart_team_usage", entity_id=str(user.id), detail={})); db.commit()
    return usage_summary(db, user.id)


@router.post("/cases", status_code=201, dependencies=[Depends(_enabled), Depends(_physician)])
def create_case(payload: HeartTeamCaseCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    try:
        case = create_case_draft(
            db,
            owner_id=user.id,
            created_by_id=user.id,
            payload=payload.model_dump(mode="json"),
        )
    except HeartTeamSafetyError as exc:
        # Erros esperados de autorização/vínculo do prontuário são
        # validação clínica, não falhas internas do servidor.
        raise HTTPException(422, str(exc)) from exc
    return _dump_case(db, case)


@router.get("/cases", dependencies=[Depends(_enabled), Depends(_physician)])
def list_cases(user=Depends(current_user), db: Session = Depends(get_db)):
    db.add(AuditLog(user_id=user.id, action="heart_team.list_read", entity="heart_team_case", detail={})); db.commit()
    return [_dump_case(db, row, include_detail=False) for row in db.query(HeartTeamCase).filter(HeartTeamCase.owner_id == user.id).order_by(HeartTeamCase.created_at.desc()).limit(100).all()]


@router.get("/cases/{case_id}", dependencies=[Depends(_enabled), Depends(_physician)])
def get_case(case_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id); audit_sensitive_read(db, case, user.id, "case_detail"); return _dump_case(db, case)


@router.patch("/cases/{case_id}", dependencies=[Depends(_enabled), Depends(_physician)])
def patch_case(case_id: int, payload: HeartTeamCasePatch, user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id, lock=True)
    if case.status != "draft": raise HTTPException(409, "Somente rascunhos podem ser editados.")
    values = payload.model_dump(exclude_unset=True)
    if "question" in values: case.question = values["question"]
    if "selected_agents" in values: case.selected_agents = values["selected_agents"]
    if "input_data" in values:
        incoming = values["input_data"] or {}
        protected = {"source_patient_id", "source_patient_authorized", "patient_context_imported", "attachments"}
        if protected.intersection(incoming):
            raise HTTPException(422, "Vínculo, autorização e anexos do prontuário não podem ser alterados por este endpoint.")
        current = dict(case.input_data or {})
        current.update(incoming)
        case.input_data = current
    audit_event(db, case, actor_id=user.id, action="draft_updated", detail={"fields": sorted(values)}); db.commit(); return _dump_case(db, case)


def _objective_extract(data: bytes, media_type: str) -> dict:
    if media_type in {"text/plain", "text/csv"}:
        text_value = data.decode("utf-8-sig")[:24000]
        return {"type": "text", "text": text_value, "truncated": len(data) > len(text_value.encode())}
    if media_type == "application/pdf":
        try:
            import fitz
            with fitz.open(stream=data, filetype="pdf") as document:
                text_value = "\n".join(page.get_text("text") or "" for page in document)[:24000]
                return {"type": "pdf_text", "pages": document.page_count, "text": text_value}
        except Exception:
            return {"type": "pdf", "text": "", "extraction": "unavailable"}
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as image: return {"type": "image", "width": image.width, "height": image.height, "format": image.format}
    except Exception: return {"type": "binary"}


@router.post("/cases/{case_id}/attachments", status_code=201, dependencies=[Depends(_enabled), Depends(_physician)])
async def upload_attachments(case_id: int, files: list[UploadFile] = File(...), user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id, lock=True)
    if case.status != "draft": raise HTTPException(409, "Anexos só podem ser adicionados ao rascunho.")
    if not 1 <= len(files) <= 5: raise HTTPException(422, "Envie entre 1 e 5 arquivos.")
    created = []
    root = Path(settings.heart_team_files_dir)
    staged = []
    for upload in files:
        source = await upload.read()
        filename = safe_filename(upload.filename)
        media_type = validate_file(source, filename, "clinical_exam")
        try:
            sanitized, sanitized_media_type = sanitize_clinical_file(source, media_type)
        except UnsafeClinicalFile as exc:
            # Fail before any file in this request is persisted.  The external
            # model can never receive an unsanitized clinical attachment.
            raise HTTPException(422, str(exc)) from exc
        staged.append((filename, source, sanitized, sanitized_media_type))
    for filename, source, sanitized, media_type in staged:
        source_sha256 = hashlib.sha256(source).hexdigest()
        sanitized_sha256 = hashlib.sha256(sanitized).hexdigest()
        storage_key = guardar(sanitized, user.id, raiz=root)
        report = {
            "status": "sanitized_locally",
            "version": "clinical-file-sanitizer-v1",
            "metadata_removed": True,
            "visible_identifiers_checked": True,
            "source_and_sanitized_differ": source_sha256 != sanitized_sha256,
        }
        row = HeartTeamAttachment(
            case_id=case.id, owner_id=user.id, kind="upload", storage_key=storage_key,
            original_name_encrypted=cifrar_campo(filename, user.id), media_type=media_type,
            size_bytes=len(sanitized), source_sha256=source_sha256, sha256=sanitized_sha256,
            sanitization_report=report, objective_extract=_objective_extract(sanitized, media_type),
        )
        db.add(row); db.flush()
        created.append({"id": row.id, "name": filename, "media_type": media_type, "size_bytes": len(sanitized), "sha256": row.sha256, "sanitized": True})
    audit_event(db, case, actor_id=user.id, action="attachments_uploaded", detail={"count": len(created), "sanitized_sha256": [x["sha256"] for x in created], "sanitizer": "clinical-file-sanitizer-v1"}); db.commit(); return created


@router.get("/cases/{case_id}/attachments/{position}", dependencies=[Depends(_enabled), Depends(_physician)])
def download_attachment(case_id: int, position: int, user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id)
    rows = db.query(HeartTeamAttachment).filter(HeartTeamAttachment.case_id == case.id, HeartTeamAttachment.owner_id == user.id).order_by(HeartTeamAttachment.id).all()
    if position < 0 or position >= len(rows) or not rows[position].storage_key: raise HTTPException(404, "Anexo não encontrado.")
    row = rows[position]; name = decifrar_campo(row.original_name_encrypted, user.id) if row.original_name_encrypted else "anexo"
    audit_sensitive_read(db, case, user.id, "attachment_download")
    return Response(ler(row.storage_key, user.id, raiz=Path(settings.heart_team_files_dir)), media_type=row.media_type, headers={"Content-Disposition": f'attachment; filename="{name}"'})


@router.post("/cases/{case_id}/analyze", status_code=202, dependencies=[Depends(_enabled), Depends(_physician)])
def analyze(case_id: int, payload: AnalyzeRequest, user=Depends(current_user), db: Session = Depends(get_db)):
    try: job = enqueue_analysis_job(db, case_id=case_id, owner_id=user.id, actor_id=user.id, confirm_deidentified=payload.confirm_deidentified, confirm_medical_review=payload.confirm_medical_review)
    except HeartTeamDisabled as exc: raise HTTPException(404, str(exc))
    except HeartTeamSafetyError as exc: raise HTTPException(422, str(exc))
    except HeartTeamBudgetExceeded as exc: raise HTTPException(429, str(exc))
    except HeartTeamError as exc: raise HTTPException(409, str(exc))
    return {"job_id": job.id, "case_id": job.case_id, "status": job.status, "poll_url": f"/api/heart-team/cases/{job.case_id}"}


@router.post("/cases/{case_id}/suggestions/{suggestion_id}/review", dependencies=[Depends(_enabled), Depends(_physician)])
def review_suggestion(case_id: int, suggestion_id: int, payload: SuggestionReviewRequest, user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id, lock=True)
    if case.status != "awaiting_review": raise HTTPException(409, "Caso não aguarda revisão.")
    suggestion = db.query(HeartTeamSuggestion).filter(HeartTeamSuggestion.id == suggestion_id, HeartTeamSuggestion.case_id == case.id).first()
    if not suggestion: raise HTTPException(404, "Sugestão não encontrada.")
    if db.query(HeartTeamSuggestionReview).filter(HeartTeamSuggestionReview.suggestion_id == suggestion.id).first(): raise HTTPException(409, "Sugestão já revisada; o histórico é imutável.")
    final_text = payload.final_text if payload.decision == "edited" else (suggestion.original_text if payload.decision == "accepted" else "")
    if payload.decision == "edited" and not (final_text or "").strip(): raise HTTPException(422, "Informe o texto editado.")
    row = HeartTeamSuggestionReview(suggestion_id=suggestion.id, reviewer_id=user.id, decision=payload.decision, final_text=final_text or None, original_hash=suggestion.original_hash, final_hash=content_hash(final_text), note=payload.note)
    db.add(row); audit_event(db, case, actor_id=user.id, action="suggestion_reviewed", detail={"suggestion_id": suggestion.id, "decision": payload.decision, "original_hash": suggestion.original_hash, "final_hash": row.final_hash}); db.commit(); return {"decision": row.decision, "final_hash": row.final_hash}


@router.post("/cases/{case_id}/final-review", dependencies=[Depends(_enabled), Depends(_physician)])
def final_review(case_id: int, payload: FinalReviewRequest, user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id, lock=True)
    if case.status != "awaiting_review": raise HTTPException(409, "Caso não aguarda revisão final.")
    if not payload.medical_responsibility_confirmed or not payload.human_decisions_confirmed: raise HTTPException(422, "As duas confirmações médicas são obrigatórias.")
    if db.query(HeartTeamFinalReview).filter(HeartTeamFinalReview.case_id == case.id).first(): raise HTTPException(409, "Revisão final já registrada.")
    suggestions = db.query(HeartTeamSuggestion).filter(HeartTeamSuggestion.case_id == case.id).all()
    reviewed = db.query(HeartTeamSuggestionReview).join(HeartTeamSuggestion).filter(HeartTeamSuggestion.case_id == case.id).count()
    if reviewed != len(suggestions): raise HTTPException(409, "Revise individualmente todas as sugestões antes da decisão final.")
    original = case.result or {}; reviews = db.query(HeartTeamSuggestionReview).join(HeartTeamSuggestion).filter(HeartTeamSuggestion.case_id == case.id).order_by(HeartTeamSuggestionReview.id).all()
    final_snapshot = {"result": original, "suggestion_reviews": [{"suggestion_id": r.suggestion_id, "decision": r.decision, "final_text": r.final_text, "final_hash": r.final_hash} for r in reviews]}
    row = HeartTeamFinalReview(case_id=case.id, reviewer_id=user.id, decision=payload.decision, medical_responsibility_confirmed=True, human_decisions_confirmed=True, original_snapshot=original, final_snapshot=final_snapshot, original_hash=content_hash(original), final_hash=content_hash(final_snapshot), note=payload.note)
    db.add(row); case.status = "completed" if payload.decision == "accepted" else "rejected"
    patient_id = (case.input_data or {}).get("source_patient_id")
    if patient_id is not None and (case.input_data or {}).get("source_patient_authorized"):
        from app.models.patient_profile import PatientProfile
        profile = db.query(PatientProfile).filter(PatientProfile.id == int(patient_id), PatientProfile.owner_id == user.id).first()
        if not profile:
            raise HTTPException(409, "O prontuário vinculado não pertence a este assinante.")
        # Append-only provenance only after the physician's final decision.
        # No diagnosis, dose, recommendation or unaccepted text is copied.
        source_ids = [str(item.get("id")) for item in (original.get("sources") or []) if isinstance(item, dict) and item.get("id")]
        db.add(HeartTeamPatientRecord(
            case_id=case.id, owner_id=user.id, patient_profile_id=int(patient_id),
            reviewer_id=user.id, decision=payload.decision, final_hash=row.final_hash,
            provenance={
                "ai_support": "CorVIA Heart Team Virtual",
                "pipeline_version": case.pipeline_version,
                "model_versions": dict(case.model_versions or {}),
                "source_ids": source_ids,
                "reviewed_at": utcnow().isoformat(),
                "physician_reviewed": True,
            },
        ))
    audit_event(db, case, actor_id=user.id, action="final_review", detail={"decision": payload.decision, "original_hash": row.original_hash, "final_hash": row.final_hash, "medical_responsibility_confirmed": True, "human_decisions_confirmed": True}); db.commit(); return {"status": case.status, "decision": row.decision, "final_hash": row.final_hash}


@router.get("/cases/{case_id}/audit", dependencies=[Depends(_enabled), Depends(_physician)])
def case_audit(case_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    case = _owned_case(db, case_id, user.id); audit_sensitive_read(db, case, user.id, "audit_read")
    return [{"id": row.id, "action": row.action, "detail": row.detail, "previous_hash": row.previous_hash, "event_hash": row.event_hash, "created_at": row.created_at} for row in db.query(HeartTeamAuditEvent).filter(HeartTeamAuditEvent.case_id == case.id).order_by(HeartTeamAuditEvent.id).all()]


@admin_router.get("/metrics", dependencies=[Depends(_enabled)])
def admin_metrics(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    statuses = {status: count for status, count in db.query(HeartTeamCase.status, func.count(HeartTeamCase.id)).group_by(HeartTeamCase.status).all()}
    cases = db.query(HeartTeamCase).order_by(HeartTeamCase.owner_id, HeartTeamCase.id).all()
    subscribers: dict[int, dict] = {}; models: dict[str, int] = {}; latencies = []
    for case in cases:
        item = subscribers.setdefault(case.owner_id, {"owner_id": case.owner_id, "cases": 0, "estimated_cost_micros": 0, "tokens_input": 0, "tokens_output": 0})
        item["cases"] += 1; item["estimated_cost_micros"] += int(case.estimated_cost_micros or 0); item["tokens_input"] += int(case.tokens_input or 0); item["tokens_output"] += int(case.tokens_output or 0)
        for model in (case.model_versions or {}).values(): models[str(model)] = models.get(str(model), 0) + 1
        if case.started_at and case.finished_at: latencies.append(max(0, (case.finished_at - case.started_at).total_seconds() * 1000))
    db.add(AuditLog(user_id=_admin.id, action="heart_team.admin_metrics_read", entity="heart_team_metrics", detail={})); db.commit()
    return {"cases_by_status": statuses, "awaiting_review": statuses.get("awaiting_review", 0), "completed": statuses.get("completed", 0), "unusable": statuses.get("unusable", 0), "tokens_input": int(db.query(func.coalesce(func.sum(HeartTeamCase.tokens_input), 0)).scalar() or 0), "tokens_output": int(db.query(func.coalesce(func.sum(HeartTeamCase.tokens_output), 0)).scalar() or 0), "estimated_cost_micros": int(db.query(func.coalesce(func.sum(HeartTeamCase.estimated_cost_micros), 0)).scalar() or 0), "reserved_cost_micros": int(db.query(func.coalesce(func.sum(HeartTeamCase.reserved_cost_micros), 0)).scalar() or 0), "models": models, "average_latency_ms": int(sum(latencies) / len(latencies)) if latencies else 0, "subscribers": list(subscribers.values()), "limits": {"daily_cases": settings.heart_team_daily_case_limit, "monthly_cases": settings.heart_team_monthly_case_limit, "monthly_cost_micros": settings.heart_team_monthly_cost_ceiling_micros}}


@admin_router.post("/retention/purge", dependencies=[Depends(_enabled)])
def purge_cache(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    deleted = purge_expired_cache(db); db.add(AuditLog(user_id=_admin.id, action="heart_team.cache_purge", entity="heart_team_cache", detail={"deleted": deleted})); db.commit(); return {"deleted": deleted}
