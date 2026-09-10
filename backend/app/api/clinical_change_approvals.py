from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import require_owner_admin
from app.models.clinical_change_proposal import ClinicalChangeProposal
from app.services import clinical_change_approvals as service
router = APIRouter(prefix="/api/clinical-change-approvals", tags=["aprovação-clínica"])

class Approval(BaseModel):
    expected_version: int = Field(ge=1)

class Rejection(Approval):
    reason: str = Field(min_length=1, max_length=2000)

@router.get("")
def listing(status: Literal["pending", "approved", "rejected"] = "pending", limit: int = Query(50, ge=1, le=50),
            offset: int = Query(0, ge=0), db: Session = Depends(get_db), user=Depends(require_owner_admin)):
    query = db.query(ClinicalChangeProposal).filter_by(status=status)
    return {"total": query.count(), "items": [service.dump(db, p, details=False) for p in query.order_by(ClinicalChangeProposal.id.desc()).offset(offset).limit(limit).all()]}

@router.get("/count")
def pending_count(db: Session = Depends(get_db), user=Depends(require_owner_admin)):
    return {"pending": db.query(ClinicalChangeProposal).filter_by(status="pending").count()}

@router.get("/{proposal_id}")
def detail(proposal_id: int, db: Session = Depends(get_db), user=Depends(require_owner_admin)):
    proposal = db.get(ClinicalChangeProposal, proposal_id)
    if not proposal: raise HTTPException(404, "Proposta clínica não encontrada.")
    return service.dump(db, proposal)

@router.post("/{proposal_id}/approve")
def approve(proposal_id: int, body: Approval, db: Session = Depends(get_db), user=Depends(require_owner_admin)):
    return service.dump(db, service.approve(db, proposal_id, body.expected_version, user))

@router.post("/{proposal_id}/reject")
def reject(proposal_id: int, body: Rejection, db: Session = Depends(get_db), user=Depends(require_owner_admin)):
    return service.dump(db, service.reject(db, proposal_id, body.expected_version, body.reason, user))
