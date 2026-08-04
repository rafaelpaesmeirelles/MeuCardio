"""Protege o total canônico das 11 coleções e o baseline científico."""

from app.api.library import (
    CATALOG_FRONTS,
    SCIENTIFIC_CORPUS_MINIMUM,
    SCIENTIFIC_FILES_EXPECTED,
    catalog,
)
from app.commands.reconcile_content import FRONTS as RECONCILIATION_FRONTS
from app.commands.reconcile_content import SCIENTIFIC_MINIMUM


MODELS_BY_KEY = {key: model for key, _, _, model in CATALOG_FRONTS}


class _ConsultaFalsa:
    def __init__(self, total: int):
        self.total = total

    def filter(self, *_args, **_kwargs):
        return self

    def count(self) -> int:
        return self.total


class _SessaoFalsa:
    def __init__(self, contagens: dict[type, int]):
        self.contagens = contagens

    def query(self, modelo):
        return _ConsultaFalsa(self.contagens.get(modelo, 0))


def _contagens_no_minimo() -> dict[type, int]:
    return {
        MODELS_BY_KEY[key]: int(config["minimum"])
        for key, config in RECONCILIATION_FRONTS.items()
    }


def test_baseline_do_catalogo_nao_diverge_do_reconciliador():
    assert SCIENTIFIC_CORPUS_MINIMUM == SCIENTIFIC_MINIMUM == 4_936
    assert set(MODELS_BY_KEY) == set(RECONCILIATION_FRONTS)


def test_catalogo_soma_as_onze_frentes_e_expõe_baselines():
    resposta = catalog(db=_SessaoFalsa(_contagens_no_minimo()), _=object())

    assert len(resposta["fronts"]) == 11
    assert resposta["total"] == SCIENTIFIC_CORPUS_MINIMUM
    assert resposta["inventory_total"] == SCIENTIFIC_CORPUS_MINIMUM
    assert resposta["expected_minimum"] == 4_936
    assert resposta["physical_files_expected"] == 1_327
    assert resposta["integrity_ok"] is True
    assert resposta["missing"] == 0
    assert resposta["below_minimum"] == {}
    assert all(frente["integrity_ok"] for frente in resposta["fronts"])


def test_excedente_em_uma_frente_nao_mascara_deficit_em_outra():
    contagens = _contagens_no_minimo()
    contagens[MODELS_BY_KEY["documentos"]] += 1
    contagens[MODELS_BY_KEY["emergencia"]] -= 1

    resposta = catalog(db=_SessaoFalsa(contagens), _=object())

    # O agregado ainda é 4.936, mas emergência está abaixo do mínimo próprio.
    assert resposta["total"] == SCIENTIFIC_CORPUS_MINIMUM
    assert resposta["integrity_ok"] is False
    assert resposta["missing"] == 1
    assert resposta["below_minimum"] == {
        "emergencia": {
            "inventory_count": RECONCILIATION_FRONTS["emergencia"]["minimum"] - 1,
            "minimum": RECONCILIATION_FRONTS["emergencia"]["minimum"],
            "missing": 1,
        }
    }
    emergencia = next(f for f in resposta["fronts"] if f["key"] == "emergencia")
    assert emergencia["integrity_ok"] is False
    assert emergencia["missing"] == 1


def test_catalogo_denuncia_reducao_real_do_corpus():
    contagens = _contagens_no_minimo()
    contagens[MODELS_BY_KEY["evidencias"]] -= 37

    resposta = catalog(db=_SessaoFalsa(contagens), _=object())

    assert resposta["integrity_ok"] is False
    assert resposta["missing"] == 37
    assert resposta["physical_files_expected"] == SCIENTIFIC_FILES_EXPECTED
