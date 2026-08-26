"""Structural integrity for curated direct links in canonical manifests."""

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def _frontmatter_value(path: Path, field: str) -> str:
    header = path.read_text(encoding="utf-8").split("---", 2)[1]
    match = re.search(
        rf'(?m)^{field}:\s*["\']?(.*?)["\']?\s*$',
        header,
    )
    return match.group(1) if match else ""


def test_evidence_document_links_exist_and_keep_the_same_theme():
    documents = {}
    for path in (ROOT / "content").rglob("*.md"):
        slug = _frontmatter_value(path, "slug") or path.stem
        documents[slug] = _frontmatter_value(path, "theme")

    evidence = json.loads(
        (ROOT / "evidencias" / "metadados.json").read_text(encoding="utf-8")
    )
    linked = [item for item in evidence if item.get("document_slug")]

    assert linked, "O manifesto perdeu todos os vínculos evidência→documento."
    assert not [
        item["slug"] for item in linked
        if item["document_slug"] not in documents
    ]
    assert not [
        item["slug"] for item in linked
        if documents[item["document_slug"]] != item["theme"]
    ]
