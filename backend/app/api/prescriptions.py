from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import Prescription
from app.services.clinical_ownership import patient_for_user
from app.services.professional_profile import document_identity
from app.services.pdf.identidade_institucional import EMPRESA

router = APIRouter(prefix="/api/prescriptions", tags=["prescricoes"])


class ItemPrescricao(BaseModel):
    drug_name: str
    presentation: str
    posology: str
    orientation: str = ""
    # Tarefa B (CLAUDE.md, 02/08/2026) — marca escolhida via CMED em
    # /drugs/{slug}/apresentacoes, sempre opcional (genérico é o padrão).
    brand_name: str | None = None
    manufacturer: str | None = None
    ggrem: str | None = None
    pmc_snapshot: float | None = None
    uf: str | None = None
    cmed_version: str | None = None

    @field_validator("drug_name", "presentation", "posology")
    @classmethod
    def obrigatorio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Medicamento, apresentação e posologia são obrigatórios.")
        return value


class PrescricaoIn(BaseModel):
    patient_id: int
    items: list[ItemPrescricao] = Field(min_length=1)
    notes: str = ""


def _dump(p: Prescription) -> dict:
    items = [{**item,
              "drug_name": item.get("drug_name") or item.get("descricao") or "",
              "presentation": item.get("presentation") or item.get("apresentacao") or "",
              "posology": item.get("posology") or item.get("posologia") or "",
              "orientation": item.get("orientation") or item.get("orientacao") or ""}
             for item in (p.items or [])]
    return {
        "id": p.id, "patient_id": p.patient_id, "items": items,
        "notes": p.notes, "created_at": p.created_at,
    }


@router.post("", status_code=201)
def criar_prescricao(dados: PrescricaoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    patient_for_user(dados.patient_id, db, user)
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
    patient_for_user(patient_id, db, user)
    rows = (
        db.query(Prescription)
        .filter(Prescription.patient_id == patient_id, Prescription.created_by == user.id)
        .order_by(Prescription.created_at.desc())
        .all()
    )
    return [_dump(p) for p in rows]


@router.get("/{pid}/imprimir")
def dados_para_impressao(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    """Retorna os dados já formatados pra tela de impressão do frontend
    montar o documento (o frontend decide o HTML/CSS de impressão)."""
    dados = dados_para_revisao(pid, db, user)
    from app.services.kyc.access import exigir_liberacao_emissao
    exigir_liberacao_emissao(db, user)
    items = dados["prescricao"]["items"]
    if not items or any(not str(item.get(field) or "").strip()
                        for item in items for field in ("drug_name", "presentation", "posology")):
        raise HTTPException(status_code=409, detail="Prescrição incompleta. Revise medicamento, apresentação e posologia antes de imprimir.")
    return dados


@router.get("/{pid}/revisao")
def dados_para_revisao(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    """Permite corrigir uma cópia de receita antiga incompleta, sem liberar impressão."""
    presc = db.get(Prescription, pid)
    if not presc or presc.created_by != user.id:
        raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
    paciente = patient_for_user(presc.patient_id, db, user)
    return {
        "prescricao": _dump(presc),
        "paciente": {"initials": paciente.initials, "record_number": paciente.record_number},
        "medico": document_identity(user),
        "operadora": dict(EMPRESA),
    }
