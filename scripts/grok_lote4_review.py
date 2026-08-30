#!/usr/bin/env python3
"""Revisor independente do lote 4 Grok. Números ⊆ abstract PubMed."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEP = json.loads(Path("/tmp/pubmed_lote4/keep.json").read_text())
DOC = set(json.loads(Path("/tmp/document_slugs.json").read_text()))
DOENCA = set(json.loads(Path("/tmp/doenca_slugs.json").read_text()))

estudos = json.loads((ROOT / "estudos/metadados.json").read_text())
evidencias = json.loads((ROOT / "evidencias/metadados.json").read_text())

ge = [r for r in estudos if r.get("fonte_producao") == "grok" and (r.get("review_note") or "").startswith("Lote 4")]
gv = [r for r in evidencias if r.get("fonte_producao") == "grok" and (r.get("review_note") or "").startswith("Lote 4")]
base_e = [r for r in estudos if r not in ge]
pmid2keep = {str(p["pmid"]): p for p in KEEP.values()}

errors: list = []
warnings: list = []


def tok_en(text: str) -> set[str]:
    t = text.replace("\u00a0", " ").replace("\u2009", " ").replace("\u202f", " ").replace("\u2007", " ")
    t = t.replace("·", ".").replace("∙", ".").replace("•", ".").replace("．", ".")
    t = t.replace("−", "-").replace("–", "-").replace("—", "-")
    t = re.sub(r"(?<=\d)[\s](?=\d{3}(?:\D|$))", "", t)
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    out: set[str] = set()
    for m in re.finditer(r"\d*\.\d+|\d+", t):
        raw = m.group(0)
        out.add(raw)
        if raw.startswith("."):
            out.add("0" + raw)
        if raw.startswith("0.") and len(raw) > 2:
            out.add(raw[1:])
        if "." in raw:
            s = raw.rstrip("0").rstrip(".")
            if s:
                out.add(s)
    return out


def pt_toks(text: str) -> list[str]:
    t = text.replace("−", "-").replace("–", "-")
    return re.findall(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+|\d+\.\d+|\d+", t)


def norm_pt(raw: str) -> str:
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw):
        return raw.replace(".", "")
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+,\d+", raw):
        a, b = raw.split(",", 1)
        return a.replace(".", "") + "." + b
    if re.fullmatch(r"\d+\.\d+", raw):
        return raw
    if "," in raw:
        return raw.replace(",", ".")
    return raw


def numbers_ok(pt_text: str, abstract: str) -> list[str]:
    ab_flat = tok_en(abstract)
    miss = []
    for tok in pt_toks(pt_text):
        n = norm_pt(tok)
        if n in ab_flat:
            continue
        try:
            f = float(n)
            if f == int(f) and 1 <= int(f) <= 9:
                continue
            if any(abs(float(a) - f) < 1e-9 for a in ab_flat if re.fullmatch(r"\d*\.?\d+", a)):
                continue
        except ValueError:
            pass
        miss.append(tok)
    return miss


for label, rows, key in [("slug_est", estudos, "slug"), ("slug_evi", evidencias, "slug")]:
    dups = [k for k, n in Counter(r[key] for r in rows).items() if n > 1]
    if dups:
        errors.append(("dup_" + label, dups[:8]))

base_pmids = {str(r.get("pmid")).strip() for r in base_e if r.get("pmid")}
base_dois = {str(r.get("doi")).strip().lower() for r in base_e if r.get("doi")}
grok_pmids = [str(r.get("pmid")).strip() for r in ge]
for p, n in Counter(grok_pmids).items():
    if n > 1:
        errors.append(("dup_lote4_pmid", p))
for p in grok_pmids:
    if p in base_pmids:
        errors.append(("pmid_collision_base", p))

for r in ge:
    doi = (r.get("doi") or "").strip().lower()
    if doi and doi in base_dois:
        errors.append(("doi_collision_base", r["slug"], doi))
    if not r.get("pmid"):
        errors.append(("empty_pmid", r["slug"]))
    if r.get("review_status") != "pendente_revisao":
        errors.append(("review_status", r["slug"]))
    if r.get("published") not in (False, None):
        errors.append(("published", r["slug"]))
    ds, dis = r.get("document_slug"), r.get("disease_slug")
    if ds and ds not in DOC:
        errors.append(("bad_doc", r["slug"], ds))
    if dis and dis not in DOENCA:
        errors.append(("bad_disease", r["slug"], dis))
    paper = pmid2keep.get(str(r.get("pmid")))
    if not paper:
        errors.append(("pmid_not_in_keep", r["slug"], r.get("pmid")))
        continue
    for field in ("summary", "key_findings", "clinical_implications", "limitations", "title"):
        val = r.get(field) or ""
        if not val.strip():
            errors.append(("empty", field, r["slug"]))
        if re.search(r"\b(TODO|TBD|placeholder)\b", val):
            errors.append(("placeholder", field, r["slug"]))
    kf = r.get("key_findings") or ""
    if re.search(r"\b(We randomly|hazard ratio for|patients were randomly)\b", kf):
        errors.append(("english_dump", r["slug"]))
    blob = (r.get("summary") or "") + " " + kf
    miss = numbers_ok(blob, paper["abstract"])
    miss = [m for m in miss if norm_pt(m) not in {str(paper.get("year") or ""), str(paper.get("pmid"))}]
    if miss:
        errors.append(("numbers", r["slug"], miss[:12]))

g_pmids = {str(r.get("pmid")) for r in ge}
for r in gv:
    if str(r.get("pmid")) not in g_pmids:
        errors.append(("evid_pmid_orphan", r["slug"], r.get("pmid")))
    if r.get("review_status") != "pendente_revisao":
        errors.append(("evid_status", r["slug"]))
    if r.get("published") not in (False, None):
        errors.append(("evid_published", r["slug"]))
    if r.get("society") not in {"RCT-índice", "Meta-análise-índice", "Coorte-índice"}:
        errors.append(("society", r["slug"], r.get("society")))
    if r.get("recommendation_class") != "Ponderado":
        errors.append(("class", r["slug"]))
    paper = pmid2keep.get(str(r.get("pmid")))
    if paper:
        miss = numbers_ok(r.get("statement") or "", paper["abstract"])
        miss = [m for m in miss if norm_pt(m) not in {str(paper.get("year") or ""), str(paper.get("pmid"))}]
        if miss:
            errors.append(("evid_numbers", r["slug"], miss[:12]))

print("INDEPENDENT REVIEW lote 4")
print("estudos_lote4", len(ge), "evidencias_lote4", len(gv), "keep", len(KEEP))
print("errors", len(errors), "warnings", len(warnings))
for e in errors:
    print("ERR", e)
for w in warnings[:20]:
    print("WARN", w)
if errors:
    sys.exit(1)
print("OK")
