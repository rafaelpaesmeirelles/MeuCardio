"""HTTP regression for disease retrieval beyond title and graph coverage."""
import pytest
from sqlalchemy import text

from app.api import search as search_api
from app.models.content import Document
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord
from app.models.lab_test import LabTest
from app.models.specialty_guide import SpecialtyDisease
from app.models.study import ScientificStudy
from app.services import search_relevance
from test_search_tudo_com_tudo import TABELAS_DA_BUSCA


@pytest.fixture(autouse=True)
def isolated_catalog(db, monkeypatch):
    tables = ", ".join((*TABELAS_DA_BUSCA, "knowledge_relations", "knowledge_entities"))
    db.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    db.commit()
    # This regression must succeed without graph or theme fan-out rescuing a
    # missing tag query. End-to-end corpus checks cover the combined services.
    monkeypatch.setattr(search_api, "buscar_relacionados_da_doenca", lambda *_: {"grupos": []})
    monkeypatch.setattr(search_relevance, "clinical_profiles", lambda: {})
    yield
    db.rollback()
    db.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    db.commit()


def disease(db):
    record = SpecialtyDisease(slug="estenose-mitral", name="Estenose mitral",
        aliases=["Estenoses mitrais", "Mitral stenosis"], area="geral", category="Valvopatia",
        summary="Definição da doença", published=True, review_status="revisado")
    db.add(record)
    return record


def study(slug, title, tags, **overrides):
    values = dict(slug=slug, title=title, tags=tags, study_type="ensaio_clinico",
        year=2022, journal="Periódico de teste", theme="Valvopatias", summary="Resumo",
        key_findings="Achados", clinical_implications="Contexto", published=True,
        review_status="revisado")
    return ScientificStudy(**{**values, **overrides})


def request(client, auth, **params):
    response = client.get("/api/search", params={"q": "estenose mitral", **params}, headers=auth)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == sum(payload["por_frente"].values()) == sum(payload["por_secao"].values())
    assert payload["count"] == len(payload["results"])
    return payload


def test_reviewed_tags_recover_invictus_ben_farhat_and_planimetry_without_graph(client, db, criar_usuario):
    disease(db)
    db.add_all([
        study("invictus-rivaroxabana-na-fibrilacao-atrial-da-valvopatia-reumatica",
              "INVICTUS: rivaroxabana versus AVK na cardiopatia reumática", ["ESTENOSE MÍTRAL"]),
        study("ben-farhat-comissurotomia", "Ben Farhat: comissurotomia percutânea versus cirurgia",
              ["Estenoses mitrais"]),
        study("coapt-insuficiencia-mitral", "COAPT: insuficiência mitral", ["insuficiência mitral"]),
        study("tag-pendente", "Estudo em revisão", ["estenose mitral"], review_status="pendente_revisao"),
        study("tag-nao-publicada", "Estudo não publicado", ["estenose mitral"], published=False),
        study("tag-parcial", "Outro estudo", ["mitral", "estenose mitral suspeita"]),
        LabTest(slug="planimetria-valvar", name="Planimetria da área valvar", category="imagem",
                theme="Valvopatias", what_it_measures="Área", indications="Avaliação",
                interpretation="Interpretação", tags=["Mitral stenosis"],
                published=True, review_status="revisado"),
        Document(slug="ruido-corpo-tema", title="Insuficiência mitral", kind="artigo",
                 theme="Estenose mitral", body_md="Estenose mitral " * 100, published=True,
                 review_status="revisado", tags=["insuficiência mitral"]),
    ])
    db.commit()
    _, token = criar_usuario(role="admin")
    auth = {"Authorization": f"Bearer {token}"}
    expected = {"invictus-rivaroxabana-na-fibrilacao-atrial-da-valvopatia-reumatica",
                "ben-farhat-comissurotomia", "planimetria-valvar", "estenose-mitral"}
    all_orders = []
    for query in ("estenose mitral", "Estenoses mitrais", "Mitral stenosis"):
        pages = [request(client, auth, q=query, limit=2, offset=offset) for offset in (0, 2, 4)]
        rows = [row for page in pages for row in page["results"]]
        assert {row["slug"] for row in rows} == expected
        assert [row["relevance_order"] for row in rows] == [1, 2, 3, 4]
        assert [page["next_offset"] for page in pages] == [2, None, None]
        assert all(page["total"] == 4 for page in pages)
        assert all(row["clinical_role"] == "direct" for row in rows)
        for row in rows:
            if row["frente"] != "doenca":
                assert any(reason["source"] == "reviewed_tag" for reason in row["match_reasons"])
        all_orders.append([row["slug"] for row in rows])
    assert all_orders[0] == all_orders[1] == all_orders[2]
    filtered = request(client, auth, frente="estudo", limit=1, offset=1)
    assert filtered["total"] == 2 and filtered["results"][0]["relevance_order"] == 2
    assert filtered["primary_disease"]["slug"] == "estenose-mitral"
    assert request(client, auth, frente="estudo", secao="exame")["total"] == 0


