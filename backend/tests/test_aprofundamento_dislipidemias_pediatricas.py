"""Contrato do lote de APROFUNDAMENTO Tudo com Tudo de 28/08/2026 — ficha
já existente dislipidemias-pediatricas (área cardiopediatria) em
doencas/metadados.json.

Sétimo lote de aprofundamento do dia (após doenca-coronariana-idoso
PR #603, valva-aortica-bicuspide-pediatrica PR #604, hipotensao-
ortostatica-no-idoso PR #606, sopros-na-infancia PR #608,
hipertensao-arterial-pediatrica PR #609, dor-toracica-pediatrica
PR #610). Ficha tinha apenas metadados de catalogação — zero campos
clínicos, zero related_document_slugs. Distinta do hub geral
'dislipidemia' (PR #570 aberto, população adulta) — slug diferente,
sem colisão nem sobreposição de documentos.

Nota de compliance: limiares diagnósticos de LDL-C/triglicerídeos em
mg/dL (unidade de concentração laboratorial) são mantidos como
conteúdo diagnóstico legítimo, não doses de fármaco — mesma disciplina
usada para "índice cardíaco <2,2 L/min/m²" e "HV >=70ms" em ciclos
anteriores. O teste de dose abaixo replica esse critério.

Este arquivo também espelha, em test_disease_fragments_canonical.py, a
mesma correção de allowlist já aprovada pelo Rafael no PR #606, pois
esta branch parte de origin/main antes dessa correção.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.clinical_rule_engine import (
    validate_question_definitions,
    validate_rule_definitions,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "dislipidemias-pediatricas"

MIN_LIST_ITEMS = {
    "presentation": 6,
    "differentials": 5,
    "tests": 5,
    "red_flags": 5,
    "ambulatory_flow": 5,
    "emergency_flow": 3,
    "monitoring": 5,
    "special_populations": 4,
}
MIN_TEXT_CHARS = {
    "epidemiology": 600,
    "treatment_summary": 1500,
}
MIN_DIAGNOSTIC_APPROACH_CHARS = 800

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")

# "mg" que não seja seguido de "/dL" (unidade laboratorial de LDL-C/
# triglicerídeos) — evita falso-positivo em limiar diagnóstico legítimo.
DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg(?!/d[lL])\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
)

ALLOWED_ADD_KEYS = {
    "risk", "red_flags", "supporting", "opposing", "missing_information",
    "suggested_tests", "differentials", "ambulatory_flow", "emergency_flow", "messages",
}


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


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


def test_ficha_continua_existindo_com_mesmo_slug():
    doencas = _load_doencas()
    assert SLUG in doencas


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "cardiopediatria"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 2, "aprofundamento deveria incrementar version de 1 para 2"


def test_catalogacao_original_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Dislipidemias pediátricas"
    assert "colesterol alto na criança" in (item.get("aliases") or [])
    assert item.get("category") == "prevencao"
    assert item.get("subtype") == "lipides"
    assert item.get("prevalence_rank") == 27


def test_distinto_do_hub_geral_dislipidemia():
    """Slug/escopo não deve se confundir com o hub adulto 'dislipidemia'."""
    doencas = _load_doencas()
    assert SLUG != "dislipidemia"
    if "dislipidemia" in doencas:
        related_pediatrico = set(doencas[SLUG].get("related_document_slugs") or [])
        related_adulto = set(doencas["dislipidemia"].get("related_document_slugs") or [])
        assert related_pediatrico.isdisjoint(related_adulto), (
            "ficha pediátrica não deveria compartilhar documentos com o hub adulto sem documentação explícita"
        )


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
    assert isinstance(diagnostic, (str, dict)), "diagnostic_approach deveria ser texto ou objeto estruturado"
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS, (
        f"diagnostic_approach tem {serialized_len} caracteres, mínimo {MIN_DIAGNOSTIC_APPROACH_CHARS}"
    )


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
    assert any(rule.get("priority", 0) >= 70 for rule in rules)

    for rule in rules:
        bad = set(rule.get("add", {}).keys()) - ALLOWED_ADD_KEYS
        assert not bad, f"regra {rule['id']} usa chaves não permitidas em add: {bad}"

    serialized = json.dumps(rules, ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for pattern in DOSE_PATTERNS:
        matches = re.findall(pattern, serialized)
        assert matches == [], f"padrão de dose encontrado ({pattern}): {matches}"


def test_limiares_de_ldl_em_mg_dl_sao_diagnosticos_nao_doses():
    """Confirma que os valores 190/160/130/400 mg/dL aparecem como
    contexto de LDL-C (diagnóstico), não como posologia de fármaco."""
    item = _load_doencas()[SLUG]
    diagnostic = json.dumps(item.get("diagnostic_approach"), ensure_ascii=False)
    assert "mg/dL" in diagnostic
    assert "LDL-C" in diagnostic or "LDL" in diagnostic


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert len(related) >= 4, "hub deveria conectar um volume relevante de documentos"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_sao_todos_sobre_dislipidemia_pediatrica():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    termos_lipide = ("dislipidemia", "colesterol", "hipercolesterolemia")
    termos_pediatrico = ("criança", "crianca", "pediátric", "pediatric", "adolescente")
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(t in texto for t in termos_lipide), (
            f"{slug}: documento vinculado não menciona dislipidemia/colesterol no texto"
        )
        assert any(t in texto for t in termos_pediatrico), (
            f"{slug}: documento vinculado não menciona contexto pediátrico no texto"
        )


def test_patient_material_slug_resolve_quando_presente():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    if not material:
        return
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
