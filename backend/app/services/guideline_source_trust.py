from __future__ import annotations

"""Política explícita de confiança de fontes do CorVIA Intelligence.

O CorVIA autoaprova itens vindos de sociedades/órgãos/periódicos científicos
cadastrados e também de PubMed, Europe PMC e Crossref, desde que o item já tenha
passado pelos filtros de alto sinal do respectivo indexador (tema cardiovascular,
tipo documental/estudo elegível, data e metadados mínimos consistentes).
"""

from urllib.parse import urlsplit


TRUSTED_INDEX_ORGS = frozenset({"PUBMED", "EUROPE_PMC", "CROSSREF"})

TRUSTED_OFFICIAL_HOSTS: dict[str, frozenset[str]] = {
    "PUBMED": frozenset({"pubmed.ncbi.nlm.nih.gov"}),
    "EUROPE_PMC": frozenset({"europepmc.org", "www.europepmc.org"}),
    "CROSSREF": frozenset({"doi.org"}),
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
    if normalized_org not in TRUSTED_OFFICIAL_HOSTS:
        return False
    host = _host(url)
    if host and host in TRUSTED_OFFICIAL_HOSTS[normalized_org]:
        return True
    # Crossref e bootstraps curados podem representar o item pelo DOI antes de
    # termos a URL definitiva do periódico; DOI válido é suficiente nesses casos.
    if normalized_org == "CROSSREF":
        return bool(str(doi or "").strip())
    return bool(str(doi or "").strip()) and (not host or host == "doi.org")


def is_trusted_official_guideline(guideline) -> bool:
    return is_trusted_official_source(
        org=getattr(guideline, "org", None),
        url=getattr(guideline, "url", None),
        doi=getattr(guideline, "doi", None),
    )
