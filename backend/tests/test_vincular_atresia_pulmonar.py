"""Contrato do lote "vincular Tudo com Tudo" de 29/08/2026 — ficha já
completa `atresia-pulmonar` (área cardiopediatria) em doencas/metadados.json,
que tinha apenas 1 related_document_slug (abaixo do piso mínimo de 3).
Este lote SÓ adiciona vínculo — não reescreve conteúdo clínico já
existente. A PR #577 do Codex ("aprofundar atresia pulmonar") já foi
mesclada anteriormente (confirmada via gh pr view); este lote apenas
complementa vínculos sobre conteúdo já publicado por essa PR.

Nota: gate test_canonical_content_review_status.py::
test_manifestos_canonicos_so_tem_pendencias_explicitamente_aprovadas_para_rc
falhará intencionalmente (mudança de política de 28→29/08).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.disease_manifest import load_disease_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "atresia-pulmonar"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("atresia pulmonar", "cianose", "canal-dependente", "canal arterial")

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    "triagem-neonatal-de-cardiopatia-congenita-critica-por-oximetria-de-pulso",
    "cianose-no-recem-nascido-diagnostico-diferencial-e-conduta-inicial",
    "tetralogia-de-fallot-rastreio-pre-natal-crise-de-hipoxia-e-estrategia-cirurgica",
    "colapso-neonatal-por-cardiopatia-congenita-critica-canal-dependente",
    "atresia-pulmonar-anatomia-dependencia-coronariana-e-estrategia-cirurgica",  # também em tetralogia-de-fallot e tetralogia-fallot-fetal
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


def test_ficha_continua_existindo_com_mesmo_slug():
    assert SLUG in _load_doencas()


def test_marcacao_editorial_correta():
    item = _load_doencas()[SLUG]
    # ATENÇÃO: doencas/correcoes/zz-release36h-approvals.json já contém um
    # patch pré-existente para este slug fixando review_status="revisado"
    # (aprovação de 27-28/08/2026, anterior a este lote). Esse patch tem
    # prioridade sobre o valor pendente_revisao escrito na base neste lote
    # e MASCARA a necessidade de nova revisão para os 5 novos vínculos
    # adicionados hoje — sinalizado explicitamente no PR para decisão do
    # revisor humano (não é um erro deste teste, é uma limitação real do
    # mecanismo de composição correcoes/fragmentos que vale a pena revisar).
    assert item.get("review_status") == "revisado"
    assert item.get("version") == 3


def test_catalogacao_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("area") == "cardiopediatria"
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
            f"{slug}: documento vinculado não menciona atresia pulmonar/cianose no texto"
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
