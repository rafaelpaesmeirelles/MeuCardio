"""Protege a sincronização entre fonte canônica e publicação no banco."""

from sqlalchemy import text

from app.commands import reconcile_content as reconciliation
from app.models.content import Document


def _document(slug: str, *, published: bool, review_status: str = "revisado") -> Document:
    return Document(
        slug=slug,
        title=slug,
        kind="modulo",
        theme="Teste",
        body_md=f"Conteúdo {slug}",
        review_status=review_status,
        published=published,
    )


def test_slug_ausente_fica_arquivado_mas_nao_publicado(db, monkeypatch):
    db.execute(text("TRUNCATE document_revisions, documents RESTART IDENTITY CASCADE"))
    db.add_all([
        _document("atual", published=True),
        _document("novo-revisado", published=False),
        _document("removido-do-commit", published=True),
    ])
    db.commit()

    monkeypatch.setattr(
        reconciliation,
        "FRONTS",
        {
            "documentos": {
                "path": "/content",
                "model": Document,
                "minimum": 2,
                "loader": None,
            }
        },
    )
    canonical = {"documentos": {"atual", "novo-revisado"}}

    publicados, despublicados = reconciliation._synchronize_publication(
        db,
        canonical,
        publish_reviewed=True,
    )
    inventario = reconciliation._database_inventory(db, canonical)

    atual = db.query(Document).filter_by(slug="atual").one()
    novo = db.query(Document).filter_by(slug="novo-revisado").one()
    removido = db.query(Document).filter_by(slug="removido-do-commit").one()

    assert atual.published is True
    assert novo.published is True
    assert removido.published is False
    assert publicados == {"documentos": 1}
    assert despublicados == {"documentos": 1}

    assert inventario["total"] == 2
    assert inventario["published_total"] == 2
    assert inventario["stored_total"] == 3
    assert inventario["archived_absent_total"] == 1
    assert inventario["below_minimum"] == {}
    assert inventario["fronts"]["documentos"] == {
        "database": 2,
        "published": 2,
        "stored": 3,
        "archived_absent": 1,
        "minimum": 2,
    }
