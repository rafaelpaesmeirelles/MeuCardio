"""Clinical relevance regressions for the contextual Tudo com Tudo matcher.

These tests are intentionally database-free: they exercise the deterministic
scoring boundary that must reject lexical noise before any item is returned.
"""

from types import SimpleNamespace

import pytest

from app.services import connected_content as connected
from app.services.topic_relevance import (
    CONTEXT_MIN_RELEVANCE_SCORE,
    relevance_tokens,
    score_contextual_relevance,
)


@pytest.fixture(autouse=True)
def _banco_limpo(monkeypatch):
    """These pure matcher regressions intentionally do not require Postgres."""
    monkeypatch.setattr(connected, "relacionados_de", lambda *_args, **_kwargs: None)
    yield


def _group(items: list[dict]) -> dict:
    return {
        "tipo": "documento",
        "rotulo": "Documentos",
        "rota_lista": "/biblioteca",
        "itens": items,
    }


def _item(slug: str, title: str) -> dict:
    return {
        "slug": slug,
        "titulo": title,
        "subtitulo": "Protocolo clínico",
        "rota": f"/biblioteca/{slug}",
    }


def test_termos_clinicos_genericos_nao_geram_score_mesmo_com_pontuacao():
    generic_only = relevance_tokens(
        "Risco, tratamento, pressão, frequência, insuficiência, agudo/crônico, "
        "prevenção, dor, imagem e diagnóstico; riscos, pressões, frequências, "
        "insuficiências, dores e imagens."
    )
    assert generic_only == set()

    match = score_contextual_relevance(
        relevance_tokens("pressão tratamento risco"),
        title_or_slug="Diagnóstico por imagem da pressão arterial",
        tags=["prevenção", "risco cardiovascular"],
    )
    assert match.score == 0
    assert not match.accepted
    assert match.reasons() == []


def test_tag_estruturada_discriminativa_preserva_relacao_dificil_e_explicavel():
    origin = relevance_tokens("mavacamten: tratamento e risco na cardiomiopatia")
    match = score_contextual_relevance(
        origin,
        title_or_slug="EXPLORER-HCM: desfechos do ensaio",
        tags=["mavacamten", "tratamento", "risco"],
    )

    assert match.accepted
    assert match.score == 5
    assert match.score >= CONTEXT_MIN_RELEVANCE_SCORE
    assert match.reasons() == [
        {"source": "structured_tag", "term": "mavacamten", "weight": 5},
    ]


def test_match_contextual_mantem_todos_os_discriminativos_acima_do_limiar():
    groups = [_group([
        _item("pressao-risco", "Pressão arterial: diagnóstico e tratamento"),
        _item("olmesartana-pratica", "Olmesartana na prática"),
        _item("olmesartana-resistente", "Olmesartana na hipertensão resistente"),
    ])]

    connected._filter_groups_by_subject(
        groups,
        ("Hipertensão",),
        "olmesartana resistente: pressão, risco e tratamento",
    )

    items = groups[0]["itens"]
    assert [item["slug"] for item in items] == [
        "olmesartana-resistente",
        "olmesartana-pratica",
    ]
    assert [item["match_score"] for item in items] == [6, 3]
    assert [item["relevance_score"] for item in items] == [1.0, 0.6]
    assert all(item["relation_scope"] == "clinical_match" for item in items)
    assert all(item["match_threshold"] == 3 for item in items)
    assert {
        reason["term"]
        for item in items
        for reason in item["match_reasons"]
    } == {"olmesartana", "resistente"}


def test_origem_editorial_preserva_multiplos_especificos_sem_maximo_relativo():
    groups = [_group([
        _item(
            "ablacao-septal-na-cardiomiopatia-hipertrofica",
            "Ablação septal na cardiomiopatia hipertrófica obstrutiva",
        ),
        _item(
            "miectomia-na-cardiomiopatia-hipertrofica",
            "Miectomia na cardiomiopatia hipertrófica obstrutiva",
        ),
        _item(
            "cardiomiopatia-hipertrofica-visao-geral",
            "Cardiomiopatia hipertrófica — visão geral",
        ),
    ])]

    connected._filter_groups_by_subject(
        groups,
        ("Cardiomiopatias",),
        (
            "ensaio-x1 Ablação septal alcoólica versus miectomia "
            "ablação septal cardiomiopatia hipertrófica"
        ),
        exigir_suporte_editorial_absoluto=True,
        strong_origin_tag_term_groups=(
            connected._strong_structured_tag_term_groups([
                "ablação septal",
                "cardiomiopatia hipertrófica",
            ])
        ),
    )

    items = groups[0]["itens"]
    assert [item["slug"] for item in items] == [
        "ablacao-septal-na-cardiomiopatia-hipertrofica",
        "miectomia-na-cardiomiopatia-hipertrofica",
    ]
    assert [item["match_score"] for item in items] == [9, 6]
    assert [
        {reason["term"] for reason in item["match_reasons"]}
        for item in items
    ] == [
        {"ablacao", "hipertrofica", "septal"},
        {"hipertrofica", "miectomia"},
    ]


