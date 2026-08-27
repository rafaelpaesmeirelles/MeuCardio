"""Contrato de profundidade do lote 5 de 27/08/2026.

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
    "sincope-pediatrica",
    "comunicacao-interventricular",
    "coarctacao-da-aorta",
    "fragilidade-pre-procedimento-cardiovascular",
    "hipertensao-por-inibidor-vegf",
    "efeitos-cardiovasculares-tardios-radioterapia",
    "protese-mecanica-na-gravidez",
    "aortopatia-na-gravidez",
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
    assert len(slugs) >= 101


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
