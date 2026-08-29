"""Contrato do lote "vincular Tudo com Tudo" de 29/08/2026 — ficha já
completa `avaliacao-cardiovascular-pre-concepcional` (área gravidez,
categoria planejamento_reprodutivo) em doencas/metadados.json, cuja base
JSON tinha 0 related_document_slugs apesar de completeness="completo" —
inconsistência do dataset apontada na tarefa. Este lote SÓ adiciona
vínculo na base — não reescreve conteúdo clínico já existente e não
altera review_status nem completeness.

Achado importante, verificado e coberto por teste dedicado abaixo:
`doencas/correcoes/zz-release36h-pr648-avaliacao-cardiovascular-pre-
concepcional.json` (ligado à PR #648, aberta, base
`release/all-science-36h-20260828`, mergeable=CONFLICTING) já sobrescreve
por completo este registro via `load_disease_records`, incluindo
`related_document_slugs` com uma lista *diferente* da adicionada por
este lote. Ou seja: o registro EFETIVO servido pelo app (composição
base + correções) já não tinha 0 vínculos antes deste lote — só a base
JSON crua tinha. Este lote corrige a base por completude e
rastreabilidade (e é o padrão pedido pela frente "vincular Tudo com
Tudo"), mas o vínculo efetivamente ativo em produção continua sendo o
do patch até decisão editorial reconciliar os dois. Não contornado:
apenas documentado e testado.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.disease_manifest import load_disease_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
CORRECAO_PATH = (
    REPOSITORY_ROOT
    / "doencas/correcoes/zz-release36h-pr648-avaliacao-cardiovascular-pre-concepcional.json"
)
SLUG = "avaliacao-cardiovascular-pre-concepcional"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = (
    "pré-concepcional",
    "pre-concepcional",
    "pré-concepção",
    "pregnancy heart team",
    "planejamento familiar",
)

VINCULOS_ADICIONADOS_NESTE_LOTE = [
    "escores-de-risco-materno-carpreg-carpreg-ii-e-zahara",
    "anticoncepcao-na-mulher-com-cardiopatia-criterios-de-elegibilidade-da-oms-posicionamento-sbc-2020",
    "fluxograma-doenca-cardiovascular-e-gravidez-esc-2025",
    "preditores-de-recuperacao-ventricular-e-aconselhamento-pre-concepcional-na-cardiomiopatia-periparto",
]

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    # cardiopatia-congenita-gravidez também cita os escores CARPREG/ZAHARA
    "escores-de-risco-materno-carpreg-carpreg-ii-e-zahara",
    # hipertensao-pulmonar-gravidez também cita a elegibilidade contraceptiva da OMS
    "anticoncepcao-na-mulher-com-cardiopatia-criterios-de-elegibilidade-da-oms-posicionamento-sbc-2020",
    # cardiomiopatia-periparto e seguimento-cardiovascular-pos-parto também citam
    # os preditores de recuperação ventricular / aconselhamento pré-concepcional
    "preditores-de-recuperacao-ventricular-e-aconselhamento-pre-concepcional-na-cardiomiopatia-periparto",
}


def _load_base_records() -> dict[str, dict]:
    """Lê doencas/metadados.json cru, SEM aplicar doencas/correcoes/*.json.

    Usado para verificar exatamente o que este lote escreveu na base —
    diferente de `_load_effective_records`, que reflete o que o app
    realmente serve (base + correções compostas).
    """
    payload = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return {item["slug"]: item for item in payload if isinstance(item, dict) and item.get("slug")}


def _load_effective_records() -> dict[str, dict]:
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


def test_ficha_continua_existindo_com_mesmo_slug():
    assert SLUG in _load_base_records()
    assert SLUG in _load_effective_records()


def test_marcacao_editorial_nao_foi_alterada():
    base = _load_base_records()[SLUG]
    # O lote NÃO altera review_status nem completeness — só o vínculo (e o
    # version/review_note de rastreabilidade, seguindo o padrão dos lotes
    # anteriores desta frente).
    assert base.get("review_status") == "revisado"
    assert base.get("completeness") == "completo"
    assert base.get("version") == 2


def test_catalogacao_preservada():
    base = _load_base_records()[SLUG]
    assert base.get("area") == "gravidez"
    assert base.get("category") == "planejamento_reprodutivo"
    assert base.get("subtype") == "pre_concepcao"
    assert base.get("prevalence_rank") == 1


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    base = _load_base_records()[SLUG]
    documentos = _all_document_paths()

    related = base.get("related_document_slugs") or []
    assert related == VINCULOS_ADICIONADOS_NESTE_LOTE
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"

    # Todos os 4 vínculos devem estar na pasta Gravidez (mesma pasta do tema).
    fora_de_gravidez = [slug for slug in related if "Gravidez" not in str(documentos[slug])]
    assert fora_de_gravidez == [], f"vínculo fora de content/Gravidez: {fora_de_gravidez}"


def test_related_document_slugs_mencionam_tema():
    base = _load_base_records()[SLUG]
    documentos = _all_document_paths()
    for slug in base.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona aconselhamento/avaliação pré-concepcional no texto"
        )


def test_candidato_estratificacao_esc_2018_foi_corretamente_descartado():
    """O candidato `doenca-cardiovascular-na-gravidez-estratificacao-de-risco-
    e-manejo-esc-2018-sbc-2020` foi avaliado e descartado: é conteúdo em boa
    parte intra-gestacional (limiares de anti-hipertensivo, anticoagulação,
    cardiomiopatia periparto, via de parto) com apenas uma menção lateral a
    "avaliação pré-concepção" num bullet de lista, sem seção substantiva
    dedicada ao aconselhamento pré-concepcional. Este teste garante que ele
    não foi incluído por engano."""
    base = _load_base_records()[SLUG]
    related = base.get("related_document_slugs") or []
    assert "doenca-cardiovascular-na-gravidez-estratificacao-de-risco-e-manejo-esc-2018-sbc-2020" not in related


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    base_records = _load_base_records()
    related = set(base_records[SLUG].get("related_document_slugs") or [])

    compartilhados_encontrados: set[str] = set()
    for outro_slug, outro_item in base_records.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (related & outros_related)

    inesperados = compartilhados_encontrados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), f"sobreposição não documentada com outra ficha: {inesperados}"


def test_patch_correcoes_pr648_existe_e_mascara_o_vinculo_deste_lote():
    """Regressão do achado documentado no docstring do módulo: um patch de
    correção pré-existente, ligado a uma PR ainda aberta (#648) baseada em
    outra branch, sobrescreve por completo o registro (inclusive
    related_document_slugs) na composição efetiva servida pelo app. Se esse
    patch for removido ou reconciliado no futuro sem que alguém note esta
    nota, o comportamento efetivo do app muda silenciosamente — por isso
    fica testado, não só narrado."""
    assert CORRECAO_PATH.exists(), (
        "patch doencas/correcoes/zz-release36h-pr648-...json não encontrado — "
        "se foi removido/reconciliado, o vínculo da base finalmente passa a valer "
        "no registro efetivo; atualize esta nota e o teste."
    )

    correcoes = json.loads(CORRECAO_PATH.read_text(encoding="utf-8"))
    patch_do_slug = next(item for item in correcoes if item.get("slug") == SLUG)
    vinculos_do_patch = patch_do_slug["set"]["related_document_slugs"]

    base = _load_base_records()[SLUG]
    efetivo = _load_effective_records()[SLUG]

    assert base.get("related_document_slugs") == VINCULOS_ADICIONADOS_NESTE_LOTE
    assert efetivo.get("related_document_slugs") == vinculos_do_patch
    assert efetivo.get("related_document_slugs") != base.get("related_document_slugs"), (
        "o patch parou de mascarar o vínculo da base — condição mudou, revisar nota editorial"
    )
