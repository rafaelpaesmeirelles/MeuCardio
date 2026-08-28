from datetime import datetime, timezone

from app.services.guideline_discovery import (
    BOOTSTRAP_DOCUMENTS,
    SOURCES,
    PageParser,
    _bootstrap_documents,
    _candidate,
    _clean_doi,
    _extract_doi,
    _fingerprint,
)


def test_extract_doi_from_oup_metadata():
    parser = PageParser()
    parser.feed(
        '<html><head><meta name="citation_doi" '
        'content="10.1093/eurheartj/EHAG100"></head></html>'
    )
    assert _extract_doi("", parser) == "10.1093/eurheartj/ehag100"
    assert _clean_doi("https://doi.org/10.1093/eurheartj/ehag100") == "10.1093/eurheartj/ehag100"


def test_doi_fingerprint_deduplicates_same_publication_across_sources():
    published = datetime(2026, 8, 28, tzinfo=timezone.utc)
    first = _fingerprint(
        "ESC",
        "https://www.escardio.org/example",
        "2026 ESC Guidelines for the management of heart failure",
        published,
        "10.1093/eurheartj/ehag100",
    )
    second = _fingerprint(
        "ESC",
        "https://academic.oup.com/example",
        "2026 ESC Guidelines for the management of heart failure | EHJ",
        published,
        "https://doi.org/10.1093/eurheartj/ehag100",
    )
    assert first == second


def test_congress_hub_accepts_curated_article_links_without_guideline_keyword():
    congress = next(
        source for source in SOURCES if "2026-simultaneous-publications" in source.index_url
    )
    url = _candidate(
        congress,
        "/eurheartj/article/47/31/4200/1234567/Some-new-trial",
        "Some new cardiovascular trial without a guideline keyword",
    )
    assert url == "https://academic.oup.com/eurheartj/article/47/31/4200/1234567/Some-new-trial"
    assert _candidate(congress, "/eurheartj/about", "About the journal and editorial board") is None


def test_bootstrap_does_not_emit_future_documents():
    now = datetime(2026, 8, 28, 23, 59, tzinfo=timezone.utc)
    cutoff = datetime(2026, 8, 10, tzinfo=timezone.utc)
    items = _bootstrap_documents(cutoff=cutoff, now=now)
    assert items
    assert all(cutoff <= item["published_at"] <= now for item in items)
    assert any(item["doi"] == "10.1093/eurheartj/ehag100" for item in items)
    assert len(BOOTSTRAP_DOCUMENTS) >= len(items)
