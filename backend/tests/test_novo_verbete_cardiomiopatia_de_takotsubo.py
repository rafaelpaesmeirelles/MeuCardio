"""Contrato do verbete NOVO "cardiomiopatia-de-takotsubo" (área geral) criado
em 29/08/2026 via doencas/fragmentos/cardiomiopatia-de-takotsubo.json — a
cardiomiopatia de takotsubo não tinha ficha própria em doencas/metadados.json,
apesar de corpus rico já existente em content/Cardiomiopatias/,
content/Saúde_mental_e_cardiologia/, content/Terapia_intensiva/ e
content/Cardio-oncologia/.

Nota sobre verificação de citações: os 14 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils (esummary) antes da montagem.
Dois deles (37352669 e 35757924) tinham citação divergente (volume/páginas/
DOI) nos documentos-fonte em relação ao registro oficial do PubMed — o
source_ref usa o dado verificado, com a divergência documentada no próprio
texto da referência.

Nota sobre review_status: este registro permanece "pendente_revisao" — não
foi revisado por humano. Por isso
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug (comportamento esperado e documentado no review_note do
próprio registro e no relatório
docs/novo-verbete-cardiomiopatia-de-takotsubo-2026-08-29.md — não é bug e não
deve ser contornado). A entrada correspondente em
PENDENTES_LOTES_TUDO_COM_TUDO foi adicionada apenas porque essa allowlist é
reaproveitada também por test_disease_fragments_canonical.py, onde a
checagem funciona corretamente.

Nota sobre category: 'cardiomiopatia' segue a mesma convenção já usada nesta
frente para cardiomiopatia-hipertrofica e para o hub geral 'cardiomiopatias'
(PR #565), mesmo a ESC 2023 tendo reclassificado takotsubo como NÃO sendo
mais uma cardiomiopatia no sentido estrito — tensão registrada
explicitamente no review_note do registro.
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
SLUG = "cardiomiopatia-de-takotsubo"

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

TERMOS_TEMA = ("takotsubo",)

EXPECTED_SHARED_WITH_CARDIOMYOPATHY_HUB = {
    "cardiomiopatia-de-takotsubo-o-registro-internacional-e-o-que-a-diferencia-da-sindrome-coronariana-aguda",
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
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("category") == "cardiomiopatia"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Cardiomiopatia de takotsubo"
    assert "Síndrome do coração partido" in (item.get("aliases") or [])


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


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "coração", "súbita", "ventrículo", "catecolaminérgico"):
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
            f"{slug}: documento vinculado menciona 'takotsubo' só {ocorrencias}x — "
            "não parece discussão central do tema"
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

    assert compartilhados_com_outras_fichas == set(), (
        "sobreposição não documentada fora do hub cardiomiopatias: "
        f"{compartilhados_com_outras_fichas}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "cardiomiopatia-de-takotsubo-sindrome-do-coracao-partido"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_com_verbete_hub_cardiomiopatias_geral():
    assert SLUG != "cardiomiopatias"


def test_pmids_corrigidos_estao_documentados_no_source_ref():
    item = _load_doencas()[SLUG]
    refs = " | ".join(item.get("source_refs") or [])
    assert "37352669" in refs and "CORRIGIDO" in refs
    assert "35757924" in refs and "CORRIGIDO" in refs
