"""Gates mínimos do hub de estenose pulmonar congênita."""

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
CHECKLISTS = ROOT / "checklists/metadados.json"
TRACKS = ROOT / "trilhas/metadados.json"
EXPLICIT_RELATIONS = ROOT / "doencas/relacoes-explicitas.json"
SLUG = "estenose-pulmonar-congenita"


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


def test_hub_incorpora_acc_e_retorna_para_revisao_humana():
    disease = _disease()
    assert disease["completeness"] == "completo"
    assert disease["review_status"] == "revisado"
    assert disease["version"] == 2
    assert disease["fonte_producao"] == "chatgpt"
    assert "exige revisão humana" in disease["review_note"].casefold()
    assert "abaixo de 3 m/s" in disease["diagnostic_approach"]["gravidade_ecocardiografica"]
    assert "não são gatilhos automáticos" in disease["diagnostic_approach"]["gravidade_ecocardiografica"]

    minimums = {
        "presentation": 10,
        "differentials": 10,
        "tests": 14,
        "red_flags": 10,
        "ambulatory_flow": 12,
        "emergency_flow": 8,
        "monitoring": 12,
        "special_populations": 10,
        "assistant_questions": 10,
        "assistant_rules": 10,
        "source_refs": 6,
        "source_urls": 6,
        "related_document_slugs": 3,
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


def test_referencias_tudo_com_tudo_resolvem_explicitamente():
    disease = _disease()
    assert set(disease["related_document_slugs"]) <= _document_slugs()
    assert "patient_material_slug" not in disease

    relations = [
        item for item in _records(EXPLICIT_RELATIONS)
        if item["source_disease_slug"] == SLUG
    ]
    assert len(relations) == 4
    targets = {
        "checklist": {item["slug"] for item in _records(CHECKLISTS)},
        "trilha": {item["slug"] for item in _records(TRACKS)},
    }
    assert all(item["target_slug"] in targets[item["target_type"]] for item in relations)
    assert all(item["review_status"] == "revisado" for item in relations)
    assert all(item["confidence"] == "explicit" for item in relations)


def test_assistente_trata_neonato_cianotico_como_emergencia_sem_dose():
    disease = _disease()
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers={
            "epc_faixa_etaria": "neonato",
            "epc_instavel_cianose": True,
            "epc_nivel": "valvar_isolada",
            "epc_gravidade": "grave",
            "epc_sintomas": True,
            "epc_progressao": True,
            "epc_intervencao_previa": False,
            "epc_ip_residual": False,
            "epc_noonan": False,
            "epc_eco_recente": False,
        },
        context="emergencia",
    )

    assert result["risk"] == "emergencia"
    assert "epc-neonato-instavel" in result["matched_rules"]
    rendered = json.dumps(result, ensure_ascii=False).casefold()
    assert "uti neonatal" in rendered
    assert "mg/kg" not in rendered
    assert "prescrever" not in rendered
