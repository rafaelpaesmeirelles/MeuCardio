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

from app.models.content import Document
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy
from app.services.related_content import LIMITE_POR_CATEGORIA, buscar_relacionados as _base
from app.services.topic_relevance import (
    CONTEXT_MIN_RELEVANCE_SCORE,
    CONTEXT_TAG_TOKEN_WEIGHT,
    SUPPORTED_DRUG_TOPICS,
    ContextualRelevance,
    canonical_theme,
    drug_matches_theme,
    relevance_tokens,
    score_contextual_relevance,
    theme_variants,
)


def _merge_groups(
    responses: list[dict], *, limit: int | None = LIMITE_POR_CATEGORIA,
) -> list[dict]:
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

    if limit is not None:
        for group in by_type.values():
            group["itens"] = group["itens"][:limit]
    return [by_type[kind] for kind in order]


def _contextual_drugs(
    db: Session, theme: str, excluir_tipo: str | None, excluir_slug: str | None,
    *, limit: int | None = LIMITE_POR_CATEGORIA,
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
        if limit is not None and len(items) >= limit:
            break
    return items


def _tokens(value: object) -> set[str]:
    return relevance_tokens(value)


def _with_match_metadata(item: dict, match: ContextualRelevance) -> dict:
    """Add an auditable explanation without changing legacy item fields."""
    return {
        **item,
        "relation_scope": "clinical_match",
        "relation_method": "discriminative_lexical_overlap",
        # `relevance_score` shares the graph's public 0..1 contract. Keep the
        # raw, auditable matcher score separately so the UI never presents an
        # unbounded integer as a percentage/probability.
        "relevance_score": min(1.0, match.score / CONTEXT_TAG_TOKEN_WEIGHT),
        "match_score": match.score,
        "match_threshold": CONTEXT_MIN_RELEVANCE_SCORE,
        "match_reasons": match.reasons(),
    }


def _contextual_studies(
    db: Session,
    themes: tuple[str, ...],
    origin_subject: str | None,
    excluir_slug: str | None,
) -> list[tuple[ScientificStudy, ContextualRelevance]]:
    """Return only studies specifically connected to the origin subject.

    A shared broad theme is a catalogue boundary, not proof of a relationship.
    Without an origin or an overlap in specific title/slug/tag terms, the safe
    result is empty instead of the most recently inserted studies in the area.
    """
    if not origin_subject:
        return []
    origin_terms = _tokens(origin_subject)
    for theme in themes:
        origin_terms -= _tokens(theme)
    if not origin_terms:
        return []

    studies = db.execute(
        select(ScientificStudy).where(
            ScientificStudy.theme.in_(themes),
            ScientificStudy.published.is_(True),
            ScientificStudy.slug != excluir_slug,
        )
    ).scalars().all()
    ranked: list[tuple[int, int, str, ScientificStudy, ContextualRelevance]] = []
    for study in studies:
        match = score_contextual_relevance(
            origin_terms,
            title_or_slug=(study.slug, study.title),
            tags=study.tags,
        )
        if not match.accepted:
            continue
        ranked.append((match.score, study.year or 0, study.title.casefold(), study, match))
    ranked.sort(key=lambda row: (-row[0], -row[1], row[2]))
    return [(row[3], row[4]) for row in ranked[:LIMITE_POR_CATEGORIA]]


def _filter_groups_by_subject(
    groups: list[dict], themes: tuple[str, ...], origin_subject: str | None,
    *, somente_melhor_por_grupo: bool = False,
) -> None:
    """Remove theme-only neighbours from every non-study content front.

    The base catalogue provides a broad candidate pool. An item-detail panel
    must additionally share at least one specific subject term with its origin;
    the study group is ranked separately with its structured tags.
    """
    if not origin_subject:
        return
    origin_terms = _tokens(origin_subject)
    for theme in themes:
        origin_terms -= _tokens(theme)
    if not origin_terms:
        for group in groups:
            if group["tipo"] != "estudo":
                group["itens"] = []
        return

    for group in groups:
        if group["tipo"] == "estudo":
            continue
        matched: list[tuple[int, int, dict, ContextualRelevance]] = []
        for position, item in enumerate(group.get("itens", [])):
            match = score_contextual_relevance(
                origin_terms,
                title_or_slug=(
                    item.get("slug"), item.get("titulo"), item.get("subtitulo"),
                ),
            )
            if match.accepted:
                matched.append((match.score, position, item, match))
        matched.sort(key=lambda row: (-row[0], row[1]))
        if somente_melhor_por_grupo and matched:
            melhor_score = matched[0][0]
            matched = [row for row in matched if row[0] == melhor_score]
        group["itens"] = [
            _with_match_metadata(row[2], row[3]) for row in matched
        ][:LIMITE_POR_CATEGORIA]


def _origin_subject(
    db: Session,
    *,
    assunto: str | None,
    excluir_tipo: str | None,
    excluir_slug: str | None,
) -> str | None:
    """Enrich an item's slug with its own reviewed structured metadata.

    Acronyms and named trials frequently make a scientifically valid item look
    orphaned when only its slug is compared with document titles. Studies reuse
    their reviewed title/tags. Evidence records reuse only their explicit
    ``document_slug`` relation and that document's reviewed title; the evidence
    statement itself is deliberately not used as an implicit relation source.
    Unknown item types and free-form subjects keep the previous slug-only
    behaviour.
    """
    if not assunto:
        return None
    if not excluir_slug or assunto != excluir_slug:
        return assunto

    if excluir_tipo == "estudo":
        item = db.execute(
            select(ScientificStudy).where(
                ScientificStudy.slug == excluir_slug,
                ScientificStudy.published.is_(True),
            )
        ).scalar_one_or_none()
        if item is not None:
            return " ".join((assunto, item.title, " ".join(item.tags or [])))

    if excluir_tipo == "evidencia":
        item = db.execute(
            select(EvidenceRecord).where(
                EvidenceRecord.slug == excluir_slug,
                EvidenceRecord.published.is_(True),
            )
        ).scalar_one_or_none()
        if item is not None and item.document_slug:
            document = db.execute(
                select(Document).where(
                    Document.slug == item.document_slug,
                    Document.published.is_(True),
                )
            ).scalar_one_or_none()
            if document is not None:
                return " ".join((assunto, document.slug, document.title))

    return assunto


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
    assunto: str | None = None,
    filtrar_grupos_por_assunto: bool = True,
) -> dict:
    canonical = canonical_theme(tema)
    if not canonical:
        return {"tema": "", "grupos": [], "total": 0}

    variants = theme_variants(canonical)
    # Contextual matching must see the full theme pool; otherwise a relevant
    # older item can be discarded before it receives a score. Theme catalogues
    # retain the normal bounded query because no item-level ranking is claimed.
    candidate_limit = None if assunto else LIMITE_POR_CATEGORIA
    responses = [
        _base(
            db, variant, excluir_tipo=excluir_tipo, excluir_slug=excluir_slug,
            limite_por_categoria=candidate_limit,
        )
        for variant in variants
    ]
    groups = _merge_groups(responses, limit=candidate_limit)
    origin_subject = _origin_subject(
        db,
        assunto=assunto,
        excluir_tipo=excluir_tipo,
        excluir_slug=excluir_slug,
    )
    origem_editorial_enriquecida = bool(
        assunto
        and excluir_slug
        and assunto == excluir_slug
        and excluir_tipo in {"estudo", "evidencia"}
        and origin_subject != assunto
    )

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
    drug_group["itens"] = _contextual_drugs(
        db, canonical, excluir_tipo, excluir_slug, limit=candidate_limit,
    )

    study_group = next((group for group in groups if group["tipo"] == "estudo"), None)
    if study_group is None:
        study_group = {
            "tipo": "estudo", "rotulo": "Estudos",
            "rota_lista": "/estudos", "itens": [],
        }
        groups.append(study_group)
    if assunto:
        studies = _contextual_studies(db, variants, origin_subject, excluir_slug)
        study_group["itens"] = [
            _with_match_metadata(
                {
                    "slug": study.slug,
                    "titulo": study.title,
                    "subtitulo": f"{study.journal} · {study.year}",
                    "rota": f"/estudos/{study.slug}",
                },
                match,
            )
            for study, match in studies
        ]
        if filtrar_grupos_por_assunto:
            _filter_groups_by_subject(
                groups,
                variants,
                origin_subject,
                # Metadados editoriais ampliam o assunto para resgatar um
                # item específico (por exemplo, título/tags de um ensaio).
                # Nesse caminho, resultados mais fracos do mesmo grupo são
                # apenas vizinhos do tema e não relações do item de origem.
                somente_melhor_por_grupo=origem_editorial_enriquecida,
            )
        relation_scope = (
            "clinical_match" if filtrar_grupos_por_assunto else "structured_clinical_topic"
        )
        relation_method = (
            "discriminative_lexical_overlap"
            if filtrar_grupos_por_assunto
            else "reviewed_drug_indication"
        )
    else:
        for group in groups:
            group["itens"] = group["itens"][:LIMITE_POR_CATEGORIA]
        relation_scope = "theme_catalog"
        relation_method = "structured_theme"

    total = sum(len(group["itens"]) for group in groups)
    response = {
        "tema": canonical,
        "relation_scope": relation_scope,
        "relation_method": relation_method,
        "grupos": groups,
        "total": total,
    }
    if relation_scope == "clinical_match":
        response["match_threshold"] = CONTEXT_MIN_RELEVANCE_SCORE
    return response


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
            db, theme, excluir_tipo="medicamento", excluir_slug=drug.slug,
            assunto=drug.slug,
            # Structured indications already prove the clinical-topic link.
            # Preserve each supported topic's documents and other fronts;
            # studies still require explicit overlap with the medication.
            filtrar_grupos_por_assunto=False,
        )
        for theme in themes
    ]
    groups = _merge_groups(responses)
    total = sum(len(group["itens"]) for group in groups)
    return {
        "medicamento": {"slug": drug.slug, "titulo": drug.generic_name},
        "temas": themes,
        "relation_scope": "structured_clinical_topic",
        "relation_method": "reviewed_drug_indication",
        "grupos": groups,
        "total": total,
    }
