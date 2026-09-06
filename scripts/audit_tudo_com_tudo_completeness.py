#!/usr/bin/env python3
"""Release gate for clinical precision and minimum completeness of Tudo com Tudo.

Exact-theme membership is only a candidate pool, never clinical proof. This gate
checks high-impact false positives, minimum structured disease cores, canonical
search precision, duplicated calculators, and structured drug-topic sentinels.
"""
from __future__ import annotations

from sqlalchemy import func, select

from app.core.db import SessionLocal
from app.models.knowledge import KnowledgeEntity
from app.models.specialty_guide import SpecialtyDisease
from app.services.connected_content import buscar_relacionados_da_doenca
from app.services.topic_relevance import drug_matches_theme
from app.api.search import search as search_api
from app.services.catalog_search import (
    INTERNAL_MARKER_SQL_PATTERN, INTERNAL_OVERRIDE_SQL_PATTERN, SQL, literal_like,
)
from app.models.drug import Drug


def main() -> int:
    errors: list[str] = []
    checked = 0
    with SessionLocal() as db:
        checked = 0

        def groups_for(slug: str) -> dict[str, list[dict]]:
            nonlocal checked
            checked += 1
            result = buscar_relacionados_da_doenca(
                db, slug, limite_por_categoria=12
            ) or {}
            return {
                group["tipo"]: list(group.get("itens", []))
                for group in result.get("grupos", [])
            }

        # FA: the original regression mixed unrelated exact-theme items and
        # omitted the minimum antithrombotic/risk-stratification nucleus.
        fa_groups = groups_for("fibrilacao-atrial")
        fa_slugs = {
            item["slug"] for items in fa_groups.values() for item in items
        }
        fa_calc = {item["slug"] for item in fa_groups.get("calculadora", [])}
        need_calc = {"cha2ds2-vasc", "has-bled", "orbit"}
        if not need_calc <= fa_calc:
            errors.append(
                f"fibrilacao-atrial:calculadoras:missing={sorted(need_calc-fa_calc)}"
            )
        for forbidden in {
            "tight-k-limiar-de-reposicao-de-potassio-pos-crm-implicacao-do-ensaio",
            "berlin-vt-primario-nulo",
        }:
            if forbidden in fa_slugs:
                errors.append(f"fibrilacao-atrial:false-positive={forbidden}")
        fa_drugs = {item["slug"] for item in fa_groups.get("medicamento", [])}
        if not ({"apixabana", "dabigatrana-etexilato", "varfarina-sodica"} & fa_drugs):
            errors.append("fibrilacao-atrial:anticoagulant-core-missing")

        # SCA: the minimum structured core must not be empty.
        sca_groups = groups_for("sindrome-coronariana-aguda")
        sca_calc = {item["slug"] for item in sca_groups.get("calculadora", [])}
        sca_need = {"crusade", "grace", "timi-stemi", "timi-ua-nstemi"}
        if not sca_need <= sca_calc:
            errors.append(f"sca:calculadoras:missing={sorted(sca_need-sca_calc)}")
        sca_material = {item["slug"] for item in sca_groups.get("material_paciente", [])}
        if "doenca-coronariana-e-infarto" not in sca_material:
            errors.append("sca:patient-material-missing")
        sca_drugs = {item["slug"] for item in sca_groups.get("medicamento", [])}
        sca_drug_need = {"acido-acetilsalicilico-aas", "fondaparinux-sodico", "ticagrelor"}
        if not sca_drug_need <= sca_drugs:
            errors.append(f"sca:drug-core:missing={sorted(sca_drug_need-sca_drugs)}")

        # Systemic hypertension must not inherit pulmonary-hypertension therapy.
        has_groups = groups_for("hipertensao-arterial-sistemica")
        has_drugs = {item["slug"] for item in has_groups.get("medicamento", [])}
        pulmonary_drugs = {"ambrisentana", "bosentana"} & has_drugs
        if pulmonary_drugs:
            errors.append(f"has:pulmonary-drug-leak={sorted(pulmonary_drugs)}")
        has_material = {item["slug"] for item in has_groups.get("material_paciente", [])}
        if "hipertensao-arterial" not in has_material:
            errors.append("has:patient-material-missing")

        # Pericarditis: explicit material + colchicine must survive the limit.
        peri_groups = groups_for("pericardite")
        peri_drugs = {item["slug"] for item in peri_groups.get("medicamento", [])}
        peri_material = {item["slug"] for item in peri_groups.get("material_paciente", [])}
        if "colchicina" not in peri_drugs:
            errors.append("pericardite:colchicina-missing")
        if "pericardite-aguda" not in peri_material:
            errors.append("pericardite:patient-material-missing")

        # Exact disease queries use a high-precision search view.
        for query, slug in {
            "fibrilacao atrial": "fibrilacao-atrial",
            "sindrome coronariana aguda": "sindrome-coronariana-aguda",
            "hipertensao arterial sistemica": "hipertensao-arterial-sistemica",
            "pericardite": "pericardite",
        }.items():
            payload = search_api(q=query, frente=None, limit=100, offset=0, db=db, _=None)
            if payload.get("count", 0) > 36:
                errors.append(f"search:{slug}:over-cap={payload.get('count')}")
            if slug == "hipertensao-arterial-sistemica":
                identity = " ".join(
                    f"{row.get('title','')} {row.get('slug','')}".casefold()
                    for row in payload.get("results", [])
                )
                if (
                    "hipertensão pulmonar" in identity
                    or "hipertensao-pulmonar" in identity
                    or "hipertensão arterial pulmonar" in identity
                ):
                    errors.append("search:has:pulmonary-leak")

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

    print(f"TCT_CLINICAL_SENTINELS_CHECKED={checked}")
    print(f"TCT_ERRORS={len(errors)}")
    for error in errors:
        print("ERROR", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
