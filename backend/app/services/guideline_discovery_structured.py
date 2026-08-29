from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

from app.services.guideline_discovery import USER_AGENT, _clean_doi, _parse_datetime

log = logging.getLogger("meucardio.guideline_discovery.structured")

CARDIO_TERMS = (
    "cardiovascular", "cardiac", "heart", "coronary", "myocard", "atrial",
    "ventricular", "arrhythm", "hypertension", "lipid", "atheroscl", "stroke",
    "aortic", "mitral", "tricuspid", "cardiorenal", "heart failure", "thrombo",
    "anticoag", "antiplatelet", "cardiomyopath", "endocard", "pericard",
)
HIGH_SIGNAL_TERMS = (
    "guideline", "guidelines", "consensus", "statement", "position paper",
    "practice update", "practice advisory", "recommendation", "recommendations",
    "universal definition", "randomized trial", "randomised trial", "clinical trial",
    "meta-analysis", "systematic review",
)


@dataclass(frozen=True)
class StructuredSourceResult:
    source: str
    status: str
    items: tuple[dict, ...]
    detail: str | None = None


def _get_json(url: str, *, timeout: int = 35) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(6_000_000).decode("utf-8", errors="strict"))


def _cardio_high_signal(title: str) -> bool:
    normalized = title.casefold()
    return (
        any(term in normalized for term in CARDIO_TERMS)
        and any(term in normalized for term in HIGH_SIGNAL_TERMS)
    )


