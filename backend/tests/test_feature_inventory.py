from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.api.evidence import _detail
from app.models.evidence import EvidenceRecord

ROOT = Path(__file__).resolve().parents[2]


def test_published_feature_inventory_is_intact():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/feature_inventory.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # Achado de auditoria (issue #52, subfase 8): os três números abaixo
    # tinham ficado defasados (rotas/routers novos entraram sem atualizar
    # este teste) — scripts/feature_inventory.py já tinha o mecanismo certo
    # (falha se um router desaparecer OU se um novo não constar da lista
    # revisada em EXPECTED_BACKEND_ROUTERS); o que faltava era só manter
    # este teste sincronizado com a contagem real depois de cada revisão.
    assert "61 rotas React" in result.stdout
    assert "37 destinos de menu" in result.stdout
    assert "48 routers FastAPI" in result.stdout


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