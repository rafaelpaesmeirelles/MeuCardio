"""Exact section counts and pagination, against isolated PostgreSQL fixtures."""
import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.drug import Drug
from app.models.specialty_guide import SpecialtyDisease
from app.services.catalog_search import PAGE_SQL, SQL, calculadoras_encontradas
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


def document(slug, title, kind="modulo", published=True):
    return Document(slug=slug, title=title, kind=kind, theme="Teste",
                    summary="Resumo sintético", body_md="Conteúdo sintético",
                    published=published, review_status="revisado")


def api_search(client, headers, q, **params):
    response = client.get("/api/search", params={"q": q, **params}, headers=headers)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["count"] == len(result["results"])
    assert result["total"] == sum(result["por_frente"].values()) == sum(result["por_secao"].values())
    return result


@pytest.mark.parametrize("query,canonical,anchor", [
    ("FA", "Fibrilação atrial", "disease"),
    ("HAS", "Hipertensão arterial sistêmica", "disease"),
    ("Eliquis", "Apixabana", "drug"),
    ("sentinelaomega", "Sentinelaomega", None),
])
def test_sections_beyond_first_page_are_counted_and_independently_retrievable(
    client, db, criar_usuario, query, canonical, anchor,
):
    entity = None
    if anchor == "disease":
        slug = "fibrilacao-atrial" if query == "FA" else "hipertensao-arterial-sistemica"
        entity = SpecialtyDisease(slug=slug, name=canonical, aliases=[query], area="geral",
                                  category="Teste", summary="Definição sintética", published=True,
                                  review_status="revisado")
        db.add(entity)
        if query == "FA":
            db.add(SpecialtyDisease(slug="fibrilacao-atrial-idoso", name="Fibrilação atrial no idoso",
                                   area="cardiogeriatria", category="Teste", summary="Definição sintética no idoso", published=True,
                                   review_status="revisado"))
    elif anchor == "drug":
        entity = Drug(slug="apixabana", generic_name=canonical, brand_names=["Eliquis"],
                      drug_class="Anticoagulante", published=True, review_status="revisado")
        db.add(entity)
    db.add_all([document(f"section-general-{i:03}", f"{canonical} fundamentos {i:03}")
                for i in range(110)])
    guidelines = [document(f"section-guideline-{i}", f"ZZZ consenso sobre {canonical} {i}", "diretriz")
                  for i in range(2)]
    db.add_all(guidelines + [
        document("section-management", f"ZZZ tratamento de {canonical}", "protocolo"),
        document("section-flow", f"ZZZ diretriz tratamento de {canonical}", "fluxograma"),
        document("section-hidden", f"{canonical} consenso oculto", "diretriz", False),
    ])
    if query == "HAS":
        db.add_all([document("has-bled-unrelated", "HAS-BLED: sangramento", "diretriz"),
                    document("pulmonary-unrelated", "Hipertensão arterial pulmonar", "diretriz")])
    db.flush()
    if entity:
        source = registrar_entidade(db, entity_type="doenca" if anchor == "disease" else "medicamento",
                                    canonical_id=entity.id, slug=entity.slug, title=canonical)
        target = registrar_entidade(db, entity_type="documento", canonical_id=guidelines[0].id,
                                    slug=guidelines[0].slug, title=guidelines[0].title)
        # Two explicit relations to the same document cannot inflate counts.
        for relation in ("mentioned_in", "associated_with"):
            registrar_relacao(db, source=source, target=target, relation_type=relation,
                             provenance_type="structured_metadata", confidence="derived")
    db.commit()
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}
    first = api_search(client, headers, query, limit=1)
    assert not any(row["secao"] == "diretriz" for row in first["results"])
    assert first["por_secao"]["diretriz"] == 2
    assert first["por_secao"]["conduta"] == first["por_secao"]["fluxo"] == 1
    assert first["por_secao"]["geral"] == 110
    if query == "FA":
        assert first["por_secao"]["doenca"] == 2
        diseases = api_search(client, headers, query, secao="doenca")
        assert {x["slug"] for x in diseases["results"]} == {"fibrilacao-atrial", "fibrilacao-atrial-idoso"}
    pages = [api_search(client, headers, query, secao="diretriz", limit=1, offset=i) for i in (0, 1, 2)]
    assert [p["count"] for p in pages] == [1, 1, 0]
    assert [p["next_offset"] for p in pages] == [1, None, None]
    assert all(p["total"] == 2 and p["por_secao"] == {"diretriz": 2} for p in pages)
    assert {x["slug"] for p in pages for x in p["results"]} == {d.slug for d in guidelines}
    assert all(x["secao"] == "diretriz" and x["frente"] == "documento" for p in pages for x in p["results"])
    if anchor:
        named = api_search(client, headers, canonical, secao="diretriz", limit=100)
        assert {x["slug"] for x in named["results"]} == {d.slug for d in guidelines}
    empty = api_search(client, headers, query, frente="estudo", secao="diretriz")
    assert empty["results"] == [] and empty["total"] == 0
    assert client.get("/api/search", params={"q": query, "secao": "inventada"}, headers=headers).status_code == 422


def test_literal_fallback_uses_same_section_counts_and_does_not_expand_empty_section(client, db, criar_usuario):
    db.add_all([document("literal-a", "Sentinelaomega fundamentos"),
                document("literal-b", "Consenso sentinelaomega", "diretriz"),
                document("literal-hidden", "Diretriz sentinelaomega", "diretriz", False)])
    db.commit()
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}
    result = api_search(client, headers, "nelaome", secao="diretriz", limit=1)
    assert result["por_secao"] == {"diretriz": 1}
    assert [x["slug"] for x in result["results"]] == ["literal-b"]
    # Full text matches only the first record. The second matches the substring
    # but must not appear via section-specific fallback after global FTS succeeds.
    db.add_all([document("exact-free", "sentinela fundamentos"),
                document("substring-free", "Diretriz supersentinelaextra", "diretriz")])
    db.commit()
    result = api_search(client, headers, "sentinela", secao="diretriz")
    assert result["total"] == 0


def test_calculator_sections_and_global_offsets_do_not_duplicate_rows(client, db, criar_usuario):
    db.add(document("score-section-doc", "Score clínico publicado"))
    db.commit()
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}
    total_calcs = len({x["slug"] for x in calculadoras_encontradas("score")})
    assert total_calcs > 1
    first = api_search(client, headers, "score", secao="calculadora", limit=1)
    second = api_search(client, headers, "score", secao="calculadora", limit=1, offset=1)
    assert first["por_secao"] == {"calculadora": total_calcs}
    assert first["results"][0]["slug"] != second["results"][0]["slug"]
    boundary = api_search(client, headers, "score", limit=2, offset=total_calcs - 1)
    assert [r["frente"] for r in boundary["results"]] == ["calculadora", "documento"]
    assert boundary["next_offset"] is None
    empty = api_search(client, headers, "score", frente="documento", secao="calculadora")
    assert empty["total"] == 0
    docs = api_search(client, headers, "score", secao="geral", limit=1)
    assert [r["slug"] for r in docs["results"]] == ["score-section-doc"]


def test_sql_callers_keep_optional_section_and_rag_bind_contract():
    assert PAGE_SQL._bindparams["secao"].value is None
    assert "secao" not in SQL._bindparams
