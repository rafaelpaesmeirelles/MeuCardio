"""Clinical relevance regressions for the contextual Tudo com Tudo matcher.

These tests are intentionally database-free: they exercise the deterministic
scoring boundary that must reject lexical noise before any item is returned.
"""

from types import SimpleNamespace

import pytest

from app.services import connected_content as connected
from app.services.topic_relevance import (
    CONTEXT_MIN_RELEVANCE_SCORE,
    drug_matches_theme,
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
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args, **_kwargs: [])

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
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args, **_kwargs: [])

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
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args, **_kwargs: [])

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
    monkeypatch.setattr(connected, "_contextual_studies", lambda *_args, **_kwargs: [])

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


def test_ecossistema_doenca_mescla_tema_exato_com_grafo_sem_truncar(monkeypatch):
    disease = SimpleNamespace(
        slug="fibrilacao-atrial",
        name="Fibrilação atrial",
        aliases=["FA"],
        tags=["anticoagulação"],
    )

    class FakeResult:
        def scalar_one_or_none(self):
            return disease

    class FakeDB:
        def execute(self, _query):
            return FakeResult()

    # Reproduces the production gap: the disease graph knows only the broad
    # topic, while the corpus has an exact disease topic discoverable by name.
    monkeypatch.setattr(
        connected, "_disease_topic_titles",
        lambda *_args, **_kwargs: ["Arritmias"],
    )
    monkeypatch.setattr(
        connected, "_disease_exact_topic_titles",
        lambda *_args, **_kwargs: ["Fibrilação atrial"],
    )
    monkeypatch.setattr(
        connected,
        "_direct_graph_groups",
        lambda *_args, **_kwargs: [{
            "tipo": "documento",
            "rotulo": "Documentos",
            "rota_lista": "/biblioteca",
            "itens": [_item("diretriz-fa", "Diretriz de FA")],
        }],
    )

    calls = []
    def fake_contextual(_db, tema, **kwargs):
        calls.append((tema, kwargs))
        if tema == "Fibrilação atrial":
            return {
                "tema": tema,
                "total": 3,
                "grupos": [{
                    "tipo": "calculadora",
                    "rotulo": "Calculadoras",
                    "rota_lista": "/calculadoras",
                    "itens": [
                        {"slug": "cha2ds2-vasc", "titulo": "CHA₂DS₂-VASc", "rota": "/calculadoras/cha2ds2-vasc"},
                        {"slug": "has-bled", "titulo": "HAS-BLED", "rota": "/calculadoras/has-bled"},
                        {"slug": "orbit", "titulo": "ORBIT", "rota": "/calculadoras/orbit"},
                    ],
                }],
            }
        return {"tema": tema, "total": 0, "grupos": []}

    monkeypatch.setattr(connected, "buscar_relacionados_contextuais", fake_contextual)

    result = connected.buscar_relacionados_da_doenca(
        FakeDB(), "fibrilacao-atrial", limite_por_categoria=None,
    )
    calculators = next(g for g in result["grupos"] if g["tipo"] == "calculadora")
    assert {item["slug"] for item in calculators["itens"]} == {
        "cha2ds2-vasc", "has-bled", "orbit",
    }
    assert all(item["context_only"] is True for item in calculators["itens"])
    assert result["temas_exatos"] == ["Fibrilação atrial"]
    assert result["temas_contextuais"] == ["Arritmias"]
    exact_call = next(kwargs for tema, kwargs in calls if tema == "Fibrilação atrial")
    assert exact_call["limite_por_categoria"] is None
    broad_call = next(kwargs for tema, kwargs in calls if tema == "Arritmias")
    assert "fibrilacao-atrial" in broad_call["assunto"]


