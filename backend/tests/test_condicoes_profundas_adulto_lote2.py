"""Gates do segundo lote profundo de doenças cardiovasculares do adulto."""

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
SLUG = "sindrome-coronariana-aguda"


def _records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


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


def test_sca_adulta_tem_profundidade_e_decisao_humana_preservada():
    diseases = {item["slug"]: item for item in _records(DISEASES)}
    disease = diseases[SLUG]

    assert disease["area"] == "geral"
    assert disease["category"] == "doenca_coronariana"
    assert disease["completeness"] == "completo"
    # O estado editorial pode evoluir de pendente para revisado sem alterar o
    # contrato clínico desta ficha. Pendências autorizadas são fiscalizadas
    # nominalmente pelo gate canônico de review_status.
    assert disease["review_status"] in {"pendente_revisao", "revisado"}
    assert disease["fonte_producao"] == "chatgpt"
    review_note = disease["review_note"].casefold()
    # A formulação editorial pode mudar, mas publicação clínica não pode perder
    # a decisão humana explícita. A redação atual registra revisão assistida e
    # autorização final pelo responsável médico.
    assert "publicação autorizada" in review_note
    assert "responsável médico" in review_note
    assert len(disease["summary"]) >= 180
    assert len(disease["epidemiology"]) >= 120
    assert len(disease["treatment_summary"]) >= 300
    assert len(disease["diagnostic_approach"]) >= 4

    minimums = {
        "presentation": 5,
        "differentials": 7,
        "tests": 3,
        "red_flags": 6,
        "ambulatory_flow": 4,
        "emergency_flow": 6,
        "monitoring": 6,
        "special_populations": 5,
        "assistant_questions": 6,
        "assistant_rules": 8,
        "source_refs": 1,
        "source_urls": 5,
        "related_document_slugs": 7,
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


def test_sca_resolve_relacoes_diretas_sem_promover_proximidade_tematica():
    disease = next(item for item in _records(DISEASES) if item["slug"] == SLUG)
    document_slugs = _document_slugs()
    material_slugs = {item["slug"] for item in _records(PATIENT_MATERIALS)}
    emergency_slugs = {item["slug"] for item in _records(EMERGENCY)}

    assert set(disease["related_document_slugs"]) <= document_slugs
    assert disease["patient_material_slug"] in material_slugs
    assert SLUG in emergency_slugs

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
    assert direct_triage == {"dor-toracica"}

    # Não existem campos canônicos que promovam medicamentos, exames, estudos,
    # evidências, calculadoras, casos ou trilhas a relação clínica direta.
    assert not any(key.startswith("related_") for key in disease if key not in {
        "related_document_slugs",
    })


def test_sca_assistente_nao_diagnostica_nao_dosa_e_nao_autoriza_alta():
    disease = next(item for item in _records(DISEASES) if item["slug"] == SLUG)
    rules = json.dumps(disease["assistant_rules"], ensure_ascii=False).casefold()

    assert "não interpreta o ecg" in rules
    assert "não sugerir fármaco ou dose" in rules
    assert "não autorizar baixa prioridade ou alta" in rules
    assert "dose de " not in rules
    assert "alta segura" not in rules


def test_sca_nao_supertria_sem_suspeita_aguda_explicita():
    disease = next(item for item in _records(DISEASES) if item["slug"] == SLUG)
    answers = {
        "current_or_recurrent_ischemic_symptoms": "nao",
        "hemodynamic_or_electrical_instability": "nao",
        "st_elevation_or_equivalent": "nao_aplicavel_sem_suspeita_aguda",
        "hs_troponin_pathway_completed": "nao_aplicavel_sem_suspeita_aguda",
        "lethal_alternative_red_flags": "nao",
        "bleeding_or_anticoagulation_risk_known": "nao_aplicavel_sem_suspeita_aguda",
    }

    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=answers,
        context="ambulatorio",
    )

    assert result["risk"] == "informativo"
    assert result["matched_rules"] == []


def test_sca_escalona_algoritmo_de_troponina_incompleto_apenas_quando_agudo():
    disease = next(item for item in _records(DISEASES) if item["slug"] == SLUG)
    answers = {
        "current_or_recurrent_ischemic_symptoms": "nao",
        "hemodynamic_or_electrical_instability": "nao",
        "st_elevation_or_equivalent": "nao",
        "hs_troponin_pathway_completed": "incompleto_suspeita_aguda",
        "lethal_alternative_red_flags": "nao",
        "bleeding_or_anticoagulation_risk_known": "sim",
    }

    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=answers,
        context="emergencia",
    )

    assert result["risk"] == "urgente"
    assert result["matched_rules"] == ["sca-troponina-seriada-incompleta"]
