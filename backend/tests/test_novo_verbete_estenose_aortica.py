"""Contrato do verbete NOVO "estenose-aortica" (área geral) criado em
29/08/2026 via doencas/fragmentos/estenose-aortica.json — cobre o espectro
GERAL de estenose aórtica (diagnóstico, gravidade e decisão de intervenção
em todas as idades), complementar à ficha já existente e explicitamente
geriátrica "estenose-aortica-tavi-idoso" (Heart Team, fragilidade e
futilidade no idoso), sem duplicar seu conteúdo.

Nota sobre verificação de citações: todos os 6 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils (esummary) antes da montagem
— nenhuma correção foi necessária.

Nota sobre overlap com "estenose-aortica-tavi-idoso": os 7
related_document_slugs deste verbete novo (diretrizes ESC/EACTS 2021/2025,
fluxogramas de decisão de intervenção/modo/timing, metanálise dos 4 RCTs de
intervenção precoce e durabilidade valvar TAVI em baixo risco) não
compartilham nenhum item com os 7 related_document_slugs já usados por
"estenose-aortica-tavi-idoso" (bloqueio AV pós-TAVI, obstrução coronária
pós-TAVI, choque no idoso e futilidade) — ver teste dedicado abaixo.

Nota sobre overlap com o verbete-hub "valvopatias" (área geral,
prevalence_rank 5, já publicado e revisado): o hub geral referencia quase
todos os documentos da pasta content/Valvopatias/ (~40 related_document_slugs,
incluindo os 8 documentos mapeados como fontes desta rodada), então os 7
related_document_slugs deste verbete específico são, por construção, um
subconjunto do hub — mesmo padrão hub-e-folha já presente no corpus antes
desta rodada (ex.: estenose-aortica-tavi-idoso e outras fichas específicas de
valvopatia já compartilham 1 documento com o hub "valvopatias" cada). O gate
de não-sobreposição não documentada é aplicado apenas entre fichas de doença
específicas (irmãs), excluindo explicitamente o hub geral "valvopatias" desse
comparativo — ver teste dedicado abaixo.
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
SLUG = "estenose-aortica"
SLUG_IDOSO = "estenose-aortica-tavi-idoso"

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

TERMOS_TEMA = ("estenose aórtica", "estenose valvar aórtica", "valva aórtica", "aortic stenosis")


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
    assert item.get("name") == "Estenose aórtica"
    assert "EA" in (item.get("aliases") or [])


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


def test_conteudo_cobre_espectro_geral_nao_apenas_geriatrico():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False).casefold()
    for termo in ("baixo fluxo e baixo gradiente", "bicúspide", "dobutamina", "assintomát"):
        assert termo in serialized, f"conteúdo esperado do espectro geral ausente: {termo!r}"


def test_texto_com_acentuacao_correta_do_portugues():
    item = _load_doencas()[SLUG]
    serialized = json.dumps(item, ensure_ascii=False)
    for palavra in ("não ", "cirúrgico", "décadas", "área valvar"):
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
            f"{slug}: documento vinculado não menciona estenose aórtica no texto"
        )


# O hub geral "valvopatias" (prevalence_rank 5, já publicado) referencia
# quase toda a pasta content/Valvopatias/ e, por isso, sobrepõe por
# construção com qualquer ficha específica de valvopatia — padrão
# hub-e-folha já presente no corpus antes desta rodada (ver nota no topo
# do arquivo). Excluído deliberadamente do comparativo de sobreposição
# entre fichas específicas (irmãs).
HUBS_COM_OVERLAP_ESPERADO = {"valvopatias"}


def test_sem_sobreposicao_nao_documentada_com_outra_ficha_especifica():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])

    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG or outro_slug in HUBS_COM_OVERLAP_ESPERADO:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (related & outros_related)

    assert compartilhados_encontrados == set(), (
        f"sobreposição não documentada com outra ficha específica: {compartilhados_encontrados}"
    )


def test_overlap_com_hub_valvopatias_e_esperado_e_documentado():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    hub = doencas.get("valvopatias")
    assert hub is not None, "hub geral 'valvopatias' deveria continuar existindo"
    hub_related = set(hub.get("related_document_slugs") or [])
    # Todos os related_document_slugs deste verbete específico já são
    # cobertos pelo hub geral — comportamento esperado e documentado, não
    # uma falha de curadoria.
    assert related <= hub_related, (
        "esperava-se que os related_document_slugs deste verbete fossem "
        "subconjunto do hub geral 'valvopatias'; divergência inesperada pode "
        "indicar que o hub mudou e a nota de overlap precisa ser revisada"
    )


def test_patient_material_slug_resolve():
    item = _load_doencas()[SLUG]
    material = item.get("patient_material_slug")
    assert material == "estenose-aortica-e-troca-de-valva"
    materiais = {
        x["slug"]
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert material in materiais, f"patient_material_slug aponta para material inexistente: {material}"


def test_slug_nao_colide_e_nao_duplica_ficha_geriatrica_existente():
    doencas = _load_doencas()
    assert SLUG != SLUG_IDOSO
    assert SLUG_IDOSO in doencas, "ficha geriátrica de referência deveria continuar existindo"

    novo = doencas[SLUG]
    idoso = doencas[SLUG_IDOSO]
    assert novo["area"] == "geral"
    assert idoso["area"] == "cardiogeriatria"

    related_novo = set(novo.get("related_document_slugs") or [])
    related_idoso = set(idoso.get("related_document_slugs") or [])
    assert related_novo.isdisjoint(related_idoso), (
        "verbete geral não deve reaproveitar os related_document_slugs da ficha geriátrica"
    )