def test_tag_unitaria_revisada_da_origem_sustenta_match_pelo_caminho_real(
    monkeypatch,
):
    target = _item("mavacamten-na-pratica", "Mavacamten na prática clínica")
    origin_study = SimpleNamespace(
        title="EXPLORER-HCM: desfechos clínicos",
        tags=["mavacamten"],
    )

    query_results = iter((origin_study, ["mavacamten"], []))

    class FakeResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

        def scalars(self):
            return self

        def all(self):
            return self.value

    class FakeDB:
        def execute(self, _query):
            return FakeResult(next(query_results))

    monkeypatch.setattr(
        connected,
        "_base",
        lambda *_args, **_kwargs: {"grupos": [_group([target])]},
    )
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args: [])

    result = connected.buscar_relacionados_contextuais(
        FakeDB(),
        "Cardiomiopatias",
        excluir_tipo="estudo",
        excluir_slug="ensaio-x1",
        assunto="ensaio-x1",
    )

    documents = next(group for group in result["grupos"] if group["tipo"] == "documento")
    assert [item["slug"] for item in documents["itens"]] == [target["slug"]]
    assert documents["itens"][0]["match_score"] == 3
    assert documents["itens"][0]["match_reasons"] == [
        {"source": "title_or_slug", "term": "mavacamten", "weight": 3},
    ]


def test_tag_unitaria_so_e_forte_quando_pertence_a_taxonomia_tipificada():
    tags = ["mavacamten", "metanálise", "mortalidade", "idoso"]
    groups = connected._strong_structured_tag_term_groups(
        tags,
        trusted_single_terms=frozenset({"mavacamten"}),
    )

    assert groups == (frozenset({"mavacamten"}),)


def test_evidencia_preserva_apenas_documento_explicito_com_um_termo(
    monkeypatch,
):
    linked = _item("olmesartana", "Olmesartana")
    neighbour = _item("olmesartana-visao-geral", "Olmesartana — visão geral")
    query_results = iter((
        SimpleNamespace(document_slug=linked["slug"]),
        SimpleNamespace(
            slug=linked["slug"],
            title=linked["titulo"],
            kind="modulo",
        ),
    ))

    class FakeResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    class FakeDB:
        def execute(self, _query):
            return FakeResult(next(query_results))

    monkeypatch.setattr(
        connected,
        "_base",
        lambda *_args, **_kwargs: {"grupos": [_group([linked, neighbour])]},
    )
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args: [])

    result = connected.buscar_relacionados_contextuais(
        FakeDB(),
        "Hipertensão",
        excluir_tipo="evidencia",
        excluir_slug="recomendacao-42",
        assunto="recomendacao-42",
    )

    documents = next(group for group in result["grupos"] if group["tipo"] == "documento")
    assert [item["slug"] for item in documents["itens"]] == [linked["slug"]]
    assert documents["itens"][0]["relation_scope"] == "structured_clinical_link"
    assert documents["itens"][0]["relation_method"] == "evidence_document_slug"


def test_filtro_contextual_pontua_pool_completo_antes_do_top_5(monkeypatch):
    calls: list[int | None] = []
    unrelated = [
        _item(f"item-sem-nexo-{index:03d}", f"Conteúdo sem nexo {index:03d}")
        for index in range(120)
    ]
    target = _item("mavacamten-monitorizacao", "Monitorização com mavacamten")

    def fake_base(_db, _theme, **kwargs):
        calls.append(kwargs["limite_por_categoria"])
        return {"grupos": [_group([*unrelated, target])]}

    monkeypatch.setattr(connected, "_base", fake_base)
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args: [])

    result = connected.buscar_relacionados_contextuais(
        object(), "Cardiomiopatias", assunto="mavacamten",
    )

    documents = next(group for group in result["grupos"] if group["tipo"] == "documento")
    assert calls and set(calls) == {None}
    assert [item["slug"] for item in documents["itens"]] == [target["slug"]]
    assert result["relation_scope"] == "clinical_match"
    assert result["match_threshold"] == 3


