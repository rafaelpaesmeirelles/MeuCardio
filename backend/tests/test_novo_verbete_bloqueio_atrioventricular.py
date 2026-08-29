"""Contrato do verbete NOVO "bloqueio-atrioventricular" (área geral) criado
em 29/08/2026 via doencas/fragmentos/bloqueio-atrioventricular.json — BAV
do adulto, distinto de bloqueio-atrioventricular-fetal (ficha própria,
exclusivamente fetal). Introduz category='disturbio_de_conducao' (nova —
nenhuma categoria existente de área geral encaixava uma bradiarritmia).

Nota: todos os 7 PMIDs verificados via NCBI e-utils antes da montagem. Um
7º candidato de related_document_slugs (síndrome BRASH) foi descartado por
resolver para content/Farmacologia.

Nota: gate test_canonical_content_review_status.py falha intencionalmente
(política vigente desde 28/08/2026).
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
SLUG = "bloqueio-atrioventricular"

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
TERMOS_TEMA = ("bloqueio atrioventricular", "bloqueio av", "bav")
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "bradicardia-sintomatica-e-bloqueio-av-de-alto-grau-na-gestacao",  # também em arritmias-na-gravidez
    "bloqueio-av-e-disturbio-de-conducao-apos-tavi",  # também em estenose-aortica-tavi-idoso
    "complicacoes-perianulares-na-endocardite-aortica-abscesso-pseudoaneurisma-e-bloqueio-atrioventricular-novo",  # também em endocardite-infecciosa
    "marcapasso-definitivo-indicacoes-estimulacao-sistema-conducao",  # também em dispositivos-cardiacos-implantaveis
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
    assert item.get("category") == "disturbio_de_conducao"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Bloqueio atrioventricular"
    assert "BAV" in (item.get("aliases") or [])


def test_slug_nao_colide_com_ficha_fetal():
    assert SLUG != "bloqueio-atrioventricular-fetal"


def test_profundidade_minima_e_nao_e_resumo():
    item = _load_doencas()[SLUG]
    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list)
        assert len(value) >= minimum, f"{field} tem {len(value)} itens, mínimo {minimum}"
    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str)
        assert len(value) >= minimum, f"{field} tem {len(value)} caracteres, mínimo {minimum}"
    diagnostic = item.get("diagnostic_approach")
    assert diagnostic
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "cardíaca", "bradicardia", "síncope"):
        assert palavra in serialized


def test_assistente_deterministico_seguro():
    item = _load_doencas()[SLUG]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []
    q_errors, q_ids = validate_question_definitions(SLUG, questions)
    r_errors = validate_rule_definitions(SLUG, rules, q_ids)
    assert q_errors == []
    assert r_errors == []
    assert any(rule.get("priority", 0) >= 90 for rule in rules)
    for question in questions:
        assert "label" in question
        assert "text" not in question
    for rule in rules:
        bad = set(rule.get("add", {}).keys()) - ALLOWED_ADD_KEYS
        assert not bad


def test_nenhuma_dose_de_farmaco_em_nenhum_campo():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for pattern in DOSE_PATTERNS:
        assert re.findall(pattern, serialized) == []


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    related = item.get("related_document_slugs") or []
    assert 3 <= len(related) <= 7
    nao_resolvidos = [s for s in related if s not in documentos]
    assert nao_resolvidos == []
    fora_de_escopo = [s for s in related if any(p in str(documentos[s]) for p in PASTAS_NAO_DOCUMENTO)]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo: {fora_de_escopo}"
    assert len(related) == len(set(related))
    assert "sindrome-brash-bradicardia-insuficiencia-renal-bloqueio-av-choque-e-hipercalemia" not in related, (
        "candidato de content/Farmacologia não deveria ter sido incluído"
    )


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(t in texto for t in TERMOS_TEMA), f"{slug}: não menciona bloqueio atrioventricular/BAV"


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
