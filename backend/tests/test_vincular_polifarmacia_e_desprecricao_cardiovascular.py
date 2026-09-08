"""Contrato do lote "vincular Tudo com Tudo" de 29/08/2026 — ficha
`polifarmacia-e-desprecricao-cardiovascular` (área cardiogeriatria) em
doencas/metadados.json.

Achado importante, sem paralelo exato nos lotes-irmãos de hoje
(persistencia-canal-arterial, atresia-pulmonar): o registro BASE em
metadados.json tinha apenas 1 related_document_slug e version=1, mas a
visão CANÔNICA (via load_disease_records, que é o que app.main e os
gates realmente consomem) já estava, antes deste lote, em version=2,
review_status="revisado" e com os MESMOS 4 related_document_slugs que
este lote adiciona — via um patch pré-existente em
`doencas/correcoes/zz-release36h-pr660-polifarmacia-e-desprecricao-cardiovascular.json`
(parte do commit `798bb8d5 "release: integrar e revisar toda produção
científica das últimas 36h"`).

Esse patch é o rastro de uma tentativa anterior idêntica: PR #660
("vincular Tudo com Tudo em polifarmacia-e-desprecricao-cardiovascular",
28/08/2026), fechada por Rafael sem merge com o comentário "Conteúdo já
revisado e integrado em produção via pipeline consolidador [...]
confirmado em main com review_status=revisado e os mesmos valores desta
branch. Fechando por redundância, sem merge desta PR." De fato, os 3
vínculos e o texto de review_note do patch coincidem com os da PR #660.

Este lote de 29/08 chegou de forma independente (candidatos fornecidos
pelo orquestrador não citavam a PR #660 nem o patch) aos mesmos 3
vínculos por leitura direta de cada candidato — convergência que reforça
a validade da escolha, não uma cópia. A diferença real deste lote: ele
sincroniza o registro BASE de metadados.json com o que o patch já
impunha, para que a visão canônica deixe de depender do patch para
mostrar os vínculos corretos (o patch continua presente e tecnicamente
redundante agora — decisão sobre removê-lo fica para o revisor humano,
fora do escopo deste lote, que só adiciona vínculo).

Os testes abaixo validam a visão CANÔNICA (load_disease_records), que já
passava antes deste lote por causa do patch — o que muda, de fato
verificável no diff de metadados.json, é que a fonte BASE agora tem os
mesmos 4 related_document_slugs, e não apenas 1.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.disease_manifest import load_disease_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "polifarmacia-e-desprecricao-cardiovascular"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("polifarmácia", "desprescri")

DOCUMENTOS_COMPARTILHADOS_COM_OUTRAS_FICHAS = {
    # também em hipotensao-ortostatica-no-idoso
    "fluxograma-desprescricao-cardiovascular-no-idoso-polifarmacia-e-fim-de-vida",
    # vínculo original; também em insuficiencia-cardiaca-no-idoso,
    # risco-quedas-cardiogeriatria e anticoagulacao-idoso
    "polifarmacia-cardiovascular-no-idoso-cascata-de-prescricao-e-desprescricao",
}


def _base_record() -> dict:
    payload = json.loads(DOENCAS_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    for item in payload:
        if item.get("slug") == SLUG:
            return item
    raise AssertionError(f"{SLUG} não encontrado no manifesto base")


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


def test_marcacao_editorial_correta_na_visao_canonica():
    item = _load_doencas()[SLUG]
    # review_status NÃO foi alterado por este lote (instrução explícita).
    # Já era "revisado" antes deste lote (base + patch concordavam nisso).
    assert item.get("review_status") == "revisado"
    assert item.get("version") == 2
    assert item.get("review_note")


def test_registro_base_foi_sincronizado_com_o_patch_pre_existente():
    """O registro BASE (sem composição de correções) tinha apenas 1
    related_document_slug e version=1 antes deste lote. Este teste
    verifica que a fonte base agora já carrega os mesmos 4 vínculos que
    a visão canônica sempre mostrou via patch — ver nota do módulo."""
    base = _base_record()
    assert base.get("version") == 2
    related_base = base.get("related_document_slugs") or []
    assert 3 <= len(related_base) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"
    assert set(related_base) == set(_load_doencas()[SLUG]["related_document_slugs"]), (
        "registro base deveria estar sincronizado com a visão canônica "
        "(hoje imposta pelo patch zz-release36h-pr660-*.json)"
    )


def test_catalogacao_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("area") == "cardiogeriatria"
    assert item.get("category") == "sindrome_geriatrica"
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


def test_candidatos_descartados_por_mencao_lateral_nao_foram_incluidos():
    """Os 3 candidatos avaliados e descartados (fragilidade, metas
    terapêuticas no muito idoso, comprometimento cognitivo) mencionam
    polifarmácia apenas de forma lateral (item de lista sobre síndromes
    geriátricas / critério de exclusão de ensaio), sem discussão central
    de desprescrição — não devem estar entre os vínculos."""
    item = _load_doencas()[SLUG]
    related = set(item.get("related_document_slugs") or [])
    descartados = {
        "fragilidade-como-modificador-de-decisao-cardiovascular",
        "metas-terapeuticas-cardiovasculares-no-muito-idoso",
        "comprometimento-cognitivo-e-demencia-como-modificador-de-decisao-cardiovascular",
    }
    assert related.isdisjoint(descartados), (
        f"candidato descartado por menção lateral acabou incluído: {related & descartados}"
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
