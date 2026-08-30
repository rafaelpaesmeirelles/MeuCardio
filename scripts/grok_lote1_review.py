#!/usr/bin/env python3
"""Revisor independente do lote 1 Grok.

Não importa o mapa de síntese do produtor. Confronta PMIDs/números com
/tmp/pubmed_lote1/keep.json (efetch) e o corpus-base.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEP = json.loads(Path("/tmp/pubmed_lote1/keep.json").read_text())
DOC = set(json.loads(Path("/tmp/document_slugs.json").read_text()))
DOENCA = set(json.loads(Path("/tmp/doenca_slugs.json").read_text()))

estudos = json.loads((ROOT / "estudos/metadados.json").read_text())
evidencias = json.loads((ROOT / "evidencias/metadados.json").read_text())

ge = [r for r in estudos if r.get("fonte_producao") == "grok"]
gv = [r for r in evidencias if r.get("fonte_producao") == "grok"]
base_e = [r for r in estudos if r.get("fonte_producao") != "grok"]
base_v = [r for r in evidencias if r.get("fonte_producao") != "grok"]
pmid2keep = {str(p["pmid"]): p for p in KEEP.values()}

errors: list = []
warnings: list = []


def tok_en(text: str) -> set[str]:
    t = text.replace("\u00a0", " ").replace("·", ".")
    t = re.sub(r"(?<=\d)[\s\u00a0\u2009\u202f](?=\d{3}(?:\D|$))", "", t)
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


# uniqueness
for label, rows, key in [("slug_est", estudos, "slug"), ("slug_evi", evidencias, "slug")]:
    dups = [k for k, n in Counter(r[key] for r in rows).items() if n > 1]
    if dups:
        errors.append(("dup_" + label, dups[:8]))

base_pmids = {str(r.get("pmid")).strip() for r in base_e if r.get("pmid")}
base_dois = {str(r.get("doi")).strip().lower() for r in base_e if r.get("doi")}
grok_pmids = [str(r.get("pmid")).strip() for r in ge]
for p, n in Counter(grok_pmids).items():
    if n > 1:
        errors.append(("dup_grok_pmid_estudo", p))
for p in grok_pmids:
    if p in base_pmids:
        errors.append(("pmid_collision_base", p))

NEUTRAL_HINT = re.compile(
    r"n[aã]o reduziu|n[aã]o foi superior|n[aã]o diferiu|n[aã]o alcan[cç]ou|"
    r"n[aã]o atingiu|prim[aá]rio (n[aã]o|neutro)|desfecho neutro|p=0,5|"
    r"n[aã]o inferioridade n[aã]o atingida|futilidade",
    re.I,
)
FALSE_BENEFIT = re.compile(
    r"(?<!n[aã]o )(?<!nao )reduziu o prim[aá]rio|(?<!n[aã]o )foi superior no prim[aá]rio|"
    r"benef[ií]cio no desfecho prim[aá]rio",
    re.I,
)

if len(ge) != 69:
    errors.append(("estudo_count", len(ge), "expected 69"))

for r in ge:
    doi = (r.get("doi") or "").strip().lower()
    if doi and doi in base_dois:
        errors.append(("doi_collision_base", r["slug"], doi))
    if not r.get("pmid"):
        errors.append(("empty_pmid", r["slug"]))
    if r.get("slug") in {x["slug"] for x in base_e}:
        errors.append(("slug_collision_base", r["slug"]))
    if r.get("review_status") != "pendente_revisao":
        errors.append(("review_status", r["slug"], r.get("review_status")))
    if r.get("published") not in (False, None):
        errors.append(("published", r["slug"]))
    ds, dis = r.get("document_slug"), r.get("disease_slug")
    if ds and ds not in DOC:
        errors.append(("bad_doc", r["slug"], ds))
    if dis and dis not in DOENCA:
        errors.append(("bad_disease", r["slug"], dis))
    if ds and ds in DOENCA and ds not in DOC:
        errors.append(("doc_is_disease", r["slug"], ds))
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
        if "sujeita à aprovação" in val.lower():
            errors.append(("hedge", field, r["slug"]))
    kf = r.get("key_findings") or ""
    if kf.startswith("Números conferidos") or re.search(
        r"\b(We randomly|hazard ratio for|patients were randomly)\b", kf
    ):
        errors.append(("english_dump", r["slug"]))
    blob = (r.get("summary") or "") + " " + kf
    miss = numbers_ok(blob, paper["abstract"])
    miss = [m for m in miss if norm_pt(m) not in {str(paper.get("year")), str(paper.get("pmid"))}]
    if miss:
        errors.append(("numbers", r["slug"], miss[:12]))
    if not (r.get("doi") or "").strip() and "gissi-prevenzione" not in r["slug"]:
        warnings.append(("empty_doi", r["slug"]))
    clin = r.get("clinical_implications") or ""
    # Only flag if the text claims the PRIMARY was reduced while also calling the primary non-significant.
    if re.search(r"reduziu o prim[aá]rio|foi superior no prim[aá]rio", clin, re.I) and re.search(
        r"prim[aá]rio.{0,80}n[aã]o (reduziu|diferiu|alcan[cç]ou|atingiu)|n[aã]o reduziu o prim[aá]rio",
        (r.get("key_findings") or "") + " " + clin,
        re.I,
    ):
        if not re.search(r"n[aã]o reduziu o prim[aá]rio|n[aã]o foi superior no prim[aá]rio", clin, re.I):
            errors.append(("possible_false_benefit", r["slug"]))

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
        errors.append(("class", r["slug"], r.get("recommendation_class")))
    st = r.get("statement") or ""
    if not st.strip():
        errors.append(("empty_statement", r["slug"]))
    if re.search(r"\b(TODO|TBD|placeholder)\b", st):
        errors.append(("placeholder_st", r["slug"]))
    ds = r.get("document_slug")
    if ds and ds not in DOC:
        errors.append(("evid_bad_doc", r["slug"], ds))
    paper = pmid2keep.get(str(r.get("pmid")))
    if paper:
        miss = numbers_ok(st, paper["abstract"])
        miss = [m for m in miss if norm_pt(m) not in {str(paper.get("year")), str(paper.get("pmid"))}]
        if miss:
            errors.append(("evid_numbers", r["slug"], miss[:12]))

print("INDEPENDENT REVIEW lote 1")
print("grok estudos", len(ge), "grok evidencias", len(gv))
print("base estudos", len(base_e), "base evidencias", len(base_v))
print("corpus", len(estudos) + len(evidencias))
print("unique grok pmids", len(g_pmids))
print("errors", len(errors))
for e in errors:
    print(" ERR", e)
print("warnings", len(warnings))
for w in warnings:
    print(" WARN", w)
if errors:
    sys.exit(2)
print("PASS")
print("BLOQUEIO_REVISAO: PDF integral não lido; classe/nível não conferidos em tabela de diretriz; review_status permanece pendente_revisao.")