def test_chamada_sem_assunto_e_catalogo_tematico_sem_score_clinico(monkeypatch):
    calls: list[int | None] = []
    catalog_item = _item("catalogo-hipertensao", "Catálogo de hipertensão")

    def fake_base(_db, _theme, **kwargs):
        calls.append(kwargs["limite_por_categoria"])
        return {"grupos": [_group([catalog_item])]}

    monkeypatch.setattr(connected, "_base", fake_base)
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])

    result = connected.buscar_relacionados_contextuais(object(), "Hipertensão")

    item = next(group for group in result["grupos"] if group["tipo"] == "documento")["itens"][0]
    assert calls and set(calls) == {5}
    assert result["relation_scope"] == "theme_catalog"
    assert result["relation_method"] == "structured_theme"
    assert "match_threshold" not in result
    assert "relevance_score" not in item
    assert "match_reasons" not in item


def test_doenca_e_triagem_entram_somente_por_relacao_direta_do_grafo(monkeypatch):
    calls: list[dict] = []

    def fake_graph(_db, **kwargs):
        calls.append(kwargs)
        return {
            "grupos": [
                {
                    "tipo": "doenca",
                    "rota_lista": "/doencas",
                    "itens": [{
                        "slug": "doenca-estruturada",
                        "titulo": "Doença estruturada",
                        "rota": "/doencas/doenca-estruturada",
                        "relation_type": "mentioned_in",
                        "relevance_score": 1.0,
                        "confidence": "derived",
                        "provenance_type": "structured_metadata",
                        "review_status": "pendente_revisao",
                    }],
                },
                {
                    "tipo": "triagem_sintoma",
                    "rota_lista": "/triagem-sintomas",
                    "itens": [{
                        "slug": "triagem-estruturada",
                        "titulo": "Triagem estruturada",
                        "rota": "/triagem-sintomas?slug=triagem-estruturada",
                        "relation_type": "differential_for",
                        "relevance_score": 0.9,
                        "confidence": "derived",
                        "provenance_type": "structured_metadata",
                        "review_status": "pendente_revisao",
                    }],
                },
                {
                    "tipo": "documento",
                    "rota_lista": "/biblioteca",
                    "itens": [_item("nao-duplicar", "Não duplicar pelo grafo")],
                },
            ],
            "total": 3,
        }

    monkeypatch.setattr(connected, "relacionados_de", fake_graph)
    monkeypatch.setattr(
        connected,
        "_base",
        lambda *_args, **_kwargs: {"grupos": [_group([])]},
    )
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args: [])

    result = connected.buscar_relacionados_contextuais(
        object(),
        "Arritmias",
        excluir_tipo="documento",
        excluir_slug="documento-origem",
        assunto="documento-origem",
    )

    assert calls == [{
        "entity_type": "documento",
        "slug": "documento-origem",
        "limite_por_tipo": 5,
        "incluir_contexto_tematico": False,
    }]
    specialty = {
        group["tipo"]: group
        for group in result["grupos"]
        if group["tipo"] in {"doenca", "triagem_sintoma"}
    }
    assert set(specialty) == {"doenca", "triagem_sintoma"}
    assert specialty["doenca"]["itens"][0]["relation_type"] == "mentioned_in"
    assert specialty["doenca"]["itens"][0]["relation_scope"] == "direct_graph_relation"
    assert specialty["doenca"]["itens"][0]["context_only"] is False
    assert specialty["triagem_sintoma"]["itens"][0]["rota"] == (
        "/triagem-sintomas?slug=triagem-estruturada"
    )
    assert not any(
        item.get("slug") == "nao-duplicar"
        for group in result["grupos"]
        for item in group["itens"]
    )


def test_catalogo_tematico_nao_promove_area_a_relacao_clinica(monkeypatch):
    chamado = False

    def fake_graph(*_args, **_kwargs):
        nonlocal chamado
        chamado = True
        return None

    monkeypatch.setattr(connected, "relacionados_de", fake_graph)
    monkeypatch.setattr(
        connected,
        "_base",
        lambda *_args, **_kwargs: {"grupos": [_group([])]},
    )
    monkeypatch.setattr(connected, "_contextual_drugs", lambda *_args, **_kwargs: [])

    result = connected.buscar_relacionados_contextuais(
        object(), "cardiogeriatria",
    )

    assert chamado is False
    assert not any(
        group["tipo"] in {"doenca", "triagem_sintoma"}
        for group in result["grupos"]
    )
