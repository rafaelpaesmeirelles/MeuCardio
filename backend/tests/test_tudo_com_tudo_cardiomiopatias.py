"""Contrato do lote Tudo com Tudo de 27/08/2026 — novo verbete-hub de
Cardiomiopatias (área geral) em doencas/metadados.json.

Sexto ciclo independente do dia (após endocardite infecciosa PR #553,
pericardite PR #554, hipertensão pulmonar PR #555, síncope PR #560 e
valvopatias PR #563). Não havia nenhum verbete-hub geral de cardiomiopatia
do adulto — só entries de subpopulação (cardiomiopatia-periparto,
cardiomiopatias-pediatricas, amiloidose-cardiaca-idoso). O lote não cria
nenhum documento, checklist, trilha ou material novo — conecta o novo
verbete a 32 itens já publicados e revisados (27 de content/Cardiomiopatias/
mais 5 de outras pastas com menção direta e explícita ao tema).
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
NOVO_SLUG = "cardiomiopatias"

MIN_LIST_ITEMS = {
    "presentation": 6,
    "differentials": 4,
    "tests": 5,
    "red_flags": 5,
    "ambulatory_flow": 5,
    "emergency_flow": 4,
    "monitoring": 5,
    "special_populations": 4,
}
MIN_TEXT_CHARS = {
    "epidemiology": 600,
    "treatment_summary": 1500,
}
MIN_DIAGNOSTIC_APPROACH_CHARS = 800

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")

SLUGS_IRMAOS_NAO_DUPLICAR = {
    "cardiomiopatia-periparto",
    "cardiomiopatias-pediatricas",
    "amiloidose-cardiaca-idoso",
}


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


def _all_document_paths() -> dict[str, Path]:
    return {p.stem: p for p in (REPOSITORY_ROOT / "content").rglob("*.md")}


def test_slug_e_genuinamente_novo():
    doencas = _load_doencas()
    assert NOVO_SLUG in doencas
    for slug in SLUGS_IRMAOS_NAO_DUPLICAR:
        assert slug in doencas, f"verbete-irmão {slug} deveria já existir na coleção"


def test_marcacao_editorial_correta():
    item = _load_doencas()[NOVO_SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "pendente_revisao"
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

    diagnostic = item.get("diagnostic_approach")
    assert diagnostic, "diagnostic_approach vazio"
    assert isinstance(diagnostic, (str, dict)), "diagnostic_approach deveria ser texto ou objeto estruturado"
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS, (
        f"diagnostic_approach tem {serialized_len} caracteres, mínimo {MIN_DIAGNOSTIC_APPROACH_CHARS}"
    )


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

    related = item.get("related_document_slugs") or []
    assert len(related) >= 25, "hub de cardiomiopatias deveria conectar um volume grande de documentos"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == []

    assert SLUGS_IRMAOS_NAO_DUPLICAR.isdisjoint(set(related))


def test_related_document_slugs_sao_todos_sobre_cardiomiopatia():
    """Vínculo direto: todo documento conectado deve mencionar cardiomiopatia
    explicitamente no próprio texto — evita link por proximidade temática."""
    item = _load_doencas()[NOVO_SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8").casefold()
        assert "cardiomiopat" in texto, f"{slug}: documento vinculado não menciona cardiomiopatia no texto"
