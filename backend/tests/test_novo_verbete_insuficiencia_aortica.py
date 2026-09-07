"""Contrato do verbete NOVO "insuficiencia-aortica" (área geral) criado em
29/08/2026 via doencas/fragmentos/insuficiencia-aortica.json — insuficiência
aórtica (regurgitação aórtica crônica e aguda) não tinha ficha própria em
doencas/metadados.json, apesar de corpus já existente em
content/Valvopatias/ e content/Terapia_intensiva/.

Nota sobre verificação de citações: os 7 PMIDs desta rodada foram verificados
individualmente via NCBI e-utils (esummary) antes da montagem do
source_refs, todos concordantes com os documentos-fonte (sem divergência de
título/volume/página/DOI a corrigir).

Nota sobre review_status: este registro permanece "pendente_revisao" — não
foi revisado por humano. Por isso
test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
FALHA para este slug (comportamento esperado e documentado no review_note do
próprio registro e no relatório
docs/novo-verbete-insuficiencia-aortica-2026-08-29.md — não é bug e não deve
ser contornado). A entrada correspondente em PENDENTES_LOTES_TUDO_COM_TUDO
foi adicionada apenas porque essa allowlist é reaproveitada também por
test_disease_fragments_canonical.py, onde a checagem funciona corretamente.

Nota sobre escopo: o registro "insuficiencia-mitral" (criado no mesmo dia,
branch claude/novo-verbete-insuficiencia-mitral-20260829) foi lido por
completo antes de iniciar esta ficha e confirmado como exclusivamente sobre
a valva mitral, sem overlap de escopo com esta ficha de valva aórtica.
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
SLUG = "insuficiencia-aortica"

MIN_LIST_ITEMS = {
    "presentation": 8,
    "differentials": 5,
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

TERMOS_TEMA = ("aórtica", "aortica", "aórtico", "aortico")

# Sobreposição esperada e documentada no review_note: o hub geral 'valvopatias'
# cita os mesmos 3 documentos centrais de regurgitação aórtica, e a ficha
# pediátrica de valva bicúspide compartilha o documento de elegibilidade
# esportiva (única seção que discute RA nesse documento).
EXPECTED_OVERLAP_BY_SLUG = {
    "valvopatias": {
        "regurgitacao-aortica-cronica-e-aguda-indicacao-cirurgica-esceacts-2021",
        "regurgitacao-aortica-nativa-grave-tratamento-transcateter-dedicado-align-ar-trilogy",
        "fluxograma-insuficiencia-aortica-cronica-grave-quando-intervir-esc-eacts-2025",
    },
    "valva-aortica-bicuspide-pediatrica": {
        "doenca-valvar-elegibilidade-esportiva-no-atleta",
    },
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
    assert item.get("category") == "valvopatia"
    assert item.get("review_note")
    assert item.get("source_refs") and len(item["source_refs"]) >= 5
    assert item.get("version") == 1


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Insuficiência aórtica"
    assert "Regurgitação aórtica" in (item.get("aliases") or [])


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


def test_cobre_forma_cronica_e_aguda():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False).casefold()
    assert "crônica" in serialized or "cronica" in serialized
    assert "aguda" in serialized
    assert "endocardite" in serialized
    assert "dissecção" in serialized or "disseccao" in serialized
    assert "iabp" in serialized or "balão intra-aórtico" in serialized


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "cardíaca", "válvula", "ventrículo", "dissecção", "aórtica"):
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


def test_regra_iabp_contraindicado_gera_emergencia():
    item = _load_doencas()[SLUG]
    rules = {rule["id"]: rule for rule in item.get("assistant_rules") or []}
    assert "ia_aguda_iabp_contraindicado" in rules
    regra = rules["ia_aguda_iabp_contraindicado"]
    assert regra["add"]["risk"] == "emergencia"
    assert regra["priority"] >= 90


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
            f"{slug}: documento vinculado menciona termos de insuficiência/regurgitação "
            f"aórtica só {ocorrencias}x — não parece discussão central do tema"
        )


def test_sobreposicao_de_related_document_slugs_e_explicitamente_documentada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])

    encontrados: dict[str, set[str]] = {}
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        overlap = related & set(outro_item.get("related_document_slugs") or [])
        if overlap:
            encontrados[outro_slug] = overlap

    esperado = {slug: overlap for slug, overlap in EXPECTED_OVERLAP_BY_SLUG.items() if overlap}
    assert encontrados == esperado, (
        "sobreposição de related_document_slugs diverge do documentado no review_note: "
        f"encontrado={encontrados} esperado={esperado}"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "regurgitacao-aortica-quando-a-valvula-vaza-e-quando-operar"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_com_ficha_mitral_nem_com_hub_valvopatias():
    doencas = _load_doencas()
    assert SLUG != "insuficiencia-mitral"
    assert SLUG != "valvopatias"
    if "insuficiencia-mitral" in doencas:
        mitral = doencas["insuficiencia-mitral"]
        # A ficha mitral (frente paralela, mesma data) não deve citar este
        # slug aórtico nem compartilhar related_document_slugs com ele.
        assert SLUG not in (mitral.get("related_document_slugs") or [])
        item = doencas[SLUG]
        overlap = set(item.get("related_document_slugs") or []) & set(
            mitral.get("related_document_slugs") or []
        )
        assert overlap == set(), f"overlap inesperado com insuficiencia-mitral: {overlap}"
