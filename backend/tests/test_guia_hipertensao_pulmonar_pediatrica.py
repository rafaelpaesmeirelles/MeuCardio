"""Gates mínimos do hub de hipertensão pulmonar pediátrica."""

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
EMERGENCIES = ROOT / "emergencia/metadados.json"
EXPLICIT_RELATIONS = ROOT / "doencas/relacoes-explicitas.json"
SLUG = "hipertensao-pulmonar-pediatrica"


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


def test_hub_incorpora_wsph_2024_e_volta_para_revisao_humana():
    disease = _disease()

    assert disease["completeness"] == "completo"
    assert disease["review_status"] == "pendente_revisao"
    assert disease["version"] == 2
    assert disease["fonte_producao"] == "chatgpt"
    assert "exige revisão humana" in disease["review_note"].casefold()
    assert "7º simpósio mundial" in disease["review_note"].casefold()
    assert len(disease["summary"]) >= 800
    assert len(disease["epidemiology"]) >= 800
    assert len(disease["treatment_summary"]) >= 2_000

    minimums = {
        "presentation": 10,
        "differentials": 10,
        "tests": 13,
        "red_flags": 10,
        "ambulatory_flow": 11,
        "emergency_flow": 8,
        "monitoring": 10,
        "special_populations": 10,
        "assistant_questions": 10,
        "assistant_rules": 10,
        "source_refs": 6,
        "source_urls": 6,
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
        ("protocolo_emergencia", "crise-de-hipertensao-pulmonar-pediatrica"),
        ("checklist", "teste-de-vasorreatividade-aguda-avaliacao-e-conduta-pos-resultado"),
        ("checklist", "manejo-da-falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo"),
        ("trilha", "trilha-cardiologia-pediatrica-insuficiencia-cardiaca-e-hipertensao-pulmonar"),
        ("trilha", "trilha-cardiopatia-congenita-hipertensao-pulmonar-associada-e-fechamento-por-dispositivo"),
    }
    targets = {
        "protocolo_emergencia": {item["slug"] for item in _records(EMERGENCIES)},
        "checklist": {item["slug"] for item in _records(CHECKLISTS)},
        "trilha": {item["slug"] for item in _records(TRACKS)},
    }
    assert all(item["target_slug"] in targets[item["target_type"]] for item in relations)
    assert all(item["review_status"] == "pendente_revisao" for item in relations)
    assert all(item["confidence"] == "explicit" for item in relations)


def test_assistente_prioriza_crise_sem_prescricao_automatica():
    disease = _disease()
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers={
            "hpp_faixa_etaria": "crianca",
            "hpp_instabilidade": True,
            "hpp_sincope": False,
            "hpp_terapia_interrompida": False,
            "hpp_fenotipo": "incerto",
            "hpp_ecocardiograma": False,
            "hpp_cateterismo": False,
            "hpp_alto_risco": True,
            "hpp_rvpi_shunt": "nao_disponivel",
            "hpp_genetica_indicada": False,
        },
        context="emergencia",
    )

    assert result["risk"] == "emergencia"
    assert "hpp-crise-instavel" in result["matched_rules"]
    rendered = json.dumps(result, ensure_ascii=False).casefold()
    assert "atendimento hospitalar imediato" in rendered
    assert "mg/kg" not in rendered
    assert "prescrever" not in rendered
    assert "iniciar sildenafila" not in rendered
