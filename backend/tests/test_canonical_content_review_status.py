"""Garante que o corpus liberado pelo proprietário permaneça explicitamente revisado."""

from __future__ import annotations

import json
from pathlib import Path
import re


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = (
    "galeria/metadados.json",
    "exames/metadados.json",
    "evidencias/metadados.json",
    "estudos/metadados.json",
    "medicamentos/metadados.json",
    "checklists/metadados.json",
    "trilhas/metadados.json",
    "material-paciente/metadados.json",
    "emergencia/metadados.json",
    "casos-clinicos/metadados.json",
    "doencas/metadados.json",
    "triagem-sintomas/metadados.json",
)


def test_todos_os_manifestos_canonicos_estao_revisados():
    pendentes: list[str] = []
    for relative_path in MANIFESTS:
        records = json.loads((REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8"))
        for record in records:
            if record.get("review_status") != "revisado":
                identifier = record.get("slug") or record.get("title") or record.get("titulo")
                pendentes.append(f"{relative_path}:{identifier}:{record.get('review_status')}")

    assert pendentes == []


def test_todos_os_documentos_markdown_estao_revisados():
    pendentes: list[str] = []
    sem_status: list[str] = []
    for path in sorted((REPOSITORY_ROOT / "content").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
        match = re.search(r"^review_status:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
        relative_path = str(path.relative_to(REPOSITORY_ROOT))
        if match is None:
            sem_status.append(relative_path)
        elif match.group(1).strip() != "revisado":
            pendentes.append(f"{relative_path}:{match.group(1).strip()}")

    assert sem_status == []
    assert pendentes == []
