import re
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.evidence import EvidenceRecord

router = APIRouter(prefix="/api/evidence", tags=["evidencias"])


def _url_segura(valor: str | None) -> str | None:
    if not valor:
        return None
    valor = valor.strip().rstrip(".,;)")
    try:
        partes = urlsplit(valor)
    except ValueError:
        return None
    if partes.scheme not in {"http", "https"} or not partes.netloc or partes.username or partes.password:
        return None
    return valor


def _documento_original(e: EvidenceRecord) -> str | None:
    direta = _url_segura(e.source_url)
    if direta:
        return direta
    if e.doi:
        doi = e.doi.strip()
        if doi.lower().startswith("https://doi.org/"):
            return _url_segura(doi)
        if re.fullmatch(r"10\.\d{4,9}/\S+", doi):
            return f"https://doi.org/{doi}"
    achado = re.search(r"https?://[^\s<>\]]+", e.reference or "")
    return _url_segura(achado.group(0)) if achado else None


def _card(e: EvidenceRecord) -> dict:
    return {
        "id": e.id,
        "slug": e.slug,
        "statement": e.statement,
        "summary": (e.summary or e.statement).strip(),
        "recommendation_class": e.recommendation_class,
        "evidence_level": e.evidence_level,
        "society": e.society,
        "year": e.year,
        "theme": e.theme,
        "source_url": _documento_original(e),
        "doi": e.doi,
    }


def _detail(e: EvidenceRecord) -> dict:
    return {
        **_card(e),
        "guideline_title": e.guideline_title,
        "reference": e.reference,
        "tags": e.tags,
        "document_slug": e.document_slug,
        "review_status": e.review_status,
        "review_note": e.review_note,
    }


@router.get("/themes")
def themes(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(EvidenceRecord.theme, func.count(EvidenceRecord.id))
        .where(EvidenceRecord.published.is_(True))
        .group_by(EvidenceRecord.theme)
        .order_by(EvidenceRecord.theme)
    ).all()
    return [{"theme": theme, "count": count} for theme, count in rows]


@router.get("")
def list_evidence(
    theme: str | None = None,
    recommendation_class: str | None = None,
    q: str | None = None,
    limit: int = Query(60, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    query = db.query(EvidenceRecord).filter(EvidenceRecord.published.is_(True))
    if theme:
        query = query.filter(EvidenceRecord.theme == theme)
    if recommendation_class:
        query = query.filter(EvidenceRecord.recommendation_class == recommendation_class)
    if q and q.strip():
        termo = f"%{q.strip()}%"
        query = query.filter(or_(
            EvidenceRecord.statement.ilike(termo),
            EvidenceRecord.summary.ilike(termo),
            EvidenceRecord.guideline_title.ilike(termo),
            EvidenceRecord.theme.ilike(termo),
            EvidenceRecord.reference.ilike(termo),
        ))
    total = query.count()
    items = (
        query.order_by(EvidenceRecord.theme, EvidenceRecord.statement)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": offset + len(items) if offset + len(items) < total else None,
        "has_more": offset + len(items) < total,
        "items": [_card(e) for e in items],
    }


@router.get("/{slug}")
def get_evidence(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    evidence = db.query(EvidenceRecord).filter(
        EvidenceRecord.slug == slug,
        EvidenceRecord.published.is_(True),
    ).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
    return _detail(evidence)
