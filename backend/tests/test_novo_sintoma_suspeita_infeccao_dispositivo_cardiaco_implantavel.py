"""Testes dedicados ao novo registro de triagem de sintomas:
`suspeita-infeccao-dispositivo-cardiaco-implantavel`.

Cobre: presença e forma do registro no manifesto canônico, validade de
perguntas/regras contra o motor de regras clínico, e os cenários clínicos
centrais especificados na missão (erosão com exposição, febre + sinais
locais, drenagem purulenta mesmo sem febre, eritema leve benigno recente ao
implante) — sem nunca escalar risco por engano via `red_flags` em achados
benignos, e sem nenhuma dose de fármaco em campo algum.
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

ROOT = Path(__file__).resolve().parents[2]
TRIAGE_PATH = ROOT / "triagem-sintomas/metadados.json"
SLUG = "suspeita-infeccao-dispositivo-cardiaco-implantavel"

DOSE_PATTERN = re.compile(
    r"\b\d+([.,]\d+)?\s*(mg|mcg|µg|g|ml|mL|UI|mEq)\b", re.IGNORECASE
)


def _load_items() -> list[dict]:
    data = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def _record() -> dict:
    items = _load_items()
    matches = [item for item in items if item.get("slug") == SLUG]
    assert len(matches) == 1, "registro deve existir exatamente uma vez no manifesto"
    return matches[0]


def _base_answers(record: dict) -> dict:
    answers = {}
    for question in record["questions"]:
        qtype = question["type"]
        if qtype == "boolean":
            answers[question["id"]] = False
        elif qtype == "number":
            answers[question["id"]] = 5
        elif qtype == "select":
            answers[question["id"]] = question["options"][0]["value"]
    return answers


def _run(record: dict, answers: dict) -> dict:
    return evaluate_rules(
        questions=record["questions"],
        rules=record["rules"],
        answers=answers,
        base_ambulatory_flow=record["ambulatory_flow"],
        base_emergency_flow=record["emergency_flow"],
        context="ambulatorio",
    )


def test_registro_existe_no_final_do_manifesto_com_slug_correto():
    items = _load_items()
    assert items[-1]["slug"] == SLUG, "novo registro deve ser adicionado ao final do array"


def test_registro_tem_campos_obrigatorios_do_schema():
    record = _record()
    for field in (
        "slug", "name", "aliases", "areas", "summary", "questions", "rules",
        "default_tests", "differentials", "red_flags", "ambulatory_flow",
        "emergency_flow", "tags", "source_refs", "source_urls",
        "review_status", "review_note", "version",
    ):
        assert field in record, f"campo ausente: {field}"

    assert record["name"]
    assert record["summary"]
    assert record["version"] == 1
    assert record["review_status"] == "pendente_revisao"
    assert record["review_note"]
    assert record["ambulatory_flow"]
    assert record["emergency_flow"]
    assert record["source_refs"]
    assert record["source_urls"]
    assert {"geral", "cardiogeriatria"} <= set(record["areas"])
    assert set(record["areas"]) <= {
        "geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez",
    }

    aliases = set(record["aliases"])
    assert "infecção no marca-passo" in aliases
    assert "ferida no local do gerador" in aliases
    assert "bolsa do CDI inflamada" in aliases


def test_perguntas_e_regras_sao_validas_no_motor_de_regras():
    record = _record()
    question_errors, question_ids = validate_question_definitions(
        record["slug"], record["questions"],
    )
    rule_errors = validate_rule_definitions(record["slug"], record["rules"], question_ids)
    assert question_errors == []
    assert rule_errors == []

    ids = [question["id"] for question in record["questions"]]
    assert len(ids) == len(set(ids))
    rule_ids = [rule["id"] for rule in record["rules"]]
    assert len(rule_ids) == len(set(rule_ids))

    for rule in record["rules"]:
        for group_name in ("all", "any", "none"):
            for condition in rule.get("when", {}).get(group_name, []):
                assert condition.get("op") != "includes", "operador 'includes' não existe no motor"


def test_perguntas_cobrem_os_sinais_clinicos_exigidos():
    ids = {question["id"] for question in _record()["questions"]}
    for expected in (
        "erosion_exposure",
        "purulent_drainage",
        "wound_dehiscence",
        "local_erythema_warmth",
        "days_since_procedure",
        "fever",
        "sepsis_signs",
        "positive_blood_cultures",
        "vegetation_on_lead_echo",
    ):
        assert expected in ids, f"pergunta esperada ausente: {expected}"


def test_erosao_com_exposicao_e_emergencia():
    record = _record()
    answers = _base_answers(record)
    answers["erosion_exposure"] = True
    result = _run(record, answers)
    assert result["risk"] == "emergencia"
    assert "erosao-exposicao" in result["matched_rules"]
    assert result["red_flags"]


def test_sepse_e_emergencia():
    record = _record()
    answers = _base_answers(record)
    answers["sepsis_signs"] = True
    result = _run(record, answers)
    assert result["risk"] == "emergencia"
    assert "sepse-sistemica" in result["matched_rules"]


def test_febre_com_sinais_locais_e_urgente():
    record = _record()
    answers = _base_answers(record)
    answers["fever"] = True
    answers["local_erythema_warmth"] = True
    result = _run(record, answers)
    assert result["risk"] == "urgente"
    assert "febre-com-sinais-locais" in result["matched_rules"]


def test_drenagem_purulenta_e_red_flag_mesmo_sem_febre():
    record = _record()
    answers = _base_answers(record)
    answers["purulent_drainage"] = True
    assert answers["fever"] is False
    result = _run(record, answers)
    assert result["risk"] == "urgente"
    assert "drenagem-purulenta" in result["matched_rules"]
    assert result["red_flags"], "drenagem purulenta deve sempre gerar red flag"


def test_eritema_leve_isolado_recente_ao_implante_e_risco_baixo_mas_nao_informativo():
    record = _record()
    answers = _base_answers(record)
    answers["local_erythema_warmth"] = True
    answers["days_since_procedure"] = 3
    result = _run(record, answers)
    assert "eritema-leve-pos-procedimento-recente" in result["matched_rules"]
    # Reação benigna: risco baixo, mas a regra não deve usar red_flags
    # (o motor escala automaticamente para "urgente" qualquer red flag).
    assert result["risk"] == "rotina"
    assert result["red_flags"] == []
    assert result["supporting"]


def test_eritema_isolado_fora_da_janela_pos_operatoria_e_mais_preocupante():
    record = _record()
    answers = _base_answers(record)
    answers["local_erythema_warmth"] = True
    answers["days_since_procedure"] = 30
    result = _run(record, answers)
    assert "eritema-tardio-sem-outros-sinais" in result["matched_rules"]
    assert result["risk"] == "prioritario"


def test_hematoma_isolado_sem_flogose_nao_e_tratado_como_infeccao():
    record = _record()
    answers = _base_answers(record)
    answers["hematoma_only"] = True
    result = _run(record, answers)
    assert "hematoma-sem-inflamacao" in result["matched_rules"]
    assert result["risk"] == "rotina"
    assert result["red_flags"] == []


def test_nenhum_sinal_positivo_e_informativo_sem_regra_disparada():
    record = _record()
    answers = _base_answers(record)
    result = _run(record, answers)
    assert result["risk"] == "informativo"
    assert result["matched_rules"] == []


def test_campo_obrigatorio_faltando_e_reportado():
    record = _record()
    answers = _base_answers(record)
    del answers["erosion_exposure"]
    result = _run(record, answers)
    assert "erosion_exposure" in result["missing_information"]


def test_nenhuma_dose_de_farmaco_em_nenhum_campo_de_texto():
    record = _record()
    textos: list[str] = [record["summary"], record["review_note"]]
    textos.extend(record["aliases"])
    textos.extend(record["default_tests"])
    textos.extend(record["differentials"])
    textos.extend(record["red_flags"])
    textos.extend(record["ambulatory_flow"])
    textos.extend(record["emergency_flow"])
    for question in record["questions"]:
        textos.append(question["label"])
    for rule in record["rules"]:
        for key in (
            "red_flags", "supporting", "opposing", "missing_information",
            "suggested_tests", "differentials", "ambulatory_flow",
            "emergency_flow", "messages",
        ):
            textos.extend(rule.get("add", {}).get(key, []))

    achados = [texto for texto in textos if DOSE_PATTERN.search(texto)]
    assert achados == [], f"possível dose de fármaco encontrada: {achados}"
