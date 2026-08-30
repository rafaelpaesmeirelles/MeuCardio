#!/usr/bin/env python3
"""Audita documentos científicos antes da promoção editorial.

O gate combina validações determinísticas locais com a resolução opcional dos
PMIDs no PubMed. Ele não substitui julgamento clínico, mas impede que um lote
seja promovido com metadados incompletos, referências inexistentes ou sinais
óbvios de sobreinterpretação.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
PMID_RE = re.compile(r"\bPMID\s*:?\s*\*{0,2}(\d{6,9})\b", re.IGNORECASE)
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD)\b|\b(?:[Ll]orem [Ii]psum|[Pp]laceholder|"
    r"[Cc]onte[uú]do indispon[ií]vel|[Aa]guardando reconstru[cç][aã]o)\b"
)
EDITORIAL_RE = re.compile(
    r"publica[cç][aã]o sujeita|aprova[cç][aã]o do respons[aá]vel t[eé]cnico|"
    r"\b(?:n[aã]o|não) relid[oa]s?\b",
    re.IGNORECASE,
)
OVERCLAIM_RE = re.compile(
    r"\b(?:salva(?:r)? vida|pro[ií]be|garante|sempre|nunca|deve obrigatoriamente|"
    r"sem qualquer risco|risco zero|indica[cç][aã]o autom[aá]tica)\b",
    re.IGNORECASE,
)
NUMERIC_RE = re.compile(
    r"(?<![\w.])(?:[<>≤≥]=?\s*)?\d+(?:[.,]\d+)?\s*(?:%|mg|g/dl|mmhg|h|d|"
    r"dias?|meses?|anos?|hr|rr|or|p\s*[<=>]|\b)",
    re.IGNORECASE,
)


def _load_paths(path_file: Path | None) -> list[Path]:
    if path_file is None:
        return sorted((ROOT / "content").rglob("*.md"))
    paths: list[Path] = []
    for raw in path_file.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            paths.append(ROOT / raw)
    return paths


def _load_document(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    try:
        header, content = raw[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc
    metadata = yaml.safe_load(header)
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter is not a mapping")
    return metadata, content


def _plain_text(metadata: dict[str, Any], content: str) -> str:
    refs = metadata.get("source_refs") or []
    if not isinstance(refs, list):
        refs = [str(refs)]
    return "\n".join(
        [
            str(metadata.get("title") or ""),
            str(metadata.get("summary") or ""),
            str(metadata.get("review_note") or ""),
            *(str(ref) for ref in refs),
            content,
        ]
    )


def _efetch(pmids: list[str]) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for offset in range(0, len(pmids), 150):
        batch = pmids[offset : offset + 150]
        params = urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(batch), "retmode": "xml"}
        )
        request = urllib.request.Request(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + params,
            headers={"User-Agent": "CorVIA-publication-audit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            root = ET.fromstring(response.read())
        for article in [
            *root.findall(".//PubmedArticle"),
            *root.findall(".//PubmedBookArticle"),
        ]:
            pmid = "".join(article.findtext(".//PMID", default="")).strip()
            title_node = article.find(".//ArticleTitle")
            if title_node is None:
                title_node = article.find(".//BookDocument/ArticleTitle")
            title = "" if title_node is None else "".join(title_node.itertext())
            abstract = " ".join(
                "".join(node.itertext())
                for node in article.findall(".//Abstract/AbstractText")
            )
            doi = ""
            for node in article.findall("./PubmedData/ArticleIdList/ArticleId"):
                if node.attrib.get("IdType") == "doi":
                    doi = (node.text or "").strip()
            if pmid:
                records[pmid] = {
                    "title": title.strip(),
                    "abstract": abstract.strip(),
                    "doi": doi,
                }
    return records


def audit(
    paths: list[Path], verify_pubmed: bool, only_status: str | None = None
) -> dict[str, Any]:
    documents: list[dict[str, Any]] = []
    slug_counts: Counter[str] = Counter()
    all_pmids: set[str] = set()

    for path in paths:
        relative = str(path.relative_to(ROOT))
        errors: list[str] = []
        warnings: list[str] = []
        try:
            metadata, content = _load_document(path)
        except Exception as exc:  # pragma: no cover - reported as audit data
            documents.append(
                {"path": relative, "errors": [f"frontmatter: {type(exc).__name__}"]}
            )
            continue

        if only_status and metadata.get("review_status") != only_status:
            continue
        for field in ("title", "slug", "theme", "kind", "review_status", "source_refs"):
            if not metadata.get(field):
                errors.append(f"missing:{field}")
        slug = str(metadata.get("slug") or "").strip()
        if slug:
            slug_counts[slug] += 1
        refs = metadata.get("source_refs") or []
        if not isinstance(refs, list):
            errors.append("source_refs:not-list")
            refs = [str(refs)]
        text = _plain_text(metadata, content)
        pmids = sorted(set(PMID_RE.findall(text)))
        dois = sorted(set(match.rstrip(".,;)") for match in DOI_RE.findall(text)))
        reference_pairs = []
        for ref in refs:
            ref_text = str(ref)
            reference_pairs.append(
                {
                    "pmids": sorted(set(PMID_RE.findall(ref_text))),
                    "dois": sorted(
                        set(match.rstrip(".,;)") for match in DOI_RE.findall(ref_text))
                    ),
                }
            )
        if not pmids:
            errors.append("source_refs:no-pmid")
        all_pmids.update(pmids)
        if PLACEHOLDER_RE.search(text):
            errors.append("placeholder")
        editorial = sorted(set(match.group(0) for match in EDITORIAL_RE.finditer(text)))
        if editorial:
            warnings.append("editorial-language:" + "|".join(editorial))
        overclaim = sorted(set(match.group(0) for match in OVERCLAIM_RE.finditer(text)))
        if overclaim:
            warnings.append("overclaim-language:" + "|".join(overclaim))
        documents.append(
            {
                "path": relative,
                "slug": slug,
                "status": metadata.get("review_status"),
                "pmids": pmids,
                "dois": dois,
                "reference_pairs": reference_pairs,
                "numeric_claims": sorted(set(NUMERIC_RE.findall(text))),
                "errors": errors,
                "warnings": warnings,
            }
        )

    duplicated = sorted(slug for slug, count in slug_counts.items() if count > 1)
    if duplicated:
        for document in documents:
            if document.get("slug") in duplicated:
                document.setdefault("errors", []).append("duplicate-slug")

    pubmed: dict[str, dict[str, str]] = {}
    if verify_pubmed:
        pubmed = _efetch(sorted(all_pmids))
        missing_pmids = all_pmids - set(pubmed)
        for document in documents:
            unresolved = sorted(set(document.get("pmids", [])) & missing_pmids)
            if unresolved:
                document.setdefault("errors", []).append(
                    "unresolved-pmid:" + ",".join(unresolved)
                )
            doi_mismatches: list[str] = []
            for pair in document.get("reference_pairs", []):
                cited_dois = {doi.lower() for doi in pair.get("dois", [])}
                if not cited_dois:
                    continue
                for pmid in pair.get("pmids", []):
                    canonical = pubmed.get(pmid, {}).get("doi", "").lower()
                    if canonical and canonical not in cited_dois:
                        doi_mismatches.append(f"{pmid}:{canonical}")
            if doi_mismatches:
                document.setdefault("errors", []).append(
                    "doi-not-among-cited:" + ",".join(doi_mismatches)
                )

    error_docs = [item["path"] for item in documents if item.get("errors")]
    warning_docs = [item["path"] for item in documents if item.get("warnings")]
    return {
        "documents": len(documents),
        "unique_slugs": len(slug_counts),
        "unique_pmids": len(all_pmids),
        "resolved_pmids": len(pubmed) if verify_pubmed else None,
        "error_documents": error_docs,
        "warning_documents": warning_docs,
        "details": documents,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-from", type=Path)
    parser.add_argument("--verify-pubmed", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--only-status")
    args = parser.parse_args()

    result = audit(_load_paths(args.paths_from), args.verify_pubmed, args.only_status)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    if args.strict and result["error_documents"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