def test_ecossistema_doenca_nao_promove_tema_amplo_a_relacao_direta(monkeypatch):
    disease = SimpleNamespace(
        slug="estenose-mitral",
        name="Estenose mitral",
        aliases=[],
        tags=[],
    )

    class FakeResult:
        def scalar_one_or_none(self):
            return disease

    class FakeDB:
        def execute(self, _query):
            return FakeResult()

    monkeypatch.setattr(connected, "_disease_topic_titles", lambda *_args, **_kwargs: ["Valvopatias"])
    monkeypatch.setattr(connected, "_disease_exact_topic_titles", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(connected, "_direct_graph_groups", lambda *_args, **_kwargs: [])
    captured = {}
    def fake_contextual(_db, tema, **kwargs):
        captured.update(kwargs)
        return {"tema": tema, "total": 0, "grupos": []}
    monkeypatch.setattr(connected, "buscar_relacionados_contextuais", fake_contextual)

    result = connected.buscar_relacionados_da_doenca(FakeDB(), disease.slug)
    assert result["temas_exatos"] == []
    assert result["temas_contextuais"] == ["Valvopatias"]
    assert captured["assunto"].startswith("estenose-mitral Estenose mitral")


def test_doenca_topico_amplo_exige_ancora_composta_no_titulo_ou_slug():
    disease = SimpleNamespace(
        slug="estenose-mitral",
        name="Estenose mitral",
        aliases=["Estenose valvar mitral"],
    )
    phrases = connected._disease_anchor_phrases(disease)
    assert connected._item_mentions_disease_anchor(
        {"slug": "eco-estresse-na-estenose-mitral", "titulo": "Eco de estresse na estenose mitral"},
        phrases,
    )
    assert not connected._item_mentions_disease_anchor(
        {"slug": "insuficiencia-mitral", "titulo": "Insuficiência mitral"},
        phrases,
    )


def test_alias_curto_so_prova_identidade_quando_esta_no_slug():
    disease = SimpleNamespace(
        slug="sindrome-coronariana-aguda",
        name="Síndrome coronariana aguda",
        aliases=["SCA", "IAM", "NSTEMI"],
    )
    phrases = connected._disease_anchor_phrases(disease)
    assert not connected._item_mentions_disease_anchor(
        {"slug": "iona-nicorandil-na-angina-estavel", "titulo": "IONA — morte/IAM sem diferença"},
        phrases,
    )
    assert connected._item_mentions_disease_anchor(
        {"slug": "riddle-nstemi-intervencao-imediata", "titulo": "RIDDLE-NSTEMI"},
        phrases,
    )


def test_drug_topic_usa_chaves_estruturadas_de_posologia_sem_inventar_indicacao():
    apixabana = SimpleNamespace(
        indications=[],
        dosing={
            "fa nao valvular padrao": "5 mg 2x/dia",
            "tvp ep tratamento inicial 7 dias": "10 mg 2x/dia",
        },
    )
    assert drug_matches_theme(apixabana, "Fibrilação atrial")
    assert drug_matches_theme(apixabana, "Tromboembolismo")
    assert not drug_matches_theme(apixabana, "Insuficiência cardíaca")


def test_drug_topic_nao_casa_sigla_curta_dentro_de_outra_palavra():
    fake = SimpleNamespace(
        indications=[],
        dosing={"falencia renal ajuste": "texto livre"},
    )
    assert not drug_matches_theme(fake, "Fibrilação atrial")


def test_drug_topic_preserva_indicacao_estruturada_existente():
    amiodarona = SimpleNamespace(
        indications=["Boa eficácia para reversão de ritmo em FA"],
        dosing={},
    )
    assert drug_matches_theme(amiodarona, "Fibrilação atrial")


def test_drug_topic_reconhece_ic_cronica_estruturada():
    sacubitril_valsartana = SimpleNamespace(
        indications=["IC crônica sintomática avançada com fração de ejeção reduzida"],
        dosing={},
    )
    assert drug_matches_theme(sacubitril_valsartana, "Insuficiência cardíaca")


def test_ecossistema_generico_mescla_direto_e_topico_contextual(monkeypatch):
    origin = SimpleNamespace(
        entity_type="calculadora", slug="cha2ds2-vasc", title="CHA₂DS₂-VASc",
    )

    class FakeResult:
        def scalar_one_or_none(self): return origin
    class FakeDB:
        def execute(self, _query): return FakeResult()

    monkeypatch.setattr(connected, "_entity_topic_titles", lambda *_args, **_kwargs: ["Fibrilação atrial"])
    monkeypatch.setattr(connected, "_direct_graph_groups", lambda *_args, **_kwargs: [{
        "tipo": "evidencia", "rotulo": "Evidências", "rota_lista": "/evidencias",
        "itens": [{"slug": "cha2-va", "titulo": "CHA2DS2-VA na FA", "rota": "/evidencias/cha2-va", "relation_type": "mentioned_in"}],
    }])
    monkeypatch.setattr(connected, "buscar_relacionados_contextuais", lambda *_args, **_kwargs: {
        "total": 1, "grupos": [{
            "tipo": "checklist", "rotulo": "Checklists", "rota_lista": "/checklists",
            "itens": [{"slug": "fa-anticoagulacao", "titulo": "Anticoagulação na FA", "rota": "/checklists/fa-anticoagulacao", "relation_scope": "clinical_match"}],
        }],
    })
    result = connected.buscar_ecossistema_de_entidade(
        FakeDB(), entity_type="calculadora", slug="cha2ds2-vasc", limite_por_categoria=None,
    )
    assert result["temas"] == ["Fibrilação atrial"]
    assert {g["tipo"] for g in result["grupos"]} == {"evidencia", "checklist"}
    assert result["total"] == 2
