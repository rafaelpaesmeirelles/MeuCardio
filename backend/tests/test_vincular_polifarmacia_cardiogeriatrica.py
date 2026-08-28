"""Contrato do lote "vincular Tudo com Tudo" de 28/08/2026 — ficha já
completa `polifarmacia-e-desprecricao-cardiovascular` (área cardiogeriatria)
em doencas/metadados.json, que tinha apenas 1 related_document_slug
(abaixo do piso mínimo de 3). Este lote SÓ adiciona vínculo — não reescreve
conteúdo clínico já existente.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "polifarmacia-e-desprecricao-cardiovascular"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("polifarmácia", "polifarmacia", "desprescri")

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    # também em hipotensao-ortostatica-no-idoso
    "fluxograma-desprescricao-cardiovascular-no-idoso-polifarmacia-e-fim-de-vida",
    # também em insuficiencia-cardiaca-no-idoso, risco-quedas-cardiogeriatria, anticoagulacao-idoso
    "polifarmacia-cardiovascular-no-idoso-cascata-de-prescricao-e-desprescricao",
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


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    assert item.get("review_status") == "pendente_revisao"
    assert item.get("version") == 2
    assert item.get("review_note")


def test_catalogacao_e_conteudo_clinico_preexistente_preservados():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Polifarmácia e desprescrição cardiovascular"
    assert item.get("area") == "cardiogeriatria"
    assert item.get("category") == "sindrome_geriatrica"
    assert item.get("prevalence_rank") == 1
    assert item.get("completeness") == "completo"


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
            f"{slug}: documento vinculado não menciona polifarmácia/desprescrição no texto"
        )


def test_documentos_compartilhados_sao_os_esperados_e_documentados():
    item = _load_doencas()[SLUG]
    doencas = _load_doencas()
    related = set(item.get("related_document_slugs") or [])

    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (related & outros_related)

    inesperados = compartilhados_encontrados - DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS
    assert inesperados == set(), f"sobreposição não documentada com outra ficha: {inesperados}"
