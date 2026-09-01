"""Regressões da consolidação científica de agosto de 2026.

Os testes são deliberadamente independentes de banco: protegem os aliases
retirados do manifesto, a migração do progresso persistido e os links Markdown
servidos pela Biblioteca antes que a reconciliação toque o PostgreSQL.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.api.library import _library_document_links
from app.commands.reconcile_content import _migrate_study_track_progress
from app.services.study_slug_aliases import (
    STUDY_SLUG_ALIASES,
    canonical_study_slug,
    canonicalize_study_slugs,
)


ROOT = Path(__file__).resolve().parents[2]

ALIASES_DEDUPLICACAO_RELEASE = {
    "deliver-dapagliflozina-icfep":
        "deliver-consistencia-por-faixa-de-feve-nao-e-reclassificacao-2026",
    "paragon-hf-sacubitril-valsartana-na-icfep":
        "paragon-hf-neutro-e-a-faixa-45-49-nao-e-paradigm",
    "finearts-hf-finerenona-na-icfem-e-icfep":
        "finearts-hf-populacao-feve-maior-igual-40-faixa-historica-icfei",
    "summit-tirzepatida-icfep-com-obesidade":
        "tirzepatida-e-icfep-com-obesidade-o-ensaio-summit",
    "advor-acetazolamida-diuretico-ic-aguda-descompensada":
        "advor-mullens-2022-acetazolamida-iv-descongestao-apos-alca",
    "select-lincoff-semaglutida-24mg-mace-obesidade-sem-diabetes":
        "select-semaglutida-desfechos-cardiovasculares-obesidade-sem-diabetes",
    "clorotic-hidroclorotiazida-associada-a-diuretico-de-alca-na-ic-aguda":
        "clorotic-trullas-2023-hctz-oral-add-on-furosemida-iv",
    "peitho-fibrinolise-em-tep-de-risco-intermediario":
        "peitho-tenecteplase-versus-placebo-tep-normotenso-vd-e-troponina",
}


def test_aliases_apontam_apenas_para_estudos_canonicos_publicaveis():
    estudos = json.loads((ROOT / "estudos" / "metadados.json").read_text(encoding="utf-8"))
    slugs = {item["slug"] for item in estudos}

    assert STUDY_SLUG_ALIASES
    assert set(STUDY_SLUG_ALIASES).isdisjoint(slugs)
    assert set(STUDY_SLUG_ALIASES.values()) <= slugs
    assert all(item["review_status"] == "revisado" for item in estudos)


def test_oito_estudos_deduplicados_preservam_compatibilidade_de_slug():
    estudos = json.loads((ROOT / "estudos" / "metadados.json").read_text(encoding="utf-8"))
    por_slug = {item["slug"]: item for item in estudos}
    slugs = set(por_slug)

    assert len(ALIASES_DEDUPLICACAO_RELEASE) == 8
    assert {
        antigo: STUDY_SLUG_ALIASES.get(antigo)
        for antigo in ALIASES_DEDUPLICACAO_RELEASE
    } == ALIASES_DEDUPLICACAO_RELEASE
    assert set(ALIASES_DEDUPLICACAO_RELEASE).isdisjoint(slugs)
    assert set(ALIASES_DEDUPLICACAO_RELEASE.values()) <= slugs
    assert all(
        por_slug[canonico]["published"] is True
        and por_slug[canonico]["review_status"] == "revisado"
        for canonico in ALIASES_DEDUPLICACAO_RELEASE.values()
    )
    assert canonicalize_study_slugs(list(ALIASES_DEDUPLICACAO_RELEASE)) == sorted(
        set(ALIASES_DEDUPLICACAO_RELEASE.values())
    )


def test_trilhas_nao_preservam_slug_de_estudo_apos_consolidacao():
    trilhas = json.loads((ROOT / "trilhas" / "metadados.json").read_text(encoding="utf-8"))
    estudos = json.loads((ROOT / "estudos" / "metadados.json").read_text(encoding="utf-8"))
    slugs_de_estudo = {item["slug"] for item in estudos}
    etapas_de_estudo = [
        etapa["item_slug"]
        for trilha in trilhas
        for etapa in trilha.get("etapas", [])
        if etapa.get("item_type") == "estudo"
    ]

    assert not (set(etapas_de_estudo) & set(STUDY_SLUG_ALIASES))
    assert set(etapas_de_estudo) <= slugs_de_estudo


def test_canonicalizacao_migra_alias_e_remove_duplicata():
    antigo, canonico = next(iter(STUDY_SLUG_ALIASES.items()))

    assert canonical_study_slug(antigo) == canonico
    assert canonical_study_slug(canonico) == canonico
    assert canonicalize_study_slugs([antigo, canonico, canonico]) == [canonico]


class _Progress:
    def __init__(self, concluidas):
        self.concluidas = concluidas


class _Query:
    def __init__(self, progressos):
        self._progressos = progressos

    def all(self):
        return self._progressos


class _Session:
    def __init__(self, progressos):
        self._progressos = progressos

    def query(self, _model):
        return _Query(self._progressos)


def test_migracao_persiste_aliases_duplicatas_e_ordem_canonica():
    antigo, canonico = next(iter(STUDY_SLUG_ALIASES.items()))
    progresso_alias = _Progress([antigo, canonico])
    progresso_duplicado = _Progress([canonico, canonico])
    progresso_ordenacao = _Progress(["z", "a"])

    atualizados = _migrate_study_track_progress(
        _Session([progresso_alias, progresso_duplicado, progresso_ordenacao])
    )

    assert atualizados == 3
    assert progresso_alias.concluidas == [canonico]
    assert progresso_duplicado.concluidas == [canonico]
    assert progresso_ordenacao.concluidas == ["a", "z"]


def test_migracao_canonicaliza_alias_dentro_da_identidade_composta():
    antigo, canonico = next(iter(STUDY_SLUG_ALIASES.items()))
    progresso = _Progress([f"estudo:{antigo}", f"estudo:{canonico}"])

    atualizados = _migrate_study_track_progress(_Session([progresso]))

    assert atualizados == 1
    assert progresso.concluidas == [f"estudo:{canonico}"]


def test_biblioteca_converte_so_links_markdown_relativos_para_documentos():
    corpo = (
        "[local](../Arritmias/fluxograma-fa.md) "
        "[local com âncora](subpasta/pericardite.md#tratamento) "
        "[externo](https://example.test/artigo.md) "
        "[absoluto](/biblioteca/documento) [âncora](#secao)"
    )

    convertido = _library_document_links(corpo)

    assert "[local](/biblioteca/fluxograma-fa)" in convertido
    assert "[local com âncora](/biblioteca/pericardite#tratamento)" in convertido
    assert "[externo](https://example.test/artigo.md)" in convertido
    assert "[absoluto](/biblioteca/documento)" in convertido
    assert "[âncora](#secao)" in convertido
