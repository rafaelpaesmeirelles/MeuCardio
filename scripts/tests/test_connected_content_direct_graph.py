"""Database-free regressions for direct, cross-theme Tudo com Tudo links."""
from types import SimpleNamespace

import pytest

from app.services import connected_content as connected


KINDS = (
    "documento", "fluxograma", "evidencia", "estudo", "medicamento", "exame",
    "caso_clinico", "trilha", "galeria", "checklist", "material_paciente",
    "protocolo_emergencia", "calculadora", "doenca", "triagem_sintoma",
)


def _item(slug="destino-editorial", **overrides):
    return {
        "slug": slug, "titulo": "Destino com outra taxonomia",
        "rota": f"/biblioteca/{slug}", "relation_type": "mentioned_in",
        "confidence": "explicit", "provenance_type": "editorial",
        "review_status": "revisado", "relevance_score": 1.0,
        **overrides,
    }


def _group(kind, items):
    return {"tipo": kind, "rotulo": kind, "rota_lista": f"/{kind}", "itens": items}


def _setup(monkeypatch, direct, contextual=None):
    calls = []
    def graph(*args, **kwargs):
        calls.append(kwargs)
        return {"grupos": direct}
    monkeypatch.setattr(connected, "relacionados_de", graph)
    monkeypatch.setattr(connected, "_base", lambda *a, **kw: {"grupos": contextual or []})
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *a, **kw: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *a, **kw: [])
    return calls


def _query():
    return connected.buscar_relacionados_contextuais(
        object(), "Hipertensão", excluir_tipo="documento",
        excluir_slug="amiloidose", assunto="amiloidose",
    )


def _items(response, kind):
    return next((g["itens"] for g in response["grupos"] if g["tipo"] == kind), [])


@pytest.mark.parametrize("kind", KINDS)
def test_direct_cross_theme_links_survive_for_every_content_front(monkeypatch, kind):
    calls = _setup(monkeypatch, [_group(kind, [_item()])])
    result = _query()
    items = _items(result, kind)
    assert [i["slug"] for i in items] == ["destino-editorial"]
    assert items[0]["relation_scope"] == "direct_graph_relation"
    assert items[0]["review_status"] == "revisado"
    assert items[0]["provenance_type"] == "editorial"
    assert items[0]["context_only"] is False
    assert calls[0]["incluir_contexto_tematico"] is False


def test_direct_link_precedes_lexical_candidates_before_limit(monkeypatch):
    pool = [_item(f"amiloidose-{i}", titulo=f"Amiloidose {i}") for i in range(5)]
    _setup(monkeypatch, [_group("documento", [_item()])], [_group("documento", pool)])
    items = _items(_query(), "documento")
    assert items[0]["slug"] == "destino-editorial"
    assert len(items) == connected.LIMITE_POR_CATEGORIA


def test_duplicate_retains_graph_provenance_instead_of_lexical_metadata(monkeypatch):
    lexical = _item("amiloidose-destino", titulo="Amiloidose")
    direct = _item("amiloidose-destino")
    _setup(monkeypatch, [_group("documento", [direct])], [_group("documento", [lexical])])
    items = _items(_query(), "documento")
    assert len(items) == 1
    assert items[0]["relation_scope"] == "direct_graph_relation"
    assert items[0]["confidence"] == "explicit"
    assert "match_score" not in items[0]


def test_medication_without_supported_theme_still_has_its_explicit_graph(monkeypatch):
    drug = SimpleNamespace(slug="farmaco-teste", generic_name="Fármaco de teste")
    db = SimpleNamespace(execute=lambda statement: SimpleNamespace(scalar_one_or_none=lambda: drug))
    monkeypatch.setattr(connected, "temas_clinicos_do_medicamento", lambda item: [])
    calls = _setup(monkeypatch, [_group("documento", [_item()])])
    result = connected.buscar_relacionados_do_medicamento(db, drug.slug)
    assert [i["slug"] for i in _items(result, "documento")] == ["destino-editorial"]
    assert result["temas"] == []
    assert calls[0]["entity_type"] == "medicamento"
    assert calls[0]["incluir_contexto_tematico"] is False


@pytest.mark.parametrize("bad_item", [
    _item(relation_type="same_theme"),
    _item(relation_type="belongs_to_topic"),
    _item(context_only=True),
    _item(review_status="rejeitado"),
])
def test_taxonomy_rejected_or_context_only_edges_are_never_promoted(monkeypatch, bad_item):
    _setup(monkeypatch, [_group("documento", [bad_item])])
    assert _items(_query(), "documento") == []


def test_unknown_graph_types_and_topic_nodes_do_not_enter_clinical_panel(monkeypatch):
    _setup(monkeypatch, [_group("tema", [_item()]), _group("paciente", [_item()])])
    result = _query()
    assert all(g["tipo"] not in {"tema", "paciente"} for g in result["grupos"])


def test_free_subject_does_not_borrow_a_different_origins_graph(monkeypatch):
    calls = _setup(monkeypatch, [_group("documento", [_item()])])
    connected.buscar_relacionados_contextuais(
        object(), "Hipertensão", excluir_tipo="documento",
        excluir_slug="amiloidose", assunto="outro-assunto",
    )
    assert calls == []


def test_structural_pending_status_is_preserved_not_upgraded(monkeypatch):
    _setup(monkeypatch, [_group("doenca", [_item(review_status="pendente_revisao")])])
    assert _items(_query(), "doenca")[0]["review_status"] == "pendente_revisao"
