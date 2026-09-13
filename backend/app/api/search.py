import json
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.specialty_guide import SpecialtyDisease
from app.models.drug import Drug
from app.services.catalog_search import (
    DISEASE_SQL,
    INTERNAL_MARKER_SQL_PATTERN,
    INTERNAL_OVERRIDE_SQL_PATTERN,
    LITERAL_PAGE_SQL,
    PRIMARY_DISEASE_SQL,
    PRIMARY_DRUG_SQL,
    PAGE_SQL,
    calculadoras_encontradas,
    literal_like,
    normalizar,
)
from app.services.clinical_text import clinical_text_without_internal_overrides
from app.services.connected_content import buscar_relacionados_da_doenca, buscar_relacionados_do_medicamento
from app.services.search_relevance import disease_identity_phrases, disease_search_metadata

router = APIRouter(prefix="/api/search", tags=["busca"])
SearchSection = Literal[
    "geral", "conduta", "diretriz", "fluxo", "galeria", "exame", "evidencia",
    "estudo", "medicamento", "caso_clinico", "trilha", "checklist",
    "material_paciente", "emergencia", "doenca", "triagem_sintoma", "calculadora", "publicacao_original",
]


def _disease_identity_phrases(disease: SpecialtyDisease) -> tuple[str, ...]:
    return disease_identity_phrases(disease)


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
            "calculadora|publicacao_original — vazio traz todas"
        )),
    secao: Annotated[SearchSection | None, Query(
        description="Seção editorial; combinada com frente por interseção")] = None,
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
    # The resolved subject remains stable when the reader filters a front.
    primary_disease = resolved
    if primary_disease is not None:
        primary_disease["summary"] = clinical_text_without_internal_overrides(
            primary_disease.get("summary")
        )

    drug_model = None
    if disease_model is None:
        drug_rows = db.execute(PRIMARY_DRUG_SQL, {"q": q}).mappings().all()
        if len(drug_rows) == 1:
            drug_model = db.execute(select(Drug).where(
                Drug.slug == drug_rows[0]["slug"], Drug.published.is_(True),
            )).scalar_one_or_none()
    primary_drug = ({"slug": drug_model.slug, "generic_name": drug_model.generic_name}
                    if drug_model is not None else None)
    query = (disease_model.name if disease_model is not None
             else drug_model.generic_name if drug_model is not None else q)
    include_calculators = frente in (None, "calculadora")
    calculadoras = calculadoras_encontradas(query) if include_calculators else []
    if disease_model is not None and include_calculators:
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
    if disease_model is not None or drug_model is not None:
        ecosystem = (buscar_relacionados_da_doenca(db, disease_model.slug)
                     if disease_model is not None else buscar_relacionados_do_medicamento(
                         db, drug_model.slug, limite_por_categoria=None))
        for group in (ecosystem or {}).get("grupos", []):
            kind = {"fluxograma": "documento", "protocolo_emergencia": "emergencia"}.get(
                group["tipo"], group["tipo"]
            )
            disease_links.extend(
                f"{kind}:{item['slug']}" for item in group.get("itens", [])
                if item.get("slug") and not item.get("context_only")
                and item.get("relation_method") != "SpecialtyDisease.tests"
            )
            for item in group.get("itens", []):
                if item.get("slug") and item.get("relation_method") != "SpecialtyDisease.tests":
                    connection_metadata.setdefault(f"{kind}:{item['slug']}", item)
            recommendations = [item for item in group.get("itens", [])
                               if item.get("relation_method") == "SpecialtyDisease.tests"]
            if recommendations:
                supplementary_groups.append({**group, "itens": recommendations})
        if disease_model is not None:
            candidate_metadata = disease_search_metadata(db, disease_model, connection_metadata)
            disease_links.extend(candidate_metadata)
        else:
            candidate_metadata = {
                key: {"relation_type": item.get("relation_type"),
                      "context_only": item.get("context_only", False),
                      "match_reasons": [{"source": item.get("relation_method") or "structured_connection", "description":
                          item.get("relation_reason") or "Vínculo estruturado com o medicamento."}]}
                for key, item in connection_metadata.items()
                if not item.get("context_only")
            }
        if include_calculators:
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
        disease_links.append(f"doenca:{disease_model.slug}" if disease_model is not None
                             else f"medicamento:{drug_model.slug}")
    else:
        candidate_metadata = {}

    # Context-only connections never recruit a result. If the published row
    # independently matches its identity, preserve the legacy relation labels.
    for key, item in connection_metadata.items():
        if key not in candidate_metadata:
            candidate_metadata[key] = {
                "clinical_role": "mention", "clinical_context": None,
                "relation_type": item.get("relation_type"),
                "context_only": item.get("context_only", False),
                "match_reasons": [{"source": item.get("relation_method") or "structured_connection",
                                   "description": "Contexto relacionado; não constitui indicação clínica."}],
            }

    # The in-memory catalogue is part of the same section/filter contract.
    # Deduplicate by its typed canonical identity before counting or slicing.
    calculadoras = list({item["slug"]: {**item, "secao": "calculadora"}
                         for item in calculadoras}.values())
    values = {
        "q": query, "q_like": literal_like(query), "frente": frente, "secao": secao,
        "limit": limit, "offset": offset,
        "candidate_metadata": json.dumps(candidate_metadata, ensure_ascii=False),
        "calculator_candidates": json.dumps(calculadoras, ensure_ascii=False),
    }
    sql = PAGE_SQL
    if disease_model is not None or drug_model is not None:
        sql = DISEASE_SQL
        values.update({
            "disease_phrases": (list(_disease_identity_phrases(disease_model))
                                if disease_model is not None else list(dict.fromkeys(
                                    normalizar(value) for value in [drug_model.generic_name,
                                    drug_model.slug, *(drug_model.brand_names or [])]
                                    if len(normalizar(value)) >= 2))),
            "disease_links": list(dict.fromkeys(disease_links)),
            "systemic_hypertension": disease_model is not None and disease_model.slug == "hipertensao-arterial-sistemica",
        })
    search_values = {
        **values,
        "internal_override_pattern": INTERNAL_OVERRIDE_SQL_PATTERN,
        "internal_marker_pattern": INTERNAL_MARKER_SQL_PATTERN,
    }
    page = db.execute(sql, search_values).mappings().one()
    raw_rows = page["results"]
    por_frente = page["por_frente"]
    if (disease_model is None and drug_model is None
            and not page.get("matched_total", sum(por_frente.values())) and normalizar(q)):
        # Selecting an empty section must not switch an otherwise successful
        # full-text candidate set to a broader literal fallback.
        page = db.execute(LITERAL_PAGE_SQL, search_values).mappings().one()
        raw_rows = page["results"]
        por_frente = page["por_frente"]

    rows = [dict(row) for row in raw_rows]
    for row in rows:
        if isinstance(row.get("snippet"), str):
            row["snippet"] = clinical_text_without_internal_overrides(row["snippet"])
        if row["frente"] == "evidencia":
            row["title"] = clinical_text_without_internal_overrides(row["title"])
    por_frente = {str(kind): int(count) for kind, count in por_frente.items()}
    por_secao = {str(section): int(count) for section, count in page["por_secao"].items()}
    total = sum(por_frente.values())
    next_offset = offset + len(rows)
    return {
        "query": q, "count": len(rows), "total": total, "limit": limit, "offset": offset,
        "next_offset": next_offset if next_offset < total else None,
        "por_frente": por_frente, "por_secao": por_secao, "primary_disease": primary_disease, "primary_drug": primary_drug,
        "supplementary_groups": supplementary_groups,
        "results": rows,
    }
