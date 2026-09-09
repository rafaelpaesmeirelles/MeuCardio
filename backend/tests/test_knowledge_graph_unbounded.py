"""Pagination composition preserves every eligible edge without database writes."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.knowledge_graph import relacionados_de


@pytest.fixture(autouse=True)
def _banco_limpo():
    # This module supplies an in-memory query boundary; no database is touched.
    yield


@pytest.mark.parametrize(("limit", "expected"), [(None, 1001), (5, 5)])
def test_internal_unbounded_graph_preserves_edges_and_explicit_limit(limit, expected):
    origin = SimpleNamespace(id=1, entity_type="doenca", slug="origem", title="Origem")
    edges = [
        (
            SimpleNamespace(
                relation_type="mentioned_in", relevance_score=1.0,
                confidence="explicit", provenance_type="editorial",
                review_status="revisado", evidence_source=None, extra={},
            ),
            SimpleNamespace(
                id=i + 2, entity_type="estudo", slug=f"estudo-{i:04}",
                title=f"Estudo {i:04}",
            ),
        )
        for i in range(1001)
    ]
    db = Mock()
    db.execute.side_effect = [
        Mock(scalar_one_or_none=Mock(return_value=origin)),
        Mock(all=Mock(return_value=edges)),
        Mock(all=Mock(return_value=[])),
    ]

    response = relacionados_de(
        db, entity_type="doenca", slug="origem", limite_por_tipo=limit,
        incluir_contexto_tematico=False,
    )

    assert response["total"] == 1001
    group = response["grupos"][0]
    assert group["total_disponivel"] == 1001
    assert len(group["itens"]) == expected
    assert group["itens"][0]["slug"] == "estudo-0000"
    assert group["itens"][-1]["slug"] == f"estudo-{expected - 1:04}"
    assert db.execute.call_count == 3
