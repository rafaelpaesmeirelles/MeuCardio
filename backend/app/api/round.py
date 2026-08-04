from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.round import Patient, PatientAISuggestion, PatientNote, PatientProblem

router = APIRouter(prefix="/api/round", tags=["round"])


class PatientIn(BaseModel):
    record_number: str
    initials: str
    birth_date: date | None = None
    sex: str | None = None
    bed: str | None = None
    unit: str | None = None
    admission_date: date | None = None


class NoteIn(BaseModel):
    body: str


class ProblemIn(BaseModel):
    label: str
    status: str = "ativo"


class ArchiveIn(BaseModel):
    reason: str | None = None


def _dump(patient: Patient) -> dict:
    return {
        "id": patient.id,
        "record_number": patient.record_number,
        "initials": patient.initials,
        "sex": patient.sex,
        "bed": patient.bed,
        "unit": patient.unit,
        "status": patient.status,
        "admission_date": patient.admission_date,
        "labs": patient.labs,
        "medications": patient.medications,
        "plan": patient.plan,
        "pending": patient.pending,
        "chief_complaint": patient.chief_complaint,
        "anamnesis": patient.anamnesis,
        "physical_exam": patient.physical_exam,
        "cardiac_exam": patient.cardiac_exam,
        "vital_signs": patient.vital_signs,
        "imaging": patient.imaging,
        "diagnostic_hypothesis": patient.diagnostic_hypothesis,
        "archived": patient.archived_at is not None,
        "archived_at": patient.archived_at,
        "archive_reason": patient.archive_reason,
        "problems": [
            {"id": problem.id, "label": problem.label, "status": problem.status}
            for problem in patient.problems
        ],
    }


def _patient_for_user(
    patient_id: int,
    db: Session,
    user,
    *,
    allow_archived: bool = False,
) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient or patient.created_by != user.id:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if patient.archived_at is not None and not allow_archived:
        raise HTTPException(status_code=410, detail="Paciente removido do round.")
    return patient


def _ai_queries_today(db: Session, user_id: int, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    start = now.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "ai_assist_round",
            AuditLog.created_at >= start,
            AuditLog.created_at < end,
        )
        .count()
    )


