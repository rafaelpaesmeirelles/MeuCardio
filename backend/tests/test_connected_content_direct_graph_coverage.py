"""Database-free regressions for direct Tudo com Tudo links across all fronts."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.services import connected_content as connected


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Override the repository's database fixture: these tests use no database."""
    yield


FRONTS = (
    "documento", "fluxograma", "evidencia", "estudo", "medicamento", "exame",
    "caso_clinico", "trilha", "galeria", "checklist", "material_paciente",
    "protocolo_emergencia", "calculadora", "doenca", "triagem_sintoma",
)


def _item(slug="destino", **metadata):
    return {
        "slug": slug, "titulo": "Destino sem sobreposição lexical",
        "rota": f"/biblioteca/{slug}", "relation_type": "mentioned_in",
        "relevance_score": 0.7, "confidence": "derived",
        "provenance_type": "structured_metadata", "review_status": "pendente_revisao",
        **metadata,
    }


def _group(kind="documento", items=None):
    return {
        "tipo": kind, "rotulo": f"Rótulo original: {kind}",
        "rota_lista": f"/catalogue/{kind}",
        "itens": [_item()] if items is None else items,
    }


def _project(db, **kwargs):
    # Resolve the legacy helper only to make the same regression reproduce
    # the pre-fix failure. Production code uses _direct_graph_groups.
    helper = getattr(connected, "_direct_graph_groups", None)
    if helper is None:
        helper = connected._specialty_direct_groups
    return helper(db, **kwargs)


@pytest.mark.parametrize("kind", FRONTS)
def test_every_content_front_preserves_a_policy_checked_direct_link(monkeypatch, kind):
    calls = []
    item = _item()
    def graph(_db, **kwargs):
        calls.append(kwargs)
        return {"grupos": [_group(kind, [item])]}
    monkeypatch.setattr(connected, "relacionados_de", graph)
    groups = _project(object(), entity_type="documento", slug="origem")
    assert len(groups) == 1
    actual = groups[0]["itens"][0]
    assert actual["slug"] == "destino"
    assert actual["review_status"] == "pendente_revisao"
    assert actual["confidence"] == "derived"
    assert actual["provenance_type"] == "structured_metadata"
    assert actual["relation_scope"] == "direct_graph_relation"
    assert item == _item(), "Projection must not mutate the graph response"
    assert calls == [{
        "entity_type": "documento", "slug": "origem",
        "limite_por_tipo": connected.LIMITE_POR_CATEGORIA,
        "incluir_contexto_tematico": False,
    }]


@pytest.mark.parametrize("entity_type,slug", [(None, "x"), ("tema", "x"), ("paciente", "x"), ("documento", None)])
def test_invalid_or_private_origin_never_queries_graph(monkeypatch, entity_type, slug):
    def forbidden(*_args, **_kwargs):
        pytest.fail("Graph must not be queried for a private/invalid origin")
    monkeypatch.setattr(connected, "relacionados_de", forbidden)
    assert _project(object(), entity_type=entity_type, slug=slug) == []


def test_taxonomy_rejected_edges_and_self_links_are_not_projected(monkeypatch):
    graph = {"grupos": [
        _group("tema"), _group("paciente"),
        _group("documento", [
            _item("same", relation_type="same_theme"),
            _item("topic", relation_type="belongs_to_topic"),
            _item("context", context_only=True),
            _item("rejected", review_status="rejeitado"),
            _item("origem"), _item("", relation_type="mentioned_in"),
            _item("missing-relation", relation_type=None), _item("valid"),
        ]),
    ]}
    monkeypatch.setattr(connected, "relacionados_de", lambda *_a, **_k: graph)
    groups = _project(object(), entity_type="documento", slug="origem")
    assert [(g["tipo"], [i["slug"] for i in g["itens"]]) for g in groups] == [("documento", ["valid"])]


def test_direct_metadata_wins_before_limit_without_changing_category_layout():
    limit = connected.LIMITE_POR_CATEGORIA
    groups = [_group("medicamento", []), _group("documento", [
        _item(f"lexical-{n}", relation_scope="clinical_match") for n in range(limit)
    ] + [_item("duplicate", relation_scope="clinical_match")])]
    direct = [_group("documento", [
        _item("duplicate", relation_scope="direct_graph_relation", review_status="revisado"),
        _item("direct-only", relation_scope="direct_graph_relation"),
    ]), _group("doenca", [_item("new-disease")])]
    snapshot = deepcopy((groups, direct))
    result = connected._merge_with_direct_groups(groups, direct)
    assert [g["tipo"] for g in result] == ["medicamento", "documento", "doenca"]
    assert result[1]["rotulo"] == groups[1]["rotulo"]
    assert len(result[1]["itens"]) == limit
    assert [i["slug"] for i in result[1]["itens"][:2]] == ["duplicate", "direct-only"]
    assert result[1]["itens"][0]["relation_scope"] == "direct_graph_relation"
    assert result[1]["itens"][0]["review_status"] == "revisado"
    assert (groups, direct) == snapshot


