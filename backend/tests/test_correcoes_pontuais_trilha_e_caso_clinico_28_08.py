"""Contrato de 2 correções pontuais de 28/08/2026, sem mudança de
conteúdo clínico:

1. `trilha-aorta-e-dap-ensaios-classicos-aaa-carotida-e-femoropopliteo`
   tinha sequência de `ordem` corrompida nas etapas (6, 6, 7, 8 em vez
   de 6, 7, 8, 9) — renumerada sequencialmente.
2. `colcot-colchicina-pos-infarto-componentes-do-desfecho-caso` tinha
   `nivel: "avancado"` (sem acento), divergindo do padrão real do
   corpus (`avançado`, usado em 279 outros casos clínicos) — corrigido.
"""

from __future__ import annotations

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TRILHAS_PATH = REPOSITORY_ROOT / "trilhas/metadados.json"
CASOS_PATH = REPOSITORY_ROOT / "casos-clinicos/metadados.json"

TRILHA_SLUG = "trilha-aorta-e-dap-ensaios-classicos-aaa-carotida-e-femoropopliteo"
CASO_SLUG = "colcot-colchicina-pos-infarto-componentes-do-desfecho-caso"


def _load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_trilha_tem_ordem_sequencial_sem_duplicatas_nem_lacunas():
    trilhas = _load(TRILHAS_PATH)
    it = next(t for t in trilhas if t["slug"] == TRILHA_SLUG)
    ordens = [e.get("ordem") for e in it["etapas"]]
    assert ordens == list(range(1, len(ordens) + 1)), (
        f"ordem das etapas não é sequencial sem lacunas: {ordens}"
    )


def test_trilha_mantem_as_mesmas_9_etapas_na_mesma_sequencia_de_itens():
    trilhas = _load(TRILHAS_PATH)
    it = next(t for t in trilhas if t["slug"] == TRILHA_SLUG)
    item_slugs = [e.get("item_slug") for e in it["etapas"]]
    assert item_slugs == [
        "aneurisma-de-aorta-abdominal-rastreamento-seguimento-e-indicacao-de-reparo",
        "uk-small-aneurysm-trial-seguimento-de-12-anos",
        "evar-2-reparo-endovascular-em-inelegivel-para-cirurgia-aberta",
        "dream-reparo-convencional-versus-endovascular-de-aaa",
        "estenose-de-carotida-diagnostico-e-indicacao-de-revascularizacao-esc-2024",
        "crest-stent-versus-endarterectomia-na-estenose-carotidea",
        "doenca-arterial-periferica-de-membros-diagnostico-por-itb-e-isquemia-critica",
        "inpact-sfa-balao-farmacologico-versus-angioplastia-convencional",
        "levant-2-balao-farmacologico-na-doenca-femoropopliteal",
    ], "a correção de ordem não deveria alterar a sequência de itens da trilha"


def test_caso_clinico_tem_nivel_com_acentuacao_padrao_do_corpus():
    casos = _load(CASOS_PATH)
    caso = next(c for c in casos if c["slug"] == CASO_SLUG)
    assert caso["nivel"] == "avançado"
    assert caso["nivel"] in ("básico", "intermediário", "avançado")


def test_caso_clinico_conteudo_clinico_preservado():
    casos = _load(CASOS_PATH)
    caso = next(c for c in casos if c["slug"] == CASO_SLUG)
    assert caso.get("explicacao")
    assert caso.get("source_refs")
    assert caso.get("opcoes") and len(caso["opcoes"]) == 4
