"""Contrato do lote "vincular Tudo com Tudo" de 29/08/2026 — ficha já
completa `parada-cardiorrespiratoria-e-morte-subita-abortada` (área geral)
em doencas/metadados.json, que tinha apenas 4 related_document_slugs
enquanto existe corpus rico de cuidados pós-parada em
content/Terapia_intensiva/ não vinculado. Este lote SÓ adiciona vínculo —
não reescreve conteúdo clínico já existente, nem review_status, nem
completeness.

Dos 8 candidatos mapeados em content/Terapia_intensiva/, foram escolhidos
3 para completar o teto de 7 (regra Tudo com Tudo), priorizando diversidade
temática e ancoragem textual direta no próprio verbete:
- neuroprognóstico multimodal (o verbete já cita "Evitar neuroprognóstico
  prematuro e usar avaliação multimodal no momento apropriado" em
  diagnostic_approach.apos_retorno_da_circulacao)
- coronariografia sem supra de ST — COACT/TOMAHAWK (o verbete já cita
  "avaliação coronariana individualizada" em emergency_flow)
- RCP extracorpórea (eCPR) na parada refratária — ARREST/INCEPTION
  (cobre o cenário de parada refratária, ausente nos 4 vínculos originais)

Descartados por redundância temática com o vínculo já existente de
controle de temperatura (controle-de-temperatura-pos-parada-...-ttm-e-ttm2):
hipotermia em ritmo não chocável (HYPERION) e metas de PA/oxigenação (BOX).
Descartados por já estarem cobertos em essência pelos vínculos escolhidos
ou por prioridade de diversidade sobre volume (regra "Rafael prioriza
descoberta sobre volume"): o protocolo-guarda-chuva AHA 2025 de cuidados
pós-parada (que recobre coronariografia/temperatura/neuroprognóstico já
representados de forma mais específica pelos 3 escolhidos), o fluxograma
de coronariografia (redundante com o documento de evidência COACT/TOMAHAWK
já escolhido) e o documento de via aérea/PARAMEDIC2 (foco em técnica de
RCP pré-hospitalar, não em cuidado pós-parada, tema já coberto pelos
vínculos de suporte avançado e DEA já existentes).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.services.disease_manifest import load_disease_records


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOENCAS_PATH = REPOSITORY_ROOT / "doencas/metadados.json"
SLUG = "parada-cardiorrespiratoria-e-morte-subita-abortada"

PASTAS_NAO_DOCUMENTO = ("Farmacologia", "Calculadoras", "Exames")
TERMOS_TEMA = ("parada cardiorrespiratória", "parada cardíaca", "pós-parada", "pós-pcr", "rosc", "reanimação")

VINCULOS_ORIGINAIS = {
    "parada-cardiorrespiratoria-no-adulto-suporte-avancado-sbc-2019",
    "fluxograma-parada-cardiorrespiratoria-ritmo-inicial",
    "dea-cadeia-de-sobrevivencia-e-plano-de-emergencia-no-esporte",
    "controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2",
}

VINCULOS_NOVOS = {
    "neuroprognostico-multimodal-pos-parada-cardiorrespiratoria-algoritmo-erc-esicm-2021-e-a-atualizacao-aha-2025",
    "coronariografia-imediata-apos-parada-cardiaca-sem-supra-de-st-coact-e-tomahawk",
    "rcp-extracorporea-ecpr-na-parada-refrataria-arrest-e-inception",
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


def test_marcacao_editorial_preservada():
    item = _load_doencas()[SLUG]
    # Este lote NÃO altera review_status nem completeness, apenas
    # related_document_slugs (e review_note/version, como nos demais lotes
    # desta frente). Nenhum patch em doencas/correcoes/ sobrescreve este
    # slug (confirmado por busca no diretório antes do commit).
    assert item.get("review_status") == "revisado"
    assert item.get("version") == 3


def test_catalogacao_preservada():
    item = _load_doencas()[SLUG]
    assert item.get("area") == "geral"
    assert item.get("completeness") == "completo"
    assert item.get("patient_material_slug") == "colapso-subito-como-reconhecer-parada-e-usar-o-dea"


def test_vinculos_originais_preservados():
    item = _load_doencas()[SLUG]
    related = set(item.get("related_document_slugs") or [])
    faltantes = VINCULOS_ORIGINAIS - related
    assert faltantes == set(), f"vínculo original removido indevidamente: {faltantes}"


def test_vinculos_tudo_com_tudo_resolvem_e_sao_documentos_narrativos():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()

    related = item.get("related_document_slugs") or []
    assert 3 <= len(related) <= 7, "regra Tudo com Tudo pede entre 3 e 7 links"
    assert len(related) == 7, "lote deveria completar exatamente o teto de 7 (4 originais + 3 novos)"

    nao_resolvidos = [slug for slug in related if slug not in documentos]
    assert nao_resolvidos == [], f"related_document_slugs aponta para documento inexistente: {nao_resolvidos}"

    fora_de_escopo = [
        slug for slug in related
        if any(pasta in str(documentos[slug]) for pasta in PASTAS_NAO_DOCUMENTO)
    ]
    assert fora_de_escopo == [], f"related_document_slugs aponta para fora do escopo permitido: {fora_de_escopo}"

    assert len(related) == len(set(related)), "related_document_slugs contém duplicatas"


def test_novos_vinculos_sao_exatamente_os_esperados():
    item = _load_doencas()[SLUG]
    related = set(item.get("related_document_slugs") or [])
    novos = related - VINCULOS_ORIGINAIS
    assert novos == VINCULOS_NOVOS, f"conjunto de novos vínculos divergente: {novos}"


def test_novos_vinculos_estao_em_terapia_intensiva():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in VINCULOS_NOVOS:
        assert "Terapia_intensiva" in str(documentos[slug]), f"{slug}: esperado em content/Terapia_intensiva/"


def test_related_document_slugs_mencionam_tema():
    item = _load_doencas()[SLUG]
    documentos = _all_document_paths()
    for slug in item.get("related_document_slugs") or []:
        texto = documentos[slug].read_text(encoding="utf-8", errors="replace").casefold()
        assert any(termo in texto for termo in TERMOS_TEMA), (
            f"{slug}: documento vinculado não menciona parada cardiorrespiratória/pós-parada no texto"
        )


def test_documentos_novos_nao_se_sobrepoem_a_outras_fichas():
    # Nenhuma outra ficha do catálogo referenciava estes 3 documentos antes
    # deste lote (verificado por varredura no momento da escolha); este
    # teste garante que a sobreposição continua zero, e não precisa de
    # lista de exceções como em outros lotes desta frente.
    doencas = _load_doencas()
    item = doencas[SLUG]
    novos = VINCULOS_NOVOS

    compartilhados_encontrados = set()
    for outro_slug, outro_item in doencas.items():
        if outro_slug == SLUG:
            continue
        outros_related = set(outro_item.get("related_document_slugs") or [])
        compartilhados_encontrados |= (novos & outros_related)

    assert compartilhados_encontrados == set(), (
        f"sobreposição não documentada com outra ficha: {compartilhados_encontrados}"
    )
