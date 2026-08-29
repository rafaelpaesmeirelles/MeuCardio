from __future__ import annotations

"""Worldwide source registry for CorVIA Intelligence.

The canonical discovery engine stays conservative. This module adds high-signal
professional societies, guideline repositories, bibliographic indexing and major
medical journals without changing review semantics: discoveries remain `detected`
until scientific review.
"""

from app.services import guideline_discovery as core


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

# PubMed/MEDLINE is the global bibliographic safety net. The query is already
# constrained to cardiovascular high-signal publication types, so result links
# can be inspected directly and then deduplicated by DOI by the canonical engine.
PUBMED_QUERY = (
    "https://pubmed.ncbi.nlm.nih.gov/?term="
    "%28cardiovascular%5BTitle%2FAbstract%5D+OR+cardiac%5BTitle%2FAbstract%5D+OR+"
    "%22heart+failure%22%5BTitle%2FAbstract%5D+OR+coronary%5BTitle%2FAbstract%5D+OR+"
    "arrhythmia%5BTitle%2FAbstract%5D+OR+stroke%5BTitle%2FAbstract%5D+OR+"
    "hypertension%5BTitle%2FAbstract%5D%29+AND+%28guideline%5BPublication+Type%5D+OR+"
    "%22practice+guideline%22%5BPublication+Type%5D+OR+clinical+trial%5BPublication+Type%5D+OR+"
    "meta-analysis%5BPublication+Type%5D+OR+systematic+review%5BPublication+Type%5D%29"
    "&sort=date&size=100"
)

SBC_HOSTS = (
    "portal.cardiol.br",
    "www.portal.cardiol.br",
    "abccardiol.org",
    "www.abccardiol.org",
)

WORLDWIDE_SOURCES = (
    # Global bibliographic indexing across publishers and countries.
    core.Source(
        "PUBMED",
        PUBMED_QUERY,
        ("pubmed.ncbi.nlm.nih.gov",),
        keywords=("pubmed.ncbi.nlm.nih.gov/",),
        max_details=100,
    ),
    # Brazil: SBC/ConDir + Arquivos Brasileiros de Cardiologia. The canonical
    # core already watches the main SBC directives page; these paginated views
    # ensure recently displaced documents are still inspected. External links
    # to ABC Cardiol are explicitly allowed and then deduplicated by DOI.
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
    # Major journals: direct early-online surveillance complements indexing latency.
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
    """Idempotently install worldwide sources into the canonical engine."""
    current = list(core.SOURCES)
    known = {(item.org, item.index_url) for item in current}
    for source in WORLDWIDE_SOURCES:
        key = (source.org, source.index_url)
        if key not in known:
            current.append(source)
            known.add(key)
    core.SOURCES = tuple(current)
    return core.SOURCES