def test_curated_warfarin_is_conditional_ordered_and_still_requires_publication(client, db, criar_usuario, monkeypatch):
    source = disease(db)
    drug = Drug(slug="varfarina", generic_name="Varfarina", drug_class="AVK",
                published=True, review_status="revisado")
    db.add_all([drug, Document(slug="estenose-mitral-galeria-secundaria", title="Estenose mitral: revisão",
                              kind="artigo", theme="Valvopatias", body_md="Revisão", published=True)])
    context = "FA com estenose mitral moderada ou grave: contexto específico para AVK."
    monkeypatch.setattr(search_relevance, "clinical_profiles", lambda: {source.slug: {"items": [{
        "frente": "medicamento", "slug": drug.slug, "role": "conditional", "priority": 100,
        "context": context, "relation_type": "associated_with",
        "evidence_sources": ["https://doi.org/10.1056/NEJMoa2209051"],
    }, {"frente": "estudo", "slug": "destino-inexistente", "role": "direct", "priority": 1,
        "context": "Alvo ausente", "relation_type": "supported_by",
        "evidence_sources": ["https://doi.org/10.1056/NEJMoa2209051"]}]}})
    db.commit()
    _, token = criar_usuario(role="admin")
    auth = {"Authorization": f"Bearer {token}"}
    first = request(client, auth, limit=1)
    row = first["results"][0]
    assert row["slug"] == "varfarina" and row["relevance_order"] == 1
    assert row["clinical_role"] == "conditional" and row["clinical_context"] == context
    assert row["relation_type"] == "associated_with" and row["context_only"] is False
    assert first["total"] == 3
    drug.published = False
    db.commit()
    assert request(client, auth, frente="medicamento")["total"] == 0
    drug.published, source.published = True, False
    db.commit()
    assert request(client, auth, frente="medicamento")["total"] == 0


def test_evidence_preserves_full_statement_and_explicit_comparison(client, db, criar_usuario, monkeypatch):
    source = disease(db)
    statement = ("A escolha de anticoagulante na fibrilação atrial deve observar a população estudada, "
                 "o contexto clínico, as contraindicações e os critérios específicos de elegibilidade; "
                 "esta recomendação não se aplica à estenose mitral moderada ou grave.")
    evidence = EvidenceRecord(slug="comparacao-doac", statement=statement,
        summary="Resumo abreviado sem todos os qualificadores", recommendation_class="I",
        evidence_level="A", society="Teste", year=2025, guideline_title="Diretriz de teste",
        reference="Referência", theme="Valvopatias", published=True, review_status="revisado")
    db.add(evidence)
    monkeypatch.setattr(search_relevance, "clinical_profiles", lambda: {source.slug: {"items": [{
        "frente": "evidencia", "slug": evidence.slug, "role": "comparison", "priority": 700,
        "context": "Comparação: esta recomendação exclui estenose mitral moderada ou grave.",
        "relation_type": "supported_by", "evidence_sources": ["https://example.org/source"],
    }]}})
    db.commit()
    _, token = criar_usuario(role="admin")
    row = request(client, {"Authorization": f"Bearer {token}"}, frente="evidencia")["results"][0]
    assert row["title"] == statement and len(row["title"]) > 180
    assert row["snippet"] == statement
    assert row["clinical_role"] == "comparison" and row["context_only"] is True
    assert "exclui estenose mitral" in row["clinical_context"]


def test_context_only_metadata_does_not_recruit_unrelated_rows(client, db, criar_usuario, monkeypatch):
    disease(db)
    db.add_all([Document(slug=slug, title=title, kind="artigo", theme="Valvopatias",
                         body_md="Conteúdo", published=True, review_status="revisado")
                for slug, title in (("estenose-mitral-contexto", "Estenose mitral: contexto"),
                                    ("insuficiencia-mitral-contexto", "Insuficiência mitral"))])
    monkeypatch.setattr(search_api, "buscar_relacionados_da_doenca", lambda *_: {"grupos": [{
        "tipo": "documento", "itens": [{"slug": slug, "context_only": True,
            "relation_type": "same_theme", "relation_method": "structured_theme"}
            for slug in ("estenose-mitral-contexto", "insuficiencia-mitral-contexto")],
    }]})
    db.commit()
    _, token = criar_usuario(role="admin")
    payload = request(client, {"Authorization": f"Bearer {token}"}, frente="documento")
    assert payload["total"] == 1
    row = payload["results"][0]
    assert row["slug"] == "estenose-mitral-contexto"
    assert row["context_only"] is True and row["relation_type"] == "same_theme"
    assert row["clinical_role"] == "mention"


def test_new_reviewed_exact_item_ranks_after_essentials_before_context_and_comparison(client, db, criar_usuario, monkeypatch):
    source = disease(db)
    records = [
        ("essencial-curado", "Documento essencial"),
        ("novo-documento-revisado", "Estenose mitral"),
        ("contexto-condicional", "Contexto de uma subpopulação"),
        ("comparacao-historica", "Comparação histórica"),
    ]
    db.add_all([Document(slug=slug, title=title, kind="artigo", theme="Valvopatias",
                         body_md="Conteúdo", published=True, review_status="revisado",
                         tags=["estenose mitral"] if slug == "novo-documento-revisado" else [])
                for slug, title in records])
    monkeypatch.setattr(search_relevance, "clinical_profiles", lambda: {source.slug: {"items": [
        {"frente": "documento", "slug": slug, "role": role, "priority": priority,
         "context": "Contexto clínico curado", "relation_type": "associated_with",
         "evidence_sources": ["https://example.org/source"]}
        for slug, role, priority in (("essencial-curado", "direct", 10),
            ("contexto-condicional", "conditional", 303), ("comparacao-historica", "comparison", 767))
    ]}})
    db.commit()
    _, token = criar_usuario(role="admin")
    rows = request(client, {"Authorization": f"Bearer {token}"}, frente="documento")["results"]
    assert [row["slug"] for row in rows] == [slug for slug, _ in records]
    assert any(reason["source"] == "reviewed_tag" for reason in rows[1]["match_reasons"])
