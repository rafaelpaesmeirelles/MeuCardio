"""Regressões do descobrimento da planilha oficial CMED."""

import pytest

from app.services import cmed_precos


class _Resposta:
    def __init__(self, html: str):
        self._html = html.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self._html


def _pagina(monkeypatch, html: str):
    monkeypatch.setattr(
        cmed_precos.urllib.request,
        "urlopen",
        lambda _req, timeout=30: _Resposta(html),
    )


def test_descobre_href_relativo_atual_da_anvisa(monkeypatch):
    _pagina(
        monkeypatch,
        '<a href="/anvisa/pt-br/assuntos/medicamentos/cmed/precos/arquivos/'
        'xls_conformidade_site_20260811_192510234.xlsx/@@download/file">PMC - xls</a>',
    )
    url, data = cmed_precos.localizar_url_planilha()
    assert data == "20260811"
    assert url.startswith("https://www.gov.br/anvisa/")
    assert url.endswith("xls_conformidade_site_20260811_192510234.xlsx/@@download/file")


def test_descobre_href_absoluto_e_escolhe_edicao_mais_recente(monkeypatch):
    _pagina(
        monkeypatch,
        '<a href="https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos/arquivos/'
        'xls_conformidade_site_20260710_1.xlsx/@@download/file">antiga</a>'
        '<a href="https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos/arquivos/'
        'xls_conformidade_site_20260811_2.xlsx">atual</a>',
    )
    url, data = cmed_precos.localizar_url_planilha()
    assert data == "20260811"
    assert url.endswith("xls_conformidade_site_20260811_2.xlsx")


def test_recusa_link_fora_do_host_oficial(monkeypatch):
    _pagina(
        monkeypatch,
        '<a href="https://evil.example/xls_conformidade_site_20260901_1.xlsx/@@download/file">x</a>',
    )
    with pytest.raises(RuntimeError, match="não encontrado"):
        cmed_precos.localizar_url_planilha()
