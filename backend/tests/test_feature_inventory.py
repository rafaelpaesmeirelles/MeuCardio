from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from app.api.evidence import _detail
from app.models.evidence import EvidenceRecord

ROOT = Path(__file__).resolve().parents[2]


def _inventory_count(output: str, label: str) -> int:
    match = re.search(rf"(\d+) {re.escape(label)}", output)
    assert match, f"contador ausente no inventário: {label}\n{output}"
    return int(match.group(1))


def test_published_feature_inventory_is_intact():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/feature_inventory.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    # Estes números são pisos certificados, não tetos: novas rotas/destinos e
    # routers publicados devem poder aumentar o inventário sem quebrar lotes
    # antigos. Queda abaixo do baseline continua sendo regressão bloqueante.
    assert _inventory_count(result.stdout, "rotas React") >= 74
    assert _inventory_count(result.stdout, "destinos") >= 48
    assert _inventory_count(result.stdout, "routers FastAPI") >= 61


def test_evidence_editorial_note_is_preserved_in_detail():
    evidence = EvidenceRecord(
        slug="teste-nota-editorial",
        statement="Recomendação de teste.",
        recommendation_class="I",
        evidence_level="A",
        society="SBC",
        year=2026,
        guideline_title="Diretriz de teste",
        reference="Referência de teste",
        theme="Teste",
        tags=["teste"],
        review_status="revisado",
        review_note="Conferido pelo corpo editorial.",
        published=True,
    )

    detail = _detail(evidence)

    assert detail["review_status"] == "revisado"
    assert detail["review_note"] == "Conferido pelo corpo editorial."
