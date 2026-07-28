from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.audit import AuditLog
from app.models.drug import Drug

router = APIRouter(prefix="/api/drugs", tags=["medicamentos"])

FIELDS = (
    "slug generic_name brand_names drug_class mechanism presentations "
    "commercial_presentations dosing "
    "renal_adjustment hepatic_adjustment contraindications interactions monitoring "
    "pregnancy lactation outcomes cost_reference half_life_hours half_life_note "
    "sbp_reduction_mmhg dbp_reduction_mmhg bp_evidence_source "
    "references review_status"
).split()


def _dump(d: Drug) -> dict:
    return {f: getattr(d, f) for f in FIELDS}


class MeiaVidaIn(BaseModel):
    half_life_hours: float | None = None
    half_life_note: str | None = None


class EficaciaPAIn(BaseModel):
    sbp_reduction_mmhg: float | None = None
    dbp_reduction_mmhg: float | None = None
    bp_evidence_source: str | None = None


class ApresentacaoComercial(BaseModel):
    brand_name: str
    manufacturer: str
    form: str = "comprimido"
    dosage: str
    pack_sizes: list[int] = []
    generic_available: bool = False


@router.get("")
def list_drugs(
    q: str | None = None,
    drug_class: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    # Só medicamento publicado aparece — mesmo checkpoint das outras frentes.
    query = db.query(Drug).filter(Drug.published.is_(True))
    if q:
        query = query.filter(Drug.generic_name.ilike(f"%{q}%"))
    if drug_class:
        query = query.filter(Drug.drug_class == drug_class)
    return [
        {"slug": d.slug, "generic_name": d.generic_name, "drug_class": d.drug_class,
         "review_status": d.review_status}
        for d in query.order_by(Drug.generic_name).limit(300)
    ]


@router.get("/compare")
def compare(
    slugs: list[str] = Query(..., alias="slug"),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    if not 1 <= len(slugs) <= 4:
        raise HTTPException(status_code=422, detail="Selecione de 1 a 4 medicamentos.")
    drugs = db.query(Drug).filter(Drug.slug.in_(slugs), Drug.published.is_(True)).all()
    found = {d.slug for d in drugs}
    missing = [s for s in slugs if s not in found]
    if missing:
        raise HTTPException(status_code=404, detail=f"Não encontrado: {', '.join(missing)}")
    return {"drugs": [_dump(d) for d in drugs]}


@router.get("/{slug}")
def get_drug(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    d = db.query(Drug).filter(Drug.slug == slug, Drug.published.is_(True)).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    return _dump(d)


@router.patch("/{slug}/meia-vida")
def definir_meia_vida(
    slug: str, dados: MeiaVidaIn, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Só admin define este número — não é extraído automaticamente do texto
    livre de farmacocinética, que é solto demais pra confiar sem revisão humana."""
    d = db.query(Drug).filter(Drug.slug == slug).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    if dados.half_life_hours is not None and not (0 < dados.half_life_hours < 1000):
        raise HTTPException(status_code=422, detail="Valor de meia-vida fora de uma faixa plausível.")

    d.half_life_hours = dados.half_life_hours
    d.half_life_note = dados.half_life_note
    db.add(AuditLog(
        user_id=admin.id, action="definir_meia_vida", entity="drug", entity_id=slug,
        detail={"half_life_hours": dados.half_life_hours},
    ))
    db.commit()
    return _dump(d)


@router.put("/{slug}/apresentacoes-comerciais")
def definir_apresentacoes_comerciais(
    slug: str, dados: list[ApresentacaoComercial],
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    """Substitui a lista inteira de apresentações comerciais do medicamento.
    Só admin — dado comercial (marca, laboratório, caixa) exige a mesma
    checagem de fonte que qualquer outro dado clínico neste sistema."""
    d = db.query(Drug).filter(Drug.slug == slug).first()
    if not d:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    d.commercial_presentations = [item.model_dump() for item in dados]
    db.add(AuditLog(
        user_id=admin.id, action="definir_apresentacoes_comerciais", entity="drug", entity_id=slug,
        detail={"quantidade": len(dados)},
    ))
    db.commit()
    return _dump(d)
