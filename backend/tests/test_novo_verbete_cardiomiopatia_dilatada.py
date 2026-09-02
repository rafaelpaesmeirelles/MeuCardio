"""Contrato do verbete NOVO "cardiomiopatia-dilatada" (área geral) criado
em 29/08/2026 via doencas/fragmentos/cardiomiopatia-dilatada.json — a
cardiomiopatia não isquêmica mais prevalente, sem ficha própria até então,
apesar de corpus rico já existente em content/Cardiomiopatias/. Distinta de
cardiomiopatia-hipertrofica (mesma category='cardiomiopatia', subtype
diferente: 'dilatada' vs. hipertrófica não usa subtype específico) — sem
nenhum related_document_slugs compartilhado entre as duas.

Nota sobre verificação de citações: todos os 8 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils antes da montagem — nenhuma
correção foi necessária.

Nota sobre related_document_slugs: reduzido de 7 propostos para 6 finais —
o 7º candidato, um documento cujo tema central é miocardite, foi excluído
por a menção à cardiomiopatia dilatada ser apenas uma progressão minoritária
de desfecho dentro do texto, não o tema central do documento (ver
review_note do fragmento).

Nota sobre category: 'cardiomiopatia' segue a mesma convenção do hub geral
'cardiomiopatias' (PR #565) e do verbete cardiomiopatia-hipertrofica. Os
slugs são distintos e este teste documenta explicitamente a sobreposição
intencional de 5 dos 6 documentos nucleares de CMD entre o verbete
específico e o hub de cardiomiopatias, além de sobreposições pontuais e
pré-existentes com cardiomiopatia-periparto, seguimento-cardiovascular-
pos-parto e taquicardia-supraventricular.

Nota: gate test_canonical_content_review_status.py falha intencionalmente
(review_status='pendente_revisao'; política vigente desde 28/08/2026 não
admite mais allowlist para registros não revisados).
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
SLUG = "cardiomiopatia-dilatada"

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

TERMOS_TEMA = ("cardiomiopatia dilatada", "cmd", "dilated cardiomyopathy")

# Sobreposição legítima e pré-existente: 5 dos 6 documentos nucleares de CMD
# também aparecem no hub geral 'cardiomiopatias', no verbete de cardiomiopatia
# periparto, no verbete de seguimento cardiovascular pós-parto e no verbete de
# taquicardia supraventricular — cada um cobre o mesmo documento sob um recorte
# clínico legítimo e distinto. Apenas cardiomiopatia-alcoolica não é
# compartilhado com nenhuma outra ficha.
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "cardiomiopatia-dilatada-cmd-diagnostico-genetico-e-manejo-esc-2023",  # também no hub cardiomiopatias
    "fluxograma-cardiomiopatia-dilatada-investigacao-etiologica",  # também no hub cardiomiopatias
    "fluxograma-cardiomiopatia-dilatada-risco-de-morte-subita-e-cdi",  # também no hub cardiomiopatias
    "taquicardiomiopatia-cardiomiopatia-induzida-por-taquicardia-reconhecimento-e-reversibilidade",  # também no hub cardiomiopatias e em taquicardia-supraventricular
    "cardiomiopatia-periparto-criterios-diagnosticos-recuperacao-e-manejo",  # também no hub cardiomiopatias, em cardiomiopatia-periparto e em seguimento-cardiovascular-pos-parto
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
    assert item.get("subtype") == "dilatada"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Cardiomiopatia dilatada"
    assert "CMD" in (item.get("aliases") or [])


def test_slug_nao_colide_com_cardiomiopatia_hipertrofica():
    doencas = _load_doencas()
    assert SLUG != "cardiomiopatia-hipertrofica"
    assert SLUG in doencas
    assert "cardiomiopatia-hipertrofica" in doencas
    dilatada = doencas[SLUG]
    hipertrofica = doencas["cardiomiopatia-hipertrofica"]
    # Mesma category (convenção do hub cardiomiopatias), subtype distinto.
    assert dilatada.get("category") == hipertrofica.get("category") == "cardiomiopatia"
    assert dilatada.get("subtype") == "dilatada"
    assert dilatada.get("subtype") != hipertrofica.get("subtype")
    # Nenhum related_document_slugs compartilhado entre os dois verbetes específicos.
    compartilhados = set(dilatada.get("related_document_slugs") or []) & set(
        hipertrofica.get("related_document_slugs") or []
    )
    assert compartilhados == set()


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

    def _collect_ops(node, ops: set[str]) -> None:
        if isinstance(node, dict):
            if "op" in node:
                ops.add(node["op"])
            for key in ("all", "any"):
                if key in node:
                    _collect_ops(node[key], ops)
        elif isinstance(node, list):
            for child in node:
                _collect_ops(child, ops)

    ops_usados: set[str] = set()
    for rule in rules:
        bad = set(rule.get("add", {}).keys()) - ALLOWED_ADD_KEYS
        assert not bad, f"regra {rule['id']} usa chaves não permitidas em add: {bad}"
        assert "monitoring" not in rule.get("add", {}), f"regra {rule['id']} usa chave inválida 'monitoring' em add"
        _collect_ops(rule.get("when", {}), ops_usados)

    assert "includes" not in ops_usados, "operador 'includes' não é válido no motor de regras"


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

    assert "miocardite-diagnostico-estratificacao-de-risco-e-biopsia-endomiocardica-esc-2025" not in related, (
        "candidato descartado (miocardite não é o tema central) não deveria ter sido incluído"
    )


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona cardiomiopatia dilatada/CMD no texto"
        )


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


def test_sem_sobreposicao_especifica_com_cardiomiopatia_hipertrofica():
    doencas = _load_doencas()
    related = set(doencas[SLUG].get("related_document_slugs") or [])
    hipertrofica_related = set(doencas["cardiomiopatia-hipertrofica"].get("related_document_slugs") or [])
    assert related & hipertrofica_related == set()


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "cardiomiopatia-dilatada-por-que-o-coracao-aumenta-de-tamanho"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"
