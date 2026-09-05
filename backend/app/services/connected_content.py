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

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Document
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord
from app.models.knowledge import TIPOS_ENTIDADE_PERMITIDOS
from app.models.specialty_guide import SpecialtyDisease
from app.models.study import ScientificStudy
from app.services.related_content import LIMITE_POR_CATEGORIA, buscar_relacionados as _base
from app.services.knowledge_graph import ROTA_LISTA_POR_TIPO, relacionados_de
from app.services.topic_relevance import (
    CONTEXT_MIN_RELEVANCE_SCORE,
    CONTEXT_TAG_TOKEN_WEIGHT,
    SUPPORTED_DRUG_TOPICS,
    ContextualRelevance,
    canonical_theme,
    drug_matches_theme,
    normalize_text,
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


def _direct_graph_groups(
    db: Session,
    *,
    entity_type: str | None,
    slug: str | None,
) -> list[dict]:
    """Expose every content front through direct, policy-checked edges.

    Explicit relations can cross canonical themes and need not repeat the
    origin's title. Reuse the bidirectional graph's publication/review policy;
    never turn theme membership or lexical resemblance into a direct edge.
    """
    if (
        not entity_type
        or entity_type == "tema"
        or entity_type not in TIPOS_ENTIDADE_PERMITIDOS
        or not slug
    ):
        return []
    graph = relacionados_de(
        db,
        entity_type=entity_type,
        slug=slug,
        limite_por_tipo=LIMITE_POR_CATEGORIA,
        incluir_contexto_tematico=False,
    )
    if not graph:
        return []

    labels = {
        "documento": "Documentos", "fluxograma": "Fluxogramas",
        "evidencia": "Evidências", "estudo": "Estudos",
        "medicamento": "Medicamentos", "exame": "Exames",
        "caso_clinico": "Casos clínicos", "trilha": "Trilhas",
        "galeria": "Galeria", "checklist": "Checklists",
        "material_paciente": "Material para o paciente",
        "protocolo_emergencia": "Protocolos de emergência",
        "calculadora": "Calculadoras", "doenca": "Doenças",
        "triagem_sintoma": "Triagem por sintomas",
    }
    groups: list[dict] = []
    for group in graph.get("grupos", []):
        kind = group.get("tipo")
        if kind not in labels:
            continue
        label = labels[kind]
        list_route = ROTA_LISTA_POR_TIPO[kind]
        items = [{
            **item,
            "subtitulo": item.get("subtitulo"),
            "relation_scope": "direct_graph_relation",
            "context_only": False,
        } for item in group.get("itens", [])
            if item.get("slug")
            and (kind, item["slug"]) != (entity_type, slug)
            and not item.get("context_only")
            and item.get("review_status") != "rejeitado"
            and item.get("relation_type") not in {None, "same_theme", "belongs_to_topic"}
        ]
        if items:
            groups.append({
                "tipo": kind,
                "rotulo": label,
                "rota_lista": list_route,
                "itens": items,
            })
    return groups


def _merge_direct_groups(groups: list[dict], direct: list[dict]) -> list[dict]:
    """Rank direct links first without rearranging the approved group order."""
    merged = {group["tipo"]: group for group in _merge_groups([
        {"grupos": direct}, {"grupos": groups},
    ])}
    for group in groups:
        # Preserve existing UI labels/routes as well as their ordering.
        merged[group["tipo"]]["rotulo"] = group["rotulo"]
        merged[group["tipo"]]["rota_lista"] = group["rota_lista"]
    order = dict.fromkeys(group["tipo"] for group in [*groups, *direct])
    return [merged[kind] for kind in order]


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


@dataclass(frozen=True)
class _OriginContext:
    subject: str | None
    strong_tag_term_groups: tuple[frozenset[str], ...] = ()
    explicit_item_keys: frozenset[tuple[str, str]] = frozenset()


def _strong_structured_tag_term_groups(
    tags: object,
    *,
    trusted_single_terms: frozenset[str] = frozenset(),
) -> tuple[frozenset[str], ...]:
    """Keep only tag groups safe enough to justify one absolute relation.

    A single-token reviewed tag is strong only when the token is also a
    published entity in a typed clinical catalogue. A multi-token tag is
    strong only when at least two of its terms are discriminative and the
    candidate matches the complete group. This prevents design, outcome and
    population tags such as ``metanalise``, ``mortalidade`` and ``idoso`` from
    creating relations while retaining named entities such as ``mavacamten``.
    """
    values = (
        tags
        if isinstance(tags, (list, tuple, set, frozenset))
        else (tags,) if tags else ()
    )
    groups: list[frozenset[str]] = []
    for value in values:
        discriminative = frozenset(_tokens(value))
        raw_terms = normalize_text(str(value)).split()
        if len(discriminative) >= 2 or (
            len(discriminative) == 1 and len(raw_terms) == 1
            and discriminative <= trusted_single_terms
        ):
            groups.append(discriminative)
    return tuple(dict.fromkeys(groups))


def _trusted_single_tag_terms(db: Session, tags: object) -> frozenset[str]:
    """Resolve one-token tags only against published typed clinical entities."""
    values = (
        tags
        if isinstance(tags, (list, tuple, set, frozenset))
        else (tags,) if tags else ()
    )
    candidates = {
        normalized
        for value in values
        if len((normalized := normalize_text(str(value))).split()) == 1
        and len(_tokens(normalized)) == 1
    }
    if not candidates:
        return frozenset()

    drug_slugs = db.execute(
        select(Drug.slug).where(
            Drug.published.is_(True),
            Drug.slug.in_(candidates),
        )
    ).scalars().all()
    disease_slugs = db.execute(
        select(SpecialtyDisease.slug).where(
            SpecialtyDisease.published.is_(True),
            SpecialtyDisease.slug.in_(candidates),
        )
    ).scalars().all()
    return frozenset(candidates & (set(drug_slugs) | set(disease_slugs)))


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


def _with_explicit_link_metadata(item: dict) -> dict:
    """Describe an evidence-to-document relation without claiming lexical proof."""
    return {
        **item,
        "relation_scope": "structured_clinical_link",
        "relation_method": "evidence_document_slug",
        "relevance_score": 1.0,
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


def _has_absolute_editorial_support(
    match: ContextualRelevance,
    strong_origin_tag_term_groups: tuple[frozenset[str], ...] = (),
) -> bool:
    """Require pool-independent support for an editorially enriched origin.

    Two distinct discriminative overlaps are sufficient. A single overlap is
    sufficient only when the terms recorded by ``Match`` fully cover a strong
    reviewed tag from the origin. Unlike comparison with the group's maximum
    score, this rule is monotonic: adding a stronger candidate cannot
    invalidate an existing one.
    """
    matched_terms = set(match.title_or_slug_terms) | set(match.tag_terms)
    return match.accepted and (
        len(matched_terms) >= 2
        or any(group <= matched_terms for group in strong_origin_tag_term_groups)
    )


def _filter_groups_by_subject(
    groups: list[dict], themes: tuple[str, ...], origin_subject: str | None,
    *, exigir_suporte_editorial_absoluto: bool = False,
    strong_origin_tag_term_groups: tuple[frozenset[str], ...] = (),
    explicit_item_keys: frozenset[tuple[str, str]] = frozenset(),
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
                group["itens"] = [
                    _with_explicit_link_metadata(item)
                    for item in group.get("itens", [])
                    if (group["tipo"], item.get("slug", ""))
                    in explicit_item_keys
                ]
        return

    for group in groups:
        if group["tipo"] == "estudo":
            continue
        matched: list[tuple[int, int, dict, ContextualRelevance]] = []
        for position, item in enumerate(group.get("itens", [])):
            item_key = (group["tipo"], item.get("slug", ""))
            match = score_contextual_relevance(
                origin_terms,
                title_or_slug=(
                    item.get("slug"), item.get("titulo"), item.get("subtitulo"),
                ),
            )
            if match.accepted or item_key in explicit_item_keys:
                matched.append((match.score, position, item, match))
        matched.sort(key=lambda row: (-row[0], row[1]))
        if exigir_suporte_editorial_absoluto:
            matched = [
                row for row in matched
                if (
                    (group["tipo"], row[2].get("slug", ""))
                    in explicit_item_keys
                    or _has_absolute_editorial_support(
                        row[3], strong_origin_tag_term_groups,
                    )
                )
            ]
            matched.sort(key=lambda row: (
                (group["tipo"], row[2].get("slug", ""))
                not in explicit_item_keys,
                -row[0],
                row[1],
            ))
        group["itens"] = [
            (
                _with_explicit_link_metadata(row[2])
                if (group["tipo"], row[2].get("slug", ""))
                in explicit_item_keys
                else _with_match_metadata(row[2], row[3])
            )
            for row in matched
        ][:LIMITE_POR_CATEGORIA]


def _origin_context(
    db: Session,
    *,
    assunto: str | None,
    excluir_tipo: str | None,
    excluir_slug: str | None,
) -> _OriginContext:
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
        return _OriginContext(None)
    if not excluir_slug or assunto != excluir_slug:
        return _OriginContext(assunto)

    if excluir_tipo == "estudo":
        item = db.execute(
            select(ScientificStudy).where(
                ScientificStudy.slug == excluir_slug,
                ScientificStudy.published.is_(True),
            )
        ).scalar_one_or_none()
        if item is not None:
            trusted_single_terms = _trusted_single_tag_terms(db, item.tags)
            return _OriginContext(
                " ".join((assunto, item.title, " ".join(item.tags or []))),
                _strong_structured_tag_term_groups(
                    item.tags,
                    trusted_single_terms=trusted_single_terms,
                ),
            )

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
                return _OriginContext(
                    " ".join((assunto, document.slug, document.title)),
                    explicit_item_keys=frozenset({
                        (
                            "fluxograma"
                            if document.kind == "fluxograma"
                            else "documento",
                            document.slug,
                        ),
                    }),
                )

    return _OriginContext(assunto)


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
    origin_context = _origin_context(
        db,
        assunto=assunto,
        excluir_tipo=excluir_tipo,
        excluir_slug=excluir_slug,
    )
    origin_subject = origin_context.subject
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
                # Nesse caminho, exige-se suporte absoluto adicional, sem
                # comparar candidatos entre si: cobertura integral de uma
                # tag forte ou dois termos discriminativos no título/slug.
                exigir_suporte_editorial_absoluto=(
                    origem_editorial_enriquecida
                ),
                strong_origin_tag_term_groups=(
                    origin_context.strong_tag_term_groups
                ),
                explicit_item_keys=origin_context.explicit_item_keys,
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

    # Arestas diretas atravessam temas e todas as frentes. Entram depois do
    # filtro lexical, mas antes dele no ranking e na deduplicação final.
    # Isso preserva a proveniência do vínculo e impede que cinco resultados
    # textuais escondam uma referência editorial explícita.
    direct = (
        _direct_graph_groups(db, entity_type=excluir_tipo, slug=excluir_slug)
        if assunto and excluir_slug and assunto == excluir_slug
        else []
    )
    groups = _merge_direct_groups(groups, direct)

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
    if not themes:
        # A drug outside the supported indication taxonomy can still have
        # explicit reviewed graph links. Do not invent a theme to expose them.
        responses.append({"grupos": _direct_graph_groups(
            db, entity_type="medicamento", slug=drug.slug,
        )})
    groups = _merge_groups(responses)
    total = sum(len(group["itens"]) for group in groups)
    return {
        "medicamento": {"slug": drug.slug, "titulo": drug.generic_name},
        "temas": themes,
        "relation_scope": "structured_clinical_topic" if themes else "direct_graph_relation",
        "relation_method": "reviewed_drug_indication" if themes else "typed_graph_relation",
        "grupos": groups,
        "total": total,
    }
