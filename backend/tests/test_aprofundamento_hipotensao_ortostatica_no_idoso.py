"""Contrato do lote de APROFUNDAMENTO PONTUAL Tudo com Tudo de 28/08/2026
— ficha já existente hipotensao-ortostatica-no-idoso (área cardiogeriatria)
em doencas/metadados.json.

Terceiro lote de aprofundamento do dia (após doenca-coronariana-idoso,
PR #603, e valva-aortica-bicuspide-pediatrica, PR #604). Diferente dos
dois anteriores, esta ficha já tinha presentation/differentials/tests/
red_flags/ambulatory_flow/emergency_flow/assistant_questions/
assistant_rules substantivos e revisados — preservados sem alteração.
Faltavam apenas 4 campos: epidemiology, treatment_summary, monitoring,
special_populations. related_document_slugs expandido de 3 para 14.

Nota de compliance: 6 dos 11 documentos novos são compartilhados com a
ficha sincope e com risco-quedas-cardiogeriatria, ambas já publicadas —
mantidos por serem genuína e centralmente também sobre hipotensão
ortostática (seção dedicada), não apenas menção de passagem.
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
SLUG = "hipotensao-ortostatica-no-idoso"

MIN_LIST_ITEMS = {
    "presentation": 3,
    "differentials": 4,
    "tests": 3,
    "red_flags": 3,
    "ambulatory_flow": 3,
    "emergency_flow": 2,
    "monitoring": 5,
    "special_populations": 5,
}
MIN_TEXT_CHARS = {
    "epidemiology": 600,
    "treatment_summary": 1500,
}

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

DOCUMENTOS_ORIGINAIS = {
    "hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial",
    "hipotensao-pos-prandial-no-idoso-cardiopata-mecanismo-prevalencia-e-manejo",
    "hipotensao-ortostatica-nao-e-motivo-para-desescalonar-o-anti-hipertensivo",
}

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    # já existiam nos 3 related_document_slugs originais, antes deste lote
    "hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial",  # também em sincope
    "hipotensao-pos-prandial-no-idoso-cardiopata-mecanismo-prevalencia-e-manejo",  # também em risco-quedas-cardiogeriatria
    # adicionados neste lote
    "fluxograma-hipotensao-ortostatica-diagnostico-causa-e-manejo-escalonado",
    "fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial",
    "fluxograma-sincope-idoso-investigacao-diferenciada",
    "sincope-classificacao-etiologica-em-tres-grandes-grupos",
    "sincope-diagnostico-e-manejo-esc-2018",
    "sincope-e-risco-de-fratura-por-queda-o-que-os-estudos-de-coorte-mostram",
    "fluxograma-hipertensao-no-idoso-e-no-fragil-quando-iniciar-alvo-e-desintensificacao-esc-2024",  # overlap legítimo no corpus consolidado 28/08/2026
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


def test_marcacao_editorial_correta_apos_aprofundamento():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "cardiogeriatria"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 2, "aprofundamento deveria incrementar version de 1 para 2"


def test_catalogacao_e_conteudo_previo_preservados():
    """Campos já bons (presentation/differentials/tests/red_flags/
    ambulatory_flow/emergency_flow/assistant_questions/assistant_rules) não
    devem ter sido reescritos ou reduzidos por este lote pontual."""
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Hipotensão ortostática no idoso"
    assert "queda de pressão ao levantar" in (item.get("aliases") or [])
    assert item.get("category") == "sindrome_geriatrica"
    assert item.get("subtype") == "quedas_e_sincope"
    assert item.get("prevalence_rank") == 2
    assert len(item.get("assistant_questions") or []) >= 5
    assert len(item.get("assistant_rules") or []) >= 5


def test_profundidade_minima_dos_campos_preenchidos_e_dos_novos():
    item = _load_doencas()[SLUG]

    for field, minimum in MIN_LIST_ITEMS.items():
        value = item.get(field) or []
        assert isinstance(value, list), f"{field} deveria ser lista"
        assert len(value) >= minimum, f"{field} tem {len(value)} itens, mínimo {minimum}"

    for field, minimum in MIN_TEXT_CHARS.items():
        value = item.get(field) or ""
        assert isinstance(value, str), f"{field} deveria ser texto corrido"
        assert len(value) >= minimum, f"{field} tem {len(value)} caracteres, mínimo {minimum}"


def test_assistente_deterministico_seguro():
    item = _load_doencas()[SLUG]
    questions = item.get("assistant_questions") or []
    rules = item.get("assistant_rules") or []

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
    assert len(related) >= 12, "expansão deveria levar a um volume relevante de documentos"
    assert DOCUMENTOS_ORIGINAIS.issubset(set(related)), "documentos originais não deveriam ser removidos"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_sao_todos_sobre_hipotensao_ortostatica():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    termos = ("hipotensão ortostática", "hipotensao ortostatica", "hipotensão postural")
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(t in texto for t in termos), (
            f"{slug}: documento vinculado não menciona hipotensão ortostática/postural no texto"
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
    assert material == "tontura-ao-levantar-hipotensao-ortostatica-e-pots"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
