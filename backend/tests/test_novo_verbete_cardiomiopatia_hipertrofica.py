"""Contrato do verbete NOVO "cardiomiopatia-hipertrofica" (área geral) criado
em 28/08/2026 via doencas/fragmentos/cardiomiopatia-hipertrofica.json —
doença cardíaca genética mais prevalente, sem ficha própria até então,
apesar de corpus rico já existente em content/Cardiomiopatias/.

Nota sobre verificação de citações: todos os 8 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils antes da montagem — nenhuma
correção foi necessária.

Nota sobre category: 'cardiomiopatia' segue a mesma convenção do hub geral
'cardiomiopatias' integrado pelo PR #565. Os slugs são distintos e o release
consolidado documenta a sobreposição intencional dos documentos nucleares de
CMH entre o verbete específico e o hub de cardiomiopatias.
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
SLUG = "cardiomiopatia-hipertrofica"

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

TERMOS_TEMA = ("hipertróf", "hipertrofia", "cmh", "sarcômero", "sarcomer")

EXPECTED_SHARED_WITH_CARDIOMYOPATHY_HUB = {
    "cardiomiopatia-hipertrofica-diagnostico-e-tratamento-diretriz-brasileira-2024",
    "cardiomiopatia-hipertrofica-obstrutiva-terapia-com-inibidores-de-miosina-cardiaca",
    "cardiomiopatia-hipertrofica-diagnostico-estratificacao-de-risco-e-tratamento-esc-2023-versao-completa",
    "fluxograma-investigacao-genetica-cardiomiopatia-historia-familiar-morte-subita",
    "fluxograma-cardiomiopatia-hipertrofica-esc-2023",
    "aficamten-na-cardiomiopatia-hipertrofica-nao-obstrutiva-forest-hcm-96-semanas",
}

EXPECTED_SHARED_WITH_OTHER_DISEASES = {
    "cardiomiopatia-hipertrofica-diagnostico-estratificacao-de-risco-e-tratamento-esc-2023-versao-completa",
    "fluxograma-cardiomiopatia-hipertrofica-esc-2023",
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
    doencas = _load_doencas()
    assert SLUG in doencas


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("category") == "cardiomiopatia"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Cardiomiopatia hipertrófica"
    assert "CMH" in (item.get("aliases") or [])


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
    for palavra in ("não ", "cardíaca", "súbita", "genética"):
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
        bad = set(rule.get("add", {}).keys()) - ALLOWED_ADD_KEYS
        assert not bad, f"regra {rule['id']} usa chaves não permitidas em add: {bad}"


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
            f"{slug}: documento vinculado não menciona cardiomiopatia hipertrófica no texto"
        )


def test_sobreposicao_com_hub_cardiomiopatias_e_explicitamente_documentada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    hub = doencas["cardiomiopatias"]
    hub_related = set(hub.get("related_document_slugs") or [])

    compartilhados_com_hub = related & hub_related
    assert compartilhados_com_hub == EXPECTED_SHARED_WITH_CARDIOMYOPATHY_HUB

    # A duplicação é aceitável somente entre o verbete específico e seu hub.
    # Qualquer nova sobreposição com outra ficha continua quebrando o gate.
    compartilhados_com_outras_fichas = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug in {SLUG, "cardiomiopatias"}:
            continue
        compartilhados_com_outras_fichas |= (
            related & set(outro_item.get("related_document_slugs") or [])
        )

    assert compartilhados_com_outras_fichas == EXPECTED_SHARED_WITH_OTHER_DISEASES, (
        "sobreposição não documentada fora do hub cardiomiopatias: "
        f"{compartilhados_com_outras_fichas}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "cardiomiopatia-hipertrofica"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_com_verbete_hub_cardiomiopatias_geral():
    assert SLUG != "cardiomiopatias"
