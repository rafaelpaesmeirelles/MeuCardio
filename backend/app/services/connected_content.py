"""Launch-grade contextual wrapper for CorVIA's "Tudo com Tudo".

It preserves the mature per-front queries in `related_content.py` and adds the
missing launch guarantees at the boundary exposed to the UI:

1. historical theme aliases are canonicalized and merged, so a valid item is
   not lost merely because an older front used a synonymous label;
2. medications outside the generic Farmacologia topic are admitted only when
   the medication's reviewed structured indications explicitly match the
   requested clinical topic;
3. a medication can ask for its own connected ecosystem: only clinical topics
   explicitly supported by its indications are traversed, then all published
   fronts from those topics are merged and deduplicated.

No fuzzy semantic similarity is used here. A missing relation is preferable to
a clinically irrelevant relation.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.drug import Drug
from app.services.related_content import LIMITE_POR_CATEGORIA, buscar_relacionados as _base
from app.services.topic_relevance import (
    SUPPORTED_DRUG_TOPICS,
    canonical_theme,
    drug_matches_theme,
    theme_variants,
)


def _merge_groups(responses: list[dict], *, limit: int = LIMITE_POR_CATEGORIA) -> list[dict]:
    order: list[str] = []
    by_type: dict[str, dict] = {}
    seen: dict[str, set[tuple[str, str]]] = {}

    for response in responses:
        for group in response.get("grupos", []):
            kind = group["tipo"]
            if kind not in by_type:
                order.append(kind)
                by_type[kind] = {
                    "tipo": kind,
                    "rotulo": group["rotulo"],
                    "rota_lista": group["rota_lista"],
                    "itens": [],
                }
                seen[kind] = set()
            for item in group.get("itens", []):
                key = (kind, item.get("slug", ""))
                if key in seen[kind]:
                    continue
                seen[kind].add(key)
                by_type[kind]["itens"].append(item)

    for group in by_type.values():
        group["itens"] = group["itens"][:limit]
    return [by_type[kind] for kind in order]


def _contextual_drugs(
    db: Session, theme: str, excluir_tipo: str | None, excluir_slug: str | None,
) -> list[dict]:
    query = select(Drug).where(Drug.published.is_(True)).order_by(Drug.generic_name)
    drugs = db.execute(query).scalars().all()
    items: list[dict] = []
    for drug in drugs:
        if excluir_tipo == "medicamento" and excluir_slug == drug.slug:
            continue
        if not drug_matches_theme(drug, theme):
            continue
        items.append({
            "slug": drug.slug,
            "titulo": drug.generic_name,
            "subtitulo": drug.drug_class,
            "rota": f"/medicamentos?slug={drug.slug}",
        })
        if len(items) >= LIMITE_POR_CATEGORIA:
            break
    return items


def temas_clinicos_do_medicamento(drug: Drug) -> list[str]:
    """Clinical topics explicitly supported by the drug's structured indications.

    This deliberately excludes the catch-all `Farmacologia`: on a drug detail
    page the subject is the drug itself, so connecting it to five arbitrary
    pharmacology items would violate the user's "within the subject, only the
    subject" rule. The broad Pharmacology catalogue remains available as a
    normal topic elsewhere.
    """
    return [
        theme for theme in sorted(SUPPORTED_DRUG_TOPICS, key=str.casefold)
        if drug_matches_theme(drug, theme)
    ]


def buscar_relacionados_contextuais(
    db: Session,
    tema: str,
    excluir_tipo: str | None = None,
    excluir_slug: str | None = None,
) -> dict:
    canonical = canonical_theme(tema)
    if not canonical:
        return {"tema": "", "grupos": [], "total": 0}

    variants = theme_variants(canonical)
    responses = [
        _base(db, variant, excluir_tipo=excluir_tipo, excluir_slug=excluir_slug)
        for variant in variants
    ]
    groups = _merge_groups(responses)

    # The legacy service intentionally attached every drug only to
    # Farmacologia. For launch, keep that broad catalogue behavior there, but
    # make clinical topics receive only drugs with a reviewed indication that
    # explicitly supports the relation.
    drug_group = next((group for group in groups if group["tipo"] == "medicamento"), None)
    if drug_group is None:
        drug_group = {
            "tipo": "medicamento", "rotulo": "Medicamentos",
            "rota_lista": "/medicamentos", "itens": [],
        }
        groups.append(drug_group)
    drug_group["itens"] = _contextual_drugs(db, canonical, excluir_tipo, excluir_slug)

    total = sum(len(group["itens"]) for group in groups)
    return {"tema": canonical, "grupos": groups, "total": total}


def buscar_relacionados_do_medicamento(db: Session, slug: str) -> dict | None:
    """Traverse all explicit clinical topics for one published medication.

    Returns None only when the drug itself is not published/found. A drug with
    no safely inferable clinical topic returns an empty ecosystem rather than
    unrelated content.
    """
    drug = db.execute(
        select(Drug).where(Drug.slug == slug, Drug.published.is_(True))
    ).scalar_one_or_none()
    if drug is None:
        return None

    themes = temas_clinicos_do_medicamento(drug)
    responses = [
        buscar_relacionados_contextuais(
            db, theme, excluir_tipo="medicamento", excluir_slug=drug.slug
        )
        for theme in themes
    ]
    groups = _merge_groups(responses)
    total = sum(len(group["itens"]) for group in groups)
    return {
        "medicamento": {"slug": drug.slug, "titulo": drug.generic_name},
        "temas": themes,
        "grupos": groups,
        "total": total,
    }
