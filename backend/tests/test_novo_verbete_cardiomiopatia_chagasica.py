"""Contrato do verbete NOVO "cardiomiopatia-chagasica" (área geral) criado
em 29/08/2026 via doencas/fragmentos/cardiomiopatia-chagasica.json — forma
clínica mais comum e mais grave da doença de Chagas, sem ficha própria até
então, apesar de corpus rico já existente em content/Cardiomiopatias/,
content/Dispositivos/, content/Arritmias/ e
content/Cardiologia_do_Esporte_e_do_Exercício/.

Nota sobre verificação de citações: os 8 PMIDs desta rodada foram
verificados individualmente via NCBI e-utils (esummary/esearch) antes da
montagem — nenhuma correção foi necessária.

Nota sobre category: 'cardiomiopatia' segue a mesma convenção adotada em
cardiomiopatia-hipertrofica (PR mergeado em 28/08/2026) e na produção
paralela de cardiomiopatia-dilatada desta mesma sessão.

Nota sobre sobreposição documentada: related_document_slugs aponta para
documentos de conteúdo (content/**/*.md), não para outras fichas de
doença — o mesmo documento pode legitimamente ser citado por mais de uma
ficha quando é central para os dois temas. Levantamento contra o catálogo
combinado (119 registros) encontrou sobreposição pré-existente e
legítima em cinco pares, nenhum deles problemático:
  - 'arritmias-ventriculares-e-morte-subita-cardiaca' compartilha a
    ablação epicárdica de TV e o escore de Rassi/indicação de CDI —
    esperado, o escore de Rassi/CDI cruza as duas fichas.
  - 'cardiomiopatias' (hub geral de cardiomiopatias, PR #565 ainda não
    mergeada nesta base local) compartilha o documento de aneurisma
    apical/trombo/AVC, o de tratamento etiológico e o de escore de
    Rassi/CDI — esperado, o hub geral cobre todas as etiologias.
  - 'acidente-vascular-cerebral-agudo' compartilha o documento de
    aneurisma apical/trombo/AVC cardioembólico — esperado, é a mesma
    complicação vista pelo ângulo do AVC.
  - 'dispositivos-cardiacos-implantaveis' compartilha o documento de
    escore de Rassi/indicação de CDI — esperado, é a mesma indicação
    vista pelo ângulo do dispositivo.
Nenhuma sobreposição foi encontrada com a produção paralela desta mesma
sessão (cardiomiopatia-dilatada, ainda sem fragmento neste worktree no
momento da criação) nem com cardiomiopatia-hipertrofica. O teste
test_sobreposicao_com_outras_fichas_esta_documentada fixa exatamente o
conjunto acima, para que qualquer sobreposição NOVA e não revisada quebre
o gate, e test_sem_overlap_com_cardiomiopatia_dilatada guarda
especificamente contra colisão com a frente paralela.

Nota sobre o gate de review_status (deliberada, ver review_note do
fragmento): este registro fica em review_status='pendente_revisao' e NÃO
foi adicionado à allowlist PENDENTES_LOTES_TUDO_COM_TUDO (hoje vazia) em
backend/tests/test_canonical_content_review_status.py. Por isso,
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
e test_disease_fragments_canonical.py::
test_catalogo_combinado_tem_slugs_unicos_e_status_editorial_explicito
FALHAM para este slug — falha esperada e documentada no relatório da
sessão, não contornada por allowlist.
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
SLUG = "cardiomiopatia-chagasica"

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

TERMOS_TEMA = ("chaga", "trypanosoma cruzi", "rassi")

# Sobreposição documentada e esperada: (slug_da_outra_ficha, doc_compartilhado).
# Ver nota no docstring do módulo.
SOBREPOSICAO_ESPERADA = {
    ("arritmias-ventriculares-e-morte-subita-cardiaca", "ablacao-epicardica-de-taquicardia-ventricular-na-cardiomiopatia-chagasica-e-nao-isquemica"),
    ("arritmias-ventriculares-e-morte-subita-cardiaca", "cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi"),
    ("cardiomiopatias", "tratamento-etiologico-da-doenca-de-chagas-cronica-benznidazol-e-nifurtimox"),
    ("cardiomiopatias", "aneurisma-apical-trombo-de-ve-e-avc-cardioembolico-na-cardiomiopatia-chagasica"),
    ("cardiomiopatias", "cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi"),
    ("acidente-vascular-cerebral-agudo", "aneurisma-apical-trombo-de-ve-e-avc-cardioembolico-na-cardiomiopatia-chagasica"),
    ("dispositivos-cardiacos-implantaveis", "cardiopatia-chagasica-cronica-escore-de-rassi-e-indicacao-de-cdi"),
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
    assert item.get("published") is not True, "registro pendente_revisao não pode estar published=True"


def test_catalogacao():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Cardiomiopatia chagásica crônica"
    assert "CCC" in (item.get("aliases") or [])


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
    for palavra in ("não ", "cardíaca", "súbita", "chagásica", "tromboembólico"):
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
        risk = rule.get("add", {}).get("risk")
        if risk is not None:
            assert risk in {"informativo", "rotina", "prioritario", "urgente", "emergencia"}, (
                f"regra {rule['id']} usa risk inválido: {risk}"
            )


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
            f"{slug}: documento vinculado não menciona cardiomiopatia chagásica no texto"
        )


def test_documento_de_miocardite_aguda_foi_excluido_deliberadamente():
    # Avaliado e excluído por leitura integral: documento é majoritariamente
    # sobre a fase AGUDA da doença de Chagas e sobre miocardites tropicais
    # não-chagásicas, sem seção substantiva sobre progressão para
    # cardiomiopatia crônica. Ver review_note do fragmento.
    item = _load_doencas()[SLUG]
    assert "miocardite-chagasica-aguda-e-miocardites-tropicais-sbc-2022" not in (
        item.get("related_document_slugs") or []
    )


def test_sobreposicao_com_outras_fichas_esta_documentada():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])

    encontrados: set[tuple[str, str]] = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        for doc in (related & outros_related):
            encontrados.add((outro_slug, doc))

    nao_documentados = encontrados - SOBREPOSICAO_ESPERADA
    assert nao_documentados == set(), (
        f"sobreposição NOVA e não documentada com outra ficha: {nao_documentados}"
    )


def test_sem_overlap_com_cardiomiopatia_dilatada():
    # Guarda específica contra colisão com a produção paralela desta mesma
    # sessão (cardiomiopatia-dilatada), pedida explicitamente na missão.
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])
    outro = doencas.get("cardiomiopatia-dilatada")
    if outro is None:
        return
    overlap = related & set(outro.get("related_document_slugs") or [])
    assert overlap == set(), f"overlap não esperado com cardiomiopatia-dilatada: {overlap}"


def test_patient_material_slug_e_null_documentado():
    item = _load_doencas()[SLUG]
    # Não existe material para paciente específico de cardiomiopatia
    # chagásica em material-paciente/metadados.json — ver review_note.
    assert item.get("patient_material_slug") is None
    materiais = {
        str(x["slug"])
        for x in json.loads((REPOSITORY_ROOT / "material-paciente/metadados.json").read_text(encoding="utf-8"))
    }
    assert "cardiomiopatia-chagasica" not in materiais


def test_slug_nao_colide_com_verbete_hub_cardiomiopatias_geral():
    # PR #565 (não mergeada) cria um slug distinto "cardiomiopatias" (hub
    # geral, multiplos_fenotipos) — este verbete é "cardiomiopatia-chagasica"
    # (subtipo/etiologia específica). Garantir que continuam sendo slugs
    # diferentes, e também diferente do slug de cardiomiopatia-hipertrofica
    # e da eventual produção paralela de cardiomiopatia-dilatada.
    assert SLUG not in {"cardiomiopatias", "cardiomiopatia-hipertrofica", "cardiomiopatia-dilatada"}


def test_indicacao_de_cdi_nao_depende_de_feve_isolada():
    # Particularidade clínica central desta doença (ver diagnostic_approach e
    # treatment_summary): ao contrário de outras cardiomiopatias, a indicação
    # de CDI na CCC exige TV documentada, não FEVE isolada. Guarda de
    # regressão simples contra reintrodução acidental dessa simplificação.
    item = _load_doencas()[SLUG]
    diagnostic = item.get("diagnostic_approach") or {}
    serialized = json.dumps(diagnostic, ensure_ascii=False).casefold()
    assert "taquicardia ventricular" in serialized
    assert "cdi" in serialized or "cardioversor-desfibrilador" in serialized
