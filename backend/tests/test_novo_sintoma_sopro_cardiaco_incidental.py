"""Contrato do registro NOVO de triagem de sintomas "sopro-cardiaco-incidental"
(triagem-sintomas/metadados.json), criado em 29/08/2026 — sopro cardíaco
identificado ao exame como achado incidental em paciente assintomático,
cobrindo adulto e criança.

Fontes: content/Geral/fluxograma-sopro-cardiaco-incidental-no-adulto-assintomatico.md
e content/Cardiopatias_congênitas/fluxograma-sopro-cardiaco-na-crianca-inocente-versus-patologico.md,
enriquecido por content/Cardiologia_pediátrica/sopros-cardiacos-na-infancia-
diferenciacao-entre-sopro-inocente-e-sopro-patologico.md. Os 7 PMIDs citados
(33332150, 34453165, 9032164, 22010618, 35289571, 40466724, 30761241) foram
conferidos nesta sessão via PubMed E-utilities (esummary): título, periódico,
ano e primeiro autor batem com o que está em source_refs.

Nota sobre review_status: este registro é publicado como "pendente_revisao"
(ainda sem aval médico independente), o que faz
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
falhar com 1 item — comportamento esperado e documentado nesse próprio
arquivo (a allowlist PENDENTES_LOTES_TUDO_COM_TUDO só isenta registros já
"revisado", então um "pendente_revisao" novo sempre aparece em `invalidos`
até receber aval editorial explícito).

Nota sobre risco de colisão: este registro foi adicionado ao FINAL do array
JSON de triagem-sintomas/metadados.json. Outros agentes trabalham em
paralelo no mesmo arquivo em branches distintas — ver corpo da PR.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.clinical_rule_engine import (
    evaluate_rules,
    validate_question_definitions,
    validate_rule_definitions,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_PATH = REPOSITORY_ROOT / "triagem-sintomas/metadados.json"
SLUG = "sopro-cardiaco-incidental"

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
    r"\d+[\.,]?\d*\s*j/kg",
)

VERIFIED_PMIDS = {
    "33332150", "34453165", "9032164", "22010618", "35289571", "40466724", "30761241",
}


def _load_all() -> list[dict]:
    data = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _record() -> dict:
    items = [item for item in _load_all() if item.get("slug") == SLUG]
    assert len(items) == 1, "slug deve existir exatamente uma vez no manifesto"
    return items[0]


def test_registro_existe_e_esta_no_final_do_arquivo():
    items = _load_all()
    slugs = [item["slug"] for item in items]
    assert SLUG in slugs
    assert len(slugs) == len(set(slugs)), "nenhum slug duplicado no manifesto inteiro"
    # Minimiza risco de conflito de merge: o registro novo fica ao final do array.
    assert slugs[-1] == SLUG


def test_campos_basicos_e_marcacao_editorial():
    item = _record()
    assert item["name"]
    assert item["summary"]
    assert set(item["aliases"]) >= {"sopro no coração", "sopro cardíaco", "achado de ausculta"}
    assert set(item["areas"]) == {"geral", "cardiopediatria"}
    assert item["review_status"] == "pendente_revisao"
    assert item["review_note"]
    assert item["version"] == 1


def test_perguntas_e_regras_sao_validas_pelo_motor_de_regras():
    item = _record()
    q_errors, q_ids = validate_question_definitions(SLUG, item["questions"])
    r_errors = validate_rule_definitions(SLUG, item["rules"], q_ids)
    assert q_errors == []
    assert r_errors == []


def test_perguntas_usam_label_nao_text_e_nao_repetem_id():
    item = _record()
    ids = [q["id"] for q in item["questions"]]
    assert len(ids) == len(set(ids))
    for question in item["questions"]:
        assert "label" in question
        assert "text" not in question
        if question["type"] in {"select", "multiselect"}:
            values = [opt["value"] for opt in question["options"]]
            assert len(values) == len(set(values))
        if question["type"] == "number":
            assert "min" in question and "max" in question and "unit" in question


def test_regras_usam_operadores_e_campos_de_adicao_permitidos():
    item = _record()
    ids = [r["id"] for r in item["rules"]]
    assert len(ids) == len(set(ids))
    allowed_ops = {
        "eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte",
        "truthy", "falsy", "contains", "exists", "missing",
    }
    allowed_add_keys = {
        "risk", "red_flags", "supporting", "opposing", "missing_information",
        "suggested_tests", "differentials", "ambulatory_flow", "emergency_flow", "messages",
    }
    for rule in item["rules"]:
        assert 0 <= rule["priority"] <= 100
        for group_name in ("all", "any", "none"):
            for condition in rule.get("when", {}).get(group_name, []):
                assert condition.get("op", "eq") in allowed_ops
                assert "includes" != condition.get("op")
        bad_keys = set(rule.get("add", {}).keys()) - allowed_add_keys
        assert not bad_keys, f"regra {rule['id']} usa chaves não permitidas: {bad_keys}"
        risk = rule.get("add", {}).get("risk")
        if risk is not None:
            assert risk in {"informativo", "rotina", "prioritario", "urgente", "emergencia"}


def test_campos_obrigatorios_no_topo_do_registro():
    item = _record()
    assert item["ambulatory_flow"]
    assert item["emergency_flow"]
    assert item["source_refs"]
    assert item["red_flags"]
    assert item["differentials"]
    assert item["default_tests"]


def test_fontes_citadas_foram_verificadas_via_pubmed_nesta_sessao():
    item = _record()
    serialized = " ".join(item["source_refs"])
    cited_pmids = set(re.findall(r"PMID:\s*(\d+)", serialized))
    assert cited_pmids == VERIFIED_PMIDS
    assert cited_pmids <= VERIFIED_PMIDS


def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    item = _record()
    serialized = json.dumps(item, ensure_ascii=False)
    for pattern in DOSE_PATTERNS:
        matches = re.findall(pattern, serialized)
        assert matches == [], f"padrão de dose encontrado ({pattern}): {matches}"


def _evaluate(item: dict, answers: dict) -> dict:
    return evaluate_rules(
        questions=item["questions"],
        rules=item["rules"],
        answers=answers,
        base_tests=item["default_tests"],
        base_differentials=item["differentials"],
        base_ambulatory_flow=item["ambulatory_flow"],
        base_emergency_flow=item["emergency_flow"],
    )


def test_sopro_diastolico_e_sempre_red_flag():
    item = _record()
    result = _evaluate(item, {
        "age": 45, "unstable": False, "murmur_timing": "diastolic",
        "murmur_grade": 1, "associated_symptoms": ["none"],
    })
    assert result["invalid_fields"] == []
    assert result["risk"] in {"urgente", "emergencia"}
    assert result["red_flags"]
    assert "sopro-diastolico" in result["matched_rules"]


def test_sopro_sistolico_intenso_ou_sintomatico_e_red_flag():
    item = _record()
    result = _evaluate(item, {
        "age": 30, "unstable": False, "murmur_timing": "systolic",
        "murmur_grade": 4, "associated_symptoms": ["none"],
    })
    assert result["risk"] in {"urgente", "emergencia"}
    assert "sopro-sistolico-alerta" in result["matched_rules"]

    result_sintoma = _evaluate(item, {
        "age": 30, "unstable": False, "murmur_timing": "systolic",
        "murmur_grade": 1, "associated_symptoms": ["dyspnea"],
    })
    assert result_sintoma["risk"] in {"urgente", "emergencia"}
    assert "sopro-sistolico-alerta" in result_sintoma["matched_rules"]


def test_lactente_com_falha_de_crescimento_ou_cianose_e_red_flag_grave():
    item = _record()
    result = _evaluate(item, {
        "age": 0.5, "unstable": False, "murmur_timing": "systolic",
        "murmur_grade": 2, "associated_symptoms": ["poor_growth_feeding"],
    })
    assert result["risk"] == "emergencia"
    assert "lactente-sinais-graves" in result["matched_rules"]

    result_cianose = _evaluate(item, {
        "age": 0.5, "unstable": False, "murmur_timing": "systolic",
        "murmur_grade": 2, "associated_symptoms": ["cyanosis"],
    })
    assert result_cianose["risk"] == "emergencia"
    assert "lactente-sinais-graves" in result_cianose["matched_rules"]


def test_sopro_inocente_classico_e_baixo_risco_sem_red_flags():
    item = _record()
    result = _evaluate(item, {
        "age": 6, "neonate": False, "unstable": False,
        "murmur_timing": "systolic", "murmur_grade": 2,
        "murmur_alarm_features": [],
        "positional_maneuver": "decreases_standing_or_louder_supine",
        "associated_symptoms": ["none"],
        "febrile_endocarditis_context": False,
        "family_history_sudden_death_cardiomyopathy": False,
        "known_structural_risk": False,
    })
    assert result["risk"] in {"informativo", "rotina"}
    assert result["red_flags"] == []
    assert "sopro-inocente-classico" in result["matched_rules"]


def test_paciente_instavel_e_sempre_emergencia():
    item = _record()
    result = _evaluate(item, {
        "age": 3, "unstable": True, "murmur_timing": "systolic",
        "murmur_grade": 1, "associated_symptoms": ["none"],
    })
    assert result["risk"] == "emergencia"
    assert result["recommended_flow"] == item["emergency_flow"]


def test_recem_nascido_com_sopro_e_urgente():
    item = _record()
    result = _evaluate(item, {
        "age": 0, "neonate": True, "unstable": False,
        "murmur_timing": "systolic", "murmur_grade": 1,
        "associated_symptoms": ["none"],
    })
    assert result["risk"] in {"urgente", "emergencia"}
    assert "recem-nascido" in result["matched_rules"]
