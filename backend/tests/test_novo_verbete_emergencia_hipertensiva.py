"""Contrato do verbete NOVO "emergencia-hipertensiva" (área geral) criado em
29/08/2026 via doencas/fragmentos/emergencia-hipertensiva.json — a crise/
emergência hipertensiva aguda (lesão de órgão-alvo em curso) não tinha ficha
própria em doencas/metadados.json: `hipertensao-arterial-sistemica` trata
exclusivamente da HAS crônica ambulatorial. Corpus de apoio já existente em
content/Hipertensão/.

Nota sobre verificação de citações: os 12 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils antes da montagem (incluindo o
PMID do ensaio CLUE, obtido por conversão do PMCID PMC3219031, e o PMID de
retratação da diretriz de PPGL 2014 da Endocrine Society).

Nota sobre category: 'emergencia_e_ressuscitacao' segue a mesma convenção já
usada por `parada-cardiorrespiratoria-e-morte-subita-abortada`.

Nota sobre review_status: este verbete permanece `pendente_revisao` (não há
aval de publicação do responsável clínico para este lote). Por isso o slug
foi adicionado a PENDENTES_LOTES_TUDO_COM_TUDO em
test_canonical_content_review_status.py apenas para uso por
test_disease_fragments_canonical.py — test_canonical_content_review_status.py
continua falhando para este registro, como esperado e documentado.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.clinical_rule_engine import (
    validate_question_definitions,
    validate_rule_definitions,
)
from app.services.disease_manifest import load_disease_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "emergencia-hipertensiva"
SIBLING_SLUG = "hipertensao-arterial-sistemica"

MIN_LIST_ITEMS = {
    "presentation": 8,
    "differentials": 6,
    "tests": 6,
    "red_flags": 6,
    "ambulatory_flow": 4,
    "emergency_flow": 8,
    "monitoring": 5,
    "special_populations": 5,
}
MIN_TEXT_CHARS = {
    "epidemiology": 600,
    "treatment_summary": 1500,
}
MIN_DIAGNOSTIC_APPROACH_CHARS = 800

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
    r"\d+[\.,]?\d*\s*j/kg",
)

ALLOWED_ADD_KEYS = {
    "risk", "red_flags", "supporting", "opposing", "missing_information",
    "suggested_tests", "differentials", "ambulatory_flow", "emergency_flow", "messages",
}

TERMOS_TEMA = ("hipertens", "pressão", "pressorica", "pressórica", "catecolamina")


def _load_doencas() -> dict[str, dict]:
    return {item["slug"]: item for item in load_disease_records(DOENCAS_PATH)}


def _all_document_paths() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in (REPOSITORY_ROOT / "content").rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        slug = None
        if text.startswith("---"):
            frontmatter = text.split("---", 2)[1]
            match = re.search(r'^slug:\s*["\']?([^"\'\n]+)', frontmatter, re.MULTILINE)
            if match:
                slug = match.group(1).strip()
        result[slug or path.stem] = path
    return result


def test_ficha_existe_via_fragmento():
    doencas = _load_doencas()
    assert SLUG in doencas


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("category") == "emergencia_e_ressuscitacao"
    assert item.get("cyanosis_class") == "nao_aplicavel"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 8
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Emergência hipertensiva"
    aliases = item.get("aliases") or []
    assert "crise hipertensiva" in aliases
    assert "urgência hipertensiva" in aliases


def test_profundidade_minima_e_nao_e_resumo():
    item = _load_doencas()[SLUG]

    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list), f"{field} deveria ser lista"
        assert len(value) >= minimum, f"{field} tem {len(value)} itens, mínimo {minimum}"

    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str), f"{field} deveria ser texto corrido"
        assert len(value) >= minimum, f"{field} tem {len(value)} caracteres, mínimo {minimum}"

    diagnostic = item.get("diagnostic_approach")
    assert isinstance(diagnostic, dict), "diagnostic_approach deveria ser dict aninhado"
    serialized_len = len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS, (
        f"diagnostic_approach tem {serialized_len} caracteres, mínimo {MIN_DIAGNOSTIC_APPROACH_CHARS}"
    )
    # Precisa diferenciar emergência de urgência e investigar etiologia secundária.
    serialized = json.dumps(diagnostic, ensure_ascii=False).casefold()
    assert "urgência" in serialized or "urgencia" in serialized
    assert "feocromocitoma" in serialized


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "órgão-alvo", "pressão", "gestação"):
        assert palavra in serialized, f"acentuação ausente: {palavra!r} não encontrada"


def test_assistente_deterministico_seguro():
    item = _load_doencas()[SLUG]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []
    assert len(questions) >= 5
    assert len(rules) >= 5

    q_errors, q_ids = validate_question_definitions(SLUG, questions)
    r_errors = validate_rule_definitions(SLUG, rules, q_ids)
    assert q_errors == []
    assert r_errors == []
    assert any(rule.get("priority", 0) >= 90 for rule in rules)

    riscos_altos = 0
    for rule in rules:
        risk = rule.get("add", {}).get("risk")
        if risk in {"urgente", "emergencia"}:
            riscos_altos += 1
    assert riscos_altos >= len(rules) - 2, "a maioria das regras deveria apontar risco alto, dado o tema"

    for question in questions:
        assert "label" in question, f"pergunta {question.get('id')} não usa a chave 'label'"
        assert "text" not in question, f"pergunta {question.get('id')} usa a chave legada 'text'"
        assert "&lt;" not in json.dumps(question, ensure_ascii=False), (
            f"pergunta {question.get('id')} contém entidade HTML não decodificada"
        )

    for rule in rules:
        bad = set(rule.get("add", {}).keys()) - ALLOWED_ADD_KEYS
        assert not bad, f"regra {rule['id']} usa chaves não permitidas em add: {bad}"
        assert "monitoring" not in rule.get("add", {}), "add nunca deve conter 'monitoring'"
        for group_name in ("all", "any", "none"):
            for condition in (rule.get("when") or {}).get(group_name, []):
                assert condition.get("op") != "includes", "op nunca deve ser 'includes'"


def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for pattern in DOSE_PATTERNS:
        matches = re.findall(pattern, serialized)
        assert matches == [], f"padrão de dose encontrado ({pattern}): {matches}"


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona o tema hipertensivo no texto"
        )


def test_sem_overlap_com_hipertensao_arterial_sistemica_cronica():
    doencas = _load_doencas()
    item = doencas[SLUG]
    sibling = doencas[SIBLING_SLUG]
    overlap = set(item.get("related_document_slugs") or []) & set(sibling.get("related_document_slugs") or [])
    assert overlap == set(), (
        "emergencia-hipertensiva não deveria compartilhar related_document_slugs com "
        f"hipertensao-arterial-sistemica (HAS crônica ambulatorial): {overlap}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "quando-a-pressao-alta-e-uma-emergencia"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_com_verbete_hipertensao_arterial_sistemica():
    assert SLUG != SIBLING_SLUG
    doencas = _load_doencas()
    assert doencas[SLUG]["slug"] != doencas[SIBLING_SLUG]["slug"]
