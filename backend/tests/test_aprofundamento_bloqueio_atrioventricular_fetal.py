"""Contrato do lote de APROFUNDAMENTO Tudo com Tudo de 28/08/2026 — ficha
já existente bloqueio-atrioventricular-fetal (área cardiopediatria) em
doencas/metadados.json.

Décimo oitavo lote de conteúdo do dia, segundo do cluster de
cardiologia fetal (após doenca-coronariana-idoso PR #603,
valva-aortica-bicuspide-pediatrica PR #604, hipotensao-ortostatica-no-
idoso PR #606, sopros-na-infancia PR #608, hipertensao-arterial-
pediatrica PR #609, dor-toracica-pediatrica PR #610, dislipidemias-
pediatricas PR #611, arritmias-pediatricas PR #612,
avaliacao-multidimensional-cardiogeriatrica PR #613,
cuidados-paliativos-cardiovasculares PR #615, cardiopatia-congenita-
gravidez PR #616, hipertensao-pulmonar-gravidez PR #621,
cardiotoxicidade-bcr-abl PR #624, medicamentos-cardiovasculares-
gestacao-lactacao PR #625, plano-parto-cardiopatia-materna PR #626,
seguimento-cardiovascular-pos-parto PR #628, indicacoes-
ecocardiograma-fetal PR #630). Ficha já tinha patient_material_slug e
2 related_document_slugs preenchidos, mas zero campos clínicos.

O lote não cria nenhum documento, checklist, trilha ou material novo —
conecta a ficha a 4 itens já publicados e revisados em content/, todos
fora de Farmacologia/Calculadoras/Exames.

Nota sobre sobreposição: os documentos compartilhados com fichas irmãs do
cluster fetal/pediátrico são deliberados e clinicamente centrais; o contrato
abaixo os enumera explicitamente para impedir tanto perda de vínculo quanto
sobreposição nova não revisada.
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
SLUG = "bloqueio-atrioventricular-fetal"

MIN_LIST_ITEMS = {
    "presentation": 8,
    "differentials": 5,
    "tests": 6,
    "red_flags": 6,
    "ambulatory_flow": 6,
    "emergency_flow": 4,
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

TERMOS_TEMA = (
    "bloqueio atrioventricular", "bloqueio cardíaco congênito",
    "anti-ro", "bav",
)

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "arritmias-fetais-taquicardia-supraventricular-e-bloqueio-atrioventricular-total-tratamento-transplacentario",
    "extrassistoles-fetais-irregularidade-do-ritmo-fetal-vigilancia-e-quando-nao-e-benigno",
    "ecocardiografia-fetal-seriada-na-gestante-anti-ro-ssa-positiva-vigilancia-do-bloqueio-cardiaco-congenito",
    "bloqueio-av-congenito-completo-no-recem-nascido",
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
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "cardiopediatria"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 2, "aprofundamento deveria incrementar version de 1 para 2"


def test_catalogacao_original_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Bloqueio atrioventricular fetal"
    assert "BAV fetal" in (item.get("aliases") or [])
    assert item.get("category") == "cardiologia_fetal"
    assert item.get("subtype") == "bradiarritmia"
    assert item.get("prevalence_rank") == 32


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
    assert diagnostic
    assert isinstance(diagnostic, (str, dict))
    serialized_len = len(diagnostic) if isinstance(diagnostic, str) else len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "cardíaca", "gestação", "atrioventricular"):
        assert palavra in serialized


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
        assert not bad
    serialized = json.dumps(rules, ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


def test_special_populations_nao_contem_substring_banida():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item.get("special_populations"), ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


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
    assert [slug for slug in related if slug not in documentos] == []
    fora_de_escopo = [slug for slug in related if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)]
    assert fora_de_escopo == []
    assert len(related) == len(set(related))


def test_related_document_slugs_mencionam_bav_fetal():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA)


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    item = _load_doencas()[SLUG]
    doencas = _load_doencas()
    related = set(item.get("related_document_slugs") or [])
    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        compartilhados_encontrados |= (related & set(outro_item.get("related_document_slugs") or []))
    inesperados = compartilhados_encontrados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), f"sobreposição não documentada com outra ficha: {inesperados}"


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "gravidez-com-anticorpo-anti-ro-ssa-vigilancia-do-coracao-do-bebe"
    materiais = {x["slug"] for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))}
    assert material in materiais