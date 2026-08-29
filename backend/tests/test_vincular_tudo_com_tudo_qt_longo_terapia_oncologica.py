"""Contrato do lote "vincular Tudo com Tudo" de 29/08/2026 — ficha
`qt-longo-terapia-oncologica` (área cardiooncologia) em doencas/metadados.json.

ACHADO desta rodada: o registro *base* em doencas/metadados.json não tem
`related_document_slugs` (campo ausente) e `completeness: basico` — é o que
motivou a tarefa. Mas o registro *composto* (o que o produto realmente lê,
via `load_disease_records`, que aplica `doencas/correcoes/*.json` por cima
da base) já está completo: o patch
`doencas/correcoes/zz-release36h-pr656-qt-longo-terapia-oncologica.json`
(mesclado em 28/08/2026, commit 798bb8d5, "39º lote de conteúdo do dia")
já eleva `completeness` para `completo`, `review_status` para `revisado`, e
já preenche `related_document_slugs` com exatamente os 6 documentos que o
briefing desta tarefa listou como candidatos.

Ou seja: este lote não precisou adicionar nenhum vínculo — a regra Tudo com
Tudo já estava satisfeita pela composição, um dia antes de esta tarefa ser
aberta. Este teste NÃO altera doencas/metadados.json; ele apenas trava o
estado composto correto como regressão, documentando o achado, para que uma
edição futura no patch de correção (ou sua remoção) não volte a descumprir
a regra silenciosamente.
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
    / "doencas/correcoes/zz-release36h-pr656-qt-longo-terapia-oncologica.json"
)
SLUG = "qt-longo-terapia-oncologica"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("qt", "qtc", "torsades", "prolongamento")

VINCULOS_ESPERADOS = {
    "prolongamento-de-qt-por-inibidores-de-cdk4-6-ribociclibe-palbociclibe-e-abemaciclibe",
    "fluxograma-prolongamento-qt-por-ribociclibe-e-risco-de-torsades",
    "prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio",
    "fluxograma-prolongamento-de-qt-e-torsades-por-trioxido-de-arsenio",
    "inibidor-de-menina-revumenibe-prolongamento-de-qtc-e-sindrome-de-diferenciacao",
    "lista-de-quimioterapicos-de-risco-de-prolongamento-do-qt-e-monitorizacao",
}

# related_document_slugs compartilhados legitimamente com outras fichas de
# cardiotoxicidade, que também citam a lista geral de quimioterápicos de
# risco de QT como referência transversal.
DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "lista-de-quimioterapicos-de-risco-de-prolongamento-do-qt-e-monitorizacao",
}


def _load_doencas() -> dict[str, dict]:
    return {item["slug"]: item for item in load_disease_records(DOENCAS_PATH)}


def _base_records() -> dict[str, dict]:
    payload = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return {item["slug"]: item for item in payload if isinstance(item, dict)}


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


def test_registro_base_esta_no_estado_que_motivou_a_tarefa():
    """Documenta o ponto de partida: base sem related_document_slugs."""
    base = _base_records()[SLUG]
    assert base.get("related_document_slugs") in (None, [])
    assert base.get("completeness") == "basico"


def test_patch_de_correcao_dedicado_existe_e_resolve_a_regra():
    assert CORRECAO_PATH.exists(), (
        "Patch doencas/correcoes/zz-release36h-pr656-qt-longo-terapia-oncologica.json "
        "não encontrado — se ele foi removido/renomeado, o registro composto pode ter "
        "voltado a violar a regra Tudo com Tudo; reabrir o lote de vínculo."
    )
    payload = json.loads(CORRECAO_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    entradas = [item for item in payload if item.get("slug") == SLUG]
    assert len(entradas) == 1
    conjunto = entradas[0].get("set", {})
    assert set(conjunto.get("related_document_slugs") or []) == VINCULOS_ESPERADOS


def test_marcacao_editorial_do_registro_composto():
    item = _load_doencas()[SLUG]
    assert item.get("review_status") == "revisado"
    assert item.get("completeness") == "completo"
    assert item.get("version") == 2


def test_catalogacao_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("area") == "cardiooncologia"
    assert item.get("category") == "arritmia"


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"
    assert set(related) == VINCULOS_ESPERADOS

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    dentro_do_escopo = [
        slug for slug in related
        if "Cardio-oncologia" not in str(documentos[slug])
    ]
    assert dentro_do_escopo == [], f"related_document_slugs fora de Cardio-oncologia: {dentro_do_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona QT/QTc/torsades no texto"
        )


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    doencas = _load_doencas()
    item = doencas[SLUG]
    related = set(item.get("related_document_slugs") or [])

    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (related & outros_related)

    inesperados = compartilhados_encontrados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), f"sobreposição não documentada com outra ficha: {inesperados}"
