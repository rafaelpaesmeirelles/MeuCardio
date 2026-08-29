from datetime import datetime, timezone
from urllib.parse import urlparse

from app.services.guideline_discovery_structured import (
    _crossref,
    _europe_pmc,
    _pubmed,
    discover_structured_sources,
)


CUTOFF = datetime(2026, 8, 10, tzinfo=timezone.utc)
NOW = datetime(2026, 8, 29, 12, tzinfo=timezone.utc)


def test_pubmed_uses_eutilities_and_extracts_doi():
    def fake(url: str):
        if "esearch.fcgi" in url:
            return {"esearchresult": {"idlist": ["123"]}}
        assert "esummary.fcgi" in url
        return {
            "result": {
                "uids": ["123"],
                "123": {
                    "title": "Randomized trial of heart failure therapy",
                    "sortpubdate": "2026/08/28 00:00",
                    "articleids": [{"idtype": "doi", "value": "10.1000/HF.123"}],
                },
            }
        }

    result = _pubmed(CUTOFF, NOW, get_json=fake)
    assert result.status == "ok"
    assert len(result.items) == 1
    assert result.items[0]["doi"] == "10.1000/hf.123"
    assert result.items[0]["url"] == "https://pubmed.ncbi.nlm.nih.gov/123/"


def test_europe_pmc_returns_recent_structured_item():
    def fake(url: str):
        assert urlparse(url).hostname == "www.ebi.ac.uk"
        return {
            "resultList": {
                "result": [{
                    "id": "456",
                    "source": "MED",
                    "title": "Consensus statement on cardiovascular disease",
                    "firstPublicationDate": "2026-08-27",
                    "doi": "10.1000/CV.456",
                }]
            }
        }

    result = _europe_pmc(CUTOFF, NOW, get_json=fake)
    assert len(result.items) == 1
    assert result.items[0]["doi"] == "10.1000/cv.456"
    assert result.items[0]["url"].endswith("/MED/456")


def test_crossref_filters_non_cardiovascular_noise_and_dedup_is_left_to_core():
    def fake(url: str):
        assert urlparse(url).hostname == "api.crossref.org"
        return {
            "message": {
                "items": [
                    {
                        "title": ["Cardiovascular guideline and randomized trial update"],
                        "DOI": "10.1000/CV.789",
                        "published-online": {"date-parts": [[2026, 8, 28]]},
                        "URL": "https://doi.org/10.1000/CV.789",
                    },
                    {
                        "title": ["Randomized trial of dermatologic therapy"],
                        "DOI": "10.1000/NOISE",
                        "published-online": {"date-parts": [[2026, 8, 28]]},
                    },
                ]
            }
        }

    result = _crossref(CUTOFF, NOW, get_json=fake)
    assert result.items
    assert all(item["doi"] == "10.1000/cv.789" for item in result.items)


def test_structured_sources_isolate_failure_per_indexer(monkeypatch):
    from app.services import guideline_discovery_structured as module

    monkeypatch.setattr(module, "_pubmed", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(
        module,
        "_europe_pmc",
        lambda *args, **kwargs: module.StructuredSourceResult("EUROPE_PMC", "ok", ()),
    )
    monkeypatch.setattr(
        module,
        "_crossref",
        lambda *args, **kwargs: module.StructuredSourceResult("CROSSREF", "ok", ()),
    )

    items, coverage = discover_structured_sources(CUTOFF, NOW, get_json=lambda _: {})
    assert items == []
    assert [entry["status"] for entry in coverage] == ["error", "ok", "ok"]
