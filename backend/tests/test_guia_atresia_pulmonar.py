"""Gates mínimos do hub de atresia pulmonar."""

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
SLUG = "atresia-pulmonar"


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


def test_hub_separa_paivs_de_pavsd_e_tem_revisao_concluida():
    disease = _disease()
    assert disease["completeness"] == "completo"
    assert disease["review_status"] == "revisado"
    assert disease["version"] == 3
    assert disease["fonte_producao"] == "chatgpt"
    assert "audit" in disease["review_note"].casefold()
    assert "PA/IVS" in disease["summary"]
    assert "PA/VSD" in disease["summary"]
    assert "MAPCA" in disease["diagnostic_approach"]["mapa_pavsd"]
    assert "potencialmente fatal" in disease["treatment_summary"]

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


def test_referencias_tudo_com_tudo_resolvem_explicitamente():
    disease = _disease()
    assert set(disease["related_document_slugs"]) <= _document_slugs()
    assert disease["patient_material_slug"] in {
        item["slug"] for item in _records(PATIENT_MATERIALS)
    }

    relations = [
        item for item in _records(EXPLICIT_RELATIONS)
        if item["source_disease_slug"] == SLUG
    ]
    assert len(relations) == 5
    targets = {
        "checklist": {item["slug"] for item in _records(CHECKLISTS)},
        "trilha": {item["slug"] for item in _records(TRACKS)},
    }
    assert all(item["target_slug"] in targets[item["target_type"]] for item in relations)
    assert all(item["review_status"] == "revisado" for item in relations)
    assert all(item["confidence"] == "explicit" for item in relations)


def test_assistente_bloqueia_descompressao_sem_definir_coronarias():
    disease = _disease()
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers={
            "ap_faixa_etaria": "neonato",
            "ap_fenotipo": "paivs",
            "ap_instavel": False,
            "ap_fluxo_dependente": True,
            "ap_coronaria_definida": False,
            "ap_descompressao_planejada": True,
            "ap_mapcas_mapeadas": False,
            "ap_paliacao_obstrucao": False,
            "ap_isquemia": False,
            "ap_genetica_22q11": False,
        },
        context="emergencia",
    )

    assert result["risk"] == "emergencia"
    assert "ap-paivs-descompressao-sem-coronaria" in result["matched_rules"]
    rendered = json.dumps(result, ensure_ascii=False).casefold()
    assert "descompressão proposta" in rendered
    assert "mg/kg" not in rendered
    assert "prescrever" not in rendered
