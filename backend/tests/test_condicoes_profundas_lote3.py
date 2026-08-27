"""Contrato de profundidade real do lote 3 de 27/08/2026 — oito fichas
especializadas já existentes (cardiopediatria, cardiogeriatria, cardiooncologia
e gravidez), empilhado sobre o lote 2 (PR #542).

O contrato protege profundidade e integridade dos verbetes do lote sem congelar
o tamanho global da coleção, que cresce continuamente pelo Tudo com Tudo.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.clinical_rule_engine import (
    validate_question_definitions,
    validate_rule_definitions,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"

LOTE_SLUGS = {
    "delirium-cardiogeriatria",
    "risco-quedas-cardiogeriatria",
    "toxicidade-cardiovascular-car-t",
    "fluoropirimidinas-isquemia",
    "sindrome-coronariana-gravidez",
    "tromboembolismo-gravidez",
    "persistencia-canal-arterial",
    "anomalia-ebstein",
}

LOTE2_SLUGS = {
    "canalopatias-pediatricas",
    "cardiomiopatias-pediatricas",
    "anticoagulacao-idoso",
    "amiloidose-cardiaca-idoso",
    "cardiotoxicidade-anti-her2",
    "doenca-pericardica-oncologia",
    "hipertensao-cronica-gravidez",
    "valvopatias-na-gravidez",
}

GERAL_PROTEGIDOS = {
    "acidente-vascular-cerebral-agudo",
    "hipertensao-arterial-sistemica",
    "fibrilacao-atrial",
    "insuficiencia-cardiaca",
    "sindrome-coronariana-cronica",
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
MIN_TEXT_CHARS = {
    "epidemiology": 400,
    "treatment_summary": 800,
}
MIN_DIAGNOSTIC_APPROACH_CHARS = 400


def _load_doenca_items() -> list[dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    assert isinstance(items, list)
    return items


def _load_doencas() -> dict[str, dict]:
    return {item["slug"]: item for item in _load_doenca_items()}


def _all_document_slugs() -> set[str]:
    return {p.stem for p in (REPOSITORY_ROOT / "content").rglob("*.md")}


def _all_patient_material_slugs() -> set[str]:
    items = json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    return {item["slug"] for item in items}


def test_lote_preserva_slugs_e_corpus_nao_regride_abaixo_do_baseline():
    items = _load_doenca_items()
    slugs = [item["slug"] for item in items]
    assert len(slugs) == len(set(slugs)), "slug de doença duplicado"
    assert LOTE_SLUGS <= set(slugs)
    assert len(slugs) >= 100


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_tem_marcacao_editorial_correta(slug: str):
    item = _load_doencas()[slug]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 2


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_atinge_profundidade_minima_e_nao_e_mero_resumo(slug: str):
    item = _load_doencas()[slug]
    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list), f"{slug}.{field} deveria ser lista"
        assert len(value) >= minimum, f"{slug}.{field} regrediu para resumo"
    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str), f"{slug}.{field} deveria ser texto corrido"
        assert len(value) >= minimum, f"{slug}.{field} regrediu para resumo"
    diagnostic = item.get("diagnostic_approach")
    assert diagnostic
    assert isinstance(diagnostic, (str, dict))
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_tem_assistente_deterministico_seguro(slug: str):
    item = _load_doencas()[slug]
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
    doencas = _load_doencas()
    serialized = json.dumps(
        [doencas[slug].get("assistant_rules", []) for slug in LOTE_SLUGS],
        ensure_ascii=False,
    ).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_vinculos_tudo_com_tudo_resolvem_e_sao_apenas_documentos_e_material(slug: str):
    item = _load_doencas()[slug]
    documentos = _all_document_slugs()
    materiais = _all_patient_material_slugs()
    related = item.get("related_document_slugs") or []
    assert related
    for target in related:
        assert target in documentos, f"{slug}: documento inexistente: {target}"
    patient_material = item.get("patient_material_slug")
    if patient_material:
        assert patient_material in materiais


def test_lote_nao_alterou_o_lote2_do_pr542():
    doencas = _load_doencas()
    assert LOTE2_SLUGS <= set(doencas)
    for slug in LOTE2_SLUGS:
        item = doencas[slug]
        assert item.get("fonte_producao") == "claude"
        assert item.get("review_status") == "revisado"
        assert item.get("completeness") == "completo"
        assert item.get("version") == 2, f"{slug}: versão mudou"
    assert LOTE2_SLUGS.isdisjoint(LOTE_SLUGS)


def test_lote_nao_alterou_os_quatro_verbetes_adultos_do_pr539_nem_o_avc_do_pr538():
    doencas = _load_doencas()
    for slug in GERAL_PROTEGIDOS:
        assert doencas[slug]["area"] == "geral"
        assert doencas[slug]["fonte_producao"] == "chatgpt"
    assert GERAL_PROTEGIDOS.isdisjoint(LOTE_SLUGS)
    assert GERAL_PROTEGIDOS.isdisjoint(LOTE2_SLUGS)
