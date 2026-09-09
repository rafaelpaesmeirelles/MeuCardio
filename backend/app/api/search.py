from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.specialty_guide import SpecialtyDisease
from app.services.catalog_search import (
    DISEASE_SQL,
    INTERNAL_MARKER_SQL_PATTERN,
    INTERNAL_OVERRIDE_SQL_PATTERN,
    LITERAL_PAGE_SQL,
    PRIMARY_DISEASE_SQL,
    PAGE_SQL,
    calculadoras_encontradas,
    literal_like,
    normalizar,
)
from app.services.clinical_text import clinical_text_without_internal_overrides
from app.services.connected_content import buscar_relacionados_da_doenca

router = APIRouter(prefix="/api/search", tags=["busca"])


def _disease_identity_phrases(disease: SpecialtyDisease) -> tuple[str, ...]:
    values = [disease.name, disease.slug.replace("-", " "), *(disease.aliases or [])]
    seen: set[str] = set()
    phrases: list[str] = []
    for value in values:
        phrase = normalizar(str(value or "")).replace("-", " ").strip()
        if len(phrase.replace(" ", "")) < 2 or phrase in seen:
            continue
        seen.add(phrase)
        phrases.append(phrase)
    return tuple(sorted(phrases, key=lambda value: (-len(value.split()), -len(value))))


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
    # Resolve aliases before retrieval. FA and its canonical name use the same
    # candidate set, including connections whose title does not repeat FA.
    disease_rows = db.execute(PRIMARY_DISEASE_SQL, {"q": q}).mappings().all()
    resolved = dict(disease_rows[0]) if len(disease_rows) == 1 else None
    disease_model = None
    if resolved is not None:
        disease_model = db.execute(
            select(SpecialtyDisease).where(
                SpecialtyDisease.slug == resolved["slug"],
                SpecialtyDisease.published.is_(True),
            )
        ).scalar_one_or_none()
    primary_disease = resolved if frente in (None, "doenca") else None
    if primary_disease is not None:
        primary_disease["summary"] = clinical_text_without_internal_overrides(
            primary_disease.get("summary")
        )

    query = disease_model.name if disease_model is not None else q
    calculadoras = calculadoras_encontradas(query) if frente in (None, "calculadora") else []
    if disease_model is not None and frente in (None, "calculadora"):
        seen_calculators = {item["slug"] for item in calculadoras}
        for phrase in _disease_identity_phrases(disease_model):
            for item in calculadoras_encontradas(phrase):
                if item["slug"] not in seen_calculators:
                    calculadoras.append(item)
                    seen_calculators.add(item["slug"])
    ecosystem = None
    disease_links: list[str] = []
    supplementary_groups: list[dict] = []
    connection_metadata: dict[str, dict] = {}
    if disease_model is not None:
        ecosystem = buscar_relacionados_da_doenca(db, disease_model.slug)
        for group in (ecosystem or {}).get("grupos", []):
            kind = {"fluxograma": "documento", "protocolo_emergencia": "emergencia"}.get(
                group["tipo"], group["tipo"]
            )
            disease_links.extend(
                f"{kind}:{item['slug']}" for item in group.get("itens", [])
                if item.get("slug") and not item.get("context_only")
            )
            for item in group.get("itens", []):
                if item.get("slug"):
                    connection_metadata.setdefault(f"{kind}:{item['slug']}", item)
            recommendations = [item for item in group.get("itens", [])
                               if item.get("relation_method") == "SpecialtyDisease.tests"]
            if recommendations:
                supplementary_groups.append({**group, "itens": recommendations})
        if frente in (None, "calculadora"):
            # Retrieve the calculator's actual catalogue row, not a synthetic
            # result or a new clinical indication inferred by the search.
            from app.services import calculators as calc
            linked = set(disease_links)
            existing = {item["slug"] for item in calculadoras}
            for calculator in calc.REGISTRY.values():
                if f"calculadora:{calculator.slug}" in linked and calculator.slug not in existing:
                    exact = [item for item in calculadoras_encontradas(calculator.slug)
                             if item["slug"] == calculator.slug]
                    calculadoras.extend(exact)
                    existing.add(calculator.slug)
        disease_links.append(f"doenca:{disease_model.slug}")

    if frente == "calculadora":
        rows = calculadoras[offset:offset + limit]
        next_offset = offset + len(rows)
        return {
            "query": q, "count": len(rows), "total": len(calculadoras),
            "limit": limit, "offset": offset,
            "next_offset": next_offset if next_offset < len(calculadoras) else None,
            "por_frente": {"calculadora": len(calculadoras)} if calculadoras else {},
            "primary_disease": None, "results": rows,
        }

    calculator_rows = calculadoras[offset:offset + limit] if frente is None else []
    database_limit = limit - len(calculator_rows)
    database_offset = max(0, offset - len(calculadoras)) if frente is None else offset
    values = {
        "q": query, "q_like": literal_like(query), "frente": frente,
        "limit": database_limit, "offset": database_offset,
    }
    sql = PAGE_SQL
    if disease_model is not None:
        sql = DISEASE_SQL
        values.update({
            "disease_phrases": list(_disease_identity_phrases(disease_model)),
            "disease_links": list(dict.fromkeys(disease_links)),
            "systemic_hypertension": disease_model.slug == "hipertensao-arterial-sistemica",
        })
    search_values = {
        **values,
        "internal_override_pattern": INTERNAL_OVERRIDE_SQL_PATTERN,
        "internal_marker_pattern": INTERNAL_MARKER_SQL_PATTERN,
    }
    page = db.execute(sql, search_values).mappings().one()
    raw_rows = page["results"]
    por_frente = page["por_frente"]
    if disease_model is None and not por_frente and normalizar(q):
        page = db.execute(LITERAL_PAGE_SQL, search_values).mappings().one()
        raw_rows = page["results"]
        por_frente = page["por_frente"]

    rows = calculator_rows + [dict(row) for row in raw_rows]
    for row in rows:
        if isinstance(row.get("snippet"), str):
            row["snippet"] = clinical_text_without_internal_overrides(row["snippet"])
        relation = connection_metadata.get(f"{row['frente']}:{row['slug']}")
        if relation is not None:
            row["relation_type"] = relation.get("relation_type")
            row["context_only"] = relation.get("context_only", False)
    por_frente = {str(kind): int(count) for kind, count in por_frente.items()}
    if calculadoras:
        por_frente["calculadora"] = len(calculadoras)
    total = sum(por_frente.values())
    next_offset = offset + len(rows)
    return {
        "query": q, "count": len(rows), "total": total, "limit": limit, "offset": offset,
        "next_offset": next_offset if next_offset < total else None,
        "por_frente": por_frente, "primary_disease": primary_disease,
        "supplementary_groups": supplementary_groups,
        "results": rows,
    }