@router.get("/patients")
def list_patients(
    status: str = "internado",
    archived: bool = Query(False),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    query = db.query(Patient).filter(Patient.created_by == user.id)
    if archived:
        query = query.filter(Patient.archived_at.isnot(None))
    else:
        query = query.filter(Patient.archived_at.is_(None), Patient.status == status)
    rows = query.order_by(Patient.archived_at.desc(), Patient.bed, Patient.initials).all()
    return [_dump(patient) for patient in rows]


@router.post("/patients", status_code=201)
def create_patient(
    data: PatientIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = Patient(**data.model_dump(), created_by=user.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return _dump(patient)


@router.get("/patients/{patient_id}")
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = _patient_for_user(patient_id, db, user)
    return {
        **_dump(patient),
        "notes": [
            {"id": note.id, "body": note.body, "created_at": note.created_at}
            for note in patient.notes
        ],
    }


@router.patch("/patients/{patient_id}")
def update_patient(
    patient_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = _patient_for_user(patient_id, db, user)
    for field in (
        "bed", "unit", "status", "labs", "medications", "plan", "pending",
        "chief_complaint", "anamnesis", "physical_exam", "cardiac_exam",
        "vital_signs", "imaging", "diagnostic_hypothesis",
    ):
        if field in payload:
            setattr(patient, field, payload[field])
    db.commit()
    return _dump(patient)


@router.delete("/patients/{patient_id}")
def archive_patient(
    patient_id: int,
    data: ArchiveIn | None = None,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = _patient_for_user(patient_id, db, user, allow_archived=True)
    if patient.archived_at is None:
        patient.archived_at = datetime.now(timezone.utc)
        patient.archived_by = user.id
        patient.archive_reason = ((data.reason if data else "") or "").strip()[:300] or None
        db.add(AuditLog(
            user_id=user.id,
            action="archive_round_patient",
            entity="patient",
            entity_id=str(patient.id),
            detail={"reason": patient.archive_reason},
        ))
        db.commit()
    return {"archived": True, "patient": _dump(patient)}


@router.post("/patients/{patient_id}/restore")
def restore_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = _patient_for_user(patient_id, db, user, allow_archived=True)
    patient.archived_at = None
    patient.archived_by = None
    patient.archive_reason = None
    db.add(AuditLog(
        user_id=user.id,
        action="restore_round_patient",
        entity="patient",
        entity_id=str(patient.id),
        detail={},
    ))
    db.commit()
    return {"restored": True, "patient": _dump(patient)}


@router.post("/patients/{patient_id}/problems", status_code=201)
def add_problem(
    patient_id: int,
    data: ProblemIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _patient_for_user(patient_id, db, user)
    problem = PatientProblem(patient_id=patient_id, **data.model_dump())
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return {"id": problem.id, "label": problem.label, "status": problem.status}


@router.post("/patients/{patient_id}/notes", status_code=201)
def add_note(
    patient_id: int,
    data: NoteIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _patient_for_user(patient_id, db, user)
    note = PatientNote(patient_id=patient_id, author_id=user.id, body=data.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"id": note.id, "body": note.body, "created_at": note.created_at}


@router.get("/patients/{patient_id}/summary")
def summary(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = _patient_for_user(patient_id, db, user)
    lines = [f"Paciente {patient.initials} — prontuário {patient.record_number}"]
    if patient.unit or patient.bed:
        lines.append(f"Local: {patient.unit or '—'} / leito {patient.bed or '—'}")
    if patient.admission_date:
        lines.append(f"Internação: {patient.admission_date.isoformat()}")
    if patient.problems:
        lines.append("Problemas ativos:")
        lines += [f"  - {problem.label}" for problem in patient.problems if problem.status == "ativo"]
    if patient.medications:
        lines.append("Medicações:")
        lines += [f"  - {medication}" for medication in patient.medications]
    if patient.labs:
        lines.append("Exames: " + "; ".join(f"{key}: {value}" for key, value in patient.labs.items()))
    if patient.plan:
        lines.append(f"Plano: {patient.plan}")
    if patient.pending:
        lines.append("Pendências:")
        lines += [f"  - {item}" for item in patient.pending]
    return {"text": "\n".join(lines)}


def _dump_suggestion(suggestion: PatientAISuggestion) -> dict:
    return {
        "id": suggestion.id,
        "created_at": suggestion.created_at,
        "model": suggestion.model,
        "differential_diagnosis": suggestion.differential_diagnosis,
        "suggested_workup": suggestion.suggested_workup,
        "treatment_considerations": suggestion.treatment_considerations,
        "sources": suggestion.sources,
        "sources_pubmed": suggestion.sources_pubmed,
    }


@router.post("/patients/{patient_id}/ai-assist", status_code=201)
def generate_ai_assistance(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    from app.services import rag

    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="A IA clínica está desligada nesta instalação.")

    patient = _patient_for_user(patient_id, db, user)
    used = _ai_queries_today(db, user.id)
    if used >= settings.ai_daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Limite diário de {settings.ai_daily_limit} consultas atingido. Recomeça amanhã.",
        )

    has_clinical_data = any([
        patient.chief_complaint,
        patient.anamnesis,
        patient.physical_exam,
        patient.vital_signs,
        patient.labs,
        patient.imaging,
        patient.problems,
    ])
    if not has_clinical_data:
        raise HTTPException(
            status_code=422,
            detail="Preencha ao menos queixa principal, anamnese, exame físico ou exames antes de pedir auxílio de IA.",
        )

    try:
        result = rag.analisar_caso(db, patient)
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"O provedor de IA não respondeu ({type(error).__name__}). Tente novamente.",
        ) from error

    suggestion = PatientAISuggestion(
        patient_id=patient.id,
        requested_by=user.id,
        case_snapshot=result["case_snapshot"],
        sources=result["sources"],
        sources_pubmed=result["sources_pubmed"],
        model=result["model"],
        differential_diagnosis=result["differential_diagnosis"],
        suggested_workup=result["suggested_workup"],
        treatment_considerations=result["treatment_considerations"],
    )
    db.add(suggestion)
    db.add(AuditLog(
        user_id=user.id,
        action="ai_assist_round",
        entity="patient",
        entity_id=str(patient.id),
        detail={"modelo": result["model"], "fontes": [source["slug"] for source in result["sources"]]},
    ))
    db.commit()
    db.refresh(suggestion)
    return _dump_suggestion(suggestion)


@router.get("/patients/{patient_id}/ai-assist")
def list_ai_assistance(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient = _patient_for_user(patient_id, db, user)
    items = sorted(patient.ai_suggestions, key=lambda suggestion: suggestion.created_at, reverse=True)
    return [_dump_suggestion(suggestion) for suggestion in items]
