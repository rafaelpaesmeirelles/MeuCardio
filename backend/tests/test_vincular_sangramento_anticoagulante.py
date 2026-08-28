"""Contrato do lote "vincular Tudo com Tudo" de 28/08/2026 — ficha já
completa `sangramento-relacionado-a-anticoagulante` (área geral) em
doencas/metadados.json, que tinha apenas 2 related_document_slugs (abaixo
do piso mínimo de 3). Este lote SÓ adiciona vínculo — não reescreve
conteúdo clínico já existente.

Nota: o agente de pesquisa propôs 4 candidatos, mas 3 (o fluxograma de
reversão emergencial, e as monografias de idarucizumabe e protamina)
resolvem para content/Farmacologia — pasta explicitamente fora do escopo
permitido pela regra Tudo com Tudo. Apenas 1 candidato genuíno foi aceito,
levando o total ao piso mínimo exato de 3.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "sangramento-relacionado-a-anticoagulante"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("sangramento", "hemorragia", "reversão", "reversao", "anticoagul")


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
    assert item.get("version") == 3
    assert item.get("review_note")


def test_catalogacao_e_conteudo_clinico_preexistente_preservados():
    item = _load_doencas()[SLUG]
    assert item.get("name") == "Sangramento relacionado a anticoagulante"
    assert item.get("area") == "geral"
    assert item.get("category") == "seguranca_antitrombotica"
    assert item.get("prevalence_rank") == 1
    assert item.get("completeness") == "completo"
    assert item.get("epidemiology")
    assert item.get("treatment_summary") or item.get("diagnostic_approach")


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

    novo_slug = "reversao-de-anticoagulante-em-sangramento-maior-idarucizumabe-e-andexanet-alfa"
    assert novo_slug in related


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona sangramento/hemorragia/reversão/anticoagulação no texto"
        )
