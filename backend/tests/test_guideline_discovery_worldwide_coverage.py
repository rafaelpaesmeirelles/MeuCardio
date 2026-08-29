from app.services import guideline_discovery_worldwide as worldwide


def test_worldwide_registry_keeps_sbc_and_major_sources():
    organizations = {source.org for source in worldwide.WORLDWIDE_SOURCES}
    assert "SBC" in organizations
    assert "JACC" in organizations
    assert "NEJM" in organizations
    assert "THE_LANCET" in organizations
    assert "COCHRANE" in organizations


def test_pubmed_html_scraper_is_not_registered_as_direct_source():
    # PubMed is now consumed through NCBI E-utilities, avoiding account/navigation
    # links from the public HTML search page.
    assert all(source.org != "PUBMED" for source in worldwide.WORLDWIDE_SOURCES)
