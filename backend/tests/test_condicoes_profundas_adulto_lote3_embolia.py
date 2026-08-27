"""Gates do lote isolado de embolia pulmonar aguda no adulto."""

from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata

from app.services.clinical_rule_engine import (
    evaluate_rules,
    validate_question_definitions,
    validate_rule_definitions,
)


ROOT = Path(__file__).resolve().parents[2]
DISEASES = ROOT / "doencas/metadados.json"
TRIAGE = ROOT / "triagem-sintomas/metadados.json"
PATIENT_MATERIALS = ROOT / "material-paciente/metadados.json"
EMERGENCY = ROOT / "emergencia/metadados.json"
CHECKLISTS = ROOT / "checklists/metadados.json"
TRACKS = ROOT / "trilhas/metadados.json"
EXPLICIT_RELATIONS = ROOT / "doencas/relacoes-explicitas.json"
SLUG = "embolia-pulmonar-aguda"


def _records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _disease() -> dict:
    matches = [item for item in _records(DISEASES) if item["slug"] == SLUG]
    assert len(matches) == 1
    return matches[0]


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _document_slugs() -> set[str]:
    slugs: set[str] = set()
    for path in (ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", text, re.MULTILINE)
        if match:
            slugs.add(match.group(1).strip())
    return slugs


def _safe_negative_answers() -> dict[str, object]:
    return {
        "pe_diagnostic_status": "not_current_suspicion",
        "pe_symptom_status": "not_applicable",
        "pe_refractory_shock_or_cardiac_arrest": "nao",
        "pe_persistent_hypotension_with_shock": "nao",
        "pe_transient_hypotension_without_hypoperfusion": "nao",
        "pe_normotensive_hypoperfusion": "nao",
        "severe_respiratory_compromise": "nao",
        "rv_dysfunction": "nao",
        "cardiac_biomarker_elevated": "nao",
        "active_major_bleeding": "nao",
        "anticoagulation_contraindicated": "nao",
        "pregnant_or_postpartum": "nao",
        "outpatient_barrier": "nao",
    }


def test_embolia_pulmonar_tem_profundidade_e_permanece_pendente():
    disease = _disease()

    assert disease["area"] == "geral"
    assert disease["category"] == "tromboembolismo"
    assert disease["completeness"] == "completo"
    assert disease["review_status"] == "pendente_revisao"
    assert disease.get("published") is not True
    assert disease["fonte_producao"] == "chatgpt"
    assert "revisão clínica humana" in disease["review_note"].casefold()
    assert len(disease["summary"]) >= 300
    assert len(disease["epidemiology"]) >= 300
    assert len(disease["treatment_summary"]) >= 700
    assert len(disease["diagnostic_approach"]) >= 4

    minimums = {
        "presentation": 6,
        "differentials": 10,
        "tests": 9,
        "red_flags": 6,
        "ambulatory_flow": 6,
        "emergency_flow": 7,
        "monitoring": 6,
        "special_populations": 8,
        "assistant_questions": 14,
        "assistant_rules": 16,
        "source_refs": 3,
        "source_urls": 6,
        "related_document_slugs": 2,
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


def test_embolia_pulmonar_resolve_referencias_e_vinculo_exato_de_triagem():
    disease = _disease()
    material_slugs = {item["slug"] for item in _records(PATIENT_MATERIALS)}

    assert set(disease["related_document_slugs"]) <= _document_slugs()
    assert disease["patient_material_slug"] in material_slugs

    names = {
        _normalize(name)
        for name in [disease["name"], *disease["aliases"]]
    }
    direct_triage = {
        triage["slug"]
        for triage in _records(TRIAGE)
        for differential in triage.get("differentials", [])
        if _normalize(str(differential)) in names
    }
    assert direct_triage == {
        "cianose",
        "dispneia",
        "dor-toracica",
        "sintomas-cardiovasculares-na-gravidez",
    }

    # Não promover proximidade temática a relação canônica neste lote.
    assert not any(
        key.startswith("related_") and key != "related_document_slugs"
        for key in disease
    )


def test_embolia_pulmonar_tem_quatro_arestas_externas_explicitas_e_resolvidas():
    relations = [
        item for item in _records(EXPLICIT_RELATIONS)
        if item["source_disease_slug"] == SLUG
    ]
    assert {
        (item["target_type"], item["target_slug"])
        for item in relations
    } == {
        ("protocolo_emergencia", "tromboembolismo-pulmonar"),
        ("checklist", "alta-pos-tromboembolismo-venoso-agudo"),
        ("checklist", "criterios-para-tratamento-ambulatorial-do-tep-de-baixo-risco"),
        (
            "trilha",
            "trilha-tromboembolismo-pulmonar-risco-intermediario-alto-e-terapia-guiada-pelo-risco",
        ),
    }
    assert all(item["confidence"] == "explicit" for item in relations)
    assert all(item["provenance_type"] == "editorial" for item in relations)

    targets = {
        "protocolo_emergencia": {item["slug"] for item in _records(EMERGENCY)},
        "checklist": {item["slug"] for item in _records(CHECKLISTS)},
        "trilha": {item["slug"] for item in _records(TRACKS)},
    }
    assert all(item["target_slug"] in targets[item["target_type"]] for item in relations)


def test_engine_nao_supertria_cenario_negativo_e_rejeita_campo_injetado():
    disease = _disease()
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=_safe_negative_answers(),
        context="ambulatorio",
    )
    assert result["risk"] == "informativo"
    assert result["matched_rules"] == []
    assert result["invalid_fields"] == []

    injected = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers={**_safe_negative_answers(), "autorizar_trombolise": True},
        context="emergencia",
    )
    assert injected["risk"] == "informativo"
    assert injected["matched_rules"] == []
    assert injected["invalid_fields"] == ["autorizar_trombolise"]


