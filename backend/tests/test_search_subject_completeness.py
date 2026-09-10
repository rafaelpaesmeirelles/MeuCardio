"""Regression: useful connections survive pagination and alias resolution."""
import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.specialty_guide import SpecialtyDisease
from app.models.study import ScientificStudy
from app.models.drug import Drug
from app.services.catalog_search import calculadoras_encontradas
from app.services.knowledge_graph import registrar_entidade, registrar_relacao
from test_search_tudo_com_tudo import TABELAS_DA_BUSCA


@pytest.fixture(autouse=True)
def isolated_catalog(db):
    tables = ", ".join((*TABELAS_DA_BUSCA, "knowledge_relations", "knowledge_entities"))
    db.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.rollback()
    db.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    db.commit()


def disease(db):
    record = SpecialtyDisease(
        slug="fibrilacao-atrial", name="Fibrilação atrial", aliases=["FA"],
        area="geral", category="Arritmia", summary="Definição clínica de teste.",
        review_status="revisado", published=True,
    )
    db.add(record)
    db.flush()
    return record


def headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_all_disease_results_paginate_and_alias_has_identical_order(client, db, criar_usuario):
    disease(db)
    db.add_all([Document(
        slug=f"fibrilacao-atrial-regression-{i:03}",
        title=f"Fibrilação atrial — documento {i:03}",
        kind="protocolo", theme="Arritmias", summary="Resumo", body_md="Conteúdo",
        review_status="revisado", published=True,
    ) for i in range(125)])
    # A high-ranking body/theme-only result must not consume a page slot.
    db.add(Document(slug="ruido-sem-identidade", title="Assunto diferente",
                    kind="protocolo", theme="Fibrilação atrial", summary="FA " * 500,
                    body_md="Fibrilação atrial " * 500, published=True))
    db.commit()
    auth = headers(criar_usuario)
    ordered = []
    for query in ("FA", "fibrilacao atrial"):
        offset, results, totals = 0, [], set()
        for _ in range(20):
            r = client.get("/api/search", params={"q": query, "limit": 17, "offset": offset}, headers=auth)
            assert r.status_code == 200, r.text
            data = r.json()
            assert 0 < data["count"] <= 17
            totals.add(data["total"])
            results.extend((x["frente"], x["slug"]) for x in data["results"])
            if data["next_offset"] is None:
                break
            assert data["next_offset"] > offset
            offset = data["next_offset"]
        else:
            pytest.fail("Pagination failed to terminate")
        assert len(totals) == 1 and totals.pop() == len(results)
        assert len(results) == len(set(results))
        assert len([x for x in results if x[0] == "documento"]) == 125
        assert ("documento", "ruido-sem-identidade") not in results
        ordered.append(results)
    assert ordered[0] == ordered[1]


def test_cross_topic_direct_link_appears_without_disease_in_title(client, db, criar_usuario):
    record = disease(db)
    study = ScientificStudy(slug="ensaio-sentinela-sem-sigla", title="Estudo sentinela",
                            study_type="ensaio_clinico", year=2024, theme="Geral",
                            journal="Periódico de teste", key_findings="Achados de teste",
                            clinical_implications="Contexto de teste", summary="Resumo",
                            published=True, review_status="revisado")
    db.add(study)
    db.flush()
    source = registrar_entidade(db, entity_type="doenca", canonical_id=record.id,
                               slug=record.slug, title=record.name)
    target = registrar_entidade(db, entity_type="estudo", canonical_id=study.id,
                               slug=study.slug, title=study.title)
    registrar_relacao(db, source=source, target=target, relation_type="mentioned_in",
                     provenance_type="structured_metadata", confidence="derived")
    db.commit()
    auth = headers(criar_usuario)
    for query in ("FA", "FA?", "fibrilacao  atrial"):
        data = client.get("/api/search", params={"q": query, "frente": "estudo"}, headers=auth).json()
        assert data["total"] == 1
        assert data["results"][0]["slug"] == study.slug
        assert data["primary_disease"] is None
    study.published = False
    db.commit()
    data = client.get("/api/search", params={"q": "FA", "frente": "estudo"}, headers=auth).json()
    assert data["total"] == 0  # stale active graph node cannot republish a study


def test_short_acronym_does_not_match_inside_words():
    slugs = {x["slug"] for x in calculadoras_encontradas("FA")}
    assert "controle-frequencia-fa-flutter-agudo-adulto-2025" in slugs
    assert not slugs & {"ventilacao-protetora-uco", "acidose-metabolica-winter-anion-gap-uco", "dapt-score", "geneva-simplificado"}


