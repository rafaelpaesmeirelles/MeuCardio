"""Proteção explícita contra exclusão física de prontuário multimodal.

A FK já é RESTRICT no banco, mas esta rota transforma a restrição em contrato
HTTP previsível antes de a exclusão canônica chegar ao flush. Quando não há
exame multimodal, delega integralmente ao fluxo existente de patient_profiles.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import patient_profiles
from app.core.db import get_db
from app.core.security import current_user
from app.models.patient_multimodal import PatientMultimodalExamRecord
from app.services.clinical_ownership import patient_profile_for_user

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])


@router.delete("/{pid}", status_code=204)
def apagar_paciente_com_guard_multimodal(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    possui_multimodal = (
        db.query(PatientMultimodalExamRecord.id)
        .filter(
            PatientMultimodalExamRecord.owner_id == user.id,
            PatientMultimodalExamRecord.patient_profile_id == pid,
        )
        .first()
        is not None
    )
    if possui_multimodal:
        raise HTTPException(
            status_code=409,
            detail=(
                "Paciente possui exame multimodal armazenado no prontuário e "
                "não pode ser apagado fisicamente."
            ),
        )
    return patient_profiles.apagar_paciente(pid=pid, db=db, user=user)
