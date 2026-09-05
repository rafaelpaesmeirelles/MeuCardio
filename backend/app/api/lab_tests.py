import unicodedata

import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Text, and_, case, cast, func, or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.lab_test import LabTest

router = APIRouter(prefix="/api/lab-tests", tags=["exames"])


def _termo_sem_acentos(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(char)
    ).strip()


def _contem_sem_acentos(column, value: str):
    return func.unaccent(func.lower(cast(column, Text))).contains(
        _termo_sem_acentos(value), autoescape=True,
    )


def _card(test: LabTest) -> dict:
    return {
        "id": test.id,
        "slug": test.slug,
        "name": test.name,
        "category": test.category,
        "theme": test.theme,
        "tags": test.tags,
    }


def _detail(test: LabTest) -> dict:
    return {
        **_card(test),
        "what_it_measures": test.what_it_measures,
        "reference_range": test.reference_range,
        "indications": test.indications,
        "interpretation": test.interpretation,
        "limitations": test.limitations,
        "source_refs": test.source_refs,
    }


@router.get("/categories")
def categories(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(LabTest.category, func.count(LabTest.id))
        .where(LabTest.published.is_(True))
        .group_by(LabTest.category)
        .order_by(LabTest.category)
    ).all()
    return [{"category": category, "count": count} for category, count in rows]


@router.get("/taxonomy")
def taxonomy(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(LabTest.category, LabTest.theme, func.count(LabTest.id))
        .where(LabTest.published.is_(True))
        .group_by(LabTest.category, LabTest.theme)
        .order_by(LabTest.category, LabTest.theme)
    ).all()
    por_tipo: dict[str, dict] = {}
    for category, theme, count in rows:
        item = por_tipo.setdefault(category, {"category": category, "count": 0, "subtypes": []})
        item["count"] += count
        item["subtypes"].append({"theme": theme, "count": count})
    return list(por_tipo.values())


@router.get("")
def list_tests(
    category: str | None = None,
    theme: str | None = None,
    q: str | None = Query(None, max_length=200),
    limit: int = Query(60, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    query = db.query(LabTest).filter(LabTest.published.is_(True))
    if category:
        query = query.filter(LabTest.category == category)
    if theme:
        query = query.filter(LabTest.theme == theme)
    if q and q.strip():
        # Cada termo digitado precisa aparecer em algum campo pesquisável, mas
        # não necessariamente como uma única substring contínua. Assim
        # "holter 24h" encontra o registro canônico `holter-24h` mesmo quando
        # o nome editorial é "Holter — monitorização eletrocardiográfica...".
        stopwords = {"a", "as", "com", "da", "das", "de", "do", "dos", "e", "em", "na", "nas", "no", "nos", "o", "os", "para", "por"}
        terms = [
            term for term in re.split(r"[^a-z0-9]+", _termo_sem_acentos(q))
            if term and term not in stopwords
        ]
        term_filters = [
            or_(
                _contem_sem_acentos(LabTest.name, term),
                _contem_sem_acentos(LabTest.slug, term),
                _contem_sem_acentos(LabTest.category, term),
                _contem_sem_acentos(LabTest.theme, term),
                _contem_sem_acentos(LabTest.tags, term),
                _contem_sem_acentos(LabTest.what_it_measures, term),
                _contem_sem_acentos(LabTest.indications, term),
                _contem_sem_acentos(LabTest.interpretation, term),
            )
            for term in terms
        ]
        if term_filters:
            query = query.filter(and_(*term_filters))
    total = query.count()
    if q and q.strip():
        normalized_q = _termo_sem_acentos(q)
        normalized_name = func.unaccent(func.lower(LabTest.name))
        normalized_slug = func.unaccent(func.lower(func.replace(LabTest.slug, "-", " ")))
        identity_rank = case(
            (normalized_slug == normalized_q, 0),
            (normalized_name == normalized_q, 0),
            (normalized_slug.like(normalized_q + "%"), 1),
            (normalized_name.like(normalized_q + "%"), 1),
            else_=2,
        )
        query = query.order_by(identity_rank, func.length(LabTest.slug), LabTest.name, LabTest.slug)
    else:
        query = query.order_by(LabTest.category, LabTest.theme, LabTest.name)
    items = query.offset(offset).limit(limit).all()
    has_more = offset + len(items) < total
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": offset + len(items) if has_more else None,
        "has_more": has_more,
        "items": [_card(test) for test in items],
    }


@router.get("/{slug}")
def get_test(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    test = db.query(LabTest).filter(
        LabTest.slug == slug,
        LabTest.published.is_(True),
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Exame não encontrado.")
    return _detail(test)
