"""Contrato do verbete NOVO "torsades-de-pointes-qt-longo-adquirido" (área
geral) criado em 29/08/2026 via
doencas/fragmentos/torsades-de-pointes-qt-longo-adquirido.json.

Escopo: forma ADQUIRIDA (induzida por fármaco/distúrbio eletrolítico) de QT
longo e torsades de pointes — distinta da canalopatia congênita
("canalopatias-cardiacas-hereditarias") e do QT longo por terapia oncológica
dirigida ("qt-longo-terapia-oncologica"), ambas já cadastradas com
category="arritmia".

Nota sobre verificação de citações: os 8 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils (esummary) em 29/08/2026 antes
da montagem do source_refs; nenhuma divergência foi encontrada em relação
aos documentos-fonte lidos nesta sessão.

Nota sobre review_status: este registro permanece "pendente_revisao" — não
foi revisado por humano. Por isso
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug (comportamento esperado e documentado no review_note do
próprio registro e em
docs/novo-verbete-torsades-de-pointes-qt-longo-adquirido-2026-08-29.md — não
é bug e não deve ser contornado). A entrada correspondente em
PENDENTES_LOTES_TUDO_COM_TUDO foi adicionada apenas porque essa allowlist é
reaproveitada também por test_disease_fragments_canonical.py, onde a
checagem funciona corretamente (mesmo padrão da PR #698,
"cardiomiopatia-de-takotsubo").

Nota sobre Farmacologia: 3 dos 6 candidatos de related_document_slugs
originalmente mapeados vivem em content/Farmacologia/ e foram
deliberadamente excluídos por instrução desta rodada, mesmo sendo
tematicamente relevantes (metadona, hipocalcemia de fase 2, sulfato de
magnésio). Dois candidatos adicionais fora de Farmacologia/Calculadoras/
Exames foram buscados ativamente e incluídos para dar folga acima do piso
de 3 (hipomagnesemia e hipocalemia grave, ambos em content/
Terapia_intensiva/, cada um com seção dedicada discutindo torsades/QT longo
adquirido de forma central).
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
SLUG = "torsades-de-pointes-qt-longo-adquirido"

MIN_LIST_ITEMS = {
    "presentation": 8,
    "differentials": 6,
    "tests": 6,
    "red_flags": 6,
    "ambulatory_flow": 6,
    "emergency_flow": 6,
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

TERMOS_TEMA = ("torsades", "qt longo")

FARMACOLOGIA_EXCLUIDOS_DELIBERADAMENTE = {
    "metadona-e-prolongamento-do-intervalo-qt",
    "hipocalcemia-grave-e-prolongamento-do-qt-mecanismo-de-fase-2-e-reversao-rapida-com-calcio",
    "sulfato-de-magnesio-em-cardiologia-torsades-de-pointes-e-adjuvante-no-controle-de-frequencia-da-fa",
}

EXPECTED_SHARED_WITH_VT_SCD_HUB = {
    "torsades-de-pointes-e-qt-longo-adquirido-escore-de-tisdale-e-manejo-agudo",
    "fluxograma-torsades-de-pointes-e-qt-longo-adquirido",
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
    assert item.get("category") == "arritmia"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Torsades de pointes e QT longo adquirido"
    assert "QT longo adquirido" in (item.get("aliases") or [])


def test_categoria_igual_as_fichas_irmas_de_qt_longo():
    doencas = _load_doencas()
    item = doencas[SLUG]
    for irmao in ("canalopatias-cardiacas-hereditarias", "qt-longo-terapia-oncologica"):
        assert irmao in doencas, f"ficha irmã {irmao} deveria existir"
        assert doencas[irmao]["category"] == item["category"] == "arritmia"


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
    for palavra in ("não ", "súbita", "polimórfica", "após", "eletrólito", "farmacodinâmico"):
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
    assert any(rule.get("priority", 0) >= 90 for rule in rules), (
        "deveria existir regra de prioridade máxima para TV polimórfica sustentada"
    )

    for question in questions:
        assert "label" in question, f"pergunta {question.get('id')} não usa a chave 'label'"
        assert "text" not in question, f"pergunta {question.get('id')} usa a chave legada 'text'"
        assert "&lt;" not in json.dumps(question, ensure_ascii=False), (
            f"pergunta {question.get('id')} contém entidade HTML não decodificada"
        )
        # ids devem ser ASCII puro (regressão do bug de digitação com caractere cirílico)
        assert re.fullmatch(r"[a-z0-9_]+", question["id"]), (
            f"id de pergunta não é ASCII/snake_case: {question['id']!r}"
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
            f"{slug}: documento vinculado menciona o tema só {ocorrencias}x — "
            "não parece discussão central de torsades/QT longo adquirido"
        )


def test_farmacologia_excluida_deliberadamente_nao_esta_nos_vinculos():
    item = _load_doencas()[SLUG]
    related = set(item.get("related_document_slugs") or [])
    intersecao = related & FARMACOLOGIA_EXCLUIDOS_DELIBERADAMENTE
    assert intersecao == set(), (
        f"candidato de content/Farmacologia/ vazou para related_document_slugs: {intersecao}"
    )


def test_sem_overlap_com_fichas_irmas_de_qt_longo():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    for irmao in ("canalopatias-cardiacas-hereditarias", "qt-longo-terapia-oncologica"):
        irmao_related = set(doencas[irmao].get("related_document_slugs") or [])
        assert related & irmao_related == set(), (
            f"sobreposição de related_document_slugs com {irmao}: {related & irmao_related}"
        )


def test_sobreposicao_com_hub_arritmias_ventriculares_e_explicitamente_documentada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    hub_slug = "arritmias-ventriculares-e-morte-subita-cardiaca"
    assert hub_slug in doencas
    hub_related = set(doencas[hub_slug].get("related_document_slugs") or [])

    compartilhados_com_hub = related & hub_related
    assert compartilhados_com_hub == EXPECTED_SHARED_WITH_VT_SCD_HUB

    # A duplicação é aceitável somente entre o verbete específico e o hub de
    # arritmias ventriculares/morte súbita. Qualquer nova sobreposição com
    # outra ficha continua quebrando o gate.
    compartilhados_com_outras_fichas = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug in {SLUG, hub_slug}:
            continue
        compartilhados_com_outras_fichas |= (
            related & set(outro_item.get("related_document_slugs") or [])
        )

    assert compartilhados_com_outras_fichas == set(), (
        "sobreposição não documentada fora do hub arritmias-ventriculares-e-morte-subita-cardiaca: "
        f"{compartilhados_com_outras_fichas}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "qt-longo-o-que-significa-e-cuidados-com-medicamentos"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_com_fichas_irmas():
    doencas = _load_doencas()
    assert SLUG != "canalopatias-cardiacas-hereditarias"
    assert SLUG != "qt-longo-terapia-oncologica"
    assert SLUG in doencas


def test_pmids_referenciados_no_source_ref():
    item = _load_doencas()[SLUG]
    refs = " | ".join(item.get("source_refs") or [])
    for pmid in ("41122884", "36017572", "23716032", "20142454", "11735845", "19144938", "14999113", "16554806"):
        assert pmid in refs, f"PMID {pmid} não encontrado em source_refs"
    assert "conferido no PubMed" in refs
