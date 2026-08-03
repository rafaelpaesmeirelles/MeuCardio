from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
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


def _dump(p: Patient) -> dict:
    return {
        "id": p.id, "record_number": p.record_number, "initials": p.initials,
        "sex": p.sex, "bed": p.bed, "unit": p.unit, "status": p.status,
        "admission_date": p.admission_date, "labs": p.labs, "medications": p.medications,
        "plan": p.plan, "pending": p.pending,
        "chief_complaint": p.chief_complaint, "anamnesis": p.anamnesis,
        "physical_exam": p.physical_exam, "cardiac_exam": p.cardiac_exam,
        "vital_signs": p.vital_signs,
        "imaging": p.imaging, "diagnostic_hypothesis": p.diagnostic_hypothesis,
        "problems": [{"id": x.id, "label": x.label, "status": x.status} for x in p.problems],
    }


def _paciente_do_usuario(pid: int, db: Session, user) -> Patient:
    """Busca um paciente garantindo que só o dono (ou um admin) o veja.
    Usa 404 — não 403 — para não revelar nem a existência de um paciente
    de outro profissional."""
    p = db.get(Patient, pid)
    if not p or (p.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return p


def _consultas_ia_hoje(db: Session, user_id: int, agora: datetime | None = None) -> int:
    """Conta solicitações de auxílio do round no dia UTC corrente.

    O registro de auditoria é gravado somente após uma resposta bem-sucedida do
    provedor, portanto falhas externas não consomem a cota diária.
    """
    agora = agora or datetime.now(timezone.utc)
    inicio = agora.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + timedelta(days=1)
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "ai_assist_round",
            AuditLog.created_at >= inicio,
            AuditLog.created_at < fim,
        )
        .count()
    )


@router.get("/patients")
def list_patients(status: str = "internado", db: Session = Depends(get_db), user=Depends(current_user)):
    query = db.query(Patient).filter(Patient.status == status)
    if user.role != "admin":
        query = query.filter(Patient.created_by == user.id)
    rows = query.order_by(Patient.bed).all()
    return [_dump(p) for p in rows]


