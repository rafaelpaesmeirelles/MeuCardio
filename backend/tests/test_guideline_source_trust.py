from app.services.guideline_source_trust import is_trusted_official_source


def test_structured_indexes_are_trusted_sources():
    assert is_trusted_official_source(
        org="PUBMED",
        url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
    )
    assert is_trusted_official_source(
        org="EUROPE_PMC",
        url="https://europepmc.org/article/MED/12345678",
    )
    assert is_trusted_official_source(
        org="CROSSREF",
        url="https://doi.org/10.1000/example",
        doi="10.1000/example",
    )


def test_registered_primary_scientific_sources_are_trusted():
    assert is_trusted_official_source(
        org="SBC",
        url="https://www.portal.cardiol.br/diretrizes/exemplo",
    )
    assert is_trusted_official_source(
        org="ESC",
        url="https://academic.oup.com/eurheartj/article/example",
    )
    assert is_trusted_official_source(
        org="NEJM",
        url="https://www.nejm.org/doi/full/10.1056/example",
    )


def test_unknown_or_mismatched_source_is_not_autoapproved():
    assert not is_trusted_official_source(
        org="BLOG_DESCONHECIDO",
        url="https://example.com/post",
    )
    assert not is_trusted_official_source(
        org="PUBMED",
        url="https://example.com/not-pubmed",
    )
    assert not is_trusted_official_source(
        org="ESC",
        url="https://example.com/not-esc",
    )
