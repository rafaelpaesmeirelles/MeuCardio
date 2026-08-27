"""Contrato do lote Tudo com Tudo de 27/08/2026 — novo verbete-hub de
Valvopatias (área geral) em doencas/metadados.json.

Quinto ciclo independente do dia (após endocardite infecciosa PR #553,
pericardite PR #554, hipertensão pulmonar PR #555 e síncope PR #560). Não
havia nenhum verbete-hub geral de doença valvar do adulto — só entries de
subpopulação (valvopatias-na-gravidez, estenose-aortica-tavi-idoso). O lote
não cria nenhum documento, checklist, trilha ou material novo — conecta o
novo verbete a 41 itens já publicados e revisados (37 de content/Valvopatias/
mais 4 de outras pastas com menção direta e explícita ao tema).
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
NOVO_SLUG = "valvopatias"

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

# Verbetes-irmãos já existentes cujo escopo específico não deve ser duplicado
# por este hub geral — são citados em special_populations como texto, nunca
# como related_document_slugs.
SLUGS_IRMAOS_NAO_DUPLICAR = {
    "valvopatias-na-gravidez",
    "estenose-aortica-tavi-idoso",
    "fragilidade-pre-procedimento-cardiovascular",
    "endocardite-infecciosa",
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
    assert len(related) >= 35, "hub de valvopatias deveria conectar um volume grande de documentos"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == []

    # related_document_slugs nunca deve conter o slug de outra doença (vínculo
    # direto é sempre a um documento narrativo, nunca a outro registro de
    # doença) — isso incluiria acidentalmente os verbetes-irmãos protegidos.
    assert SLUGS_IRMAOS_NAO_DUPLICAR.isdisjoint(set(related))


def test_related_document_slugs_sao_todos_sobre_valvopatia():
    """Vínculo direto: todo documento conectado deve mencionar valva/valvar
    explicitamente no próprio texto — evita link por proximidade temática."""
    item = _load_doencas()[NOVO_SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8").casefold()
        assert "valv" in texto, f"{slug}: documento vinculado não menciona valva/valvar no texto"


def test_nao_duplica_escopo_de_gravidez_tavi_idoso_fragilidade_ou_endocardite():
    """O hub geral não deve reivindicar como vínculo direto (related_document_slugs)
    conteúdo cujo escopo já pertence a um verbete-irmão mais específico."""
    item = _load_doencas()[NOVO_SLUG]
    related = set(item.get("related_document_slugs") or [])
    assert "estenose-mitral-e-aortica-na-gravidez" not in related


def test_bloqueios_clinicos_e_editoriais_da_revisao_foram_corrigidos():
    item = _load_doencas()[NOVO_SLUG]
    serializado = json.dumps(item, ensure_ascii=False).casefold()

    assert item["category"] == "valvopatia"
    assert item["review_status"] == "revisado"
    assert item["version"] == 2
    assert "dobutamina não é o exame-padrão desse fenótipo" in item["diagnostic_approach"]["estenose_aortica"]
    assert "baixo fluxo/baixo gradiente com feve preservada; formalmente" not in serializado

    regras = {r["id"]: r for r in item["assistant_rules"]}
    assert {"protese_biologica_janela_3_meses_posicao_ausente",
            "bioprotese_aortica_menor_3_meses",
            "bioprotese_mitral_tricuspide_menor_3_meses",
            "planejamento_gestacional_escolha_protese",
            "idade_menor_60_escolha_compartilhada",
            "idade_60_ou_mais_escolha_compartilhada"} <= set(regras)
    assert {"field": "protese_posicao", "op": "missing"} in regras[
        "protese_biologica_janela_3_meses_posicao_ausente"
    ]["when"]["all"]
    assert "aproximadamente a cada 6 meses" in item["monitoring"][0]
