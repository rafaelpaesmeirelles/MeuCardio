from __future__ import annotations

from statistics import mean

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.cmed import CmedApresentacao, CmedVersao
from app.models.drug import Drug
from app.services.cmed_precos import preco_pmc

router = APIRouter(prefix="/api/drug-insights", tags=["medicamentos"])


class CompareIn(BaseModel):
    slugs: list[str] = Field(min_length=2, max_length=4)
    uf: str | None = Field(default=None, min_length=2, max_length=2)


def _versao_atual(db: Session) -> CmedVersao | None:
    return db.query(CmedVersao).order_by(CmedVersao.id.desc()).first()


def _cmed(db: Session, drug: Drug, uf: str | None, versao: CmedVersao | None) -> dict:
    if versao is None:
        return {
            "published_at": None,
            "uf": uf,
            "presentations": [],
            "average_pmc": None,
            "average_label": "Nenhuma lista CMED foi importada.",
        }

    rows = (
        db.query(CmedApresentacao)
        .filter(
            CmedApresentacao.drug_id == drug.id,
            CmedApresentacao.cmed_versao_id == versao.id,
        )
        .order_by(CmedApresentacao.produto, CmedApresentacao.apresentacao)
        .all()
    )
    presentations = []
    prices: list[float] = []
    for row in rows:
        price = preco_pmc(row.pmc_por_aliquota or {}, uf)
        value = price.get("valor")
        if value is not None:
            prices.append(float(value))
        presentations.append({
            "brand_name": row.produto,
            "manufacturer": row.laboratorio,
            "presentation": row.apresentacao,
            "ggrem": row.ggrem,
            "hospital_only": row.restricao_hospitalar,
            "pmc": value,
            "pmc_label": price.get("rotulo"),
        })

    average = round(mean(prices), 2) if prices else None
    label = (
        "Média aritmética dos tetos PMC das apresentações com preço publicado; "
        "não corresponde ao preço final praticado pela farmácia."
        if average is not None else
        "Nenhuma apresentação possui PMC ao consumidor publicado."
    )
    return {
        "published_at": versao.publicado_em,
        "uf": uf,
        "presentations": presentations[:120],
        "average_pmc": average,
        "average_label": label,
    }


def _payload(db: Session, drug: Drug, uf: str | None, versao: CmedVersao | None) -> dict:
    return {
        "slug": drug.slug,
        "generic_name": drug.generic_name,
        "drug_class": drug.drug_class,
        "brand_names": drug.brand_names or [],
        "mechanism": drug.mechanism,
        "presentations": drug.presentations or [],
        "commercial_presentations": drug.commercial_presentations or [],
        "dosing": drug.dosing or {},
        "renal_adjustment": drug.renal_adjustment,
        "hepatic_adjustment": drug.hepatic_adjustment,
        "contraindications": drug.contraindications or [],
        "interactions": drug.interactions or [],
        "monitoring": drug.monitoring or [],
        "indications": drug.indications or [],
        "adverse_effects": drug.adverse_effects or [],
        "pregnancy": drug.pregnancy,
        "lactation": drug.lactation,
        "notes": drug.notes or {},
        "half_life_hours": float(drug.half_life_hours) if drug.half_life_hours is not None else None,
        "half_life_note": drug.half_life_note,
        "duration_of_action_hours": drug.duration_of_action_hours,
        "duration_of_action_note": drug.duration_of_action_note,
        "duration_of_action_source": drug.duration_of_action_source,
        "sbp_reduction_mmhg": float(drug.sbp_reduction_mmhg) if drug.sbp_reduction_mmhg is not None else None,
        "dbp_reduction_mmhg": float(drug.dbp_reduction_mmhg) if drug.dbp_reduction_mmhg is not None else None,
        "bp_evidence_source": drug.bp_evidence_source,
        "references": drug.references or [],
        "review_status": drug.review_status,
        "cmed": _cmed(db, drug, uf, versao),
    }


@router.get("/{slug}")
def detail(
    slug: str,
    uf: str | None = Query(None, min_length=2, max_length=2),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    drug = db.query(Drug).filter(Drug.slug == slug, Drug.published.is_(True)).first()
    if not drug:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado.")
    resolved_uf = (uf or user.council_state or "").upper() or None
    return _payload(db, drug, resolved_uf, _versao_atual(db))


@router.post("/compare")
def compare(
    data: CompareIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    slugs = list(dict.fromkeys(data.slugs))
    if not 2 <= len(slugs) <= 4:
        raise HTTPException(status_code=422, detail="Selecione de 2 a 4 medicamentos diferentes.")
    drugs = db.query(Drug).filter(Drug.slug.in_(slugs), Drug.published.is_(True)).all()
    by_slug = {drug.slug: drug for drug in drugs}
    missing = [slug for slug in slugs if slug not in by_slug]
    if missing:
        raise HTTPException(status_code=404, detail=f"Não encontrado: {', '.join(missing)}")
    resolved_uf = (data.uf or user.council_state or "").upper() or None
    version = _versao_atual(db)
    return {
        "uf": resolved_uf,
        "drugs": [_payload(db, by_slug[slug], resolved_uf, version) for slug in slugs],
        "warnings": [
            "A redução de pressão arterial provém de fontes e populações que podem ser heterogêneas; não representa resposta individual.",
            "Meia-vida e duração de ação são grandezas diferentes e não devem ser interpretadas como equivalentes.",
            "Preço CMED é teto regulatório de referência, não preço final da farmácia.",
        ],
    }
