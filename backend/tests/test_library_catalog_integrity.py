"""Protege o total canônico das 11 coleções e o baseline científico."""

from app.api.library import (
    CATALOG_FRONTS,
    SCIENTIFIC_CORPUS_MINIMUM,
    SCIENTIFIC_FILES_EXPECTED,
    catalog,
)


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


def _contagens_com_total(total: int) -> dict[type, int]:
    contagens = {modelo: 0 for _, _, _, modelo in CATALOG_FRONTS}
    contagens[CATALOG_FRONTS[0][3]] = total
    return contagens


def test_catalogo_soma_as_onze_frentes_e_expõe_baselines():
    resposta = catalog(
        db=_SessaoFalsa(_contagens_com_total(SCIENTIFIC_CORPUS_MINIMUM)),
        _=object(),
    )

    assert len(resposta["fronts"]) == 11
    assert resposta["total"] == SCIENTIFIC_CORPUS_MINIMUM
    assert resposta["expected_minimum"] == 4_936
    assert resposta["physical_files_expected"] == 1_327
    assert resposta["integrity_ok"] is True
    assert resposta["missing"] == 0


def test_catalogo_denuncia_reducao_do_corpus():
    resposta = catalog(
        db=_SessaoFalsa(_contagens_com_total(SCIENTIFIC_CORPUS_MINIMUM - 37)),
        _=object(),
    )

    assert resposta["integrity_ok"] is False
    assert resposta["missing"] == 37
    assert resposta["physical_files_expected"] == SCIENTIFIC_FILES_EXPECTED
