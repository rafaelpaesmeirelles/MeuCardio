from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.gallery import GalleryImage

router = APIRouter(prefix="/api/gallery", tags=["galeria"])


def _card(img: GalleryImage) -> dict:
    return {
        "id": img.id, "slug": img.slug, "title": img.title,
        "modality": img.modality, "theme": img.theme,
        "file_path": f"/galeria/{img.file_path}",
        "thumbnail_path": f"/galeria/{img.thumbnail_path}" if img.thumbnail_path else None,
        "tags": img.tags,
    }


def _detail(img: GalleryImage) -> dict:
    return {
        **_card(img),
        "findings": img.findings,
        "teaching_points": img.teaching_points,
        "source_name": img.source_name,
        "source_url": img.source_url,
        "license": img.license,
        "attribution": img.attribution,
    }


@router.get("/modalities")
def modalities(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(GalleryImage.modality, func.count(GalleryImage.id))
        .where(GalleryImage.published.is_(True))
        .group_by(GalleryImage.modality).order_by(GalleryImage.modality)
    ).all()
    return [{"modality": m, "count": c} for m, c in rows]


@router.get("/images")
def list_images(
    modality: str | None = None,
    theme: str | None = None,
    q: str | None = None,
    limit: int = Query(60, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    query = db.query(GalleryImage).filter(GalleryImage.published.is_(True))
    if modality:
        query = query.filter(GalleryImage.modality == modality)
    if theme:
        query = query.filter(GalleryImage.theme == theme)
    if q:
        termo = f"%{q.strip()}%"
        query = query.filter(or_(
            GalleryImage.title.ilike(termo),
            GalleryImage.theme.ilike(termo),
            GalleryImage.findings.ilike(termo),
            cast(GalleryImage.tags, Text).ilike(termo),
        ))
    total = query.count()
    items = query.order_by(GalleryImage.theme, GalleryImage.title).offset(offset).limit(limit).all()
    return {"total": total, "items": [_card(i) for i in items]}


@router.get("/images/{slug}")
def get_image(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    img = db.query(GalleryImage).filter(
        GalleryImage.slug == slug, GalleryImage.published.is_(True)
    ).first()
    if not img:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    return _detail(img)