def _date_parts(parts: list[list[int]] | None) -> datetime | None:
    if not parts or not parts[0]:
        return None
    values = list(parts[0]) + [1, 1]
    try:
        return datetime(values[0], values[1], values[2], tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _pubmed(cutoff: datetime, now: datetime, *, get_json=_get_json) -> StructuredSourceResult:
    term = (
        '((cardiovascular[Title/Abstract] OR cardiac[Title/Abstract] OR "heart failure"[Title/Abstract] '
        'OR coronary[Title/Abstract] OR myocardial[Title/Abstract] OR arrhythmia[Title/Abstract] '
        'OR hypertension[Title/Abstract] OR stroke[Title/Abstract]) AND '
        '(guideline[Publication Type] OR practice guideline[Publication Type] OR '
        'clinical trial[Publication Type] OR randomized controlled trial[Publication Type] OR '
        'meta-analysis[Publication Type] OR systematic review[Publication Type] OR '
        'consensus[Title] OR statement[Title]))'
    )
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": 150,
        "sort": "pub date",
        "mindate": cutoff.strftime("%Y/%m/%d"),
        "maxdate": now.strftime("%Y/%m/%d"),
        "datetype": "pdat",
    })
    search = get_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}")
    ids = search.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return StructuredSourceResult("NCBI_PUBMED", "ok", ())

    summary_params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json",
    })
    summary = get_json(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{summary_params}")
    result = summary.get("result", {})
    items: list[dict] = []
    for uid in result.get("uids", []):
        record = result.get(uid, {})
        title = re.sub(r"\s+", " ", str(record.get("title") or "")).strip()
        if not title:
            continue
        published_at = _parse_datetime(str(record.get("sortpubdate") or "").split(" ", 1)[0])
        if published_at is None:
            published_at = _parse_datetime(record.get("pubdate"))
        if published_at is None or not (cutoff <= published_at <= now):
            continue
        doi = None
        for identifier in record.get("articleids", []) or []:
            if str(identifier.get("idtype", "")).casefold() == "doi":
                doi = _clean_doi(identifier.get("value"))
                break
        items.append({
            "org": "PUBMED",
            "title": title,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            "doi": doi,
            "published_at": published_at,
        })
    return StructuredSourceResult("NCBI_PUBMED", "ok", tuple(items))


def _europe_pmc(cutoff: datetime, now: datetime, *, get_json=_get_json) -> StructuredSourceResult:
    query = (
        '((TITLE:"cardiovascular" OR TITLE:"cardiac" OR TITLE:"heart failure" OR '
        'TITLE:"coronary" OR TITLE:"myocardial" OR TITLE:"arrhythmia" OR TITLE:"hypertension" '
        'OR TITLE:"stroke") AND (TITLE:"guideline" OR TITLE:"consensus" OR TITLE:"statement" '
        'OR TITLE:"randomized trial" OR TITLE:"randomised trial" OR TITLE:"meta-analysis" '
        'OR TITLE:"systematic review")) '
        f'AND FIRST_PDATE:[{cutoff.date().isoformat()} TO {now.date().isoformat()}] sort_date:y'
    )
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
        "resultType": "lite",
        "pageSize": 200,
    })
    payload = get_json(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{params}")
    items: list[dict] = []
    for record in payload.get("resultList", {}).get("result", []) or []:
        title = re.sub(r"\s+", " ", str(record.get("title") or "")).strip()
        if not title:
            continue
        published_at = _parse_datetime(record.get("firstPublicationDate"))
        if published_at is None or not (cutoff <= published_at <= now):
            continue
        source = str(record.get("source") or "MED")
        ext_id = str(record.get("id") or record.get("pmid") or "").strip()
        if not ext_id:
            continue
        items.append({
            "org": "EUROPE_PMC",
            "title": title,
            "url": f"https://europepmc.org/article/{source}/{ext_id}",
            "doi": _clean_doi(record.get("doi")),
            "published_at": published_at,
        })
    return StructuredSourceResult("EUROPE_PMC", "ok", tuple(items))


def _crossref(cutoff: datetime, now: datetime, *, get_json=_get_json) -> StructuredSourceResult:
    queries = (
        "cardiovascular guideline consensus statement",
        "heart failure randomized trial meta-analysis",
        "coronary myocardial randomized trial meta-analysis",
        "arrhythmia atrial fibrillation randomized trial guideline",
        "hypertension lipid cardiovascular meta-analysis guideline",
    )
    items: list[dict] = []
    for query in queries:
        params = urllib.parse.urlencode({
            "query.bibliographic": query,
            "filter": (
                f"from-pub-date:{cutoff.date().isoformat()},"
                f"until-pub-date:{now.date().isoformat()},type:journal-article"
            ),
            "rows": 80,
            "sort": "published",
            "order": "desc",
            "select": "DOI,title,published-online,published-print,issued,URL,publisher,container-title,type",
        })
        payload = get_json(f"https://api.crossref.org/works?{params}")
        for record in payload.get("message", {}).get("items", []) or []:
            titles = record.get("title") or []
            title = re.sub(r"\s+", " ", str(titles[0] if titles else "")).strip()
            if not title or not _cardio_high_signal(title):
                continue
            published_at = (
                _date_parts((record.get("published-online") or {}).get("date-parts"))
                or _date_parts((record.get("published-print") or {}).get("date-parts"))
                or _date_parts((record.get("issued") or {}).get("date-parts"))
            )
            if published_at is None or not (cutoff <= published_at <= now):
                continue
            doi = _clean_doi(record.get("DOI"))
            url = f"https://doi.org/{doi}" if doi else str(record.get("URL") or "").strip()
            if not url:
                continue
            items.append({
                "org": "CROSSREF",
                "title": title,
                "url": url,
                "doi": doi,
                "published_at": published_at,
            })
    return StructuredSourceResult("CROSSREF", "ok", tuple(items))


def discover_structured_sources(
    cutoff: datetime,
    now: datetime,
    *,
    get_json=_get_json,
) -> tuple[list[dict], list[dict]]:
    """Query structured scholarly indexes; one failure never blocks the others."""
    items: list[dict] = []
    coverage: list[dict] = []
    for name, discoverer in (
        ("NCBI_PUBMED", _pubmed),
        ("EUROPE_PMC", _europe_pmc),
        ("CROSSREF", _crossref),
    ):
        try:
            result = discoverer(cutoff, now, get_json=get_json)
            items.extend(result.items)
            coverage.append({"source": name, "status": result.status, "items": len(result.items)})
        except Exception as error:
            log.exception("Falha no indexador estruturado %s", name)
            coverage.append({
                "source": name,
                "status": "error",
                "items": 0,
                "error": type(error).__name__,
            })
    return items, coverage
