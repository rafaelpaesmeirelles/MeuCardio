"""Contrato do lote Tudo com Tudo de 27/08/2026 — novo verbete-hub de
Endocardite Infecciosa adulta (área geral) em doencas/metadados.json.

Este é o PRIMEIRO registro de doença adulta geral para endocardite; a
coleção já tinha endocardite-pediatrica, mas nenhum hub para o adulto. O
lote não cria nenhum documento, checklist, trilha ou material novo — conecta
o novo verbete a ~28 itens de content/Endocardite/ (e correlatos em Gravidez)
já publicados e revisados, hoje órfãos de um hub central em doencas/.

O teste mede: (1) que o slug é genuinamente novo e não colide com nada
existente; (2) marcação editorial correta; (3) profundidade real de
conteúdo; (4) assistente determinístico seguro; (5) que todos os vínculos
Tudo com Tudo resolvem contra documento/material já existentes; (6) que
nenhum vínculo aponta para medicamento/exame/calculadora (que também vivem
sob content/**/*.md mas não são documentos narrativos elegíveis).
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
NOVO_SLUG = "endocardite-infecciosa"

MIN_LIST_ITEMS = {
    "presentation": 5,
    "differentials": 4,
    "tests": 5,
    "red_flags": 4,
    "ambulatory_flow": 4,
    "emergency_flow": 4,
    "monitoring": 4,
    "special_populations": 6,
}
MIN_TEXT_CHARS = {
    "epidemiology": 600,
    "diagnostic_approach": 600,
    "treatment_summary": 1000,
}

# Pastas de coleções que NÃO são documento narrativo elegível para
# related_document_slugs, mesmo vivendo sob content/**/*.md.
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
    # endocardite-pediatrica continua existindo e intocada — o lote não
    # mexeu em nenhum registro pré-existente, só acrescentou um novo.
    assert "endocardite-pediatrica" in doencas
    ped = doencas["endocardite-pediatrica"]
    assert ped["area"] == "cardiopediatria"


def test_marcacao_editorial_correta():
    item = _load_doencas()[NOVO_SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 2


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
    assert any(rule.get("priority", 0) >= 70 for rule in rules), "sem regra de alta prioridade"

    serialized = json.dumps(rules, ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[NOVO_SLUG]
    documentos = _all_document_paths()
    materiais = _all_patient_material_slugs()

    related = item.get("related_document_slugs") or []
    assert len(related) >= 15, "hub de endocardite deveria conectar a um número substancial de documentos já existentes"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], (
        f"related_document_slugs aponta para medicamento/exame/calculadora, não documento narrativo: {fora_de_escopo}"
    )

    patient_material = item.get("patient_material_slug")
    assert patient_material, "verbete geral de endocardite deveria ter material ao paciente"
    assert patient_material in materiais


def test_related_document_slugs_sao_todos_sobre_endocardite():
    """Vínculo direto: todo documento conectado deve mencionar endocardite
    explicitamente no próprio texto — evita link por proximidade temática."""
    item = _load_doencas()[NOVO_SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8").casefold()
        assert "endocardite" in texto, f"{slug}: documento vinculado não menciona endocardite no texto"
