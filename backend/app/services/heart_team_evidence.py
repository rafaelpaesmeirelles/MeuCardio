"""Fail-closed citation and structured-fact validation for Heart Team."""

from __future__ import annotations

import re
import unicodedata
from html import unescape
from dataclasses import dataclass
from typing import Iterable
from xml.etree import ElementTree

import httpx

DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.I)
PMID_RE = re.compile(r"^\d{1,9}$")
NUMBER_RE = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?\s*(?:%|mg|mcg|g|kg|ml|l|mmhg|bpm|mmol/l|mg/dl)?", re.I)
DATE_RE = re.compile(r"\b(?:19|20)\d{2}\b")
N_RE = re.compile(r"\b(?:n\s*=\s*)\d+\b", re.I)


def normalize_text(value: str | None) -> str:
    raw = unicodedata.normalize("NFKD", value or "")
    return re.sub(r"\s+", " ", "".join(c for c in raw if not unicodedata.combining(c)).lower()).strip()


def tokens(value: str | None) -> set[str]:
    stop = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "para", "com", "por", "um", "uma", "the", "of", "and", "in"}
    return {t for t in re.findall(r"[a-z0-9]+", normalize_text(value)) if len(t) > 2 and t not in stop}


def _required_overlap(needle: str, haystack: str) -> bool:
    wanted = tokens(needle)
    found = tokens(haystack)
    if not wanted:
        return False
    need = len(wanted) if len(wanted) <= 3 else max(3, int(len(wanted) * .6 + .999))
    return len(wanted & found) >= need