def test_identity_is_retrieved_even_with_missing_search_vector(client, db, criar_usuario):
    disease(db)
    db.add(Document(slug="outro-slug", title="FA: acompanhamento",
                    kind="protocolo", theme="Geral", body_md="Conteúdo", published=True))
    db.commit()
    db.execute(text("UPDATE documents SET search_vector = NULL WHERE slug='outro-slug'"))
    db.commit()
    data = client.get("/api/search", params={"q": "fibrilacao atrial", "frente": "documento"},
                      headers=headers(criar_usuario)).json()
    assert [x["slug"] for x in data["results"]] == ["outro-slug"]


def test_generic_identity_survives_null_vector_when_other_fulltext_hits_exist(client, db, criar_usuario):
    for slug, title in [("holter-24h", "Monitorização ambulatorial"),
                        ("monitorizacao-canonica", "Holter 24h"),
                        ("holter-24h-comparacao", "Comparação de Holter 24h")]:
        db.add(Document(slug=slug, title=title, kind="protocolo", theme="Geral",
                        body_md="Conteúdo publicado", published=True))
    db.commit()
    db.execute(text("UPDATE documents SET search_vector = NULL WHERE slug IN "
                    "('holter-24h', 'monitorizacao-canonica')"))
    db.commit()
    response = client.get("/api/search", params={"q": "holter 24h", "frente": "documento"},
                          headers=headers(criar_usuario))
    assert response.status_code == 200, response.text
    assert {x["slug"] for x in response.json()["results"]} == {
        "holter-24h", "monitorizacao-canonica", "holter-24h-comparacao",
    }


def test_has_is_not_the_has_bled_score_but_real_hypertension_context_survives(client, db, criar_usuario):
    db.add(SpecialtyDisease(
        slug="hipertensao-arterial-sistemica", name="Hipertensão arterial sistêmica",
        aliases=["HAS", "hipertensão arterial"], area="geral", category="Hipertensão",
        summary="Definição de teste", published=True, review_status="revisado",
    ))
    for slug, title in [
        ("has-bled-sangramento", "HAS-BLED: avaliação de sangramento"),
        ("has-resistente", "HAS resistente: investigação"),
        ("hipertensao-e-sangramento", "HAS-BLED em pacientes com hipertensão arterial"),
        ("hipertensao-pulmonar", "Hipertensão arterial pulmonar"),
        ("comparacao-sistemica-pulmonar", "Hipertensão arterial sistêmica versus hipertensão pulmonar"),
    ]:
        db.add(Document(slug=slug, title=title, theme="Geral", kind="protocolo",
                        summary="Resumo", body_md="Conteúdo de teste", published=True))
    db.commit()
    data = client.get("/api/search", params={"q": "HAS", "frente": "documento"},
                      headers=headers(criar_usuario)).json()
    assert {x["slug"] for x in data["results"]} == {"has-resistente", "hipertensao-e-sangramento", "comparacao-sistemica-pulmonar"}
    assert "has-bled" not in {x["slug"] for x in calculadoras_encontradas("HAS")}
    assert "has-bled" in {x["slug"] for x in calculadoras_encontradas("HAS-BLED")}


def test_drug_brand_and_generic_share_paginated_direct_connections(client, db, criar_usuario):
    drug = Drug(slug="amiodarona", generic_name="Amiodarona", brand_names=["Ancoron"],
                drug_class="Antiarrítmico", published=True, review_status="revisado")
    db.add(drug)
    db.flush()
    source = registrar_entidade(db, entity_type="medicamento", canonical_id=drug.id,
                               slug=drug.slug, title=drug.generic_name)
    for i in range(9):
        doc = Document(slug=f"monitorizacao-sentinela-{i}", title=f"Monitorização sentinela {i}",
                       kind="protocolo", theme="Geral", body_md="Conteúdo", published=True)
        db.add(doc)
        db.flush()
        target = registrar_entidade(db, entity_type="documento", canonical_id=doc.id,
                                   slug=doc.slug, title=doc.title)
        registrar_relacao(db, source=source, target=target, relation_type="mentioned_in",
                         provenance_type="structured_metadata", confidence="derived")
    db.commit()
    auth = headers(criar_usuario)
    pages = []
    for query in ("amiodarona", "Ancoron"):
        found, offset = [], 0
        while True:
            r = client.get("/api/search", params={"q": query, "frente": "documento",
                                                 "limit": 4, "offset": offset}, headers=auth)
            assert r.status_code == 200, r.text
            data = r.json()
            assert data["total"] == 9
            found.extend(x["slug"] for x in data["results"])
            if data["next_offset"] is None:
                break
            offset = data["next_offset"]
            assert offset <= 9
        assert len(found) == len(set(found)) == 9
        pages.append(found)
    assert pages[0] == pages[1]
