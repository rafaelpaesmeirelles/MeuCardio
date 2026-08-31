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
    SUPPORTED_DRUG_TOPICS,
    canonical_theme,
    drug_matches_theme,
    normalize_text,
    theme_variants,
)


_GENERIC_TOPIC_TOKENS = frozenset({
    "cardiologia", "cardiovascular", "cardiaco", "cardiaca", "doenca", "sindrome",
    "manejo", "tratamento", "terapia", "avaliacao", "diagnostico", "risco", "estudo",
    "evidencia", "diretriz", "clinico", "clinica", "paciente", "adulto", "adultos",
    "crianca", "criancas", "adolescente", "agudo", "aguda", "cronico", "cronica",
    "grave", "arterial", "atrial", "ventricular", "atleta", "esporte", "exercicio",
    "cardiomiopatia", "cardiomiopatias",
    "para", "pela", "pelo", "pelos", "pelas", "com", "sem", "entre", "versus",
    "apos", "antes", "durante", "como", "quando", "qual", "quais", "uma", "umas",
    "uns", "sobre", "este", "esta", "esse", "essa", "dos", "das", "nas", "nos",
})


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


def _tokens(value: object) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        text = " ".join(str(item) for item in value if item)
    else:
        text = str(value or "")
    return {
        token for token in normalize_text(text).split()
        if len(token) >= 3 and not token.isdigit() and token not in _GENERIC_TOPIC_TOKENS
    }


def _contextual_studies(
    db: Session,
    themes: tuple[str, ...],
    origin_subject: str | None,
    excluir_slug: str | None,
) -> list[ScientificStudy]:
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
    ranked: list[tuple[int, int, str, ScientificStudy]] = []
    for study in studies:
        title_overlap = origin_terms & _tokens((study.slug, study.title))
        tag_overlap = origin_terms & _tokens(study.tags)
        if not title_overlap and not tag_overlap:
            continue
        score = 3 * len(title_overlap) + 5 * len(tag_overlap)
        ranked.append((score, study.year or 0, study.title.casefold(), study))
    ranked.sort(key=lambda row: (-row[0], -row[1], row[2]))
    return [row[3] for row in ranked[:LIMITE_POR_CATEGORIA]]


def _filter_groups_by_subject(
    groups: list[dict], themes: tuple[str, ...], origin_subject: str | None,
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
        matched: list[tuple[int, int, dict]] = []
        for position, item in enumerate(group.get("itens", [])):
            candidate_terms = _tokens((
                item.get("slug"), item.get("titulo"), item.get("subtitulo"),
            ))
            overlap = origin_terms & candidate_terms
            if overlap:
                matched.append((len(overlap), position, {**item, "motivo_relacao": f"Termo específico compartilhado: {', '.join(sorted(overlap))}"}))
        matched.sort(key=lambda row: (-row[0], row[1]))
        best_score = matched[0][0] if matched else 0
        group["itens"] = [
            row[2] for row in matched
            if row[0] == best_score
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
    responses = [
        _base(
            db, variant, excluir_tipo=excluir_tipo, excluir_slug=excluir_slug,
            limite_por_categoria=100,
        )
        for variant in variants
    ]
    groups = _merge_groups(responses, limit=100)
    origin_subject = _origin_subject(
        db,
        assunto=assunto,
        excluir_tipo=excluir_tipo,
        excluir_slug=excluir_slug,
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
    drug_group["itens"] = _contextual_drugs(db, canonical, excluir_tipo, excluir_slug)

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
            {
                "slug": study.slug,
                "titulo": study.title,
                "subtitulo": f"{study.journal} · {study.year}",
                "rota": f"/estudos/{study.slug}",
            }
            for study in studies
        ]
        if filtrar_grupos_por_assunto:
            _filter_groups_by_subject(groups, variants, origin_subject)
    else:
        for group in groups:
            group["itens"] = group["itens"][:LIMITE_POR_CATEGORIA]

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
            db, theme, excluir_tipo="medicamento", excluir_slug=drug.slug,
            assunto=f"{drug.slug} {drug.generic_name}",
            # A indicação prova medicamento -> tema, mas não prova que todo
            # item do tema se relacione ao medicamento. Cada vizinho precisa
            # compartilhar o assunto específico no próprio metadado.
            filtrar_grupos_por_assunto=True,
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
