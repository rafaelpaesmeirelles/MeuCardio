"""Gates mínimos do verbete-hub de febre reumática e cardite."""

from __future__ import annotations

import json
from pathlib import Path
import re

from app.services.clinical_rule_engine import (
    evaluate_rules,
    validate_question_definitions,
    validate_rule_definitions,
)


ROOT = Path(__file__).resolve().parents[2]
DISEASES = ROOT / "doencas/metadados.json"
PATIENT_MATERIALS = ROOT / "material-paciente/metadados.json"
CHECKLISTS = ROOT / "checklists/metadados.json"
TRACKS = ROOT / "trilhas/metadados.json"
EXPLICIT_RELATIONS = ROOT / "doencas/relacoes-explicitas.json"
SLUG = "febre-reumatica-cardite"


def _records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return payload


def _disease() -> dict:
    matches = [item for item in _records(DISEASES) if item["slug"] == SLUG]
    assert len(matches) == 1
    return matches[0]


def _document_slugs() -> set[str]:
    slugs: set[str] = set()
    for path in (ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", text, re.MULTILINE)
        if match:
            slugs.add(match.group(1).strip())
    return slugs


def test_hub_tem_profundidade_e_volta_para_revisao_humana():
    disease = _disease()

    assert disease["completeness"] == "completo"
    assert disease["review_status"] == "revisado"
    assert disease["version"] == 2
    assert disease["fonte_producao"] == "chatgpt"
    assert "exige revisão humana" in disease["review_note"].casefold()
    assert len(disease["summary"]) >= 500
    assert len(disease["epidemiology"]) >= 500
    assert len(disease["treatment_summary"]) >= 1_000

    minimums = {
        "presentation": 8,
        "differentials": 8,
        "tests": 8,
        "red_flags": 7,
        "ambulatory_flow": 8,
        "emergency_flow": 7,
        "monitoring": 6,
        "special_populations": 6,
        "assistant_questions": 9,
        "assistant_rules": 8,
        "source_refs": 4,
        "source_urls": 4,
        "related_document_slugs": 6,
    }
    for field, minimum in minimums.items():
        assert len(disease[field]) >= minimum, f"{SLUG}:{field}"

    question_errors, question_ids = validate_question_definitions(
        SLUG, disease["assistant_questions"]
    )
    rule_errors = validate_rule_definitions(
        SLUG, disease["assistant_rules"], question_ids
    )
    assert question_errors == []
    assert rule_errors == []


def test_referencias_tudo_com_tudo_resolvem_sem_inferencia_temática():
    disease = _disease()
    assert set(disease["related_document_slugs"]) <= _document_slugs()

    material_slugs = {item["slug"] for item in _records(PATIENT_MATERIALS)}
    assert disease["patient_material_slug"] in material_slugs

    relations = [
        item for item in _records(EXPLICIT_RELATIONS)
        if item["source_disease_slug"] == SLUG
    ]
    assert {
        (item["target_type"], item["target_slug"])
        for item in relations
    } == {
        (
            "checklist",
            "aplicacao-dos-criterios-de-jones-2015-para-diagnostico-de-febre-reumatica-aguda",
        ),
        ("checklist", "inicio-de-profilaxia-secundaria-da-febre-reumatica"),
        (
            "trilha",
            "trilha-febre-reumatica-do-diagnostico-a-profilaxia-secundaria",
        ),
        (
            "trilha",
            "trilha-febre-reumatica-cardite-aguda-grave-a-decisao-cirurgica",
        ),
    }
    targets = {
        "checklist": {item["slug"] for item in _records(CHECKLISTS)},
        "trilha": {item["slug"] for item in _records(TRACKS)},
    }
    assert all(item["target_slug"] in targets[item["target_type"]] for item in relations)
    assert all(item["review_status"] == "revisado" for item in relations)
    assert all(item["confidence"] == "explicit" for item in relations)


def test_assistente_prioriza_instabilidade_e_nao_prescreve_automaticamente():
    disease = _disease()
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers={
            "fra_contexto": "suspeita_aguda",
            "fra_risco_populacional": "incerto",
            "fra_instabilidade": True,
            "fra_febre_persistente_toxemia": False,
            "fra_monoartrite_febril": False,
            "fra_coreia_grave": False,
            "fra_ecocardiograma_realizado": False,
            "fra_profilaxia_atrasada": False,
            "fra_gestacao": False,
        },
        context="emergencia",
    )

    assert result["risk"] == "emergencia"
    assert "fra-cardite-instavel" in result["matched_rules"]
    rendered = json.dumps(result, ensure_ascii=False).casefold()
    assert "atendimento hospitalar imediato" in rendered
    assert "prescrever" not in rendered

