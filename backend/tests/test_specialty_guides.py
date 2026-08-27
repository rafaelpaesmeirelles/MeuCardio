from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

from app.commands.reconcile_content import FRONTS
from app.services.clinical_rule_engine import (
    evaluate_rules,
    validate_answers,
    validate_question_definitions,
    validate_rule_definitions,
)

ROOT = Path(__file__).resolve().parents[2]
DISEASES_PATH = ROOT / "doencas/metadados.json"
TRIAGE_PATH = ROOT / "triagem-sintomas/metadados.json"


def _load(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _assert_urls(items: list[dict]) -> None:
    for item in items:
        for url in item.get("source_urls", []):
            parsed = urlparse(url)
            assert parsed.scheme in {"http", "https"}
            assert parsed.netloc


def test_specialty_catalog_has_all_areas_and_canonical_minimum():
    items = _load(DISEASES_PATH)
    slugs = [item["slug"] for item in items]

    assert len(items) >= 88
    assert len(slugs) == len(set(slugs))
    assert {item["area"] for item in items} == {
        "geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez",
    }
    assert FRONTS["doencas_especializadas"]["minimum"] == 88
    assert all(item.get("summary") for item in items)
    assert {item.get("review_status") for item in items} <= {
        "revisado", "pendente_revisao", "lacuna_declarada",
    }
    assert sum(item.get("review_status") == "revisado" for item in items) >= 26
    assert all(
        item.get("review_note")
        for item in items
        if item.get("review_status") != "revisado"
    )
    assert all(item.get("source_refs") for item in items)
    _assert_urls(items)


def test_congenital_and_fetal_catalog_taxonomy_is_searchable():
    items = _load(DISEASES_PATH)
    congenital = [item for item in items if item.get("category") == "cardiopatia_congenita"]
    fetal = [item for item in items if item.get("category") == "cardiologia_fetal"]

    assert congenital
    assert fetal
    assert {item.get("cyanosis_class") for item in congenital} >= {
        "cianotica", "acianotica",
    }
    assert all(item.get("subtype") for item in congenital + fetal)
    assert all(item.get("aliases") for item in congenital + fetal)
    assert all(item.get("tags") for item in congenital + fetal)


def test_assistants_exist_in_every_specialty_without_protected_score_replication():
    items = _load(DISEASES_PATH)
    assistants = [item for item in items if item.get("assistant_questions")]

    assert {item["area"] for item in assistants} == {
        "geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez",
    }
    serialized_rules = json.dumps(
        [item.get("assistant_rules", []) for item in assistants],
        ensure_ascii=False,
    ).casefold()
    assert "mwho" not in serialized_rules
    assert "hfa-icos" not in serialized_rules


def test_triage_manifest_has_two_flows_and_special_populations():
    items = _load(TRIAGE_PATH)
    slugs = [item["slug"] for item in items]

    assert len(items) >= 15
    assert len(slugs) == len(set(slugs))
    assert FRONTS["triagem_sintomas"]["minimum"] == 15
    assert all(item.get("questions") for item in items)
    assert all(item.get("rules") for item in items)
    assert all(item.get("ambulatory_flow") for item in items)
    assert all(item.get("emergency_flow") for item in items)
    assert all(item.get("source_refs") for item in items)
    assert {area for item in items for area in item.get("areas", [])} >= {
        "geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez",
    }
    _assert_urls(items)


def test_rule_engine_escalates_and_selects_emergency_flow():
    questions = [
        {"id": "unstable", "type": "boolean", "required": True},
    ]
    rules = [
        {
            "id": "instabilidade",
            "priority": 100,
            "when": {"all": [{"field": "unstable", "op": "truthy"}]},
            "add": {
                "risk": "emergencia",
                "red_flags": ["Instabilidade"],
                "emergency_flow": ["Atendimento imediato"],
            },
        },
    ]

    result = evaluate_rules(
        questions=questions,
        rules=rules,
        answers={"unstable": True},
        base_ambulatory_flow=["Consulta"],
        base_emergency_flow=["ABC"],
        context="ambulatorio",
    )

    assert result["risk"] == "emergencia"
    assert result["red_flags"] == ["Instabilidade"]
    assert result["recommended_flow"] == ["ABC", "Atendimento imediato"]
    assert result["matched_rules"] == ["instabilidade"]


def test_invalid_boolean_or_unknown_field_never_fires_rule():
    questions = [{"id": "unstable", "type": "boolean", "required": True}]
    rules = [
        {
            "id": "nao-deve-disparar",
            "when": {"all": [{"field": "unstable", "op": "truthy"}]},
            "add": {"risk": "emergencia", "red_flags": ["Inválido"]},
        },
    ]

    result = evaluate_rules(
        questions=questions,
        rules=rules,
        answers={"unstable": "false", "campo_injetado": True},
        context="emergencia",
    )

    assert result["risk"] == "informativo"
    assert result["matched_rules"] == []
    assert result["red_flags"] == []
    assert set(result["invalid_fields"]) == {"unstable", "campo_injetado"}


def test_missing_required_is_reported_but_partial_safe_rules_can_run():
    questions = [
        {"id": "required", "type": "boolean", "required": True},
        {"id": "red_flag", "type": "boolean", "required": False},
    ]
    rules = [
        {
            "id": "red-flag",
            "when": {"all": [{"field": "red_flag", "op": "truthy"}]},
            "add": {"risk": "urgente", "red_flags": ["Alarme"]},
        },
    ]

    result = evaluate_rules(
        questions=questions,
        rules=rules,
        answers={"red_flag": True},
        context="ambulatorio",
    )

    assert result["missing_information"] == ["required"]
    assert result["risk"] == "urgente"
    assert result["red_flags"] == ["Alarme"]


def test_answer_validation_rejects_non_finite_and_oversized_values():
    questions = [
        {"id": "number", "type": "number"},
        {"id": "text", "type": "text"},
        {"id": "multi", "type": "multiselect", "options": [{"value": "a"}]},
    ]

    _, invalid = validate_answers(
        questions,
        {
            "number": float("inf"),
            "text": "x" * 2001,
            "multi": ["a", "a"],
        },
    )

    assert invalid == ["multi", "number", "text"]


def test_required_empty_multiselect_and_blank_text_are_reported_missing():
    questions = [
        {"id": "multi", "type": "multiselect", "required": True},
        {"id": "text", "type": "text", "required": True},
    ]

    missing, invalid = validate_answers(
        questions,
        {"multi": [], "text": "   "},
    )

    assert missing == ["multi", "text"]
    assert invalid == []


def test_manifest_schema_rejects_unsafe_or_malformed_rules():
    question_errors, question_ids = validate_question_definitions(
        "guia-invalido",
        [{"id": "choice", "type": "select", "options": []}],
    )
    rule_errors = validate_rule_definitions(
        "guia-invalido",
        [{
            "id": "regra",
            "when": {"all": ["condicao-nao-estruturada"]},
            "add": {"risk": "critico", "prescricao": "automatica"},
        }],
        question_ids,
    )

    assert any("precisa de opções" in error for error in question_errors)
    assert any("condição inválida" in error for error in rule_errors)
    assert any("campos não permitidos" in error for error in rule_errors)
    assert any("risco inválido" in error for error in rule_errors)


def test_engine_rejects_unsupported_context_and_excessive_rules():
    with pytest.raises(ValueError, match="Contexto"):
        evaluate_rules(questions=[], rules=[], answers={}, context="internacao")

    with pytest.raises(ValueError, match="regras"):
        evaluate_rules(
            questions=[],
            rules=[{} for _ in range(501)],
            answers={},
            context="ambulatorio",
        )
