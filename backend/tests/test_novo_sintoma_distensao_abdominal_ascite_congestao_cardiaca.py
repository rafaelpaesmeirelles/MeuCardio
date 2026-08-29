"""Contrato do registro NOVO de Triagem de Sintomas
"distensao-abdominal-ascite-congestao-cardiaca" (áreas geral e
cardiogeriatria), criado em 29/08/2026 em triagem-sintomas/metadados.json —
NÃO confundir com o Guia de Doenças (doencas/metadados.json): a Triagem de
Sintomas usa manifesto e schema próprios (questions/rules com
validate_question_definitions/validate_rule_definitions e evaluate_rules do
clinical_rule_engine).

Fontes-base lidas por completo antes da montagem das perguntas e regras:
- hepatopatia-congestiva-cronica-na-insuficiencia-cardiaca-direita-de-longa-data-reconhecimento-e-prognostico.md
- insuficiencia-cardiaca-direita-isolada-por-doenca-tricuspide-fisiopatologia-da-congestao-e-manejo-clinico.md
- falencia-aguda-do-ventriculo-direito-na-uco-pre-carga-pos-carga-e-intubacao.md
- fluxograma-edema-bilateral-membros-inferiores-diferencial-cardiaco.md

Os 5 PMIDs citados em source_refs (29650544, 19215833, 42154163, 23939641,
26995592) foram verificados individualmente via NCBI E-utilities (esummary)
em 29/08/2026 (título, autoria, journal, volume, páginas e DOI), sem
divergência.

Nota sobre o gate de review_status: este registro é conteúdo novo, ainda
"pendente_revisao" — por isso
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug, comportamento esperado e documentado (ver review_note
do próprio registro). Diferente do padrão usado na PR #698 para
doencas/metadados.json, nenhuma entrada foi adicionada a
PENDENTES_LOTES_TUDO_COM_TUDO nesse teste: não existe, para
triagem-sintomas, um segundo teste que reaproveite essa allowlist para
registros pendentes (ao contrário de test_disease_fragments_canonical.py
para doenças), então a entrada não teria efeito em nenhum gate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest
from fastapi import HTTPException

from app.api.specialty_guides import TriagePayload, assess_triage
from app.services.clinical_rule_engine import (
    ALLOWED_ADDITION_FIELDS,
    RISK_ORDER,
    evaluate_rules,
    validate_answers,
    validate_question_definitions,
    validate_rule_definitions,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRIAGE_PATH = REPOSITORY_ROOT / "triagem-sintomas/metadados.json"
SLUG = "distensao-abdominal-ascite-congestao-cardiaca"

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
    r"\d+[\.,]?\d*\s*ui\b",
)


def _load_item() -> dict:
    data = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    matches = [item for item in data if item.get("slug") == SLUG]
    assert len(matches) == 1, "registro deve existir exatamente uma vez no manifesto"
    return matches[0]


def _question_ids(item: dict) -> set[str]:
    return {question["id"] for question in item["questions"]}


def test_registro_existe_no_final_do_manifesto_e_tem_slug_unico():
    data = json.loads(TRIAGE_PATH.read_text(encoding="utf-8"))
    slugs = [item["slug"] for item in data]
    assert slugs.count(SLUG) == 1
    assert slugs[-1] == SLUG, "registro deve estar ao final do array (risco de colisão com outros agentes)"
    assert len(slugs) == len(set(slugs))


def test_campos_obrigatorios_do_schema_presentes():
    item = _load_item()
    for campo in (
        "slug", "name", "aliases", "areas", "summary", "questions", "rules",
        "default_tests", "differentials", "red_flags", "ambulatory_flow",
        "emergency_flow", "tags", "source_refs", "source_urls",
        "review_status", "review_note", "version",
    ):
        assert campo in item, f"campo ausente: {campo}"
    assert item["review_status"] == "pendente_revisao"
    assert item["review_note"]
    assert item["version"] == 1
    assert item["ambulatory_flow"]
    assert item["emergency_flow"]
    assert item["source_refs"]


def test_areas_incluem_geral_e_cardiogeriatria_e_sao_validas():
    item = _load_item()
    areas_validas = {"geral", "cardiopediatria", "cardiogeriatria", "cardiooncologia", "gravidez"}
    assert set(item["areas"]) <= areas_validas
    assert {"geral", "cardiogeriatria"} <= set(item["areas"])


def test_aliases_cobrem_os_termos_leigos_esperados():
    item = _load_item()
    aliases = set(item["aliases"])
    for termo in ("barriga inchada", "ascite", "distensão abdominal", "abdômen inchado"):
        assert termo in aliases


def test_source_urls_sao_https_validas():
    item = _load_item()
    assert item["source_urls"]
    for url in item["source_urls"]:
        parsed = urlparse(url)
        assert parsed.scheme in {"http", "https"}
        assert parsed.netloc


def test_questions_e_rules_passam_no_validador_do_motor_clinico():
    item = _load_item()
    question_errors, question_ids = validate_question_definitions(SLUG, item["questions"])
    assert question_errors == []
    rule_errors = validate_rule_definitions(SLUG, item["rules"], question_ids)
    assert rule_errors == []


def test_perguntas_cobrem_historia_cardiaca_e_diferenciais_nao_cardiacos():
    item = _load_item()
    ids = _question_ids(item)
    # História de IC/doença tricúspide, edema, ganho de peso, dispneia, hepatomegalia, jugular
    for campo in (
        "known_hf_or_tricuspid_disease", "lower_limb_edema", "rapid_weight_gain",
        "acute_dyspnea_hypoxia", "associated_dyspnea_on_exertion",
        "painful_hepatomegaly", "jugular_distension_known",
    ):
        assert campo in ids
    # Agudo vs. crônico progressivo
    assert "onset_pattern" in ids
    onset = next(q for q in item["questions"] if q["id"] == "onset_pattern")
    assert onset["type"] == "select"
    assert {opt["value"] for opt in onset["options"]} == {"agudo", "cronico_progressivo"}
    # Causas não cardíacas de ascite
    for campo in ("known_liver_disease", "alcohol_use", "oncologic_alarm_weight_loss"):
        assert campo in ids


def test_pergunta_numerica_tem_min_max_e_unit():
    item = _load_item()
    numero = next(q for q in item["questions"] if q["type"] == "number")
    assert numero["min"] == 0
    assert numero["max"] > numero["min"]
    assert numero["unit"]


def test_nenhum_operador_includes_e_todos_operadores_sao_permitidos():
    item = _load_item()
    permitidos = {
        "eq", "neq", "in", "not_in", "gt", "gte", "lt", "lte",
        "truthy", "falsy", "contains", "exists", "missing",
    }
    for rule in item["rules"]:
        for grupo in ("all", "any", "none"):
            for condicao in rule["when"].get(grupo, []):
                op = condicao.get("op", "eq")
                assert op != "includes"
                assert op in permitidos


def test_regras_so_usam_campos_de_adicao_permitidos_e_riscos_validos():
    item = _load_item()
    for rule in item["rules"]:
        assert set(rule["add"]) <= ALLOWED_ADDITION_FIELDS
        risco = rule["add"].get("risk")
        if risco is not None:
            assert risco in RISK_ORDER


def test_nenhuma_dose_de_farmaco_em_campo_de_texto():
    item = _load_item()
    texto = json.dumps(item, ensure_ascii=False).casefold()
    for pattern in DOSE_PATTERNS:
        assert not re.search(pattern, texto), f"possível dose encontrada com o padrão {pattern}"


# --- Cenários clínicos via evaluate_rules -----------------------------------

def _evaluate(item: dict, answers: dict, context: str = "ambulatorio") -> dict:
    return evaluate_rules(
        questions=item["questions"],
        rules=item["rules"],
        answers=answers,
        base_tests=item["default_tests"],
        base_differentials=item["differentials"],
        base_ambulatory_flow=item["ambulatory_flow"],
        base_emergency_flow=item["emergency_flow"],
        context=context,
    )


def test_padrao_classico_de_congestao_direita_e_prioritario():
    item = _load_item()
    resultado = _evaluate(item, {
        "fever_or_severe_abdominal_pain": False,
        "acute_dyspnea_hypoxia": False,
        "hemodynamic_instability": False,
        "rapid_weight_gain": False,
        "known_hf_or_tricuspid_disease": True,
        "lower_limb_edema": True,
        "associated_dyspnea_on_exertion": True,
        "onset_pattern": "cronico_progressivo",
        "known_liver_disease": False,
        "oncologic_alarm_weight_loss": False,
    })
    assert resultado["risk"] == "prioritario"
    assert "congestao_direita_classica_descompensada" in resultado["matched_rules"]
    assert resultado["recommended_flow"] == resultado["ambulatory_flow"]


def test_dispneia_aguda_ou_instabilidade_hemodinamica_e_emergencia():
    item = _load_item()
    resultado = _evaluate(item, {
        "fever_or_severe_abdominal_pain": False,
        "acute_dyspnea_hypoxia": True,
        "hemodynamic_instability": False,
        "rapid_weight_gain": False,
        "known_hf_or_tricuspid_disease": True,
        "onset_pattern": "agudo",
        "known_liver_disease": False,
        "oncologic_alarm_weight_loss": False,
    })
    assert resultado["risk"] == "emergencia"
    assert "emergencia_instabilidade_hemodinamica_ou_hipoxia" in resultado["matched_rules"]
    assert resultado["recommended_flow"] == resultado["emergency_flow"]


def test_ganho_de_peso_rapido_isolado_ja_e_red_flag_urgente():
    item = _load_item()
    resultado = _evaluate(item, {
        "fever_or_severe_abdominal_pain": False,
        "acute_dyspnea_hypoxia": False,
        "hemodynamic_instability": False,
        "rapid_weight_gain": True,
        "known_hf_or_tricuspid_disease": False,
        "onset_pattern": "agudo",
        "known_liver_disease": False,
        "oncologic_alarm_weight_loss": False,
    })
    assert resultado["risk"] in {"urgente", "emergencia"}
    assert "ganho_peso_rapido_descompensacao" in resultado["matched_rules"]


def test_hepatopatia_primaria_sem_contexto_cardiaco_e_diferencial_hepatologico():
    item = _load_item()
    resultado = _evaluate(item, {
        "fever_or_severe_abdominal_pain": False,
        "acute_dyspnea_hypoxia": False,
        "hemodynamic_instability": False,
        "rapid_weight_gain": False,
        "known_hf_or_tricuspid_disease": False,
        "onset_pattern": "cronico_progressivo",
        "known_liver_disease": True,
        "alcohol_use": True,
        "oncologic_alarm_weight_loss": False,
    })
    assert resultado["risk"] == "informativo"
    assert "hepatopatia_primaria_sem_contexto_cardiaco" in resultado["matched_rules"]
    assert "alcool_uso_risco_diferencial" in resultado["matched_rules"]
    assert any("hepát" in d.casefold() or "hepat" in d.casefold() for d in resultado["differentials"])


def test_febre_ou_dor_abdominal_importante_sinaliza_peritonite_em_emergencia():
    item = _load_item()
    resultado = _evaluate(item, {
        "fever_or_severe_abdominal_pain": True,
        "acute_dyspnea_hypoxia": False,
        "hemodynamic_instability": False,
        "rapid_weight_gain": False,
        "known_hf_or_tricuspid_disease": False,
        "onset_pattern": "agudo",
        "known_liver_disease": True,
        "oncologic_alarm_weight_loss": False,
    }, context="emergencia")
    assert resultado["risk"] == "emergencia"
    assert "emergencia_infeccao_ou_peritonite" in resultado["matched_rules"]


def test_perda_de_peso_com_alarme_oncologico_e_urgente_com_diferencial_neoplasico():
    item = _load_item()
    resultado = _evaluate(item, {
        "fever_or_severe_abdominal_pain": False,
        "acute_dyspnea_hypoxia": False,
        "hemodynamic_instability": False,
        "rapid_weight_gain": False,
        "known_hf_or_tricuspid_disease": False,
        "onset_pattern": "cronico_progressivo",
        "known_liver_disease": False,
        "oncologic_alarm_weight_loss": True,
    })
    assert resultado["risk"] in {"urgente", "emergencia"}
    assert "sinal_alarme_oncologico" in resultado["matched_rules"]
    assert any("neoplás" in d.casefold() for d in resultado["differentials"])


def test_campos_obrigatorios_ausentes_sao_reportados_sem_quebrar_avaliacao():
    item = _load_item()
    missing, invalid = validate_answers(item["questions"], {})
    assert invalid == []
    obrigatorios = {q["id"] for q in item["questions"] if q.get("required")}
    assert set(missing) == obrigatorios


# --- Integração com o endpoint de avaliação ---------------------------------

class _Query:
    def __init__(self, item):
        self._item = item

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._item


class _Session:
    def __init__(self, item):
        self._item = item

    def query(self, *_args, **_kwargs):
        return _Query(self._item)


def _published_guide() -> SimpleNamespace:
    item = _load_item()
    return SimpleNamespace(
        slug=item["slug"],
        name=item["name"],
        version=item["version"],
        questions=item["questions"],
        rules=item["rules"],
        default_tests=item["default_tests"],
        differentials=item["differentials"],
        ambulatory_flow=item["ambulatory_flow"],
        emergency_flow=item["emergency_flow"],
        source_refs=item["source_refs"],
        source_urls=item["source_urls"],
    )


def test_endpoint_assess_triage_rejeita_resposta_obrigatoria_ausente():
    with pytest.raises(HTTPException) as erro:
        assess_triage(
            SLUG,
            TriagePayload(context="ambulatorio", answers={}),
            db=_Session(_published_guide()),
        )
    assert erro.value.status_code == 422
    assert erro.value.detail["erro"] == "Respostas obrigatórias ausentes."


def test_endpoint_assess_triage_retorna_emergencia_para_dispneia_aguda():
    resultado = assess_triage(
        SLUG,
        TriagePayload(context="ambulatorio", answers={
            "fever_or_severe_abdominal_pain": False,
            "acute_dyspnea_hypoxia": True,
            "hemodynamic_instability": False,
            "rapid_weight_gain": False,
            "known_hf_or_tricuspid_disease": True,
            "onset_pattern": "agudo",
            "known_liver_disease": False,
            "oncologic_alarm_weight_loss": False,
        }),
        db=_Session(_published_guide()),
    )
    assert resultado["risk"] == "emergencia"
    assert resultado["symptom"]["slug"] == SLUG
    assert resultado["incomplete"] is False
