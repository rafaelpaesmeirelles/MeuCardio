from __future__ import annotations

"""Política explícita de confiança de fontes do CorVIA Intelligence.

Aprovação automática é reservada a fontes primárias oficiais (sociedades,
órgãos públicos e periódicos científicos de primeira parte já cadastrados).
Indexadores como PubMed, Europe PMC e Crossref são excelentes mecanismos de
descoberta, mas não são, isoladamente, a fonte editorial original do trabalho.
"""

from urllib.parse import urlsplit


AGGREGATOR_ORGS = frozenset({"PUBMED", "EUROPE_PMC", "CROSSREF"})

TRUSTED_OFFICIAL_HOSTS: dict[str, frozenset[str]] = {
    "SBC": frozenset({"portal.cardiol.br", "www.portal.cardiol.br", "abccardiol.org", "www.abccardiol.org", "doi.org"}),
    "ESC": frozenset({"escardio.org", "www.escardio.org", "corporate-prod.dxc.escardio.org", "academic.oup.com", "doi.org"}),
    "ESC/ACC/AHA/WHF": frozenset({"academic.oup.com", "doi.org"}),
    "ESC/EHRA/HFA": frozenset({"academic.oup.com", "doi.org"}),
    "ESC/EHRA/ACNAP": frozenset({"academic.oup.com", "doi.org"}),
    "ACC": frozenset({"acc.org", "www.acc.org", "jacc.org", "www.jacc.org", "doi.org"}),
    "AHA": frozenset({"professional.heart.org", "heart.org", "www.heart.org", "ahajournals.org", "www.ahajournals.org", "doi.org"}),
    "HRS": frozenset({"hrsonline.org", "www.hrsonline.org", "doi.org"}),
    "HFSA": frozenset({"hfsa.org", "www.hfsa.org", "doi.org"}),
    "SCAI": frozenset({"scai.org", "www.scai.org", "jscai.org", "www.jscai.org", "doi.org"}),
    "ASE": frozenset({"asecho.org", "www.asecho.org", "doi.org"}),
    "ASNC": frozenset({"asnc.org", "www.asnc.org", "doi.org"}),
    "CCS": frozenset({"ccs.ca", "www.ccs.ca", "doi.org"}),
    "JCS": frozenset({"j-circ.or.jp", "www.j-circ.or.jp", "doi.org"}),
    "NICE": frozenset({"nice.org.uk", "www.nice.org.uk"}),
    "WHO": frozenset({"who.int", "www.who.int"}),
    "COCHRANE": frozenset({"cochranelibrary.com", "www.cochranelibrary.com", "doi.org"}),
    "JACC": frozenset({"jacc.org", "www.jacc.org", "doi.org"}),
    "CIRCULATION": frozenset({"ahajournals.org", "www.ahajournals.org", "doi.org"}),
    "JAMA_CARDIOLOGY": frozenset({"jamanetwork.com", "www.jamanetwork.com", "doi.org"}),
    "JAMA": frozenset({"jamanetwork.com", "www.jamanetwork.com", "doi.org"}),
    "NEJM": frozenset({"nejm.org", "www.nejm.org", "doi.org"}),
    "THE_LANCET": frozenset({"thelancet.com", "www.thelancet.com", "doi.org"}),
    "BMJ": frozenset({"bmj.com", "www.bmj.com", "doi.org"}),
    "HEART_BMJ": frozenset({"heart.bmj.com", "bmj.com", "www.bmj.com", "doi.org"}),
    "NATURE_MEDICINE": frozenset({"nature.com", "www.nature.com", "doi.org"}),
}

TRUSTED_OFFICIAL_ORGS = frozenset(TRUSTED_OFFICIAL_HOSTS)


def _host(url: str | None) -> str:
    if not url:
        return ""
    try:
        return (urlsplit(url).hostname or "").casefold()
    except ValueError:
        return ""


def is_trusted_official_source(*, org: str | None, url: str | None, doi: str | None = None) -> bool:
    normalized_org = str(org or "").strip().upper()
    if normalized_org in AGGREGATOR_ORGS or normalized_org not in TRUSTED_OFFICIAL_HOSTS:
        return False
    host = _host(url)
    if host and host in TRUSTED_OFFICIAL_HOSTS[normalized_org]:
        return True
    # Bootstrap curado: DOI válido de uma organização explicitamente confiável
    # pode chegar antes da URL primária definitiva.
    return bool(str(doi or "").strip()) and (not host or host == "doi.org")


def is_trusted_official_guideline(guideline) -> bool:
    return is_trusted_official_source(
        org=getattr(guideline, "org", None),
        url=getattr(guideline, "url", None),
        doi=getattr(guideline, "doi", None),
    )
