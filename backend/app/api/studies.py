import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.study import ScientificStudy
from app.services.study_slug_aliases import canonical_study_slug

router = APIRouter(prefix="/api/studies", tags=["estudos"])


def _termo_sem_acentos(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(char)
    ).strip()


def _contem_sem_acentos(column, value: str):
    return func.unaccent(func.lower(cast(column, Text))).contains(
        _termo_sem_acentos(value), autoescape=True,
    )


def _card(s: ScientificStudy) -> dict:
    return {
        "id": s.id, "slug": s.slug, "title": s.title, "study_type": s.study_type,
        "journal": s.journal, "year": s.year, "theme": s.theme,
    }


def _detail(s: ScientificStudy) -> dict:
    return {
        **_card(s), "authors": s.authors, "doi": s.doi, "pmid": s.pmid, "url": s.url,
        "summary": s.summary, "key_findings": s.key_findings,
        "clinical_implications": s.clinical_implications, "limitations": s.limitations,
        "tags": s.tags,
    }


@router.get("/types")
def types(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(ScientificStudy.study_type, func.count(ScientificStudy.id))
        .where(ScientificStudy.published.is_(True)).group_by(ScientificStudy.study_type)
    ).all()
    return [{"study_type": t, "count": c} for t, c in rows]


@router.get("/themes")
def themes(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(ScientificStudy.theme, func.count(ScientificStudy.id))
        .where(ScientificStudy.published.is_(True))
        .group_by(ScientificStudy.theme)
        .order_by(ScientificStudy.theme)
    ).all()
    return [{"theme": theme, "count": count} for theme, count in rows]


@router.get("")
def list_studies(
    study_type: str | None = None, theme: str | None = None,
    q: str | None = Query(None, max_length=200),
    limit: int = Query(60, ge=1, le=500), offset: int = Query(0, ge=0),
    db: Session = Depends(get_db), _=Depends(current_user),
):
    query = db.query(ScientificStudy).filter(ScientificStudy.published.is_(True))
    if study_type:
        query = query.filter(ScientificStudy.study_type == study_type)
    if theme:
        query = query.filter(ScientificStudy.theme == theme)
    if q and q.strip():
        query = query.filter(or_(
            _contem_sem_acentos(ScientificStudy.title, q),
            _contem_sem_acentos(ScientificStudy.theme, q),
            _contem_sem_acentos(ScientificStudy.journal, q),
            _contem_sem_acentos(ScientificStudy.tags, q),
        ))
    total = query.count()
    items = query.order_by(ScientificStudy.title).offset(offset).limit(limit).all()
    has_more = offset + len(items) < total
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": offset + len(items) if has_more else None,
        "has_more": has_more,
        "items": [_card(s) for s in items],
    }


@router.get("/{slug}")
def get_study(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    canonical_slug = canonical_study_slug(slug)
    s = db.query(ScientificStudy).filter(
        ScientificStudy.slug == canonical_slug,
        ScientificStudy.published.is_(True),
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    return _detail(s)
