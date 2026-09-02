from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
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
    por_frente = {
        str(row["frente"]): int(row["total"])
        for row in count_rows
    }
    total_banco = sum(por_frente.values())
    disease_rows = (
        db.execute(PRIMARY_DISEASE_SQL, {"q": q}).mappings().all()
        if frente in (None, "doenca") else []
    )
    primary_disease = dict(disease_rows[0]) if len(disease_rows) == 1 else None
    if primary_disease is not None:
        primary_disease["summary"] = clinical_text_without_internal_overrides(
            primary_disease.get("summary")
        )
    if calculadoras:
        por_frente["calculadora"] = len(calculadoras)
    total = total_banco + len(calculadoras)
    next_offset = offset + len(rows)
    return {
        "query": q,
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": next_offset if next_offset < total else None,
        "por_frente": por_frente,
        "primary_disease": primary_disease,
        "results": rows,
    }
