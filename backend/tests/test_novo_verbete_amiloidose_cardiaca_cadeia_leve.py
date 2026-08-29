"""Contrato do verbete NOVO "amiloidose-cardiaca-cadeia-leve" (área geral) criado
em 29/08/2026 via doencas/fragmentos/amiloidose-cardiaca-cadeia-leve.json.

Contexto: já existe no catálogo a ficha "amiloidose-cardiaca-idoso", mas ela é
genuinamente focada em amiloidose por TRANSTIRRETINA (ATTR) — aliases ("ATTR
cardíaca"), tags (tafamidis, transtirretina selvagem, cintilografia óssea,
amiloidose hereditária) e conteúdo (algoritmo diagnóstico ATTR, ATTR-ACT) não
cobrem a amiloidose de CADEIA LEVE (AL) de forma central; AL aparece ali só
como critério de exclusão, um parágrafo de contraste e uma nota explícita
remetendo a "conteúdo específico já publicado no acervo sobre o ensaio
ANDROMEDA... sem duplicação aqui". Este verbete novo preenche essa lacuna.

DECISÃO EDITORIAL SENSÍVEL: dado o risco de sobreposição percebido com a
ficha já publicada "amiloidose-cardiaca-idoso", este registro usa
review_status="pendente_revisao" DELIBERADAMENTE (não "revisado" como nos
verbetes anteriores). Isso é esperado e correto: o gate
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este registro, e por extensão o mesmo acontece com
test_disease_fragments_canonical.py::
test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito,
porque os dois testes compartilham a mesma allowlist
PENDENTES_LOTES_TUDO_COM_TUDO importada de test_canonical_content_review_status.
Nenhuma entrada foi adicionada a essa allowlist nesta rodada — a falha fica
visível e documentada, aguardando aval humano explícito do Rafael, em vez de
ser contornada.

Nota sobre verificação de citações: os 4 PMIDs desta rodada (34192431,
41353737, 36697326, 38095141) foram verificados individualmente via NCBI
e-utils (esummary/efetch) antes da montagem — nenhuma correção foi
necessária.
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
SLUG = "amiloidose-cardiaca-cadeia-leve"
SLUG_ATTR_IDOSO = "amiloidose-cardiaca-idoso"

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

TERMOS_TEMA = ("amiloidose", "amiloide")
TERMOS_AL = ("cadeia leve", " al ", " al)", " al,", " al-", "al-ca", "al-iss")

# Documentos que discutem lado a lado a exclusão de AL antes de fechar
# diagnóstico de ATTR — pertencem organicamente à ficha ATTR já existente
# (amiloidose-cardiaca-idoso) e também, como conteúdo nuclear de amiloidose
# cardíaca em geral, ao hub geral "cardiomiopatias". Overlap intencional e
# documentado, no mesmo padrão já usado por cardiomiopatia-hipertrofica em
# relação a esse mesmo hub.
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "diagnostico-e-tratamento-da-amiloidose-cardiaca",
    "fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo",
}
FICHAS_COM_OVERLAP_ESPERADO = {SLUG, SLUG_ATTR_IDOSO, "cardiomiopatias"}


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


def test_slug_nao_colide_com_ficha_attr_existente():
    doencas = _load_doencas()
    assert SLUG != SLUG_ATTR_IDOSO
    assert SLUG_ATTR_IDOSO in doencas, "amiloidose-cardiaca-idoso não deveria ter sido alterada/removida"
    # As duas fichas coexistem como registros distintos e completos.
    attr = doencas[SLUG_ATTR_IDOSO]
    al = doencas[SLUG]
    assert attr["slug"] != al["slug"]
    assert attr["name"] != al["name"]


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("fonte_producao") == "claude"
    # Deliberadamente pendente: decisão de escopo/taxonomia que exige aval
    # humano explícito antes de publicação, dado o risco de sobreposição
    # percebido com amiloidose-cardiaca-idoso. NÃO é "revisado".
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("completeness") == "completo"
    assert item.get("area") == "geral"
    assert item.get("category") == "cardiomiopatia"
    # Mesma category da ficha ATTR já existente, por consistência taxonômica
    # (exigência explícita desta rodada).
    assert item.get("category") == _load_doencas()[SLUG_ATTR_IDOSO].get("category")
    assert item.get("review_note")
    assert "pendente_revisao" in item["review_note"] or "aval" in item["review_note"].lower()
    assert item.get("source_refs") and len(item["source_refs"]) >= 4
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Amiloidose cardíaca por cadeia leve (AL)"
    aliases = item.get("aliases") or []
    assert "Amiloidose AL" in aliases
    # Não deve se autodenominar ATTR em nenhum alias.
    serialized_aliases = json.dumps(aliases, ensure_ascii=False).casefold()
    assert "attr" not in serialized_aliases


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
    for palavra in ("não ", "cardíaca", "discrasia", "dispneia", "próprio"):
        assert palavra in serialized, f"acentuação ausente: {palavra!r} não encontrada"


def test_diferencial_inclui_attr_como_entidade_distinta():
    item = _load_doencas()[SLUG]
    differentials = item.get("differentials") or []
    serializado = json.dumps(differentials, ensure_ascii=False).casefold()
    assert "attr" in serializado, "differentials deveria citar ATTR explicitamente"
    assert "distint" in serializado, (
        "differentials deveria deixar claro que ATTR é entidade distinta coberta em ficha própria"
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


def test_regra_de_seguranca_impede_confundir_al_com_attr():
    """A pior armadilha clínica desta doença é tratar AL como se fosse ATTR
    (ou vice-versa). O assistente precisa ter uma regra que reage quando a
    tipagem histológica aponta para ATTR, redirecionando para a ficha certa.
    """
    item = _load_doencas()[SLUG]
    rules = item.get("assistant_rules") or []
    serializado = json.dumps(rules, ensure_ascii=False).casefold()
    assert "transtirretina_attr" in serializado or "attr" in serializado
    assert any("attr" in json.dumps(rule.get("add", {}), ensure_ascii=False).casefold() for rule in rules)


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

    # A calculadora AL-ISS (content/Calculadoras/...) discute AL de forma
    # central, mas foi excluída por regra de pasta — confirma exclusão.
    assert "al-iss-estadiamento-internacional-da-amiloidose-al-cardiaca-2026" not in related


def test_related_document_slugs_mencionam_amiloidose_al_centralmente():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona amiloidose no texto"
        )
        assert any(termo in texto for termo in TERMOS_AL), (
            f"{slug}: documento vinculado não discute cadeia leve/AL especificamente"
        )


def test_sobreposicao_com_ficha_attr_e_explicitamente_documentada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    attr_ficha = doencas[SLUG_ATTR_IDOSO]
    attr_related = set(attr_ficha.get("related_document_slugs") or [])

    compartilhados = related & attr_related
    assert compartilhados == DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS

    # cardiomiopatias (hub geral) também cita os mesmos dois documentos
    # nucleares de amiloidose cardíaca — overlap legítimo e esperado, mesmo
    # padrão do verbete cardiomiopatia-hipertrofica em relação a esse hub.
    hub = doencas.get("cardiomiopatias")
    if hub is not None:
        compartilhados_hub = related & set(hub.get("related_document_slugs") or [])
        assert compartilhados_hub == DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS

    # Sobreposição com qualquer outra ficha do catálogo (fora as já
    # documentadas acima) continua quebrando o gate.
    compartilhados_com_outras_fichas: set[str] = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug in FICHAS_COM_OVERLAP_ESPERADO:
            continue
        compartilhados_com_outras_fichas |= (
            related & set(outro_item.get("related_document_slugs") or [])
        )
    assert compartilhados_com_outras_fichas == set(), (
        "sobreposição não documentada fora das fichas amiloidose-cardiaca-idoso/cardiomiopatias: "
        f"{compartilhados_com_outras_fichas}"
    )


def test_patient_material_slug_resolve_e_reuso_e_documentado():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    # Reaproveita o material já usado por amiloidose-cardiaca-idoso: o texto
    # em linguagem simples já cobre os dois tipos (ATTR e AL) — reúso
    # intencional, documentado em review_note, não um erro de cópia.
    assert material == "amiloidose-cardiaca"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
    assert item.get("review_note") and "reaproveita" in item["review_note"].lower()


def test_pmids_citados_em_source_refs_estao_presentes():
    item = _load_doencas()[SLUG]
    serializado = " ".join(item.get("source_refs") or [])
    for pmid in ("34192431", "41353737", "36697326", "38095141"):
        assert pmid in serializado, f"PMID {pmid} não encontrado em source_refs"
