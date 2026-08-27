"""Contrato de profundidade do lote 4 de 27/08/2026.

Protege substância clínica, regras determinísticas e vínculos Tudo com Tudo das
oito fichas do lote sem congelar o tamanho global da coleção de doenças.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.clinical_rule_engine import validate_question_definitions, validate_rule_definitions

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"

LOTE_SLUGS = {
    "insuficiencia-cardiaca-no-idoso",
    "pre-eclampsia-e-risco-cardiovascular",
    "cardiomiopatia-periparto",
    "fibrilacao-atrial-no-idoso",
    "cardiotoxicidade-por-antraciclinas",
    "miocardite-por-inibidor-checkpoint",
    "tetralogia-de-fallot",
    "transposicao-das-grandes-arterias",
}
MIN_LIST_ITEMS = {
    "presentation": 4,
    "differentials": 3,
    "tests": 4,
    "red_flags": 4,
    "ambulatory_flow": 3,
    "emergency_flow": 3,
    "monitoring": 4,
    "special_populations": 3,
}
MIN_TEXT_CHARS = {"epidemiology": 400, "treatment_summary": 800}
MIN_DIAGNOSTIC_APPROACH_CHARS = 400


def _items() -> list[dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    assert isinstance(items, list)
    return items


def _doencas() -> dict[str, dict]:
    return {item["slug"]: item for item in _items()}


def _document_slugs() -> set[str]:
    return {p.stem for p in (REPOSITORY_ROOT / "content").rglob("*.md")}


def _patient_material_slugs() -> set[str]:
    items = json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    return {item["slug"] for item in items}


def test_lote_preserva_slugs_e_corpus_nao_regride_abaixo_do_baseline():
    slugs = [item["slug"] for item in _items()]
    assert len(slugs) == len(set(slugs)), "slug de doença duplicado"
    assert LOTE_SLUGS <= set(slugs)
    assert len(slugs) >= 100


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_tem_marcacao_editorial_correta(slug: str):
    item = _doencas()[slug]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 2


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_atinge_profundidade_minima_e_nao_e_mero_resumo(slug: str):
    item = _doencas()[slug]
    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list)
        assert len(value) >= minimum, f"{slug}.{field} regrediu para resumo"
    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str)
        assert len(value) >= minimum, f"{slug}.{field} regrediu para resumo"
    diagnostic = item.get("diagnostic_approach")
    assert diagnostic and isinstance(diagnostic, (str, dict))
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_tem_assistente_deterministico_seguro(slug: str):
    item = _doencas()[slug]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []
    assert len(questions) >= 3
    assert len(rules) >= 3
    q_errors, q_ids = validate_question_definitions(slug, questions)
    r_errors = validate_rule_definitions(slug, rules, q_ids)
    assert q_errors == []
    assert r_errors == []
    assert any(rule.get("priority", 0) >= 70 for rule in rules)


def test_nenhuma_regra_do_lote_reproduz_escore_proprietario():
    doencas = _doencas()
    serialized = json.dumps([doencas[slug].get("assistant_rules", []) for slug in LOTE_SLUGS], ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_vinculos_tudo_com_tudo_resolvem_e_sao_apenas_documentos_e_material(slug: str):
    item = _doencas()[slug]
    documentos = _document_slugs()
    materiais = _patient_material_slugs()
    related = item.get("related_document_slugs") or []
    assert related
    for target in related:
        assert target in documentos, f"{slug}: documento inexistente: {target}"
    patient_material = item.get("patient_material_slug")
    if patient_material:
        assert patient_material in materiais


def test_bloqueios_clinicos_da_revisao_foram_corrigidos():
    doencas = _doencas()

    tof = doencas["tetralogia-de-fallot"]
    required = {q["id"] for q in tof["assistant_questions"] if q.get("required")}
    assert {"hypercyanotic_crisis_signs", "crisis_refractory", "pulse_lost"} <= required

    pe = doencas["pre-eclampsia-e-risco-cardiovascular"]
    assert "não confirma o diagnóstico isoladamente" in pe["diagnostic_approach"]
    assert "manejo expectante" in pe["treatment_summary"]
    fetal = next(r for r in pe["assistant_rules"] if r["id"] == "disfuncao-uteroplacentaria")
    assert any(c.get("field") == "new_hypertension_after_20w" for c in fetal["when"]["all"])

    anth = doencas["cardiotoxicidade-por-antraciclinas"]
    active = next(r for r in anth["assistant_rules"] if r["id"] == "emergencia-ic-sintomatica-feve-baixa")
    assert any(c.get("field") == "phase" and c.get("value") == "during" for c in active["when"]["all"])
    no_alarm = next(r for r in anth["assistant_rules"] if r["id"] == "sem-sinais-de-alarme")
    assert any(c.get("field") == "lvef_band" and c.get("value") == "ge50" for c in no_alarm["when"]["all"])

    tga = doencas["transposicao-das-grandes-arterias"]
    assert any(r["id"] == "falencia-vd-sistemico-sintomatica" for r in tga["assistant_rules"])
