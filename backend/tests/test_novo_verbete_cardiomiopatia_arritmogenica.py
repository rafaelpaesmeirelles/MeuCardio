"""Contrato do verbete NOVO "cardiomiopatia-arritmogenica" (área geral) criado
em 29/08/2026 via doencas/fragmentos/cardiomiopatia-arritmogenica.json — a
cardiomiopatia arritmogênica (ACM/DAVD) não tinha ficha própria em
doencas/metadados.json, apesar de corpus rico já existente em
content/Cardiomiopatias/, content/Arritmias/,
content/Cardiologia_do_Esporte_e_do_Exercício/ e content/Cardiologia_pediátrica/.

Nota sobre verificação de citações: os 12 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils (esummary) antes da montagem,
todos conferidos sem divergência contra a citação usada nos documentos-fonte.

Nota sobre review_status: este registro permanece "pendente_revisao" — não
foi revisado por humano. Por isso
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug (comportamento esperado e documentado no review_note do
próprio registro e no relatório
docs/novo-verbete-cardiomiopatia-arritmogenica-2026-08-29.md — não é bug e
não deve ser contornado). A entrada correspondente em
PENDENTES_LOTES_TUDO_COM_TUDO foi adicionada apenas porque essa allowlist é
reaproveitada também por test_disease_fragments_canonical.py, onde a
checagem funciona corretamente (mesmo padrão da branch
claude/novo-verbete-cardiomiopatia-de-takotsubo-20260829, PR #698).

Nota sobre category/subtype: 'cardiomiopatia'/'arritmogenica' seguem a
convenção já usada nesta frente para cardiomiopatia-hipertrofica e para o
hub geral 'cardiomiopatias' (PR #565).

Nota sobre sobreposição de related_document_slugs: este verbete específico
compartilha documentos com vários registros "hub"/guarda-chuva já existentes
(cardiomiopatias, arritmias-ventriculares-e-morte-subita-cardiaca,
arritmias-pediatricas, cardiomiopatias-pediatricas, sincope-pediatrica) —
esperado, pois hubs listam amplamente documentos específicos do próprio
domínio. A sobreposição é documentada explicitamente abaixo, slug a slug.
Confirmado nesta sessão: NENHUMA sobreposição de related_document_slugs com
cardiomiopatia-hipertrofica (já integrada) nem com cardiomiopatia-dilatada
(produzida em paralelo, ainda não integrada nesta base — verificação
repetida quando a branch for integrada).
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
SLUG = "cardiomiopatia-arritmogenica"

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

TERMOS_TEMA = ("arritmogênica", "arritmogenica", "arvc", "davd", "cavd")

# Verbetes "hub"/guarda-chuva já existentes que legitimamente compartilham
# documentos específicos de ACM com este verbete — checado individualmente
# nesta sessão via load_disease_records().
EXPECTED_SHARED_WITH_OTHER_RECORDS = {
    "cardiomiopatias": {
        "cardiomiopatia-arritmogenica-criterios-de-padua-2020-e-task-force-revisada-de-2010",
        "cardiomiopatia-arritmogenica-acm-diagnostico-e-manejo-esc-2023",
    },
    "arritmias-ventriculares-e-morte-subita-cardiaca": {
        "calculadora-de-risco-da-cardiomiopatia-arritmogenica-desempenho-por-genotipo",
        "cardiomiopatia-arritmogenica-no-atleta-exercicio-risco-e-retorno-ao-esporte",
        "cardiomiopatia-arritmogenica-criterios-de-padua-2020-e-task-force-revisada-de-2010",
        "restricao-de-exercicio-na-cardiomiopatia-arritmogenica-de-ventriculo-direito-dose-resposta-e-mecanismo",
    },
    "arritmias-pediatricas": {
        "cardiomiopatia-arritmogenica-na-crianca-penetrancia-idade-dependente-rastreio-familiar-e-restricao-de-exercicio",
    },
    "cardiomiopatias-pediatricas": {
        "cardiomiopatia-arritmogenica-na-crianca-penetrancia-idade-dependente-rastreio-familiar-e-restricao-de-exercicio",
    },
    "sincope-pediatrica": {
        "cardiomiopatia-arritmogenica-na-crianca-penetrancia-idade-dependente-rastreio-familiar-e-restricao-de-exercicio",
    },
}

# A tarefa exige checagem explícita de ausência de colisão/overlap excessivo
# com estes dois verbetes específicos produzidos na mesma frente.
NO_OVERLAP_EXPECTED_WITH = ("cardiomiopatia-hipertrofica", "cardiomiopatia-dilatada")


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
    assert item.get("category") == "cardiomiopatia"
    assert item.get("subtype") == "arritmogenica"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Cardiomiopatia arritmogênica"
    aliases = item.get("aliases") or []
    for esperado in ("DAVD", "ACM", "displasia arritmogênica de ventrículo direito"):
        assert esperado in aliases, f"alias obrigatório ausente: {esperado!r}"


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
    assert isinstance(diagnostic, dict), "diagnostic_approach deveria ser dict aninhado (tema complexo)"
    serialized_len = len(json.dumps(diagnostic, ensure_ascii=False))
    assert serialized_len >= MIN_DIAGNOSTIC_APPROACH_CHARS, (
        f"diagnostic_approach tem {serialized_len} caracteres, mínimo {MIN_DIAGNOSTIC_APPROACH_CHARS}"
    )

    # Deve mencionar explicitamente as duas ferramentas diagnósticas obrigatórias.
    serialized_diag = json.dumps(diagnostic, ensure_ascii=False)
    assert "Padua" in serialized_diag
    assert "Task Force" in serialized_diag


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "coração", "genética", "ventrículo", "cardíaca"):
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
        if "risk" in rule["add"]:
            assert rule["add"]["risk"] in {
                "informativo", "rotina", "prioritario", "urgente", "emergencia",
            }, f"regra {rule['id']} usa risk inválido: {rule['add']['risk']}"


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


def test_related_document_slugs_mencionam_tema_de_forma_central():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        ocorrencias = sum(texto.count(termo) for termo in TERMOS_TEMA)
        assert ocorrencias >= 5, (
            f"{slug}: documento vinculado menciona termos de ACM só {ocorrencias}x — "
            "não parece discussão central do tema"
        )


def test_calculadora_de_risco_relacionada_esta_fisicamente_fora_de_calculadoras():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    alvo = "calculadora-de-risco-da-cardiomiopatia-arritmogenica-desempenho-por-genotipo"
    assert alvo in (item.get("related_document_slugs") or [])
    caminho = str(documentos[alvo])
    assert "content/Arritmias/" in caminho
    assert "content/Calculadoras/" not in caminho


def test_sobreposicao_de_related_document_slugs_e_explicitamente_documentada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])

    for outro_slug, esperado in EXPECTED_SHARED_WITH_OTHER_RECORDS.items():
        outro = doencas.get(outro_slug)
        assert outro is not None, f"registro hub esperado ausente: {outro_slug}"
        outro_related = set(outro.get("related_document_slugs") or [])
        compartilhados = related & outro_related
        assert compartilhados == esperado, (
            f"sobreposição com {outro_slug} mudou: esperado {esperado}, encontrado {compartilhados}"
        )

    hubs_documentados = set(EXPECTED_SHARED_WITH_OTHER_RECORDS.keys()) | {SLUG}
    sobreposicao_nao_documentada = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug in hubs_documentados:
            continue
        sobreposicao_nao_documentada |= (
            related & set(outro_item.get("related_document_slugs") or [])
        )
    assert sobreposicao_nao_documentada == set(), (
        "sobreposição de related_document_slugs não documentada fora dos hubs esperados: "
        f"{sobreposicao_nao_documentada}"
    )


def test_sem_colisao_com_cardiomiopatia_hipertrofica_e_dilatada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    for outro_slug in NO_OVERLAP_EXPECTED_WITH:
        outro = doencas.get(outro_slug)
        if outro is None:
            # cardiomiopatia-dilatada pode ainda não estar integrada nesta base
            # (produzida em branch paralela) — sem registro, não há colisão a checar.
            continue
        overlap = related & set(outro.get("related_document_slugs") or [])
        assert overlap == set(), f"overlap inesperado de related_document_slugs com {outro_slug}: {overlap}"


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "cardiomiopatia-arritmogenica-musculo-do-coracao-trocado-por-gordura-e-cicatriz"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_com_verbete_hub_cardiomiopatias_geral():
    assert SLUG != "cardiomiopatias"


def test_pmids_citados_no_source_refs():
    item = _load_doencas()[SLUG]
    refs = " | ".join(item.get("source_refs") or [])
    urls = " | ".join(item.get("source_urls") or [])
    pmids_esperados = (
        "37622657", "20172912", "32561223", "37844667", "30915475",
        "33296238", "38938828", "23871885", "25896080", "25516436",
        "32860412", "38763377",
    )
    for pmid in pmids_esperados:
        assert pmid in refs, f"PMID {pmid} ausente de source_refs"
        assert pmid in urls, f"PMID {pmid} ausente de source_urls"
