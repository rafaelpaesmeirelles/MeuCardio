"""Contrato da busca agregada usada pela experiência “Tudo com Tudo”."""

import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy


TABELAS_DA_BUSCA = (
    "document_revisions",
    "documents",
    "gallery_images",
    "lab_tests",
    "evidence_records",
    "scientific_studies",
)


@pytest.fixture(autouse=True)
def _conteudo_de_busca_limpo(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS_DA_BUSCA)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {', '.join(TABELAS_DA_BUSCA)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def _documento(slug: str, title: str, *, published: bool = True) -> Document:
    return Document(
        slug=slug,
        title=title,
        kind="farmacologia",
        theme="Hipertensão arterial",
        summary="Conteúdo clínico sobre olmesartana.",
        body_md="Características, indicações e posologia.",
        review_status="revisado" if published else "pendente_revisao",
        published=published,
    )


def test_busca_preserva_frentes_ano_e_oculta_nao_publicado(client, db, criar_usuario):
    db.add_all([
        _documento("olmesartana-caracteristicas-teste", "Olmesartana: características"),
        _documento(
            "olmesartana-rascunho-teste",
            "Olmesartana: conteúdo ainda não publicado",
            published=False,
        ),
        EvidenceRecord(
            slug="olmesartana-evidencia-teste",
            statement="Olmesartana é uma opção terapêutica para hipertensão arterial.",
            recommendation_class="I",
            evidence_level="A",
            society="Sociedade de teste",
            year=2024,
            guideline_title="Diretriz de teste sobre olmesartana",
            reference="Referência de teste",
            theme="Hipertensão arterial",
            review_status="revisado",
            published=True,
        ),
        ScientificStudy(
            slug="olmesartana-estudo-teste",
            title="Estudo clínico de olmesartana",
            study_type="ensaio_clinico",
            journal="Periódico de teste",
            year=2022,
            summary="Avaliação da olmesartana.",
            key_findings="Achados clínicos da olmesartana.",
            clinical_implications="Implicações terapêuticas.",
            theme="Hipertensão arterial",
            review_status="revisado",
            published=True,
        ),
    ])
    db.commit()

    resposta = client.get(
        "/api/search",
        params={"q": "olmesartana"},
        headers=_headers(criar_usuario),
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    por_slug = {item["slug"]: item for item in corpo["results"]}
    assert set(por_slug) == {
        "olmesartana-caracteristicas-teste",
        "olmesartana-evidencia-teste",
        "olmesartana-estudo-teste",
    }
    assert por_slug["olmesartana-caracteristicas-teste"]["frente"] == "documento"
    assert por_slug["olmesartana-caracteristicas-teste"]["ano"] is None
    assert por_slug["olmesartana-evidencia-teste"]["frente"] == "evidencia"
    assert por_slug["olmesartana-evidencia-teste"]["ano"] == 2024
    assert por_slug["olmesartana-estudo-teste"]["frente"] == "estudo"
    assert por_slug["olmesartana-estudo-teste"]["ano"] == 2022
    assert corpo["por_frente"] == {"documento": 1, "evidencia": 1, "estudo": 1}


def test_filtro_de_frente_e_aplicado_antes_do_limite(client, db, criar_usuario):
    db.add_all([
        _documento(
            f"olmesartana-documento-dominante-{indice}",
            "Olmesartana olmesartana olmesartana",
        )
        for indice in range(3)
    ])
    db.add(ScientificStudy(
        slug="olmesartana-unico-estudo",
        title="Olmesartana em estudo",
        study_type="coorte",
        journal="Periódico de teste",
        year=2023,
        summary="Olmesartana.",
        key_findings="Achado clínico.",
        clinical_implications="Implicação clínica.",
        theme="Hipertensão arterial",
        review_status="revisado",
        published=True,
    ))
    db.commit()

    resposta = client.get(
        "/api/search",
        params={"q": "olmesartana", "frente": "estudo", "limit": 1},
        headers=_headers(criar_usuario),
    )

    assert resposta.status_code == 200
    resultados = resposta.json()["results"]
    assert len(resultados) == 1
    assert resultados[0]["frente"] == "estudo"
    assert resultados[0]["slug"] == "olmesartana-unico-estudo"
    assert resultados[0]["ano"] == 2023


def test_limite_padrao_e_validado_pela_api(client, db, criar_usuario):
    db.add_all([
        _documento(
            f"olmesartana-limite-{indice:02d}",
            f"Olmesartana item {indice:02d}",
        )
        for indice in range(61)
    ])
    db.commit()
    headers = _headers(criar_usuario)

    resposta_padrao = client.get(
        "/api/search", params={"q": "olmesartana"}, headers=headers,
    )
    assert resposta_padrao.status_code == 200
    assert resposta_padrao.json()["count"] == 60

    assert client.get(
        "/api/search", params={"q": "olmesartana", "limit": 0}, headers=headers,
    ).status_code == 422
    assert client.get(
        "/api/search", params={"q": "olmesartana", "limit": 101}, headers=headers,
    ).status_code == 422
