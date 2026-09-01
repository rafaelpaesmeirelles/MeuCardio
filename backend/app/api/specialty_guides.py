import unicodedata
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Text, cast, func, or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.services.clinical_rule_engine import evaluate_rules, validate_answers
from app.services.disease_taxonomy import CLINICAL_DOMAINS, categories_for_domain

router = APIRouter(prefix="/api/specialty-guides", tags=["guias especializados"])


_ACCENTED_SEARCH_CHARS = "áàâãäéèêëíìîïóòôõöúùûüçñýÿ"
_PLAIN_SEARCH_CHARS = "aaaaaeeeeiiiiooooouuuucnyy"


def _normalize_search_term(value: str) -> str:
    """Normaliza a entrada sem depender da extensão PostgreSQL ``unaccent``."""
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in decomposed
        if not unicodedata.combining(character)
    )
    return " ".join(
        without_accents.casefold().replace("-", " ").replace("_", " ").split()
    )


def _normalized_search_column(column):
    """Expressão portável dentro do PostgreSQL base, sem extensões opcionais."""
    normalized = func.translate(
        func.lower(cast(column, Text)),
        _ACCENTED_SEARCH_CHARS,
        _PLAIN_SEARCH_CHARS,
    )
    return func.replace(func.replace(normalized, "-", " "), "_", " ")


def _escaped_like_term(value: str) -> str:
    normalized = _normalize_search_term(value)
    escaped = normalized.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _disease_search_predicate(value: str):
    term = _escaped_like_term(value)
    return or_(*(
        _normalized_search_column(column).like(term, escape="\\")
        for column in (
            SpecialtyDisease.slug,
            SpecialtyDisease.name,
            SpecialtyDisease.summary,
            SpecialtyDisease.epidemiology,
            SpecialtyDisease.category,
            SpecialtyDisease.subtype,
            SpecialtyDisease.aliases,
            SpecialtyDisease.tags,
            SpecialtyDisease.presentation,
            SpecialtyDisease.diagnostic_approach,
            SpecialtyDisease.differentials,
            SpecialtyDisease.tests,
            SpecialtyDisease.red_flags,
        )
    ))


class AssessmentPayload(BaseModel):
    context: Literal["ambulatorio", "emergencia"] = "ambulatorio"
    answers: dict[str, Any] = Field(default_factory=dict)


class TriagePayload(BaseModel):
    context: Literal["ambulatorio", "emergencia"]
    answers: dict[str, Any] = Field(default_factory=dict)


def _disease_list_item(item: SpecialtyDisease) -> dict[str, Any]:
    return {
        "slug": item.slug,
        "name": item.name,
        "aliases": item.aliases or [],
        "area": item.area,
        "category": item.category,
        "subtype": item.subtype,
        "cyanosis_class": item.cyanosis_class,
        "prevalence_rank": item.prevalence_rank,
        "completeness": item.completeness,
        "summary": item.summary,
        "tags": item.tags or [],
        "has_assistant": bool(item.assistant_questions),
        "version": item.version,
        "updated_at": item.updated_at,
    }


def _disease_detail(item: SpecialtyDisease) -> dict[str, Any]:
    return {
        **_disease_list_item(item),
        "epidemiology": item.epidemiology,
        "presentation": item.presentation or [],
        "diagnostic_approach": item.diagnostic_approach or {},
        "differentials": item.differentials or [],
        "tests": item.tests or [],
        "red_flags": item.red_flags or [],
        "ambulatory_flow": item.ambulatory_flow or [],
        "emergency_flow": item.emergency_flow or [],
        "treatment_summary": item.treatment_summary,
        "monitoring": item.monitoring or [],
        "special_populations": item.special_populations or [],
        "assistant_questions": item.assistant_questions or [],
        "source_refs": item.source_refs or [],
        "source_urls": item.source_urls or [],
        "related_document_slugs": item.related_document_slugs or [],
        "patient_material_slug": item.patient_material_slug,
        "review_status": item.review_status,
    }


def _triage_list_item(item: SymptomTriageGuide) -> dict[str, Any]:
    return {
        "slug": item.slug,
        "name": item.name,
        "aliases": item.aliases or [],
        "areas": item.areas or [],
        "summary": item.summary,
        "tags": item.tags or [],
        "version": item.version,
        "updated_at": item.updated_at,
    }


