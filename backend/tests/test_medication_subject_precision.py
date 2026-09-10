"""Medication connections preserve identity and typed links, not whole themes.

Pure service regressions: run the actual ecosystem/merger/matcher while
substituting only persistence and the already policy-checked graph response.
"""
from types import SimpleNamespace

import pytest

from app.services import connected_content as connected


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Override the database cleanup fixture: these checks are database-free."""
    yield


def item(slug, title, **metadata):
    return {"slug": slug, "titulo": title, "subtitulo": "Documento",
            "rota": f"/biblioteca/{slug}", **metadata}


def group(items):
    return {"tipo": "documento", "rotulo": "Documentos",
            "rota_lista": "/biblioteca", "itens": items}


class FakeDB:
    def __init__(self, drug):
        self.drug = drug

    def execute(self, _query):
        return SimpleNamespace(scalar_one_or_none=lambda: self.drug)


def medication(**overrides):
    return SimpleNamespace(**{
        "slug": "apixabana", "generic_name": "Apixabana",
        "brand_names": ["Eliquis"],
        "indications": ["Prevenção de AVC na fibrilação atrial não valvar."],
        "dosing": {}, "review_status": "revisado", "published": True,
        **overrides,
    })


def arrange(monkeypatch, candidates, direct=()):
    monkeypatch.setattr(connected, "_base", lambda *_args, **_kwargs:
                        {"grupos": [group(candidates)]})
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "relacionados_de", lambda *_args, **_kwargs:
                        {"grupos": [group(list(direct))], "total": len(direct)})


def flattened(result):
    return {i["slug"]: i for g in result["grupos"] for i in g["itens"]}


def test_medication_keeps_brand_and_cross_topic_direct_link_without_theme_noise(monkeypatch):
    arrange(monkeypatch, [
        item("ablacao-isolamento", "Ablação e isolamento de veias pulmonares"),
        item("fa-generica", "Fibrilação atrial — visão geral"),
        item("apixabana-monitorizacao", "Monitorização da apixabana"),
        item("orientacao-marca", "Eliquis: orientação publicada"),
    ], [item("referencia-transversal", "Referência de outro tema",
             relation_type="mentioned_in", review_status="revisado",
             context_only=False)])
    result = connected.buscar_relacionados_do_medicamento(
        FakeDB(medication()), "apixabana", limite_por_categoria=None,
    )
    rows = flattened(result)
    assert set(rows) == {"apixabana-monitorizacao", "orientacao-marca", "referencia-transversal"}
    assert rows["referencia-transversal"]["relation_scope"] == "direct_graph_relation"
    assert rows["referencia-transversal"]["relation_type"] == "mentioned_in"
    assert rows["orientacao-marca"]["relation_scope"] == "clinical_match"
    assert rows["orientacao-marca"]["match_reasons"] == [
        {"source": "title_or_slug", "term": "eliquis", "weight": 3},
    ]
    assert all(not row["context_only"] for row in rows.values())


def test_medication_unbounded_request_keeps_all_matches_after_noise(monkeypatch):
    arrange(monkeypatch, [
        *(item(f"noise-{n}", "Fibrilação atrial — conteúdo geral") for n in range(10)),
        *(item(f"apixabana-{n}", f"Apixabana — documento {n}") for n in range(9)),
    ])
    result = connected.buscar_relacionados_do_medicamento(
        FakeDB(medication()), "apixabana", limite_por_categoria=None,
    )
    assert set(flattened(result)) == {f"apixabana-{n}" for n in range(9)}
    assert result["total"] == 9


def test_medication_without_supported_theme_preserves_typed_graph_and_no_1000_cap(monkeypatch):
    calls = []
    def graph(_db, **kwargs):
        calls.append(kwargs)
        return {"grupos": [group([item(
            "associacao-contraindicada", "Associação contraindicada",
            relation_type="contraindicated_with", review_status="revisado",
            context_only=False,
        )])], "total": 1}
    monkeypatch.setattr(connected, "relacionados_de", graph)
    result = connected.buscar_relacionados_do_medicamento(
        FakeDB(medication(indications=[])), "apixabana", limite_por_categoria=None,
    )
    assert set(flattened(result)) == {"associacao-contraindicada"}
    assert flattened(result)["associacao-contraindicada"]["relation_type"] == "contraindicated_with"
    assert calls[0]["limite_por_tipo"] is None
    assert calls[0]["incluir_contexto_tematico"] is False
