from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.lab_test import LabTest

router = APIRouter(prefix="/api/lab-tests", tags=["exames"])


def _card(t: LabTest) -> dict:
    return {"id": t.id, "slug": t.slug, "name": t.name, "category": t.category, "theme": t.theme, "tags": t.tags}


def _detail(t: LabTest) -> dict:
    return {
        **_card(t),
        "what_it_measures": t.what_it_measures, "reference_range": t.reference_range,
        "indications": t.indications, "interpretation": t.interpretation,
        "limitations": t.limitations, "source_refs": t.source_refs,
    }


@router.get("/categories")
def categories(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(LabTest.category, func.count(LabTest.id))
        .where(LabTest.published.is_(True)).group_by(LabTest.category).order_by(LabTest.category)
    ).all()
    return [{"category": c, "count": n} for c, n in rows]


@router.get("")
def list_tests(
    category: str | None = None, q: str | None = None,
    limit: int = Query(60, le=200), offset: int = 0,
    db: Session = Depends(get_db), _=Depends(current_user),
):
    query = db.query(LabTest).filter(LabTest.published.is_(True))
    if category:
        query = query.filter(LabTest.category == category)
    if q:
        query = query.filter(LabTest.name.ilike(f"%{q.strip()}%"))
    total = query.count()
    items = query.order_by(LabTest.name).offset(offset).limit(limit).all()
    return {"total": total, "items": [_card(t) for t in items]}


@router.get("/{slug}")
def get_test(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    t = db.query(LabTest).filter(LabTest.slug == slug, LabTest.published.is_(True)).first()
    if not t:
        raise HTTPException(status_code=404, detail="Exame não encontrado.")
    return _detail(t)