def structured_facts(text: str | None) -> dict[str, set[str]]:
    normalized = normalize_text(text)
    values = {re.sub(r"\s+", "", m.group(0).replace(",", ".").lower()) for m in NUMBER_RE.finditer(normalized)}
    populations = {term for term in ("criancas", "pediatrica", "adultos", "idosos", "gestantes", "mulheres", "homens", "doenca renal", "insuficiencia renal", "doenca hepatica", "insuficiencia cardiaca", "fibrilacao atrial", "diabetes") if term in normalized}
    outcomes = {term for term in ("mortalidade", "hospitalizacao", "avc", "infarto", "sangramento", "congestao", "qualidade de vida", "evento cardiovascular") if term in normalized}
    drug_classes = {term for term in ("anticoagulante", "antiagregante", "betabloqueador", "inibidor da eca", "bloqueador do receptor", "diuretico", "antiarritmico", "estatina", "vasodilatador") if term in normalized}
    return {
        "quantities": values,
        "sample_sizes": {re.sub(r"\s+", "", m.group(0).lower()) for m in N_RE.finditer(normalized)},
        "dates": set(DATE_RE.findall(normalized)),
        "doi": {m.lower().rstrip(".,;)") for m in re.findall(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", normalized, re.I)},
        "pmid": set(re.findall(r"\bpmid\s*:?\s*(\d{1,9})\b", normalized, re.I)),
        "directions": {word for word in ("aumentou", "reduziu", "superior", "inferior", "nao inferior", "sem diferenca", "mortalidade") if word in normalized},
        "classes": {m.group(0) for m in re.finditer(r"\bclasse\s+(?:i{1,3}|iv|[1-4])\b", normalized)},
        "levels": {m.group(0) for m in re.finditer(r"\b(?:nivel|level)\s+[abc]\b", normalized)},
        "populations": populations,
        "outcomes": outcomes,
        "drug_classes": drug_classes,
    }


def exact_facts_supported(claim: str, source_text: str) -> tuple[bool, str | None]:
    cf, sf = structured_facts(claim), structured_facts(source_text)
    for key in ("quantities", "sample_sizes", "dates", "doi", "pmid", "directions", "classes", "levels", "populations", "outcomes", "drug_classes"):
        if not cf[key].issubset(sf[key]):
            return False, f"{key} não coincide exatamente com a fonte"
    return True, None


@dataclass(frozen=True)
class ReopenedPublication:
    title: str
    doi: str | None
    pmid: str | None
    date: str | None
    population: str | None
    results: str | None
    url: str | None


def _title_matches(left: str, right: str) -> bool:
    a, b = tokens(left), tokens(right)
    if not a or not b:
        return False
    smaller = min(len(a), len(b))
    needed = max(2 if smaller > 1 else 1, int(smaller * .6 + .999))
    return len(a & b) >= needed


def _xml_text(element) -> str:
    return " ".join("".join(element.itertext()).split()) if element is not None else ""


def _clean_abstract(value: str | None) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def reopen_publication(*, title: str, doi: str | None, pmid: str | None, timeout: float = 8.0) -> ReopenedPublication | None:
    """Reopen primary registries. Any ambiguity or network error is insufficient."""
    crossref = None
    pubmed = None
    try:
        if doi:
            if not DOI_RE.fullmatch(doi.strip()):
                return None
            response = httpx.get(f"https://api.crossref.org/works/{doi.strip()}", timeout=timeout, follow_redirects=True)
            response.raise_for_status()
            msg = response.json().get("message") or {}
            crossref = {
                "title": " ".join(msg.get("title") or []),
                "doi": (msg.get("DOI") or "").lower(),
                "date": str(((msg.get("published") or {}).get("date-parts") or [[None]])[0][0] or ""),
                "url": msg.get("URL"),
                "text": " ".join(filter(None, [" ".join(msg.get("title") or []), _clean_abstract(msg.get("abstract"))])),
            }
        if pmid:
            if not PMID_RE.fullmatch(pmid.strip()):
                return None
            response = httpx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params={"db": "pubmed", "id": pmid, "retmode": "xml"}, timeout=timeout)
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
            article = root.find(".//PubmedArticle")
            if article is None:
                return None
            article_title = _xml_text(article.find(".//ArticleTitle"))
            abstract = " ".join(filter(None, (_xml_text(node) for node in article.findall(".//Abstract/AbstractText"))))
            pubmed_id = _xml_text(article.find(".//PMID"))
            pubmed_doi = None
            for node in article.findall(".//ArticleId"):
                if str(node.attrib.get("IdType") or "").lower() == "doi":
                    pubmed_doi = _xml_text(node).lower()
            date = _xml_text(article.find(".//PubDate/Year")) or _xml_text(article.find(".//ArticleDate/Year")) or _xml_text(article.find(".//PubDate/MedlineDate"))
            pubmed = {"title": article_title, "pmid": pubmed_id, "doi": pubmed_doi, "date": date, "text": " ".join(filter(None, [article_title, abstract]))}
    except (httpx.HTTPError, ElementTree.ParseError, ValueError, KeyError, TypeError):
        return None
    if crossref and not _title_matches(title, crossref["title"]):
        return None
    if pubmed and not _title_matches(title, pubmed["title"]):
        return None
    if pubmed and pubmed["pmid"] != str(pmid):
        return None
    if crossref and pubmed and not _title_matches(crossref["title"], pubmed["title"]):
        return None
    if crossref and pubmed and (not pubmed.get("doi") or pubmed["doi"] != crossref["doi"]):
        return None
    data = crossref or pubmed
    if not data:
        return None
    external_text = " ".join(dict.fromkeys(filter(None, [pubmed and pubmed.get("text"), crossref and crossref.get("text")])))
    facts = structured_facts(external_text)
    population = ", ".join(sorted(facts["populations"])) or None
    return ReopenedPublication((pubmed or data)["title"], crossref and crossref["doi"] or pubmed and pubmed.get("doi"), pubmed and pubmed["pmid"], (pubmed or data).get("date"), population, external_text or None, (crossref or {}).get("url"))


def source_catalog(db, *, query: str = "", limit: int = 16) -> list[dict]:
    """Only reviewed/published local sources enter the clinical context."""
    from app.models.content import Document
    from app.models.evidence import EvidenceRecord
    from app.models.guideline import Guideline
    from app.models.study import ScientificStudy

    rows: list[dict] = []
    # Do not limit before relevance ranking: the corpus has ~11k records and
    # an arbitrary first page made case-relevant evidence effectively absent.
    for item in db.query(EvidenceRecord).filter(EvidenceRecord.published.is_(True), EvidenceRecord.review_status == "revisado").all():
        text = " ".join(filter(None, [item.statement, item.summary, item.reference]))
        rows.append({"id": f"evidence:{item.id}", "entity_type": "evidencia", "slug": item.slug, "route": f"/evidencias/{item.slug}", "theme": item.theme, "title": item.guideline_title, "text": text, "doi": item.doi, "pmid": None, "date": str(item.year), "society": item.society, "url": item.source_url, "reviewed": True})
    for item in db.query(ScientificStudy).filter(ScientificStudy.published.is_(True), ScientificStudy.review_status == "revisado").all():
        text = " ".join(filter(None, [item.summary, item.key_findings, item.clinical_implications, item.limitations]))
        rows.append({"id": f"study:{item.id}", "entity_type": "estudo", "slug": item.slug, "route": f"/estudos/{item.slug}", "theme": item.theme, "title": item.title, "text": text, "doi": item.doi, "pmid": item.pmid, "date": str(item.year), "society": item.journal, "url": item.url, "reviewed": True})
    for item in db.query(Document).filter(Document.published.is_(True), Document.review_status == "revisado").all():
        entity_type = "fluxograma" if item.kind == "fluxograma" else "documento"
        rows.append({"id": f"document:{item.id}", "entity_type": entity_type, "slug": item.slug, "route": f"/biblioteca/{item.slug}", "theme": item.theme, "title": item.title, "text": " ".join(filter(None, [item.summary, item.body_md])), "doi": None, "pmid": None, "date": None, "society": None, "url": None, "reviewed": True})
    for item in db.query(Guideline).filter(Guideline.published_at.isnot(None), Guideline.detection_status == "revisada").all():
        rows.append({"id": f"guideline:{item.id}", "entity_type": "diretriz", "slug": item.slug, "route": f"/diretrizes?slug={item.slug}", "theme": item.tema, "title": item.titulo, "text": " ".join(filter(None, [item.titulo, item.tema, item.org])), "doi": item.doi, "pmid": None, "date": str(item.ano), "society": item.org, "url": item.url, "reviewed": True})
    qtokens = tokens(query)
    if qtokens:
        rows.sort(key=lambda row: len(qtokens & tokens(row["title"] + " " + row["text"])), reverse=True)
    return rows[:limit]


def verify_source_rows(rows: list[dict], *, opener=reopen_publication) -> list[dict]:
    """Reopen identifiers and fail closed on malformed/mismatched metadata."""
    verified: list[dict] = []
    for original in rows:
        row = dict(original)
        doi, pmid = row.get("doi"), row.get("pmid")
        if doi or pmid:
            publication = opener(title=str(row.get("title") or ""), doi=doi, pmid=pmid)
            if publication is None:
                row["reviewed"] = False
                row["validation"] = "external_registry_mismatch_or_unavailable"
            else:
                external_text = str(publication.results or "").strip()
                local_text = str(row.get("text") or "")
                local_facts, external_facts = structured_facts(local_text), structured_facts(external_text)
                fact_mismatches = [key for key in ("quantities", "sample_sizes", "directions", "classes", "levels", "populations", "outcomes", "drug_classes") if not local_facts[key].issubset(external_facts[key])]
                local_years = set(DATE_RE.findall(str(row.get("date") or "")))
                external_years = set(DATE_RE.findall(str(publication.date or "")))
                date_mismatch = bool(local_years and (not external_years or not local_years.issubset(external_years)))
                authorized = bool(external_text and not fact_mismatches and not date_mismatch)
                row["validation"] = "external_registry_verified" if authorized else "external_bibliography_only_clinical_facts_unverified"
                row["verified_title"] = publication.title
                row["verified_doi"] = publication.doi
                row["verified_pmid"] = publication.pmid
                row["verified_date"] = publication.date
                row["verified_population"] = publication.population
                row["external_text"] = external_text
                row["clinical_claims_authorized"] = authorized
                row["clinical_fact_mismatches"] = fact_mismatches + (["date"] if date_mismatch else [])
                if not authorized:
                    row["reviewed"] = False
        else:
            row["validation"] = "internal_reviewed_record_no_identifier"
            row["clinical_claims_authorized"] = False
        verified.append(row)
    return verified


def validate_claim_support(claim: str, source_ids: Iterable[str], registry: dict[str, dict]) -> tuple[bool, str | None]:
    ids = list(source_ids or [])
    if not ids:
        return False, "afirmação clínica sem fonte"
    sources = [registry[sid] for sid in ids if sid in registry and registry[sid].get("reviewed") and (registry[sid].get("clinical_claims_authorized") is not False)]
    if len(sources) != len(ids):
        return False, "fonte ausente ou não revisada"
    combined = " ".join(str(s.get("external_text") if s.get("validation") == "external_registry_verified" else s.get("text") or "") for s in sources)
    if not _required_overlap(claim, combined):
        return False, "afirmação não encontrada nas fontes"
    return exact_facts_supported(claim, combined)


def sanitize_registry_for_persistence(registry: list[dict]) -> list[dict]:
    """Never persist provider abstracts fetched for verification."""
    return [{k: v for k, v in row.items() if k not in {"external_abstract", "external_text"}} for row in registry]
