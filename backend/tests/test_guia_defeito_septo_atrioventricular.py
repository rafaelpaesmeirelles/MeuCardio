"""Gates mínimos do hub de defeito do septo atrioventricular."""

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
SLUG = "defeito-septo-atrioventricular"


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


def test_hub_incorpora_acc_2026_e_volta_para_revisao_humana():
    disease = _disease()

    assert disease["completeness"] == "completo"
    assert disease["review_status"] == "revisado"
    assert disease["version"] == 2
    assert disease["fonte_producao"] == "chatgpt"
    assert "exige revisão humana" in disease["review_note"].casefold()
    assert "26/08/2026" in disease["review_note"]
    assert "10–25%" in disease["treatment_summary"]
    assert "3 e 6 meses" in disease["treatment_summary"]

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
        "source_refs": 7,
        "source_urls": 7,
        "related_document_slugs": 1,
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


def test_referencias_tudo_com_tudo_resolvem_sem_inferencia_tematica():
    disease = _disease()
    assert set(disease["related_document_slugs"]) <= _document_slugs()

    material_slugs = {item["slug"] for item in _records(PATIENT_MATERIALS)}
    assert disease["patient_material_slug"] in material_slugs

    relations = [
        item
        for item in _records(EXPLICIT_RELATIONS)
        if item["source_disease_slug"] == SLUG
    ]
    assert {
        (item["target_type"], item["target_slug"])
        for item in relations
    } == {
        (
            "trilha",
            "trilha-cardiologia-pediatrica-insuficiencia-cardiaca-e-hipertensao-pulmonar",
        ),
        ("trilha", "trilha-cardiopatia-congenita-triagem-para-centro-terciario"),
        (
            "checklist",
            "elegibilidade-esportiva-na-crianca-e-no-adolescente-com-cardiopatia-congenita-por-lesao",
        ),
    }
    targets = {
        "checklist": {item["slug"] for item in _records(CHECKLISTS)},
        "trilha": {item["slug"] for item in _records(TRACKS)},
    }
    assert all(item["target_slug"] in targets[item["target_type"]] for item in relations)
    assert all(item["review_status"] == "revisado" for item in relations)
    assert all(item["confidence"] == "explicit" for item in relations)


def test_assistente_prioriza_instabilidade_sem_prescricao_automatica():
    disease = _disease()
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers={
            "dsav_faixa_etaria": "lactente",
            "dsav_reparado": False,
            "dsav_subtipo": "completo_intermediario",
            "dsav_instavel": True,
            "dsav_falha_crescimento": True,
            "dsav_hp_tardia": False,
            "dsav_lesao_residual": False,
            "dsav_arritmia": False,
            "dsav_down": True,
            "dsav_eco_recente": True,
        },
        context="emergencia",
    )

    assert result["risk"] == "emergencia"
    assert "dsav-instabilidade" in result["matched_rules"]
    rendered = json.dumps(result, ensure_ascii=False).casefold()
    assert "atendimento hospitalar imediato" in rendered
    assert "mg/kg" not in rendered
    assert "prescrever" not in rendered

