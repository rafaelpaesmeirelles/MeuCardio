from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.specialty_guide import SpecialtyDisease
from app.services.catalog_search import (
    COUNT_SQL,
    INTERNAL_MARKER_SQL_PATTERN,
    INTERNAL_OVERRIDE_SQL_PATTERN,
    LITERAL_COUNT_SQL,
    LITERAL_SQL,
    PRIMARY_DISEASE_SQL,
    SQL,
    calculadoras_encontradas,
    literal_like,
    normalizar,
)
from app.services.clinical_text import clinical_text_without_internal_overrides

router = APIRouter(prefix="/api/search", tags=["busca"])


def _disease_identity_phrases(disease: SpecialtyDisease) -> tuple[str, ...]:
    values = [disease.name, disease.slug.replace("-", " "), *(disease.aliases or [])]
    seen: set[str] = set()
    phrases: list[str] = []
    for value in values:
        phrase = normalizar(str(value or "")).replace("-", " ").strip()
        if not phrase or phrase in seen:
            continue
        seen.add(phrase)
        phrases.append(phrase)
    return tuple(sorted(phrases, key=lambda value: (-len(value.split()), -len(value))))


def _row_has_strong_disease_identity(row: dict, disease: SpecialtyDisease) -> bool:
    """Disease-mode search accepts identity in title/slug, never body-only mentions."""
    if row.get("frente") == "calculadora":
        return True
    if row.get("frente") == "doenca" and row.get("slug") == disease.slug:
        return True

    title = normalizar(str(row.get("title") or "")).replace("-", " ")
    slug = normalizar(str(row.get("slug") or "")).replace("-", " ")
    haystack = f" {title} {slug} "
    slug_tokens = set(slug.split())

    # Prevent the high-impact lexical collision reported in production.
    if disease.slug == "hipertensao-arterial-sistemica" and (
        "hipertensao pulmonar" in haystack or "hipertensao arterial pulmonar" in haystack
    ):
        return False

    for phrase in _disease_identity_phrases(disease):
        parts = phrase.split()
        if len(parts) == 1:
            # One-word aliases/acronyms are accepted only as a slug token.
            if parts[0] in slug_tokens:
                return True
        elif f" {phrase} " in haystack:
            return True
    return False


def _precision_disease_rows(
    rows: list[dict], disease: SpecialtyDisease, *, cap: int = 36,
) -> list[dict]:
    kept = [row for row in rows if _row_has_strong_disease_identity(row, disease)]
    return kept[:cap]

# A consulta SQL do catálogo (as 13 frentes + calculadoras) mora em
# `app/services/catalog_search.py` — reaproveitada também pela busca léxica
# da IA (Parte 2 da correção coordenada de 02/09/2026, `app/services/rag.py`),
# para as duas nunca divergirem sobre o que é "todo o acervo elegível".


@router.get("")
def search(
    q: str = Query(..., min_length=2, max_length=200),
    frente: str | None = Query(
        None, description=(
            "documento|galeria|exame|evidencia|estudo|medicamento|caso_clinico|"
            "trilha|checklist|material_paciente|emergencia|doenca|triagem_sintoma|"
            "calculadora — vazio traz todas"
        )),
    limit: int = Query(60, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    calculadoras = calculadoras_encontradas(q) if frente in (None, "calculadora") else []
    if frente == "calculadora":
        rows = calculadoras[offset:offset + limit]
        next_offset = offset + len(rows)
        return {
            "query": q,
            "count": len(rows),
            "total": len(calculadoras),
            "limit": limit,
            "offset": offset,
            "next_offset": next_offset if next_offset < len(calculadoras) else None,
            "por_frente": {"calculadora": len(calculadoras)} if calculadoras else {},
            "primary_disease": None,
            "results": rows,
        }

    # Na busca transversal, calculadoras ocupam o início da sequência paginada
    # e o banco recebe apenas as vagas restantes. Descontar essa frente do
    # offset mantém páginas estáveis e garante `count <= limit`.
    calculator_rows = (
        calculadoras[offset:offset + limit]
        if frente is None and offset < len(calculadoras)
        else []
    )
    database_limit = limit - len(calculator_rows)
    database_offset = max(0, offset - len(calculadoras)) if frente is None else offset
    values = {
        "q": q, "q_like": literal_like(q), "frente": frente,
        "limit": database_limit, "offset": database_offset,
    }
    search_values = {
        **values,
        # Binds intencionais: interpolar regex POSIX em `text()` faria o parser
        # do SQLAlchemy interpretar `:space`/`:plain` como parâmetros espúrios.
        "internal_override_pattern": INTERNAL_OVERRIDE_SQL_PATTERN,
        "internal_marker_pattern": INTERNAL_MARKER_SQL_PATTERN,
    }
    raw_rows = db.execute(SQL, search_values).mappings().all() if database_limit else []
    count_rows = db.execute(COUNT_SQL, values).mappings().all()
    # A busca literal é um fallback, nunca um segundo braço OR da consulta
    # indexada. Isso evita duas varreduras integrais em toda busca normal.
    if not count_rows and normalizar(q):
        raw_rows = db.execute(LITERAL_SQL, search_values).mappings().all() if database_limit else []
        count_rows = db.execute(LITERAL_COUNT_SQL, values).mappings().all()

    rows = calculator_rows + [dict(row) for row in raw_rows]
    for row in rows:
        if isinstance(row.get("snippet"), str):
            row["snippet"] = clinical_text_without_internal_overrides(row["snippet"])

    disease_rows = (
        db.execute(PRIMARY_DISEASE_SQL, {"q": q}).mappings().all()
        if frente in (None, "doenca") else []
    )
    primary_disease = dict(disease_rows[0]) if len(disease_rows) == 1 else None
    disease_model = None
    if primary_disease is not None:
        primary_disease["summary"] = clinical_text_without_internal_overrides(
            primary_disease.get("summary")
        )
        disease_model = db.execute(
            select(SpecialtyDisease).where(
                SpecialtyDisease.slug == primary_disease["slug"],
                SpecialtyDisease.published.is_(True),
            )
        ).scalar_one_or_none()

    if disease_model is not None and frente is None:
        # Exact disease query: high precision only. The structured ecosystem
        # supplies indirect but clinically curated connections separately.
        rows = _precision_disease_rows(rows, disease_model, cap=min(limit, 36))
        por_frente: dict[str, int] = {}
        for row in rows:
            key = str(row.get("frente") or row.get("kind") or "")
            if key:
                por_frente[key] = por_frente.get(key, 0) + 1
        total = len(rows)
        next_offset = None
    else:
        por_frente = {
            str(row["frente"]): int(row["total"])
            for row in count_rows
        }
        if calculadoras:
            por_frente["calculadora"] = len(calculadoras)
        total_banco = sum(
            value for key, value in por_frente.items() if key != "calculadora"
        )
        total = total_banco + len(calculadoras)
        next_offset_value = offset + len(rows)
        next_offset = next_offset_value if next_offset_value < total else None
    return {
        "query": q,
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": next_offset,
        "por_frente": por_frente,
        "primary_disease": primary_disease,
        "results": rows,
    }
