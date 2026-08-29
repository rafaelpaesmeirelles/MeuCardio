from datetime import datetime, timezone

from sqlalchemy import Text, create_engine
from sqlalchemy.orm import Session

from app.models.guideline import Guideline
from app.services import guideline_discovery as discovery
from app.services.guideline_discovery import (
    BOOTSTRAP_DOCUMENTS,
    SOURCES,
    PageParser,
    _bootstrap_documents,
    _candidate,
    _clean_doi,
    _extract_doi,
    _fingerprint,
    _page_title,
    _slug,
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


def test_guideline_title_column_preserves_long_scientific_titles():
    assert isinstance(Guideline.__table__.c.titulo.type, Text)


def test_page_title_does_not_silently_truncate_over_300_characters():
    long_title = "Long scientific title " + ("cardiovascular evidence " * 20)
    parser = PageParser()
    parser.feed(
        '<html><head><meta name="citation_title" content="'
        + long_title
        + '"></head></html>'
    )
    assert len(long_title) > 300
    assert _page_title(parser, "fallback") == long_title


def test_discovery_reuses_existing_slug_when_metadata_changed(monkeypatch):
    """Reproduz a colisão Europe PMC observada no Intelligence em produção."""
    published = datetime(2026, 8, 26, tzinfo=timezone.utc)
    title = (
        "Reader Response: Bridging or Direct Thrombectomy in Posterior Circulation "
        "Large-Vessel Occlusion Stroke: Analysis of Binational Registries and Meta-Analysis."
    )
    item = {
        "org": "EUROPE_PMC",
        "title": title,
        "doi": "10.1212/wnl.0000000000214824",
        "url": "https://europepmc.org/article/MED/42647785",
        "published_at": published,
    }
    expected_slug = _slug(item["org"], title, published)

    engine = create_engine("sqlite:///:memory:")
    Guideline.__table__.create(engine)
    with Session(engine) as db:
        # Mesmo achado já persistido por uma execução/indexador anterior, mas
        # ainda sem os metadados enriquecidos que chegam nesta nova rodada.
        db.add(
            Guideline(
                slug=expected_slug,
                org="EUROPE_PMC",
                titulo=title,
                ano=2026,
                doi=None,
                url="https://europepmc.org/article/OLD/42647785",
                published_at=published,
                source_fingerprint="a" * 64,
                detection_status="detected",
            )
        )
        db.commit()

        monkeypatch.setattr(discovery, "BOOTSTRAP_DOCUMENTS", (item,))
        monkeypatch.setattr(discovery, "SOURCES", ())
        monkeypatch.setattr(discovery, "_ensure_notifications", lambda _db, _g: (0, 0))

        result = discovery.discover_and_publish(db)
        rows = db.query(Guideline).all()

        assert result["created"] == 0
        assert result["updated"] == 1
        assert len(rows) == 1
        assert rows[0].slug == expected_slug
        assert rows[0].doi == item["doi"]
