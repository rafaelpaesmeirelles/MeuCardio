from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import Appointment
from app.models.round import Patient
from app.services.clinical_ownership import patient_for_user

router = APIRouter(prefix="/api/appointments", tags=["agenda"])

TIPOS_VALIDOS = {"consulta", "retorno", "exame", "outro"}
STATUS_VALIDOS = {"confirmado", "cancelado", "realizado", "faltou"}


class AgendamentoIn(BaseModel):
    patient_id: int | None = None
    patient_name_temp: str | None = None
    patient_phone_temp: str | None = None
    scheduled_at: datetime
    duration_minutes: int = 30
    appointment_type: str = "consulta"
    notes: str | None = None


def _dump(a: Appointment, db: Session) -> dict:
    nome = a.patient_name_temp
    if a.patient_id:
        p = db.get(Patient, a.patient_id)
        if p:
            nome = f"{p.initials} (prontuário {p.record_number})"
    return {
        "id": a.id, "patient_id": a.patient_id, "patient_name": nome,
        "patient_phone_temp": a.patient_phone_temp,
        "scheduled_at": a.scheduled_at, "duration_minutes": a.duration_minutes,
        "appointment_type": a.appointment_type, "status": a.status, "notes": a.notes,
    }


@router.get("")
def listar(
    inicio: datetime | None = None, fim: datetime | None = None,
    db: Session = Depends(get_db), user=Depends(current_user),
):
    query = db.query(Appointment).filter(Appointment.owner_id == user.id)
    if inicio:
        query = query.filter(Appointment.scheduled_at >= inicio)
    if fim:
        query = query.filter(Appointment.scheduled_at <= fim)
    rows = query.order_by(Appointment.scheduled_at).all()
    return [_dump(a, db) for a in rows]


@router.post("", status_code=201)
def criar(dados: AgendamentoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if dados.appointment_type not in TIPOS_VALIDOS:
        raise HTTPException(status_code=422, detail="Tipo de agendamento inválido.")
    if dados.patient_id:
        patient_for_user(dados.patient_id, db, user)
    if not dados.patient_id and not dados.patient_name_temp:
        raise HTTPException(status_code=422, detail="Informe o paciente cadastrado ou ao menos um nome.")

    a = Appointment(owner_id=user.id, **dados.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return _dump(a, db)


@router.patch("/{aid}")
def atualizar(aid: int, payload: dict, db: Session = Depends(get_db), user=Depends(current_user)):
    a = db.get(Appointment, aid)
    if not a or a.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    if "status" in payload and payload["status"] not in STATUS_VALIDOS:
        raise HTTPException(status_code=422, detail="Status inválido.")
    for campo in ("scheduled_at", "duration_minutes", "appointment_type", "status", "notes"):
        if campo in payload:
            setattr(a, campo, payload[campo])
    db.commit()
    return _dump(a, db)


@router.delete("/{aid}", status_code=204)
def apagar(aid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    db.query(Appointment).filter(Appointment.id == aid, Appointment.owner_id == user.id).delete()
    db.commit()
