"""Contrato editorial do lote Tudo com Tudo sobre colapso súbito/PCR."""

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTO_PCR = "parada-cardiorrespiratoria-no-adulto-suporte-avancado-sbc-2019"
FLUXOGRAMA_PCR = "fluxograma-parada-cardiorrespiratoria-ritmo-inicial"


def _por_slug(relative_path: str) -> dict[str, dict]:
    items = json.loads((REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8"))
    return {item["slug"]: item for item in items}


def test_lote_colapso_pcr_preserva_revisao_humana_e_fontes_primarias():
    triagem = _por_slug("triagem-sintomas/metadados.json")[
        "colapso-subito-inconsciencia-e-respiracao-anormal"
    ]
    doenca = _por_slug("doencas/metadados.json")[
        "parada-cardiorrespiratoria-e-morte-subita-abortada"
    ]
    checklist = _por_slug("checklists/metadados.json")[
        "resposta-imediata-ao-colapso-subito-e-suspeita-de-parada-no-adulto"
    ]
    material = _por_slug("material-paciente/metadados.json")[
        "colapso-subito-como-reconhecer-parada-e-usar-o-dea"
    ]

    assert {triagem["review_status"], doenca["review_status"], checklist["review_status"], material["review_status"]} == {
        "pendente_revisao"
    }
    assert all("cpr.heart.org" in url or "ahajournals.org" in url or "abccardiol.org" in url for url in triagem["source_urls"])
    assert all("cpr.heart.org" in url or "ahajournals.org" in url or "abccardiol.org" in url for url in doenca["source_urls"])


def test_lote_colapso_pcr_tem_cadeia_direta_sem_relacoes_inventadas():
    triagem = _por_slug("triagem-sintomas/metadados.json")[
        "colapso-subito-inconsciencia-e-respiracao-anormal"
    ]
    doenca = _por_slug("doencas/metadados.json")[
        "parada-cardiorrespiratoria-e-morte-subita-abortada"
    ]
    checklist = _por_slug("checklists/metadados.json")[
        "resposta-imediata-ao-colapso-subito-e-suspeita-de-parada-no-adulto"
    ]
    material = _por_slug("material-paciente/metadados.json")[
        "colapso-subito-como-reconhecer-parada-e-usar-o-dea"
    ]
    emergencia = _por_slug("emergencia/metadados.json")["parada-cardiorrespiratoria"]
    evidencias = _por_slug("evidencias/metadados.json")
    trilhas = _por_slug("trilhas/metadados.json")

    # O casamento doença↔triagem é exato e não depende de fuzzy matching.
    assert doenca["name"] == "Parada cardiorrespiratória"
    assert triagem["differentials"].count(doenca["name"]) == 1

    # Os novos nós apontam para os mesmos objetos canônicos já publicados.
    assert {DOCUMENTO_PCR, FLUXOGRAMA_PCR} <= set(doenca["related_document_slugs"])
    assert checklist["documento_origem"] == DOCUMENTO_PCR
    assert material["documento_slug"] == DOCUMENTO_PCR
    assert doenca["patient_material_slug"] == material["slug"]
    assert emergencia["documento_slug"] == DOCUMENTO_PCR
    assert emergencia["fluxograma_slug"] == FLUXOGRAMA_PCR

    # Evidências e trilha já existentes fecham a cadeia por referência estruturada.
    assert any(item.get("document_slug") == DOCUMENTO_PCR for item in evidencias.values())
    assert any(item.get("document_slug") == FLUXOGRAMA_PCR for item in evidencias.values())
    trilha_pcr = trilhas["trilha-parada-cardiorrespiratoria-e-cuidados-pos-parada"]
    slugs_da_trilha = {etapa["item_slug"] for etapa in trilha_pcr["etapas"]}
    assert {DOCUMENTO_PCR, FLUXOGRAMA_PCR} <= slugs_da_trilha


def test_estudos_de_pcr_permanecem_proximidade_tematica_declarada():
    estudos = _por_slug("estudos/metadados.json")

    # Não há campo editorial estudo↔doença neste schema; estes nós são do mesmo
    # tema e não devem ser promovidos artificialmente a relação clínica direta.
    for slug in (
        "ttm2-hipotermia-versus-normotermia-pos-parada-cardiorrespiratoria",
        "paramedic2-adrenalina-parada-extra-hospitalar",
    ):
        assert estudos[slug]["theme"] == "Terapia intensiva"
        assert estudos[slug]["review_status"] == "revisado"

