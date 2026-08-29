from types import SimpleNamespace

from app.services.scientific_document_ai import find_duplicate


class _Query:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _DB:
    def __init__(self, rows):
        self._rows = rows

    def query(self, *_args, **_kwargs):
        return _Query(self._rows)


def _document(title: str, refs: list[str]):
    return SimpleNamespace(title=title, source_refs=refs)


def test_deduplica_por_url_canonica_mesmo_com_titulo_divergente():
    existing = _document(
        "Título canônico já publicado",
        ["https://example.org/science/article-2026/"],
    )
    duplicate = find_duplicate(
        _DB([existing]),
        {
            "title": "Título traduzido diferente",
            "doi": None,
            "source_url": "HTTPS://EXAMPLE.ORG/science/article-2026",
        },
    )
    assert duplicate is existing


def test_deduplica_por_fingerprint_antes_da_incorporacao_global():
    fingerprint = "a" * 64
    existing = _document(
        "Metadados antigos",
        [f"sha256:{fingerprint}"],
    )
    duplicate = find_duplicate(
        _DB([existing]),
        {
            "title": "Metadados novos",
            "doi": "10.9999/outro-doi",
            "source_url": "https://outro.example/artigo",
        },
        fingerprint=fingerprint.upper(),
    )
    assert duplicate is existing


def test_doi_normalizado_reconhece_referencia_doi_org():
    existing = _document(
        "Artigo",
        ["https://doi.org/10.1234/ABC.DEF"],
    )
    duplicate = find_duplicate(
        _DB([existing]),
        {
            "title": "Outro título",
            "doi": "10.1234/abc.def",
            "source_url": None,
        },
    )
    assert duplicate is existing
