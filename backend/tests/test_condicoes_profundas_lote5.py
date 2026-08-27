"""Contrato de profundidade real do lote 5 de 27/08/2026 — oito fichas
especializadas já existentes (cardiopediatria, cardiogeriatria, cardiooncologia
e gravidez), produzido a partir do main atual (já com os lotes 1-4 e os hubs
Tudo com Tudo anteriores mesclados e revisados).

Este teste não mede só presença de campo: mede volume mínimo de conteúdo, para
que uma edição futura não possa esvaziar silenciosamente a ficha de volta a um
resumo de poucas linhas e ainda passar no gate. Nenhum slug novo foi criado em
nenhuma coleção — só os oito registros abaixo, já existentes, foram
aprofundados. A proteção dos lotes anteriores é responsabilidade dos próprios
arquivos de teste desses lotes, já presentes em main — este arquivo não os
duplica.
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
    "sincope-pediatrica",
    "comunicacao-interventricular",
    "coarctacao-da-aorta",
    "fragilidade-pre-procedimento-cardiovascular",
    "hipertensao-por-inibidor-vegf",
    "efeitos-cardiovasculares-tardios-radioterapia",
    "protese-mecanica-na-gravidez",
    "aortopatia-na-gravidez",
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
# (dict) — ambos os formatos são suportados pelo schema (SpecialtyDisease.
# diagnostic_approach é JSONB/dict) e pelo frontend (StructuredBlock). O
# mínimo de substância é medido pelo tamanho serializado.
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
    # de main no momento em que este lote foi produzido (100 doenças).
    assert len(doencas) == 101


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

    sincope = doencas["sincope-pediatrica"]
    age = next(q for q in sincope["assistant_questions"] if q["id"] == "age_months")
    assert age["min"] == 0 and age["max"] == 71
    breath = next(r for r in sincope["assistant_rules"] if r["id"] == "espasmo_do_choro_lactente")
    assert {"field": "age_months", "op": "gte", "value": 6} in breath["when"]["all"]

    civ = doencas["comunicacao-interventricular"]
    hf = next(r for r in civ["assistant_rules"] if r["id"] == "civ_lactente_sinais_ic")
    assert not any(c["field"] == "tamanho_civ" for c in hf["when"]["all"])

    fragilidade = doencas["fragilidade-pre-procedimento-cardiovascular"]
    cfs = next(q for q in fragilidade["assistant_questions"] if q["id"] == "cfs_score")
    assert (cfs["min"], cfs["max"]) == (1, 9)
    assert any(r["id"] == "procedimento_urgente_ou_emergencia_nao_atrasar" for r in fragilidade["assistant_rules"])

    vegf = doencas["hipertensao-por-inibidor-vegf"]
    emergencia = next(r for r in vegf["assistant_rules"] if r["id"] == "emergencia_lesao_orgao_alvo")
    assert emergencia["when"]["all"] == [{"field": "lesao_aguda_orgao_alvo", "op": "truthy"}]

    radioterapia = doencas["efeitos-cardiovasculares-tardios-radioterapia"]
    assert {"dispneia_pos_rt_avaliacao_prioritaria", "rastreio_dose_desconhecida_fallback"} <= {
        r["id"] for r in radioterapia["assistant_rules"]
    }

    protese = doencas["protese-mecanica-na-gravidez"]
    anticoag = next(q for q in protese["assistant_questions"] if q["id"] == "anticoagulante_atual")
    assert any(o["value"] == "nenhum_ou_interrompido" for o in anticoag["options"])
    gestacao = next(q for q in protese["assistant_questions"] if q["id"] == "idade_gestacional_semanas")
    assert (gestacao["min"], gestacao["max"]) == (0, 44)

    aorta = doencas["aortopatia-na-gravidez"]
    assert any(q["id"] == "indice_tamanho_aortico_mm_m2" for q in aorta["assistant_questions"])
    assert {"turner_indice_maior_25", "turner_indice_20_a_25", "historia_familiar_disseccao_prioridade"} <= {
        r["id"] for r in aorta["assistant_rules"]
    }
