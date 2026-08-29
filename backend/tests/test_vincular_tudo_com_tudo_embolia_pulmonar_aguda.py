"""Contrato do lote "vincular Tudo com Tudo" (enriquecimento) de 29/08/2026
— ficha já completa `embolia-pulmonar-aguda` (área geral, categoria
tromboembolismo) em doencas/metadados.json, que atendia apenas 2 dos 3
related_document_slugs mínimos exigidos pela regra Tudo com Tudo, apesar de
existir corpus rico de TEP grave/maciça-submaciça em content/Tromboembolismo/
ainda não vinculado (um PR anterior, #544, tentou aprofundar esta ficha mas
ficou obsoleto/superado por main sem nunca ter tocado related_document_slugs).

Este lote SÓ adiciona vínculo — não reescreve conteúdo clínico já existente,
e não altera review_status nem completeness.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "embolia-pulmonar-aguda"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("tep", "embolia pulmonar", "tromboembolismo pulmonar")

SLUGS_ORIGINAIS = {
    "aha-acc-2026-tep-agudo-categorias-clinicas-anticoagulacao-e-terapias-avancadas",
    "tratamento-farmacologico-do-tep-diretriz-brasileira-sbpt-2025-grade",
}
SLUGS_NOVOS = {
    "fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise",
    "trombolise-sistemica-em-dose-reduzida-no-tep-de-risco-intermediario-o-ensaio-mopett",
    "trombectomia-mecanica-versus-anticoagulacao-isolada-no-tep-de-risco-intermediario-alto-storm-pe",
    "terapia-dirigida-por-cateter-no-tep-peerless-e-o-que-ainda-nao-esta-respondido",
    "filtro-de-veia-cava-inferior-recuperavel-no-tep-agudo-o-ensaio-prepic2",
}


def _load_doencas() -> dict[str, dict]:
    items = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


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
    assert SLUG in _load_doencas()


def test_marcacao_editorial_preservada_review_status_e_completeness():
    item = _load_doencas()[SLUG]
    assert item.get("review_status") == "revisado", (
        "este lote não deve alterar review_status (regra explícita da tarefa)"
    )
    assert item.get("completeness") == "completo", (
        "este lote não deve alterar completeness (regra explícita da tarefa)"
    )
    assert item.get("review_note")


def test_catalogacao_e_conteudo_clinico_preexistente_preservados():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Embolia pulmonar aguda"
    assert item.get("category") == "tromboembolismo"
    assert item.get("patient_material_slug") == (
        "embolia-pulmonar-o-que-aconteceu-com-meu-pulmao-e-o-que-esperar-da-recuperacao"
    )


def test_vinculos_originais_foram_preservados():
    item = _load_doencas()[SLUG]
    related = set(item.get("related_document_slugs") or [])
    faltando = SLUGS_ORIGINAIS - related
    assert faltando == set(), f"vínculos originais removidos: {faltando}"


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"
    assert len(related) == 7, "lote deveria fechar em exatamente 7 vínculos (piso relaxado ao máximo permitido)"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"

    assert set(related) == SLUGS_ORIGINAIS | SLUGS_NOVOS


def test_novos_vinculos_vem_de_content_tromboembolismo():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in SLUGS_NOVOS:
        caminho = str(documentos[slug])
        assert "content/Tromboembolismo/" in caminho, f"{slug}: esperado em content/Tromboembolismo/, achado em {caminho}"


def test_novos_vinculos_mencionam_tema_central_de_tep_agudo_grave():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in SLUGS_NOVOS:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona TEP/embolia pulmonar no texto"
        )


def test_novos_vinculos_cobrem_as_quatro_frentes_de_diversidade_pedidas():
    """Estratificação de risco, trombólise sistêmica, trombectomia/terapia
    dirigida por cateter e filtro de veia cava — conforme pedido na tarefa."""
    assert "fluxograma-tep-agudo-estratificacao-de-risco-e-decisao-de-trombolise" in SLUGS_NOVOS
    assert "trombolise-sistemica-em-dose-reduzida-no-tep-de-risco-intermediario-o-ensaio-mopett" in SLUGS_NOVOS
    assert {
        "trombectomia-mecanica-versus-anticoagulacao-isolada-no-tep-de-risco-intermediario-alto-storm-pe",
        "terapia-dirigida-por-cateter-no-tep-peerless-e-o-que-ainda-nao-esta-respondido",
    } <= SLUGS_NOVOS
    assert "filtro-de-veia-cava-inferior-recuperavel-no-tep-agudo-o-ensaio-prepic2" in SLUGS_NOVOS


def test_nenhuma_outra_ficha_de_doenca_compartilha_os_novos_vinculos():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])

    compartilhados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados |= (related & outros_related)

    assert compartilhados == set(), f"sobreposição não documentada com outra ficha: {compartilhados}"


def test_pr544_nao_deixou_related_document_slugs_desatualizado_sem_deteccao():
    """Documenta a checagem feita antes deste lote: o PR #544 (aberto,
    'feat: aprofundar embolia pulmonar aguda') tentou aprofundar esta ficha,
    mas seu diff efetivo contra origin/main atual está vazio em
    doencas/metadados.json (branch obsoleta/superada por outros merges) —
    ele nunca chegou a elevar related_document_slugs acima de 2. A lacuna
    verificada por load_disease_records() era real e não um artefato de
    patch em doencas/correcoes/*.json."""
    item = _load_doencas()[SLUG]
    assert len(item.get("related_document_slugs") or []) > 2