def test_equal_slugs_in_different_fronts_remain_distinct():
    result = connected._merge_with_direct_groups(
        [_group("documento", [_item("shared")])],
        [_group("estudo", [_item("shared")])],
    )
    assert sum(len(g["itens"]) for g in result) == 2


def _stub_catalogue(monkeypatch):
    monkeypatch.setattr(connected, "canonical_theme", lambda value: value)
    monkeypatch.setattr(connected, "theme_variants", lambda value: (value,))
    monkeypatch.setattr(connected, "_base", lambda *_a, **_k: {"grupos": []})
    monkeypatch.setattr(connected, "_origin_context", lambda _db, **kw: connected._OriginContext(kw["assunto"]))
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_a, **_k: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_a, **_k: [])
    monkeypatch.setattr(connected, "_filter_groups_by_subject", lambda *_a, **_k: None)


def test_actual_contextual_entrypoint_recovers_links_after_lexical_filter(monkeypatch):
    _stub_catalogue(monkeypatch)
    monkeypatch.setattr(connected, "relacionados_de", lambda *_a, **_k: {"grupos": [_group("estudo")]})
    result = connected.buscar_relacionados_contextuais(
        object(), "Tema amplo", excluir_tipo="documento", excluir_slug="origem", assunto="origem",
    )
    assert result["total"] == 1
    assert next(g for g in result["grupos"] if g["tipo"] == "estudo")["itens"][0]["relation_scope"] == "direct_graph_relation"


@pytest.mark.parametrize("subject", [None, "consulta-livre"])
def test_free_search_does_not_claim_the_excluded_items_graph(monkeypatch, subject):
    _stub_catalogue(monkeypatch)
    def forbidden(*_args, **_kwargs):
        pytest.fail("Free text is not a typed origin")
    monkeypatch.setattr(connected, "relacionados_de", forbidden)
    result = connected.buscar_relacionados_contextuais(
        object(), "Tema amplo", excluir_tipo="documento", excluir_slug="origem", assunto=subject,
    )
    assert result["total"] == 0


def _drug_db(monkeypatch, drug):
    query = SimpleNamespace(where=lambda *_a: None)
    monkeypatch.setattr(connected, "select", lambda *_a: query)
    return SimpleNamespace(execute=lambda _q: SimpleNamespace(scalar_one_or_none=lambda: drug))


def test_drug_without_recognized_topic_still_has_direct_graph_links(monkeypatch):
    drug = SimpleNamespace(slug="medicamento-raro", generic_name="Medicamento de teste")
    db = _drug_db(monkeypatch, drug)
    monkeypatch.setattr(connected, "temas_clinicos_do_medicamento", lambda _drug: [])
    monkeypatch.setattr(connected, "relacionados_de", lambda *_a, **_k: {"grupos": [_group("documento")]})
    result = connected.buscar_relacionados_do_medicamento(db, drug.slug)
    assert result["temas"] == []
    assert result["total"] == 1
    assert result["relation_scope"] == "direct_graph_relation"
    assert result["relation_method"] == "policy_checked_graph"


def test_missing_drug_does_not_expose_a_stale_graph(monkeypatch):
    db = _drug_db(monkeypatch, None)
    def forbidden(*_args, **_kwargs):
        pytest.fail("A missing/unpublished drug must not reach the graph")
    monkeypatch.setattr(connected, "relacionados_de", forbidden)
    assert connected.buscar_relacionados_do_medicamento(db, "missing") is None


def test_drug_without_topic_or_direct_links_remains_empty(monkeypatch):
    drug = SimpleNamespace(slug="isolado", generic_name="Isolado")
    db = _drug_db(monkeypatch, drug)
    monkeypatch.setattr(connected, "temas_clinicos_do_medicamento", lambda _drug: [])
    monkeypatch.setattr(connected, "relacionados_de", lambda *_a, **_k: None)
    result = connected.buscar_relacionados_do_medicamento(db, drug.slug)
    assert result["total"] == 0
    assert result["grupos"] == []
