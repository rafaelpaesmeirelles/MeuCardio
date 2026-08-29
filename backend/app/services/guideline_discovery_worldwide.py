from __future__ import annotations

"""Worldwide source registry and resilient orchestration for CorVIA Intelligence.

Structured scholarly indexes are the primary safety net because many publisher
sites intentionally block automated HTML clients. Direct society/journal pages
remain enabled as redundant first-party discovery paths. Every discovery remains
`detected` until scientific review; this module never changes clinical guidance.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services import guideline_discovery as core
from app.services.guideline_discovery_structured import discover_structured_sources


CARDIOVASCULAR_TERMS = (
    "cardiovascular",
    "cardiac",
    "heart",
    "coronary",
    "myocard",
    "atrial",
    "ventricular",
    "arrhythm",
    "hypertension",
    "lipid",
    "atheroscl",
    "stroke",
    "aortic",
    "mitral",
    "tricuspid",
    "pulmonary hypertension",
    "cardiorenal",
    "heart failure",
    "thrombo",
    "anticoag",
    "antiplatelet",
    "cardiomyopath",
    "endocard",
    "pericard",
)

HIGH_SIGNAL_TERMS = tuple(dict.fromkeys(
    core.GUIDANCE_KEYWORDS
    + (
        "clinical practice update",
        "practice advisory",
        "expert consensus",
        "scientific statement",
        "rapid science update",
        "appropriate use criteria",
        "randomized trial",
        "randomised trial",
        "clinical trial",
        "meta-analysis",
        "systematic review",
    )
))

SBC_HOSTS = (
    "portal.cardiol.br",
    "www.portal.cardiol.br",
    "abccardiol.org",
    "www.abccardiol.org",
)

WORLDWIDE_SOURCES = (
    # Brazil: SBC/ConDir + Arquivos Brasileiros de Cardiologia. The canonical
    # core already watches the main SBC directives page; paginated views keep
    # recently displaced documents in the discovery window.
    core.Source(
        "SBC",
        "https://www.portal.cardiol.br/diretrizes?dba05c42_page=1",
        SBC_HOSTS,
        keywords=HIGH_SIGNAL_TERMS,
        max_details=180,
    ),
    core.Source(
        "SBC",
        "https://www.portal.cardiol.br/diretrizes?dba05c42_page=2",
        SBC_HOSTS,
        keywords=HIGH_SIGNAL_TERMS,
        max_details=180,
    ),
    core.Source(
        "SBC",
        "https://www.portal.cardiol.br/diretrizes?dba05c42_page=3",
        SBC_HOSTS,
        keywords=HIGH_SIGNAL_TERMS,
        max_details=180,
    ),
    # Professional societies and guideline repositories.
    core.Source(
        "HRS",
        "https://www.hrsonline.org/publications-resources/resource-library/hrs-documents/",
        ("hrsonline.org", "www.hrsonline.org"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=100,
    ),
    core.Source(
        "HFSA",
        "https://hfsa.org/heart-failure-guidelines",
        ("hfsa.org", "www.hfsa.org"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=80,
    ),
    core.Source(
        "SCAI",
        "https://www.scai.org/publications/jscai",
        ("scai.org", "www.scai.org", "www.jscai.org", "jscai.org"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=100,
    ),
    core.Source(
        "ASE",
        "https://www.asecho.org/practice-clinical-resources/ase-guidelines/",
        ("asecho.org", "www.asecho.org"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=100,
    ),
    core.Source(
        "ASNC",
        "https://www.asnc.org/clinical-guidelines-tools/clinical-guidelines/",
        ("asnc.org", "www.asnc.org"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=100,
    ),
    core.Source(
        "CCS",
        "https://ccs.ca/guidelines-and-clinical-practice-update-library/",
        ("ccs.ca", "www.ccs.ca"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=120,
    ),
    core.Source(
        "JCS",
        "https://www.j-circ.or.jp/english/cj/jcs-guidelines/",
        ("j-circ.or.jp", "www.j-circ.or.jp"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=120,
    ),
    core.Source(
        "NICE",
        "https://www.nice.org.uk/guidance/conditions-and-diseases/cardiovascular-conditions",
        ("nice.org.uk", "www.nice.org.uk"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=100,
    ),
    core.Source(
        "WHO",
        "https://www.who.int/health-topics/cardiovascular-diseases",
        ("who.int", "www.who.int"),
        keywords=HIGH_SIGNAL_TERMS,
        max_details=80,
    ),
    core.Source(
        "COCHRANE",
        "https://www.cochranelibrary.com/cdsr/reviews",
        ("cochranelibrary.com", "www.cochranelibrary.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=80,
    ),
    # Major journals: early-online HTML is a fallback. PubMed/Europe PMC/Crossref
    # provide structured coverage when these sites return 403 to automated clients.
    core.Source(
        "JACC",
        "https://www.jacc.org/onlinefirst",
        ("jacc.org", "www.jacc.org"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=80,
    ),
    core.Source(
        "CIRCULATION",
        "https://www.ahajournals.org/toc/circ/0/0",
        ("ahajournals.org", "www.ahajournals.org"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=80,
    ),
    core.Source(
        "JAMA_CARDIOLOGY",
        "https://jamanetwork.com/journals/jamacardiology/newonline",
        ("jamanetwork.com", "www.jamanetwork.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=80,
    ),
    core.Source(
        "JAMA",
        "https://jamanetwork.com/journals/jama/newonline",
        ("jamanetwork.com", "www.jamanetwork.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=60,
    ),
    core.Source(
        "NEJM",
        "https://www.nejm.org/medical-articles/research",
        ("nejm.org", "www.nejm.org"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=60,
    ),
    core.Source(
        "THE_LANCET",
        "https://www.thelancet.com/journals/lancet/onlinefirst",
        ("thelancet.com", "www.thelancet.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=60,
    ),
    core.Source(
        "BMJ",
        "https://www.bmj.com/research/research",
        ("bmj.com", "www.bmj.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=60,
    ),
    core.Source(
        "HEART_BMJ",
        "https://heart.bmj.com/online-first",
        ("heart.bmj.com", "bmj.com", "www.bmj.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=80,
    ),
    core.Source(
        "NATURE_MEDICINE",
        "https://www.nature.com/nm/research-articles",
        ("nature.com", "www.nature.com"),
        keywords=CARDIOVASCULAR_TERMS,
        max_details=60,
    ),
)


def enable_worldwide_sources() -> tuple[core.Source, ...]:
    """Idempotently install direct worldwide sources into the canonical engine."""
    current = list(core.SOURCES)
    known = {(item.org, item.index_url) for item in current}
    for source in WORLDWIDE_SOURCES:
        key = (source.org, source.index_url)
        if key not in known:
            current.append(source)
            known.add(key)
    core.SOURCES = tuple(current)
    return core.SOURCES


def discover_and_publish_worldwide(db: Session) -> dict:
    """Run structured indexes first, then direct first-party fallbacks.

    Structured results are injected only for the duration of this synchronous
    discovery call and are persisted by the same canonical dedup/review pipeline.
    """
    enable_worldwide_sources()
    now = datetime.now(timezone.utc)
    cutoff = core._effective_cutoff(now)
    structured_items, structured_coverage = discover_structured_sources(cutoff, now)

    original_bootstrap = core.BOOTSTRAP_DOCUMENTS
    try:
        core.BOOTSTRAP_DOCUMENTS = tuple(original_bootstrap) + tuple(structured_items)
        result = core.discover_and_publish(db)
    finally:
        core.BOOTSTRAP_DOCUMENTS = original_bootstrap

    failed_direct = result.get("source_failures", [])
    structured_ok = sum(1 for item in structured_coverage if item.get("status") == "ok")
    structured_failed = len(structured_coverage) - structured_ok
    result["structured_sources"] = structured_coverage
    result["coverage"] = {
        "structured_total": len(structured_coverage),
        "structured_ok": structured_ok,
        "structured_failed": structured_failed,
        "structured_items_seen": len(structured_items),
        "direct_sources_total": len(core.SOURCES),
        "direct_sources_failed": len(failed_direct),
        "direct_sources_ok": max(0, len(core.SOURCES) - len(failed_direct)),
        "mode": "structured_primary_direct_fallback",
    }
    return result
