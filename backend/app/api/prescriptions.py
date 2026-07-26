from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import Prescription
from app.models.round import Patient

router = APIRouter(prefix="/api/prescriptions", tags=["prescricoes"])


class ItemPrescricao(BaseModel):
    drug_name: str
    presentation: str = ""
    posology: str
    orientation: str = ""


class PrescricaoIn(BaseModel):
    patient_id: int
    items: list[ItemPrescricao]
    notes: str = ""


def _dono_do_paciente(patient_id: int, db: Session, user) -> Patient:
    p = db.get(Patient, patient_id)
    if not p or (p.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return p


def _dump(p: Prescription) -> dict:
    return {
        "id": p.id, "patient_id": p.patient_id, "items": p.items,
        "notes": p.notes, "created_at": p.created_at,
    }


@router.post("", status_code=201)
def criar_prescricao(dados: PrescricaoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    _dono_do_paciente(dados.patient_id, db, user)
    p = Prescription(
        patient_id=dados.patient_id, created_by=user.id,
        items=[i.model_dump() for i in dados.items], notes=dados.notes or None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _dump(p)


@router.get("/patient/{patient_id}")
def listar_por_paciente(patient_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    _dono_do_paciente(patient_id, db, user)
    rows = (
        db.query(Prescription)
        .filter(Prescription.patient_id == patient_id)
        .order_by(Prescription.created_at.desc())
        .all()
    )
    return [_dump(p) for p in rows]


@router.get("/{pid}/imprimir")
def dados_para_impressao(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    """Retorna os dados já formatados pra tela de impressão do frontend
    montar o documento (o frontend decide o HTML/CSS de impressão)."""
    presc = db.get(Prescription, pid)
    if not presc:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
    paciente = _dono_do_paciente(presc.patient_id, db, user)
    return {
        "prescricao": _dump(presc),
        "paciente": {"initials": paciente.initials, "record_number": paciente.record_number},
        "medico": {"full_name": user.full_name, "council_name": user.council_name,
                    "council_number": user.council_number, "council_state": user.council_state},
    }