def test_engine_escalona_falencia_sem_prescrever_terapia_automaticamente():
    disease = _disease()
    answers = _safe_negative_answers()
    answers["pe_diagnostic_status"] = "confirmed"
    answers["pe_symptom_status"] = "symptomatic"
    answers["spesi_score"] = 0
    answers["pe_refractory_shock_or_cardiac_arrest"] = "sim"

    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=answers,
        context="emergencia",
    )

    assert result["risk"] == "emergencia"
    assert "ep-categoria-e2-parada-ou-choque-refratario" in result["matched_rules"]
    assert "ep-baixa-gravidade-nao-basta-para-alta" not in result["matched_rules"]
    messages = " ".join(map(str, result["messages"])).casefold()
    assert "decisão individualizada" in messages


def test_engine_c3_exige_conjunto_completo_e_nega_reperfusao_automatica():
    disease = _disease()
    answers = _safe_negative_answers()
    answers.update({
        "pe_diagnostic_status": "confirmed",
        "pe_symptom_status": "symptomatic",
        "spesi_score": 1,
        "rv_dysfunction": "sim",
        "cardiac_biomarker_elevated": "sim",
    })

    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=answers,
        context="emergencia",
    )

    assert result["risk"] == "urgente"
    assert result["matched_rules"] == [
        "ep-categoria-c-hospitalizacao",
        "ep-categoria-c3",
    ]
    messages = " ".join(map(str, result["messages"])).casefold()
    assert "não autoriza trombólise ou trombectomia de rotina" in messages


def test_engine_hospitaliza_categoria_c_mesmo_sem_vd_ou_biomarcador():
    disease = _disease()
    answers = _safe_negative_answers()
    answers.update({
        "pe_diagnostic_status": "confirmed",
        "pe_symptom_status": "symptomatic",
        "spesi_score": 1,
    })

    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=answers,
        context="ambulatorio",
    )

    assert result["risk"] == "urgente"
    assert "ep-categoria-c-hospitalizacao" in result["matched_rules"]
    assert "Hospitalizar" in " ".join(result["recommended_flow"])


def test_engine_baixo_risco_nao_casa_com_choque_ou_barreira_a_alta():
    disease = _disease()
    base = {
        **_safe_negative_answers(),
        "pe_diagnostic_status": "confirmed",
        "pe_symptom_status": "symptomatic",
        "spesi_score": 0,
    }

    low = evaluate_rules(
        questions=disease["assistant_questions"], rules=disease["assistant_rules"],
        answers=base, context="ambulatorio",
    )
    assert low["matched_rules"] == ["ep-baixa-gravidade-nao-basta-para-alta"]

    for field in ("pe_refractory_shock_or_cardiac_arrest", "outpatient_barrier"):
        result = evaluate_rules(
            questions=disease["assistant_questions"], rules=disease["assistant_rules"],
            answers={**base, field: "sim"}, context="ambulatorio",
        )
        assert "ep-baixa-gravidade-nao-basta-para-alta" not in result["matched_rules"]
        assert result["risk"] in {"urgente", "emergencia"}