@router.post("/patients", status_code=201)
def create_patient(data: PatientIn, db: Session = Depends(get_db), user=Depends(current_user)):
    p = Patient(**data.model_dump(), created_by=user.id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return _dump(p)


@router.get("/patients/{pid}")
def get_patient(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    p = _paciente_do_usuario(pid, db, user)
    return {**_dump(p), "notes": [
        {"id": n.id, "body": n.body, "created_at": n.created_at} for n in p.notes
    ]}


@router.patch("/patients/{pid}")
def update_patient(pid: int, payload: dict, db: Session = Depends(get_db), user=Depends(current_user)):
    p = _paciente_do_usuario(pid, db, user)
    for f in ("bed", "unit", "status", "labs", "medications", "plan", "pending",
              "chief_complaint", "anamnesis", "physical_exam", "cardiac_exam",
              "vital_signs", "imaging", "diagnostic_hypothesis"):
        if f in payload:
            setattr(p, f, payload[f])
    db.commit()
    return _dump(p)


@router.post("/patients/{pid}/problems", status_code=201)
def add_problem(pid: int, data: ProblemIn, db: Session = Depends(get_db), user=Depends(current_user)):
    _paciente_do_usuario(pid, db, user)
    pr = PatientProblem(patient_id=pid, **data.model_dump())
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return {"id": pr.id, "label": pr.label, "status": pr.status}


@router.post("/patients/{pid}/notes", status_code=201)
def add_note(pid: int, data: NoteIn, db: Session = Depends(get_db), user=Depends(current_user)):
    _paciente_do_usuario(pid, db, user)
    n = PatientNote(patient_id=pid, author_id=user.id, body=data.body)
    db.add(n)
    db.commit()
    db.refresh(n)
    return {"id": n.id, "body": n.body, "created_at": n.created_at}


@router.get("/patients/{pid}/summary")
def summary(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    """Resumo estruturado do paciente, montado apenas com dados já registrados."""
    p = _paciente_do_usuario(pid, db, user)
    lines = [f"Paciente {p.initials} — prontuário {p.record_number}"]
    if p.unit or p.bed:
        lines.append(f"Local: {p.unit or '—'} / leito {p.bed or '—'}")
    if p.admission_date:
        lines.append(f"Internação: {p.admission_date.isoformat()}")
    if p.problems:
        lines.append("Problemas ativos:")
        lines += [f"  - {x.label}" for x in p.problems if x.status == "ativo"]
    if p.medications:
        lines.append("Medicações:")
        lines += [f"  - {m}" for m in p.medications]
    if p.labs:
        lines.append("Exames: " + "; ".join(f"{k}: {v}" for k, v in p.labs.items()))
    if p.plan:
        lines.append(f"Plano: {p.plan}")
    if p.pending:
        lines.append("Pendências:")
        lines += [f"  - {x}" for x in p.pending]
    return {"text": "\n".join(lines)}


# --------------------------------------------------------- auxílio de IA --
# Envia dado clínico do caso (sem nome, iniciais, prontuário, leito ou data
# de nascimento — ver rag._resumo_caso) ao provedor externo de IA já em uso
# no assistente. Decisão institucional explícita do responsável técnico.
# A sugestão NUNCA é gravada como fato no prontuário — fica em registro à
# parte, sempre exigindo validação clínica.

def _dump_sugestao(s: PatientAISuggestion) -> dict:
    return {
        "id": s.id, "created_at": s.created_at, "model": s.model,
        "differential_diagnosis": s.differential_diagnosis,
        "suggested_workup": s.suggested_workup,
        "treatment_considerations": s.treatment_considerations,
        "sources": s.sources,
        "sources_pubmed": s.sources_pubmed,
    }


@router.post("/patients/{pid}/ai-assist", status_code=201)
def gerar_auxilio_ia(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    from app.services import rag

    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="A IA clínica está desligada nesta instalação.")

    p = _paciente_do_usuario(pid, db, user)
    usado = _consultas_ia_hoje(db, user.id)
    if usado >= settings.ai_daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Limite diário de {settings.ai_daily_limit} consultas atingido. Recomeça amanhã.",
        )

    tem_dado_clinico = any([
        p.chief_complaint, p.anamnesis, p.physical_exam, p.vital_signs,
        p.labs, p.imaging, p.problems,
    ])
    if not tem_dado_clinico:
        raise HTTPException(
            status_code=422,
            detail="Preencha ao menos queixa principal, anamnese, exame físico ou exames antes de pedir auxílio de IA.",
        )

    try:
        r = rag.analisar_caso(db, p)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"O provedor de IA não respondeu ({type(e).__name__}). Tente novamente.",
        )

    sugestao = PatientAISuggestion(
        patient_id=p.id, requested_by=user.id,
        case_snapshot=r["case_snapshot"], sources=r["sources"],
        sources_pubmed=r["sources_pubmed"], model=r["model"],
        differential_diagnosis=r["differential_diagnosis"],
        suggested_workup=r["suggested_workup"],
        treatment_considerations=r["treatment_considerations"],
    )
    db.add(sugestao)
    db.add(AuditLog(
        user_id=user.id, action="ai_assist_round", entity="patient", entity_id=str(p.id),
        detail={"modelo": r["model"], "fontes": [f["slug"] for f in r["sources"]]},
    ))
    db.commit()
    db.refresh(sugestao)
    return _dump_sugestao(sugestao)


@router.get("/patients/{pid}/ai-assist")
def listar_auxilios_ia(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    p = _paciente_do_usuario(pid, db, user)
    itens = sorted(p.ai_suggestions, key=lambda s: s.created_at, reverse=True)
    return [_dump_sugestao(s) for s in itens]
