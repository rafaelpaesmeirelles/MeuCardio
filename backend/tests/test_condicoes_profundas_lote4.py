"""Contrato de profundidade real do lote 4 de 27/08/2026 — oito fichas
especializadas já existentes (cardiogeriatria, gravidez, cardiooncologia e
cardiopediatria), empilhado sobre o main já com o lote 3 mesclado e revisado
(PR #551) e demais lotes/hubs Tudo com Tudo mesclados até 27/08/2026.

Este teste não mede só presença de campo: mede volume mínimo de conteúdo, para
que uma edição futura não possa esvaziar silenciosamente a ficha de volta a um
resumo de poucas linhas e ainda passar no gate. Nenhum slug novo foi criado em
nenhuma coleção — só os oito registros abaixo, já existentes, foram
aprofundados. A proteção dos lotes anteriores (lote 2/3, verbetes adultos,
AVC, hubs Tudo com Tudo já mesclados) é responsabilidade dos próprios arquivos
de teste desses lotes, já presentes em main — este arquivo não os duplica.
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
    "insuficiencia-cardiaca-no-idoso",
    "pre-eclampsia-e-risco-cardiovascular",
    "cardiomiopatia-periparto",
    "fibrilacao-atrial-no-idoso",
    "cardiotoxicidade-por-antraciclinas",
    "miocardite-por-inibidor-checkpoint",
    "tetralogia-de-fallot",
    "transposicao-das-grandes-arterias",
}

# Campos de lista com um mínimo de itens abaixo do qual a ficha volta a ser
# um resumo, não uma ficha profunda.
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
# diagnostic_approach pode ser texto corrido (str) ou objeto estruturado
# (dict, ex.: insuficiencia-cardiaca-no-idoso com sub-blocos "o que não muda"
# / "o que muda no idoso") — ambos os formatos são suportados pelo schema
# (SpecialtyDisease.diagnostic_approach é JSONB/dict) e pelo frontend
# (StructuredBlock). O mínimo de substância é medido pelo tamanho serializado.
MIN_DIAGNOSTIC_APPROACH_CHARS = 400


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


def _all_document_slugs() -> set[str]:
    return {p.stem for p in (REPOSITORY_ROOT / "content").rglob("*.md")}


def _all_patient_material_slugs() -> set[str]:
    items = json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    return {item["slug"] for item in items}


def test_lote_nao_criou_nem_removeu_slug_de_doenca():
    doencas = _load_doencas()
    assert LOTE_SLUGS <= set(doencas)
    # Nenhum contador global mudou por este lote: o total é o mesmo baseline
    # de main no momento em que este lote foi produzido (100 doenças — lote 3
    # já mesclado e revisado, mais os hubs Tudo com Tudo mesclados até aqui).
    assert len(doencas) == 100


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_tem_marcacao_editorial_correta(slug: str):
    doencas = _load_doencas()
    item = doencas[slug]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("review_note"), "ficha aprofundada precisa de review_note explicando o que mudou"
    assert item.get("source_refs") and len(item["source_refs"]) >= 2


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_atinge_profundidade_minima_e_nao_e_mero_resumo(slug: str):
    doencas = _load_doencas()
    item = doencas[slug]

    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list), f"{slug}.{field} deveria ser lista"
        assert len(value) >= minimum, (
            f"{slug}.{field} tem {len(value)} itens, mínimo exigido {minimum} "
            "— ficha regrediu para resumo"
        )

    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str), f"{slug}.{field} deveria ser texto corrido"
        assert len(value) >= minimum, (
            f"{slug}.{field} tem {len(value)} caracteres, mínimo exigido {minimum} "
            "— ficha regrediu para resumo"
        )

    diagnostic = item.get("diagnostic_approach")
    assert diagnostic, f"{slug}.diagnostic_approach vazio"
    assert isinstance(diagnostic, (str, dict)), f"{slug}.diagnostic_approach deveria ser texto ou objeto estruturado"
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS, (
        f"{slug}.diagnostic_approach tem {serialized_len} caracteres, mínimo exigido "
        f"{MIN_DIAGNOSTIC_APPROACH_CHARS} — ficha regrediu para resumo"
    )


@pytest.mark.parametrize("slug", sorted(LOTE_SLUGS))
def test_ficha_tem_assistente_deterministico_seguro(slug: str):
    doencas = _load_doencas()
    item = doencas[slug]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []
    assert len(questions) >= 3, f"{slug}: menos de 3 perguntas de assistente"
    assert len(rules) >= 3, f"{slug}: menos de 3 regras de assistente"

    q_errors, q_ids = validate_question_definitions(slug, questions)
    r_errors = validate_rule_definitions(slug, rules, q_ids)
    assert q_errors == []
    assert r_errors == []

    # Prioridade máxima (100) reservada a um cenário de emergência real —
    # toda ficha do lote define pelo menos uma regra de alta prioridade.
    assert any(rule.get("priority", 0) >= 70 for rule in rules), (
        f"{slug}: nenhuma regra de alta prioridade — assistente não escala risco"
    )


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
    doencas = _load_doencas()
    item = doencas[slug]
    documentos = _all_document_slugs()
    materiais = _all_patient_material_slugs()

    related = item.get("related_document_slugs") or []
    assert related, f"{slug}: sem nenhum vínculo direto a documento"
    for target in related:
        assert target in documentos, f"{slug}: related_document_slugs aponta para documento inexistente: {target}"

    patient_material = item.get("patient_material_slug")
    if patient_material:
        assert patient_material in materiais, (
            f"{slug}: patient_material_slug aponta para material inexistente: {patient_material}"
        )


def test_bloqueios_clinicos_da_revisao_foram_corrigidos():
    doencas = _load_doencas()

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
