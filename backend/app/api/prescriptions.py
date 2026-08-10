from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import Prescription
from app.services.clinical_ownership import patient_for_user
from app.services.professional_profile import council_display

router = APIRouter(prefix="/api/prescriptions", tags=["prescricoes"])


class ItemPrescricao(BaseModel):
    drug_name: str
    presentation: str = ""
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


class PrescricaoIn(BaseModel):
    patient_id: int
    items: list[ItemPrescricao]
    notes: str = ""


def _dump(p: Prescription) -> dict:
    return {
        "id": p.id, "patient_id": p.patient_id, "items": p.items,
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
    paciente = patient_for_user(presc.patient_id, db, user)
    nome_conselho, estado_conselho = council_display(user)
    return {
        "prescricao": _dump(presc),
        "paciente": {"initials": paciente.initials, "record_number": paciente.record_number},
        # RQE e especialidade entram no cabeçalho impresso: num receituário que
        # circula fora da plataforma, é o registro do especialista que dá peso ao
        # documento — e é dado que o médico já preencheu em Minha Conta.
        # `document_logo_url` (Tarefa 4) — logo pessoal/do consultório, exibida
        # JUNTO da logo da Corvia em `CabecalhoDocumento.tsx`, mesmo par que o
        # PDF do backend já desenha em `pdf_documento.py`.
        # `council_display()` troca "OUTRO" pelo nome/estado que o médico
        # digitou no cadastro, quando houver (08/08/2026) — nunca afeta o
        # escopo de prescrição, que é decidido à parte por `user.council_name`.
        "medico": {"full_name": user.full_name, "council_name": nome_conselho,
                    "council_number": user.council_number, "council_state": estado_conselho,
                    "rqe": user.rqe, "specialty": user.specialty,
                    "document_logo_url": user.document_logo_url},
    }
