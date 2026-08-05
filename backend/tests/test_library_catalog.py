from sqlalchemy import text

from app.api import library as library_api
from app.models.content import Document


def _clear_documents(db):
    db.execute(text("TRUNCATE document_revisions, documents RESTART IDENTITY CASCADE"))
    db.commit()


def _seed_documents(db, count: int = 205):
    for index in range(count):
        db.add(Document(
            slug=f"documento-{index:04d}",
            title=f"Documento {index:04d}",
            kind="modulo",
            theme="Insuficiência cardíaca" if index % 2 == 0 else "Arritmias",
            body_md=f"Conteúdo científico {index}",
            source_tier="A",
            review_status="revisado",
            published=True,
        ))
    db.add(Document(
        slug="documento-retido",
        title="Documento retido",
        kind="modulo",
        theme="Arritmias",
        body_md="Ainda em revisão",
        source_tier="A",
        review_status="pendente_revisao",
        published=False,
    ))
    db.commit()


def test_library_documents_are_paginated_without_silent_truncation(
    client, db, criar_usuario
):
    _clear_documents(db)
    _seed_documents(db)
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    first = client.get("/api/library/documents?limit=100&offset=0", headers=headers)
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["total"] == 205
    assert len(first_body["items"]) == 100
    assert first_body["next_offset"] == 100
    assert first_body["has_more"] is True

    second = client.get("/api/library/documents?limit=100&offset=100", headers=headers)
    assert second.status_code == 200
    second_body = second.json()
    assert len(second_body["items"]) == 100
    assert second_body["next_offset"] == 200

    last = client.get("/api/library/documents?limit=100&offset=200", headers=headers)
    assert last.status_code == 200
    last_body = last.json()
    assert len(last_body["items"]) == 5
    assert last_body["next_offset"] is None
    assert last_body["has_more"] is False
    assert all(item["slug"] != "documento-retido" for item in last_body["items"])


def test_presentation_options_are_complete_lightweight_and_published_only(
    client, db, criar_usuario
):
    _clear_documents(db)
    _seed_documents(db)
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/library/presentation-options", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 205
    assert body[0]["theme"] in {"Arritmias", "Insuficiência cardíaca"}
    assert all(item["slug"] != "documento-retido" for item in body)
    assert all(set(item) == {
        "slug", "title", "theme", "kind", "summary", "review_status",
    } for item in body)


def test_library_catalog_counts_inventory_and_published_separately(
    client, db, criar_usuario, monkeypatch
):
    _clear_documents(db)
    _seed_documents(db, count=3)
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    monkeypatch.setattr(
        library_api,
        "CATALOG_FRONTS",
        (("documentos", "Documentos científicos", "/biblioteca", Document),),
    )

    response = client.get("/api/library/catalog", headers=headers)
    assert response.status_code == 200
    body = response.json()
    minimum = int(library_api.RECONCILIATION_FRONTS["documentos"]["minimum"])
    missing = minimum - 4

    # Três documentos estão publicados e um quarto permanece preservado em
    # revisão. O total integral não pode esconder esse registro retido.
    assert body["total"] == 4
    assert body["inventory_total"] == 4
    assert body["published_total"] == 3
    assert body["unpublished"] == 1
    assert body["fronts"] == [{
        "key": "documentos",
        "label": "Documentos científicos",
        "route": "/biblioteca",
        "count": 3,
        "inventory_count": 4,
        "minimum": minimum,
        "missing": missing,
        "integrity_ok": False,
    }]
    assert body["expected_minimum"] == library_api.SCIENTIFIC_CORPUS_MINIMUM
    assert body["physical_files_expected"] == library_api.SCIENTIFIC_FILES_EXPECTED
    assert body["integrity_ok"] is False
    assert body["missing"] == missing
    assert body["below_minimum"] == {
        "documentos": {
            "inventory_count": 4,
            "minimum": minimum,
            "missing": missing,
        }
    }
