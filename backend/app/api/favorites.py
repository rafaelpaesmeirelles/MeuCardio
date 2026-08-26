from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.content import Document
from app.models.drug import Drug
from app.models.favorite import Favorite
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy
from app.models.user import User
from app.services.study_slug_aliases import canonical_study_slug

router = APIRouter(prefix="/api/favorites", tags=["favoritos"])

TIPOS_VALIDOS = {"documento", "medicamento", "imagem", "exame", "evidencia", "estudo"}


def _resumo_item(db: Session, item_type: str, item_id: int) -> dict | None:
    if item_type == "documento":
        d = db.get(Document, item_id)
        if not d:
            return None
        return {"title": d.title, "slug": d.slug, "url": f"/biblioteca/{d.slug}", "meta": d.theme}
    if item_type == "medicamento":
        d = db.get(Drug, item_id)
        if not d:
            return None
        return {"title": d.generic_name, "slug": d.slug, "url": f"/medicamentos?slug={d.slug}", "meta": d.drug_class}
    if item_type == "imagem":
        d = db.get(GalleryImage, item_id)
        if not d:
            return None
        return {"title": d.title, "slug": d.slug, "url": f"/galeria/{d.slug}", "meta": d.modality}
    if item_type == "exame":
        d = db.get(LabTest, item_id)
        if not d:
            return None
        return {"title": d.name, "slug": d.slug, "url": f"/exames/{d.slug}", "meta": d.category}
    if item_type == "evidencia":
        d = db.get(EvidenceRecord, item_id)
        if not d:
            return None
        # Diretriz em GRADE (OMS, e as brasileiras de Chagas e eco de estresse) usa
        # forca forte/condicional, nao Classe I-III — "Classe Forte" nao existe em
        # nenhum dos dois sistemas. Mesma distincao feita em Evidencia.tsx.
        rotulo = ("Classe" if d.recommendation_class in ("I", "IIa", "IIb", "III") else "Força")
        return {"title": d.statement[:80], "slug": d.slug, "url": f"/evidencias/{d.slug}",
                "meta": f"{rotulo} {d.recommendation_class}"}
    if item_type == "estudo":
        d = db.get(ScientificStudy, item_id)
        if not d:
            return None
        canonical_slug = canonical_study_slug(d.slug)
        if canonical_slug != d.slug:
            canonical = db.query(ScientificStudy).filter(
                ScientificStudy.slug == canonical_slug,
                ScientificStudy.published.is_(True),
            ).first()
            if canonical:
                d = canonical
        return {"title": d.title, "slug": d.slug, "url": f"/estudos/{d.slug}", "meta": str(d.year)}
    return None


class NovoFavorito(BaseModel):
    item_type: str
    item_id: int


@router.get("")
def listar(db: Session = Depends(get_db), user: User = Depends(current_user)):
    itens = db.query(Favorite).filter(Favorite.user_id == user.id).order_by(Favorite.created_at.desc()).all()
    resultado = []
    for f in itens:
        resumo = _resumo_item(db, f.item_type, f.item_id)
        if resumo:  # o item pode ter sido apagado depois de favoritado — ignora silenciosamente
            resultado.append({"id": f.id, "item_type": f.item_type, "item_id": f.item_id, **resumo})
    return resultado


@router.post("", status_code=201)
def adicionar(dados: NovoFavorito, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if dados.item_type not in TIPOS_VALIDOS:
        raise HTTPException(status_code=422, detail="Tipo de item inválido.")
    if not _resumo_item(db, dados.item_type, dados.item_id):
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    existente = db.query(Favorite).filter(
        Favorite.user_id == user.id, Favorite.item_type == dados.item_type, Favorite.item_id == dados.item_id
    ).first()
    if existente:
        return {"id": existente.id, "ja_existia": True}
    novo = Favorite(user_id=user.id, item_type=dados.item_type, item_id=dados.item_id)
    db.add(novo)
    db.commit()
    return {"id": novo.id, "ja_existia": False}


@router.delete("/{item_type}/{item_id}", status_code=204)
def remover(item_type: str, item_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    db.query(Favorite).filter(
        Favorite.user_id == user.id, Favorite.item_type == item_type, Favorite.item_id == item_id
    ).delete()
    db.commit()
