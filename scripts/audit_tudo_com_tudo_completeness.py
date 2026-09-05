#!/usr/bin/env python3
"""Release gate for clinical completeness of Tudo com Tudo.

Fails on missing exact-theme members, duplicated active calculator nodes,
missing AF risk calculators, or broken structured drug-topic sentinels.
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, select

from app.core.db import SessionLocal
from app.models.knowledge import KnowledgeEntity
from app.models.specialty_guide import SpecialtyDisease
from app.services.connected_content import buscar_relacionados_da_doenca
from app.services.knowledge_graph import _itens_por_tema, _normalizar_chave_clinica
from app.services.topic_relevance import drug_matches_theme
from app.services.catalog_search import (
    INTERNAL_MARKER_SQL_PATTERN, INTERNAL_OVERRIDE_SQL_PATTERN, SQL, literal_like,
)
from app.models.drug import Drug


def main() -> int:
    errors: list[str] = []
    checked = 0
    with SessionLocal() as db:
        por_tema, _ = _itens_por_tema(db)
        diseases = db.execute(select(SpecialtyDisease).where(SpecialtyDisease.published.is_(True))).scalars().all()
        for disease in diseases:
            keys = {_normalizar_chave_clinica(disease.name), _normalizar_chave_clinica(disease.slug.replace("-", " "))}
            keys.update(_normalizar_chave_clinica(alias) for alias in (disease.aliases or []))
            exact = [items for theme, items in por_tema.items() if _normalizar_chave_clinica(theme) in keys]
            if not exact:
                continue
            checked += 1
            expected: dict[str, set[str]] = defaultdict(set)
            for items in exact:
                for item in items:
                    if item.tipo not in {"tema", "doenca"}:
                        expected[item.tipo].add(item.slug)
            result = buscar_relacionados_da_doenca(db, disease.slug, limite_por_categoria=None)
            actual = {g["tipo"]: {x["slug"] for x in g.get("itens", [])} for g in (result or {}).get("grupos", [])}
            for entity_type, slugs in expected.items():
                missing = slugs - actual.get(entity_type, set())
                if missing:
                    errors.append(f"{disease.slug}:{entity_type}:missing={sorted(missing)[:8]} count={len(missing)}")

        # Busca transversal por identidade: um exame básico não pode sumir
        # porque a duração esteja no slug e não no título editorial.
        q = "holter 24h"
        search_rows = db.execute(SQL, {
            "q": q, "q_like": literal_like(q), "frente": None,
            "limit": 10, "offset": 0,
            "internal_override_pattern": INTERNAL_OVERRIDE_SQL_PATTERN,
            "internal_marker_pattern": INTERNAL_MARKER_SQL_PATTERN,
        }).mappings().all()
        if not search_rows or not (
            search_rows[0]["frente"] == "exame"
            and search_rows[0]["slug"] == "holter-24h"
        ):
            errors.append("search:holter-24h-not-first")

        fa = buscar_relacionados_da_doenca(db, "fibrilacao-atrial", limite_por_categoria=None) or {}
        fa_calc = next((g for g in fa.get("grupos", []) if g["tipo"] == "calculadora"), {"itens": []})
        got = {x["slug"] for x in fa_calc["itens"]}
        need = {"cha2ds2-vasc", "has-bled", "orbit"}
        if not need <= got:
            errors.append(f"fibrilacao-atrial:calculadoras:missing={sorted(need-got)}")

        dns = buscar_relacionados_da_doenca(
            db, "disfuncao-do-no-sinusal", limite_por_categoria=None
        ) or {}
        structured_tests = [
            item for group in dns.get("grupos", []) if group["tipo"] == "exame"
            for item in group.get("itens", [])
            if item.get("relation_method") == "SpecialtyDisease.tests"
        ]
        if not structured_tests:
            errors.append("disfuncao-do-no-sinusal:structured-tests-missing")

        sarcopenia = buscar_relacionados_da_doenca(
            db, "sarcopenia-cardiovascular", limite_por_categoria=None
        ) or {}
        if not any(
            item.get("relation_method") == "global_disease_identity_fallback"
            for group in sarcopenia.get("grupos", []) for item in group.get("itens", [])
        ):
            errors.append("sarcopenia-cardiovascular:global-context-missing")

        dup = db.execute(
            select(KnowledgeEntity.slug, func.count(KnowledgeEntity.id))
            .where(KnowledgeEntity.entity_type == "calculadora", KnowledgeEntity.status == "ativo")
            .group_by(KnowledgeEntity.slug).having(func.count(KnowledgeEntity.id) > 1)
        ).all()
        if dup:
            errors.append(f"active_calculator_duplicates={dup}")

        for slug, expected_themes in {
            "apixabana": {"Fibrilação atrial", "Tromboembolismo"},
            "rivaroxabana": {"Fibrilação atrial", "Tromboembolismo"},
            "sacubitrilvalsartana": {"Insuficiência cardíaca"},
        }.items():
            drug = db.execute(select(Drug).where(Drug.slug == slug, Drug.published.is_(True))).scalar_one_or_none()
            if drug is None:
                errors.append(f"drug_not_found={slug}")
                continue
            missing = {theme for theme in expected_themes if not drug_matches_theme(drug, theme)}
            if missing:
                errors.append(f"{slug}:missing_themes={sorted(missing)}")

    print(f"TCT_EXACT_DISEASES_CHECKED={checked}")
    print(f"TCT_ERRORS={len(errors)}")
    for error in errors:
        print("ERROR", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
