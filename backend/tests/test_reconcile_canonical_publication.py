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
        _document("lote-aprovado", published=False),
        _document("quarentena-aprovada", published=True),
        _document("lote-sem-aprovacao", published=True),
        _document("legado-novo", published=False),
        _document("rebaixado-para-revisao", published=True, review_status="pendente_revisao"),
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
    canonical = {
        "documentos": {
            "atual",
            "lote-aprovado",
            "quarentena-aprovada",
            "lote-sem-aprovacao",
            "legado-novo",
            "rebaixado-para-revisao",
        }
    }
    intents = {
        "documentos": {
            "atual": None,
            "lote-aprovado": True,
            "quarentena-aprovada": False,
            "lote-sem-aprovacao": True,
            "legado-novo": None,
            "rebaixado-para-revisao": True,
        }
    }

    (
        publicados,
        despublicados,
        despublicados_sem_revisao,
        despublicados_inelegiveis,
    ) = reconciliation._synchronize_publication(
        db,
        canonical,
        publish_reviewed=True,
        approved_slugs={
            "documentos": {
                "lote-aprovado",
                "quarentena-aprovada",
                "rebaixado-para-revisao",
            }
        },
        publication_intents=intents,
    )
    inventario = reconciliation._database_inventory(db, canonical)

    atual = db.query(Document).filter_by(slug="atual").one()
    aprovado = db.query(Document).filter_by(slug="lote-aprovado").one()
    quarentena = db.query(Document).filter_by(slug="quarentena-aprovada").one()
    sem_aprovacao = db.query(Document).filter_by(slug="lote-sem-aprovacao").one()
    legado_novo = db.query(Document).filter_by(slug="legado-novo").one()
    rebaixado = db.query(Document).filter_by(slug="rebaixado-para-revisao").one()
    removido = db.query(Document).filter_by(slug="removido-do-commit").one()

    assert atual.published is True
    assert aprovado.published is True
    assert quarentena.published is False
    assert sem_aprovacao.published is False
    assert legado_novo.published is False
    assert rebaixado.published is False
    assert removido.published is False
    assert publicados == {"documentos": 1}
    assert despublicados == {"documentos": 1}
    assert despublicados_sem_revisao == {"documentos": 1}
    assert despublicados_inelegiveis == {"documentos": 2}

    assert inventario["total"] == 6
    assert inventario["published_total"] == 2
    assert inventario["stored_total"] == 7
    assert inventario["archived_absent_total"] == 1
    assert inventario["below_minimum"] == {}
    assert inventario["fronts"]["documentos"] == {
        "database": 6,
        "published": 2,
        "stored": 7,
        "archived_absent": 1,
        "minimum": 2,
    }
