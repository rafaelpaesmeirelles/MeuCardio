"""Contrato do lote de APROFUNDAMENTO Tudo com Tudo de 28/08/2026 — ficha
já existente doenca-coronariana-idoso (área cardiogeriatria) em
doencas/metadados.json.

Diferente dos 20 ciclos anteriores do dia (que criaram hubs gerais novos),
este lote pivotou para aprofundar uma ficha especializada JÁ PUBLICADA que
tinha apenas metadados de catalogação (nome, aliases, área, categoria,
1 frase de resumo, 1 referência genérica) e nenhum campo clínico. O gap-
finding de hubs gerais novos foi declarado esgotado para hoje: o único
candidato restante (cardiopatia reumática crônica do adulto) tinha
sobreposição conceitual real com o PR aberto #567 (Codex), então foi
descartado por decisão do Rafael. A ficha doenca-coronariana-idoso foi
escolhida por ser a mais rasa entre as clinicamente relevantes e livre de
qualquer PR aberto.

O lote não cria nenhum documento, checklist, trilha ou material novo —
conecta a ficha a 19 itens já publicados e revisados em content/, todos
fora de Farmacologia/Calculadoras/Exames.

Notas de compliance:
- Operador "includes" (inexistente no motor de regras real) usado pelo
  agente de pesquisa na regra demencia_avancada_ou_neoplasia_ativa foi
  corrigido para "contains" na montagem, antes do commit.
- 2 dos 21 documentos propostos pelo agente de pesquisa (sintomas-
  prodromicos-e-agudos-de-infarto-em-mulheres-o-que-perguntar-na-anamnese
  e limiar-de-transfusao-no-cardiopata-mint-reality-e-trics-iii) foram
  removidos na montagem por não mencionarem população idosa/geriátrica no
  próprio texto, apesar de tratarem de DAC/infarto em geral.
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
SLUG = "doenca-coronariana-idoso"

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

DOSE_PATTERNS = (
    r"\d+[\.,]?\d*\s*mg\b",
    r"\d+[\.,]?\d*\s*mg/kg",
    r"\d+[\.,]?\d*\s*mcg",
)

ALLOWED_ADD_KEYS = {
    "risk", "red_flags", "supporting", "opposing", "missing_information",
    "suggested_tests", "differentials", "ambulatory_flow", "emergency_flow", "messages",
}

# Documentos legitimamente compartilhados com outras fichas (verificados
# durante a montagem: ambos genuína e centralmente sobre DAC no idoso).
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "fragilidade-como-modificador-de-decisao-cardiovascular",
    "reabilitacao-cardiaca-no-muito-idoso-seguranca-fragilidade-e-adesao",
}


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


def _all_document_paths() -> dict[str, Path]:
    """Resolve documentos por slug de frontmatter (com fallback ao nome do
    arquivo), igual a scripts/audit_tudo_com_tudo.py."""
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


def test_marcacao_editorial_correta_apos_aprofundamento():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "cardiogeriatria"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 2, "aprofundamento deveria incrementar version de 1 para 2"


def test_catalogacao_original_preservada():
    """O aprofundamento não deve apagar os metadados de catalogação
    originais (name/aliases/area/category/subtype/prevalence_rank/tags)."""
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Doença coronariana no idoso"
    assert "DAC no idoso" in (item.get("aliases") or [])
    assert item.get("category") == "doenca_coronariana"
    assert item.get("subtype") == "multimorbidade"
    assert item.get("prevalence_rank") == 13


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


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert len(related) >= 15, "ficha aprofundada deveria conectar um volume relevante de documentos"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_sao_todos_sobre_dac_no_idoso():
    """Vínculo direto: todo documento conectado deve mencionar idoso/muito
    idoso/geriátrico/fragilidade em conjunto com termos de DAC/coronariopatia/
    infarto no próprio texto — evita link por proximidade temática."""
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    termos_idoso = ("idoso", "geriátric", "octogenário", "nonagenário", "muito idoso", "fragilidade", "fragil")
    termos_dac = (
        "coronari", "infarto", "isquêmi", "isquemi", "angina", "revasculariz",
        "estatina", "cardiovascular", "cardiopata",
    )
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(t in texto for t in termos_idoso), (
            f"{slug}: documento vinculado não menciona população idosa/geriátrica no texto"
        )
        assert any(t in texto for t in termos_dac), (
            f"{slug}: documento vinculado não menciona doença coronariana/isquêmica no texto"
        )


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    """Os únicos documentos que também pertencem a related_document_slugs de
    outra ficha devem ser exatamente os dois já verificados e documentados
    no review_note (pertencimento múltiplo legítimo)."""
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
    assert material, "patient_material_slug deveria estar preenchido"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
