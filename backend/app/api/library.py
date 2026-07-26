from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.content import Document, DocumentRevision

router = APIRouter(prefix="/api/library", tags=["biblioteca"])


def _card(d: Document) -> dict:
    return {
        "id": d.id,
        "slug": d.slug,
        "title": d.title,
        "kind": d.kind,
        "theme": d.theme,
        "summary": d.summary,
        "tags": d.tags,
        "evidence_level": d.evidence_level,
        "review_status": d.review_status,
        "source_tier": d.source_tier,
        "gaps": d.gaps,
        "updated_at": d.updated_at,
    }


@router.get("/themes")
def themes(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(Document.theme, func.count(Document.id))
        .where(Document.published.is_(True))
        .group_by(Document.theme).order_by(Document.theme)
    ).all()
    return [{"theme": t, "count": c} for t, c in rows]


@router.get("/documents")
def list_documents(
    theme: str | None = None,
    kind: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    q = db.query(Document).filter(Document.published.is_(True))
    if theme:
        q = q.filter(Document.theme == theme)
    if kind:
        q = q.filter(Document.kind == kind)
    total = q.count()
    items = q.order_by(Document.title).offset(offset).limit(limit).all()
    return {"total": total, "items": [_card(d) for d in items]}


@router.get("/documents/{slug}")
def get_document(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    d = db.query(Document).filter(Document.slug == slug, Document.published.is_(True)).first()
    if not d:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou ainda em revisão.")
    return {**_card(d), "body_md": d.body_md, "source_refs": d.source_refs,
            "source_tier": d.source_tier, "gaps": d.gaps, "version": d.version}


@router.put("/documents/{slug}")
def update_document(
    slug: str, payload: dict, db: Session = Depends(get_db), user=Depends(require_admin)
):
    d = db.query(Document).filter(Document.slug == slug).first()
    if not d:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    db.add(DocumentRevision(
        document_id=d.id, version=d.version, body_md=d.body_md, author_id=user.id
    ))
    for f in ("title", "summary", "body_md", "theme", "kind", "review_status", "evidence_level"):
        if f in payload:
            setattr(d, f, payload[f])
    d.version += 1
    db.commit()
    return {"slug": d.slug, "version": d.version}