def _triage_detail(item: SymptomTriageGuide) -> dict[str, Any]:
    return {
        **_triage_list_item(item),
        "questions": item.questions or [],
        "default_tests": item.default_tests or [],
        "differentials": item.differentials or [],
        "red_flags": item.red_flags or [],
        "ambulatory_flow": item.ambulatory_flow or [],
        "emergency_flow": item.emergency_flow or [],
        "source_refs": item.source_refs or [],
        "source_urls": item.source_urls or [],
        "review_status": item.review_status,
    }


@router.get("/areas")
def list_areas(db: Session = Depends(get_db)):
    rows = (
        db.query(SpecialtyDisease.area, func.count(SpecialtyDisease.id))
        .filter(SpecialtyDisease.published.is_(True))
        .group_by(SpecialtyDisease.area)
        .order_by(SpecialtyDisease.area)
        .all()
    )
    return [{"area": area, "count": int(count)} for area, count in rows]


@router.get("/disease-facets")
def list_disease_facets(
    area: str | None = Query(None, max_length=60),
    category: str | None = Query(None, max_length=100),
    clinical_domain: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    """Facetas publicadas e condicionais para combinações sempre acionáveis.

    Cada lado é restringido pelo outro: ao selecionar uma população/contexto,
    só retornamos grupos clínicos que possuem conteúdo nessa área; ao selecionar
    um grupo, só retornamos áreas que contêm esse grupo.
    """
    area_query = db.query(
        SpecialtyDisease.area,
        func.count(SpecialtyDisease.id),
    ).filter(SpecialtyDisease.published.is_(True))
    if clinical_domain:
        domain_categories = categories_for_domain(clinical_domain)
        if domain_categories:
            area_query = area_query.filter(SpecialtyDisease.category.in_(domain_categories))
        else:
            area_query = area_query.filter(False)
    elif category:
        area_query = area_query.filter(SpecialtyDisease.category == category)
    areas = (
        area_query
        .group_by(SpecialtyDisease.area)
        .order_by(SpecialtyDisease.area)
        .all()
    )

    category_query = db.query(
        SpecialtyDisease.category,
        func.count(SpecialtyDisease.id),
    ).filter(SpecialtyDisease.published.is_(True))
    if area:
        category_query = category_query.filter(SpecialtyDisease.area == area)
    categories = (
        category_query
        .group_by(SpecialtyDisease.category)
        .order_by(SpecialtyDisease.category)
        .all()
    )
    category_counts = {
        category: int(count) for category, count in categories if category
    }
    clinical_domains = []
    for domain in CLINICAL_DOMAINS:
        count = sum(category_counts.get(category, 0) for category in domain["categories"])
        if count:
            clinical_domains.append({
                "id": domain["id"],
                "label": domain["label"],
                "count": count,
            })
    return {
        "areas": [{"id": area, "count": int(count)} for area, count in areas],
        "clinical_domains": clinical_domains,
        "categories": [
            {"id": category, "count": int(count)}
            for category, count in categories
            if category
        ],
    }


@router.get("/diseases")
def list_diseases(
    q: str | None = Query(None, max_length=160),
    area: str | None = Query(None, max_length=60),
    category: str | None = Query(None, max_length=100),
    clinical_domain: str | None = Query(None, max_length=100),
    subtype: str | None = Query(None, max_length=400),
    cyanosis_class: str | None = Query(None, max_length=20),
    assistant_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(40, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(SpecialtyDisease).filter(SpecialtyDisease.published.is_(True))
    if area:
        query = query.filter(SpecialtyDisease.area == area)
    if clinical_domain:
        domain_categories = categories_for_domain(clinical_domain)
        if domain_categories:
            query = query.filter(SpecialtyDisease.category.in_(domain_categories))
        else:
            query = query.filter(False)
    elif category:
        query = query.filter(SpecialtyDisease.category == category)
    if subtype:
        query = query.filter(SpecialtyDisease.subtype == subtype)
    if cyanosis_class:
        query = query.filter(SpecialtyDisease.cyanosis_class == cyanosis_class)
    if assistant_only:
        query = query.filter(cast(SpecialtyDisease.assistant_questions, Text) != "[]")
    if q and q.strip():
        query = query.filter(_disease_search_predicate(q))

    total = query.count()
    items = (
        query.order_by(
            SpecialtyDisease.area,
            SpecialtyDisease.prevalence_rank,
            SpecialtyDisease.name,
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [_disease_list_item(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_more": page * page_size < total,
    }


@router.get("/diseases/{slug}")
def get_disease(slug: str, db: Session = Depends(get_db)):
    item = db.query(SpecialtyDisease).filter(
        SpecialtyDisease.slug == slug,
        SpecialtyDisease.published.is_(True),
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Doença não encontrada.")
    return _disease_detail(item)


@router.post("/diseases/{slug}/assess")
def assess_disease(slug: str, payload: AssessmentPayload, db: Session = Depends(get_db)):
    item = db.query(SpecialtyDisease).filter(
        SpecialtyDisease.slug == slug,
        SpecialtyDisease.published.is_(True),
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Doença não encontrada.")
    if not item.assistant_questions:
        raise HTTPException(status_code=409, detail="Este verbete ainda não possui assistente estruturado.")

    missing, invalid = validate_answers(item.assistant_questions or [], payload.answers)
    if invalid:
        raise HTTPException(
            status_code=422,
            detail={"erro": "Respostas inválidas.", "campos": invalid},
        )
    if missing:
        raise HTTPException(
            status_code=422,
            detail={"erro": "Respostas obrigatórias ausentes.", "campos": missing},
        )
    result = evaluate_rules(
        questions=item.assistant_questions or [],
        rules=item.assistant_rules or [],
        answers=payload.answers,
        # Exames e fluxos do verbete são conteúdo educacional de referência.
        # O assessment só deve rotular como sugestão o que uma regra explícita
        # adicionou para as respostas atuais.
        base_tests=[],
        base_differentials=item.differentials or [],
        base_ambulatory_flow=[],
        base_emergency_flow=[],
        context=payload.context,
    )
    result.update({
        "disease": {"slug": item.slug, "name": item.name},
        "guide_version": item.version,
        "source_refs": item.source_refs or [],
        "source_urls": item.source_urls or [],
        "incomplete": bool(missing),
    })
    return result


@router.get("/triage")
def list_triage(
    q: str | None = Query(None, max_length=160),
    area: str | None = Query(None, max_length=60),
    db: Session = Depends(get_db),
):
    query = db.query(SymptomTriageGuide).filter(SymptomTriageGuide.published.is_(True))
    if area:
        query = query.filter(SymptomTriageGuide.areas.any(area))
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(or_(
            SymptomTriageGuide.name.ilike(term),
            SymptomTriageGuide.summary.ilike(term),
            cast(SymptomTriageGuide.aliases, Text).ilike(term),
            cast(SymptomTriageGuide.tags, Text).ilike(term),
        ))
    items = query.order_by(SymptomTriageGuide.name).all()
    return [_triage_list_item(item) for item in items]


@router.get("/triage/{slug}")
def get_triage(slug: str, db: Session = Depends(get_db)):
    item = db.query(SymptomTriageGuide).filter(
        SymptomTriageGuide.slug == slug,
        SymptomTriageGuide.published.is_(True),
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Fluxo de triagem não encontrado.")
    return _triage_detail(item)


@router.post("/triage/{slug}/assess")
def assess_triage(slug: str, payload: TriagePayload, db: Session = Depends(get_db)):
    item = db.query(SymptomTriageGuide).filter(
        SymptomTriageGuide.slug == slug,
        SymptomTriageGuide.published.is_(True),
    ).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Fluxo de triagem não encontrado.")

    missing, invalid = validate_answers(item.questions or [], payload.answers)
    if invalid:
        raise HTTPException(
            status_code=422,
            detail={"erro": "Respostas inválidas.", "campos": invalid},
        )
    result = evaluate_rules(
        questions=item.questions or [],
        rules=item.rules or [],
        answers=payload.answers,
        base_tests=item.default_tests or [],
        base_differentials=item.differentials or [],
        base_ambulatory_flow=item.ambulatory_flow or [],
        base_emergency_flow=item.emergency_flow or [],
        context=payload.context,
    )
    result.update({
        "symptom": {"slug": item.slug, "name": item.name},
        "guide_version": item.version,
        "source_refs": item.source_refs or [],
        "source_urls": item.source_urls or [],
        "incomplete": bool(missing),
    })
    return result
