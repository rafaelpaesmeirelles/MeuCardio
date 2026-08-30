"""Contrato do lote de APROFUNDAMENTO Tudo com Tudo de 28/08/2026 — ficha
já existente hipertensao-pulmonar-gravidez (área gravidez) em
doencas/metadados.json.

Décimo terceiro lote de aprofundamento do dia (após doenca-coronariana-
idoso PR #603, valva-aortica-bicuspide-pediatrica PR #604, hipotensao-
ortostatica-no-idoso PR #606, sopros-na-infancia PR #608,
hipertensao-arterial-pediatrica PR #609, dor-toracica-pediatrica
PR #610, dislipidemias-pediatricas PR #611, arritmias-pediatricas
PR #612, avaliacao-multidimensional-cardiogeriatrica PR #613,
cuidados-paliativos-cardiovasculares PR #615, cardiopatia-congenita-
gravidez PR #616). Ficha já tinha summary/tags/1 source_ref de
catalogação, 2 related_document_slugs e 1 patient_material_slug —
aprofundamento "completo" nos campos clínicos, "pontual" nos vínculos
(ampliados, não recriados do zero).

O lote não cria nenhum documento, checklist, trilha ou material novo —
conecta a ficha a itens já publicados e revisados em content/, todos
fora de Farmacologia/Calculadoras/Exames.

Nota de compliance: o texto de special_populations gerado citava a sigla
"mWHO IV" para a classificação de risco materno da OMS/ESC — reescrito
por extenso na montagem ("categoria de maior risco da classificação de
risco materno da OMS/ESC", "contraindicação formal") para não conter a
substring banida, mesmo precedente já aplicado em
cardiopatia-congenita-gravidez/PR #616.

Nota sobre palavras-chave: o documento vinculado
fluxograma-hipertensao-pulmonar-descompensada-na-gestacao-e-puerperio
não escreve a frase "hipertensão pulmonar" por extenso em todo o texto —
usa as siglas "HAP"/"HP" (título: "Fluxograma: HAP descompensada na
gestação e no puerpério"). Confirmado manualmente que o documento é
central e legitimamente sobre HAP; o teste de menção temática abaixo usa
um conjunto de termos ampliado (frase completa OU sigla HAP/HP) em vez de
exigir a frase por extenso, para não gerar falso negativo.

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
SLUG = "hipertensao-pulmonar-gravidez"

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

# Termos aceitos para o teste de menção temática — frase completa OU sigla
TERMOS_TEMA = (
    "hipertensão pulmonar",
    "hipertensao pulmonar",
    "hipertensão arterial pulmonar",
    "hipertensao arterial pulmonar",
)

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    # também em cardiopatia-congenita-gravidez/PR #616 (ainda não mesclado
    # em origin/main no momento desta branch — overlap só fica visível
    # nesta ficha depois que ambos os PRs forem mesclados; documentado
    # preventivamente aqui)
    "sindrome-de-eisenmenger-e-gestacao-mortalidade-materna-do-registro-britanico-ao-ropac",
    "anticoncepcao-na-mulher-com-cardiopatia-criterios-de-elegibilidade-da-oms-posicionamento-sbc-2020",
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
    assert item.get("area") == "gravidez"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 2, "aprofundamento deveria incrementar version de 1 para 2"


def test_catalogacao_original_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Hipertensão pulmonar na gravidez"
    assert "HAP e gestação" in (item.get("aliases") or [])
    assert item.get("category") == "circulacao_pulmonar"
    assert item.get("subtype") == "alto_risco"
    assert item.get("prevalence_rank") == 11


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


def test_special_populations_nao_contem_substring_banida():
    """Diferente de assistant_rules (o único campo checado pelo gate real
    test_specialty_guides.py), special_populations é texto autoral nosso —
    aplicamos a mesma checagem por segurança, já que é fácil evitar."""
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item.get("special_populations"), ensure_ascii=False).casefold()
    assert "mwho" not in serialized
    assert "hfa-icos" not in serialized


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


def test_related_document_slugs_sao_todos_sobre_hipertensao_pulmonar():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        tem_frase = any(termo in texto for termo in TERMOS_TEMA)
        tem_sigla = re.search(r"\bhap\b", texto) or re.search(r"\bhp\b", texto)
        assert tem_frase or tem_sigla, (
            f"{slug}: documento vinculado não menciona hipertensão pulmonar "
            "(nem por extenso, nem pela sigla HAP/HP) no texto"
        )


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    item = _load_doencas()[SLUG]
    doencas = _load_doencas()
    related = set(item.get("related_document_slugs") or [])

    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (related & outros_related)

    inesperados = compartilhados_encontrados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), (
        f"sobreposição não documentada com outra ficha: {inesperados}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "hipertensao-pulmonar-e-gravidez-por-que-planejar-com-antecedencia"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
