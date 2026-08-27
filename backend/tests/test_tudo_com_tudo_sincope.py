"""Contrato do lote Tudo com Tudo de 27/08/2026 — novo verbete-hub de Síncope
(área geral) em doencas/metadados.json.

Quarto ciclo independente do dia (após endocardite infecciosa PR #553,
pericardite PR #554 e hipertensão pulmonar PR #555). A coleção não tinha verbete geral/adulto de síncope; já existia o irmão
pediátrico `sincope-pediatrica`, preservado por este lote; o lote não cria nenhum documento, checklist,
trilha ou material novo — conecta o novo verbete a 30 itens já publicados e
revisados em content/Síncope/ (ESC 2018, EHRA/HRS/APHRS/LAHRS 2024, EuSEM
2024, ensaio SEEDS e demais fontes primárias já presentes no corpus).
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
NOVO_SLUG = "sincope"

MIN_LIST_ITEMS = {
    "presentation": 5,
    "differentials": 4,
    "tests": 5,
    "red_flags": 5,
    "ambulatory_flow": 4,
    "emergency_flow": 4,
    "monitoring": 4,
    "special_populations": 4,
}
MIN_TEXT_CHARS = {
    "epidemiology": 800,
    "diagnostic_approach": 1500,
    "treatment_summary": 1500,
}

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


def _all_document_paths() -> dict[str, Path]:
    return {p.stem: p for p in (REPOSITORY_ROOT / "content").rglob("*.md")}


def _all_patient_material_slugs() -> set[str]:
    items = json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    return {item["slug"] for item in items}


def test_slug_e_genuinamente_novo():
    doencas = _load_doencas()
    assert NOVO_SLUG in doencas
    # Antes deste lote não havia verbete geral/adulto; o registro pediátrico
    # preexistente deve continuar preservado e separado.
    assert "sincope-pediatrica" in doencas
    assert len(doencas) == 101


def test_marcacao_editorial_correta():
    item = _load_doencas()[NOVO_SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_profundidade_minima_e_nao_e_resumo():
    item = _load_doencas()[NOVO_SLUG]

    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list), f"{field} deveria ser lista"
        assert len(value) >= minimum, f"{field} tem {len(value)} itens, mínimo {minimum}"

    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str), f"{field} deveria ser texto corrido"
        assert len(value) >= minimum, f"{field} tem {len(value)} caracteres, mínimo {minimum}"


def test_assistente_deterministico_seguro():
    item = _load_doencas()[NOVO_SLUG]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []
    assert len(questions) >= 3
    assert len(rules) >= 3

    q_errors, q_ids = validate_question_definitions(NOVO_SLUG, questions)
    r_errors = validate_rule_definitions(NOVO_SLUG, rules, q_ids)
    assert q_errors == []
    assert r_errors == []
    assert any(rule.get("priority", 0) >= 70 for rule in rules)

    serialized = json.dumps(rules, ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[NOVO_SLUG]
    documentos = _all_document_paths()
    materiais = _all_patient_material_slugs()

    related = item.get("related_document_slugs") or []
    assert len(related) >= 25, "hub de síncope deveria conectar um volume grande de documentos de content/Síncope/"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == []

    patient_material = item.get("patient_material_slug")
    assert patient_material
    assert patient_material in materiais


def test_related_document_slugs_sao_todos_sobre_sincope():
    """Vínculo direto: todo documento conectado deve mencionar síncope
    explicitamente no próprio texto — evita link por proximidade temática."""
    item = _load_doencas()[NOVO_SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8").casefold()
        assert "síncope" in texto or "sincope" in texto, (
            f"{slug}: documento vinculado não menciona síncope no texto"
        )


def test_nao_reproduz_escore_de_risco_cardiovascular_proprietario_em_nenhum_campo():
    """A ficha discute regras de decisão clínica específicas de síncope
    (San Francisco Syncope Rule, Canadian Syncope Risk Score, EGSYS, ROMEO)
    apenas por nome público — nenhuma delas é o escore proprietário banido
    nesta base (mWHO/HFA-ICOS, usados em outras fichas de gestação/oncologia)."""
    item = _load_doencas()[NOVO_SLUG]
    blob = json.dumps(item, ensure_ascii=False).casefold()
    assert "mwho" not in blob
    assert "hfa-icos" not in blob


def test_bloqueios_clinicos_da_revisao_foram_corrigidos():
    item = _load_doencas()[NOVO_SLUG]
    rules = {r["id"]: r for r in item["assistant_rules"]}
    questions = {q["id"]: q for q in item["assistant_questions"]}

    assert rules["sincope-alto-risco-cardiaco-esforco-estrutural"]["when"] == {
        "all": [{"field": "known_structural_heart_disease", "op": "truthy"}]
    }
    low_fields = {c["field"] for c in rules["sincope-situacional-baixo-risco"]["when"]["all"]}
    assert "syncope_during_exertion" in low_fields
    assert {"syncope_supine_or_seated", "sudden_palpitations_before", "family_history_young_scd"} <= set(questions)

    ilr_fields = {c["field"] for c in rules["sincope-recorrente-inexplicada"]["when"]["all"]}
    assert {"unexplained_after_initial_evaluation", "initial_workup_non_diagnostic"} <= ilr_fields

    assert "não são indicados" in item["treatment_summary"]
    assert "baixo risco" in item["emergency_flow"][-2]
    refs = " ".join(item["source_refs"])
    assert "Brignole M, Menozzi C" in refs
    assert "Aksu T, Brignole M" in refs
