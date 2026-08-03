from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.evidence import EvidenceRecord

router = APIRouter(prefix="/api/evidence", tags=["evidencias"])


def _card(e: EvidenceRecord) -> dict:
    return {
        "id": e.id, "slug": e.slug, "statement": e.statement,
        "recommendation_class": e.recommendation_class, "evidence_level": e.evidence_level,
        "society": e.society, "year": e.year, "theme": e.theme,
    }


def _detail(e: EvidenceRecord) -> dict:
    return {
        **_card(e), "guideline_title": e.guideline_title, "reference": e.reference,
        "tags": e.tags, "document_slug": e.document_slug,
        "review_status": e.review_status, "review_note": e.review_note,
    }


@router.get("/themes")
def themes(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(EvidenceRecord.theme, func.count(EvidenceRecord.id))
        .where(EvidenceRecord.published.is_(True)).group_by(EvidenceRecord.theme).order_by(EvidenceRecord.theme)
    ).all()
    return [{"theme": t, "count": c} for t, c in rows]


@router.get("")
def list_evidence(
    theme: str | None = None, recommendation_class: str | None = None,
    q: str | None = None, limit: int = Query(60, le=200), offset: int = 0,
    db: Session = Depends(get_db), _=Depends(current_user),
):
    query = db.query(EvidenceRecord).filter(EvidenceRecord.published.is_(True))
    if theme:
        query = query.filter(EvidenceRecord.theme == theme)
    if recommendation_class:
        query = query.filter(EvidenceRecord.recommendation_class == recommendation_class)
    if q:
        query = query.filter(EvidenceRecord.statement.ilike(f"%{q.strip()}%"))
    total = query.count()
    items = query.order_by(EvidenceRecord.theme, EvidenceRecord.statement).offset(offset).limit(limit).all()
    return {"total": total, "items": [_card(e) for e in items]}


@router.get("/{slug}")
def get_evidence(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    e = db.query(EvidenceRecord).filter(EvidenceRecord.slug == slug, EvidenceRecord.published.is_(True)).first()
    if not e:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
    return _detail(e)
