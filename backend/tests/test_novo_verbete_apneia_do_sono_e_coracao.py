"""Contrato do verbete NOVO "apneia-do-sono-e-coracao" (área geral) criado
em 29/08/2026 via doencas/fragmentos/apneia-do-sono-e-coracao.json —
apneia do sono como fator de risco/comorbidade cardiovascular, distinguindo
o fenótipo obstrutivo (AOS, hipertensão resistente, FA) do fenótipo central
(respiração de Cheyne-Stokes/apneia central na ICFEr, SERVE-HF). Não tinha
ficha própria até então, apesar de corpus já rico e existente (CPAP e
hipertensão, CPAP e recorrência de FA pós-ablação, SERVE-HF, Cheyne-Stokes,
STOP-BANG pré-operatório, apneia no idoso, estimulação do nervo frênico
REMEDE).

Nota sobre verificação de citações: todos os 9 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils antes da montagem — nenhuma
correção foi necessária.

Nota: gate test_canonical_content_review_status.py falha intencionalmente
(política vigente desde 28/08/2026) — registro fica pendente_revisao até
revisão humana, sem exceção via allowlist para esse teste específico.
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
SLUG = "apneia-do-sono-e-coracao"

MIN_LIST_ITEMS = {
    "presentation": 8,
    "differentials": 6,
    "tests": 6,
    "red_flags": 6,
    "ambulatory_flow": 6,
    "emergency_flow": 4,
    "monitoring": 5,
    "special_populations": 5,
}
MIN_TEXT_CHARS = {"epidemiology": 600, "treatment_summary": 1500}
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
TERMOS_TEMA = ("apneia", "cpap", "cheyne-stokes")

# Overlaps legítimos e pré-existentes com fichas já publicadas — related_document_slugs
# compartilhados intencionalmente (documento é central para as duas fichas). Qualquer
# outra sobreposição fora deste conjunto quebra o gate abaixo.
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "apneia-obstrutiva-do-sono-no-idoso-cardiopata-prevalencia-risco-modificado-pela-idade-e-limites-do-cpap",  # também em doenca-coronariana-idoso
    "apneia-obstrutiva-do-sono-e-hipertensao-quanto-o-cpap-realmente-baixa-a-pressao",  # também em hipertensao-resistente-e-refrataria
}


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
    assert SLUG in _load_doencas()


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("category") == "prevencao_e_risco"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Apneia do sono e doença cardiovascular"
    assert "SAOS e doença cardiovascular" in (item.get("aliases") or [])


def test_slug_nao_colide_com_outras_fichas_de_sono_ou_arritmia():
    doencas = _load_doencas()
    assert SLUG not in {"insuficiencia-cardiaca", "hipertensao-resistente-e-refrataria"}
    assert SLUG in doencas


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
    assert diagnostic, "diagnostic_approach vazio"
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS, (
        f"diagnostic_approach tem {serialized_len} caracteres, mínimo {MIN_DIAGNOSTIC_APPROACH_CHARS}"
    )


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "cardíaca", "diagnóstico", "polissonografia", "sonolência"):
        assert palavra in serialized, f"acentuação ausente: {palavra!r} não encontrada"


def test_assistente_deterministico_seguro():
    item = _load_doencas()[SLUG]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []
    assert len(questions) >= 3
    assert len(rules) >= 3

    q_errors, q_ids = validate_question_definitions(SLUG, questions)
    r_errors = validate_rule_definitions(SLUG, rules, q_ids)
    assert q_errors == []
    assert r_errors == []
    assert any(rule.get("priority", 0) >= 90 for rule in rules)

    for question in questions:
        assert "label" in question, f"pergunta {question.get('id')} não usa a chave 'label'"
        assert "text" not in question, f"pergunta {question.get('id')} usa a chave legada 'text'"
        assert "&lt;" not in json.dumps(question, ensure_ascii=False), (
            f"pergunta {question.get('id')} contém entidade HTML não decodificada"
        )

    for rule in rules:
        condition = rule.get("when") or {}
        for group_name in ("all", "any", "none"):
            for condition_item in condition.get(group_name, []) or []:
                op = condition_item.get("op")
                assert op != "includes", f"regra {rule['id']} usa operador legado 'includes'"
        bad = set(rule.get("add", {}).keys()) - ALLOWED_ADD_KEYS
        assert not bad, f"regra {rule['id']} usa chaves não permitidas em add: {bad}"
        assert "monitoring" not in rule.get("add", {}), f"regra {rule['id']} usa chave inválida 'monitoring' em add"


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
            f"{slug}: documento vinculado não menciona apneia do sono/CPAP/Cheyne-Stokes no texto"
        )


def test_sem_sobreposicao_nao_documentada_com_outra_ficha():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    compartilhados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        compartilhados |= (related & set(outro_item.get("related_document_slugs") or []))
    inesperados = compartilhados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), f"sobreposição não documentada: {inesperados}"
    # A sobreposição documentada precisa continuar existindo de fato — se deixar de
    # existir, o conjunto acima está desatualizado e precisa ser revisto.
    ausentes = DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS - compartilhados
    assert ausentes == set(), f"sobreposição documentada não foi mais encontrada: {ausentes}"


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "apneia-do-sono-e-o-coracao"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
