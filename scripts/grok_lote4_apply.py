#!/usr/bin/env python3
"""Aplica lote 4 Grok (estudos + evidências) no clone local. Não publica. Não mexe em main."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEP = json.loads(Path("/tmp/pubmed_lote4/keep.json").read_text())
SYNTH = json.loads(Path("/tmp/lote4_synth.json").read_text())
DOC = set(json.loads(Path("/tmp/document_slugs.json").read_text()))
DOENCA = set(json.loads(Path("/tmp/doenca_slugs.json").read_text()))

JOURNAL = {
    "The New England journal of medicine": "New England Journal of Medicine",
    "The New England Journal of Medicine": "New England Journal of Medicine",
    "Lancet (London, England)": "Lancet",
    "The Lancet": "Lancet",
    "European heart journal": "European Heart Journal",
    "Journal of the American College of Cardiology": "Journal of the American College of Cardiology",
    "JAMA": "JAMA",
    "Circulation": "Circulation",
}

NOTE_E = (
    "Lote 4 Grok 2026-08-30. Síntese portuguesa original a partir do abstract PubMed (efetch). "
    "Números restritos ao abstract. PDF integral não lido. Manter pendente_revisao até revisão "
    "independente de fonte, números, interpretação e segurança."
)
NOTE_V = (
    "Lote 4 Grok 2026-08-30. Não é classe de diretriz ESC/AHA/SBC. Derivado do ensaio-índice "
    "(abstract). Manter pendente_revisao até casar com tabela oficial e revisão independente."
)
NOTE_V2 = (
    "Lote 4 Grok 2026-08-30. Segunda evidência do mesmo ensaio-índice (segurança, secundário ou "
    "limite de desenho). Não é classe de diretriz ESC/AHA/SBC. Números do abstract. Manter "
    "pendente_revisao até casar com tabela oficial e revisão independente."
)

LEVEL = {
    "ensaio_clinico": "B-R",
    "metanalise": "A",
    "coorte_prospectiva": "B-NR",
    "estudo_de_coorte": "B-NR",
}
SOC = {
    "ensaio_clinico": "RCT-índice",
    "metanalise": "Meta-análise-índice",
    "coorte_prospectiva": "Coorte-índice",
    "estudo_de_coorte": "Coorte-índice",
}


def main() -> int:
    missing = [k for k in SYNTH if k not in KEEP]
    extra = [k for k in KEEP if k not in SYNTH]
    if missing:
        print("synth/keep mismatch missing", missing)
        return 1
    if extra:
        print("keep extra skipped", extra)

    estudos = json.loads((ROOT / "estudos/metadados.json").read_text())
    evidencias = json.loads((ROOT / "evidencias/metadados.json").read_text())
    slugs = {r["slug"] for r in estudos} | {r["slug"] for r in evidencias}
    pmids = {str(r.get("pmid")) for r in estudos if r.get("pmid")}
    dois = {(r.get("doi") or "").strip().lower() for r in estudos if r.get("doi")}

    new_e, new_v = [], []
    for key, s in SYNTH.items():
        p = KEEP[key]
        pmid = str(p["pmid"])
        doi = (p.get("doi") or "").strip()
        if pmid in pmids:
            print("PMID collision", key, pmid)
            return 1
        if doi and doi.lower() in dois:
            print("DOI collision", key, doi)
            return 1
        if s["slug"] in slugs:
            print("slug collision", s["slug"])
            return 1
        if s.get("document_slug") and s["document_slug"] not in DOC:
            print("bad doc", s["slug"], s["document_slug"])
            return 1
        if s.get("disease_slug") and s["disease_slug"] not in DOENCA:
            print("bad disease", s["slug"], s["disease_slug"])
            return 1
        year = p.get("year") or s.get("year")
        authors = (p.get("authors") or "").strip() or s.get("authors") or "Investigadores do estudo"
        rec = {
            "slug": s["slug"],
            "title": s["title"],
            "study_type": s.get("study_type", "ensaio_clinico"),
            "authors": authors,
            "journal": JOURNAL.get(p.get("journal") or "", p.get("journal") or s.get("journal") or ""),
            "year": year,
            "doi": doi,
            "pmid": pmid,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "summary": s["summary"],
            "key_findings": s["key_findings"],
            "clinical_implications": s["clinical_implications"],
            "limitations": s["limitations"],
            "theme": s["theme"],
            "tags": s["tags"],
            "review_status": "pendente_revisao",
            "published": False,
            "fonte_producao": "grok",
            "review_note": NOTE_E,
        }
        if s.get("document_slug"):
            rec["document_slug"] = s["document_slug"]
        if s.get("disease_slug"):
            rec["disease_slug"] = s["disease_slug"]
        new_e.append(rec)
        slugs.add(s["slug"])
        pmids.add(pmid)
        if doi:
            dois.add(doi.lower())

        stype = rec["study_type"]
        ev = {
            "slug": s["slug"] + "-implicacao-do-ensaio",
            "statement": s["statement"],
            "recommendation_class": "Ponderado",
            "evidence_level": LEVEL.get(stype, "B-R"),
            "society": SOC.get(stype, "RCT-índice"),
            "year": year,
            "guideline_title": s["title"],
            "reference": f"{authors}. {s['title']}. {rec['journal']}. {year}. DOI: {doi}. PMID: {pmid}." if doi else f"{authors}. {s['title']}. {rec['journal']}. {year}. PMID: {pmid}.",
            "theme": s["theme"],
            "tags": s["tags"],
            "review_status": "pendente_revisao",
            "published": False,
            "fonte_producao": "grok",
            "pmid": pmid,
            "doi": doi,
            "review_note": NOTE_V,
        }
        if s.get("document_slug"):
            ev["document_slug"] = s["document_slug"]
        if ev["slug"] in slugs:
            print("evid slug collision", ev["slug"])
            return 1
        new_v.append(ev)
        slugs.add(ev["slug"])

        sec = s.get("second")
        if sec:
            ev2 = deepcopy(ev)
            ev2["slug"] = sec["slug"]
            ev2["statement"] = sec["statement"]
            ev2["tags"] = sec["tags"]
            ev2["review_note"] = NOTE_V2
            if ev2["slug"] in slugs:
                print("evid2 slug collision", ev2["slug"])
                return 1
            new_v.append(ev2)
            slugs.add(ev2["slug"])

    estudos.extend(new_e)
    evidencias.extend(new_v)
    (ROOT / "estudos/metadados.json").write_text(
        json.dumps(estudos, ensure_ascii=False, indent=2) + "\n"
    )
    (ROOT / "evidencias/metadados.json").write_text(
        json.dumps(evidencias, ensure_ascii=False, indent=2) + "\n"
    )
    print("applied estudos", len(new_e), "evidencias", len(new_v), "total_e", len(estudos), "total_v", len(evidencias))
    return 0


if __name__ == "__main__":
    sys.exit(main())
