"""Protege a sincronização entre fonte canônica e publicação no banco."""

import json

import pytest
from sqlalchemy import text

from app.commands import reconcile_content as reconciliation
from app.models.content import Document
from app.services.corpus_release_authorization import (
    FULL_CORPUS_DECISION,
    FULL_CORPUS_SCOPE,
    build_front_fingerprint,
    corpus_inventory_sha256,
)


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
        _document("corvia-intelligence-runtime", published=True),
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
    runtime = db.query(Document).filter_by(slug="corvia-intelligence-runtime").one()

    assert atual.published is True
    assert aprovado.published is True
    assert quarentena.published is False
    assert sem_aprovacao.published is False
    assert legado_novo.published is False
    assert rebaixado.published is False
    assert removido.published is False
    assert runtime.published is True
    assert publicados == {"documentos": 1}
    assert despublicados == {"documentos": 1}
    assert despublicados_sem_revisao == {"documentos": 1}
    assert despublicados_inelegiveis == {"documentos": 2}

    assert inventario["total"] == 6
    assert inventario["published_total"] == 2
    assert inventario["stored_total"] == 8
    assert inventario["archived_absent_total"] == 1
    assert inventario["runtime_managed_total"] == 1
    assert inventario["below_minimum"] == {}
    assert inventario["fronts"]["documentos"] == {
        "database": 6,
        "published": 2,
        "stored": 8,
        "runtime_managed": 1,
        "archived_absent": 1,
        "minimum": 2,
    }


def test_autorizacao_integral_supera_flag_legada_mas_exige_revisao_e_canonicalidade(
    db,
    monkeypatch,
):
    db.execute(text("TRUNCATE document_revisions, documents RESTART IDENTITY CASCADE"))
    db.add_all([
        _document("canonico-revisado", published=False),
        _document(
            "canonico-nao-revisado",
            published=False,
            review_status="pendente_revisao",
        ),
        _document("historico-fora-do-corpus", published=True),
        _document("corvia-intelligence-release", published=True),
    ])
    db.commit()
    monkeypatch.setattr(
        reconciliation,
        "FRONTS",
        {"documentos": {"model": Document}},
    )
    canonical = {"canonico-revisado", "canonico-nao-revisado"}

    reconciliation._synchronize_publication(
        db,
        {"documentos": canonical},
        publish_reviewed=True,
        approved_slugs={"documentos": set(canonical)},
        publication_intents={
            "documentos": {
                "canonico-revisado": False,
                "canonico-nao-revisado": False,
            }
        },
        full_corpus_authorized_slugs={"documentos": set(canonical)},
    )

    state = {
        item.slug: item.published
        for item in db.query(Document).order_by(Document.slug)
    }
    assert state == {
        "canonico-nao-revisado": False,
        "canonico-revisado": True,
        "historico-fora-do-corpus": False,
        "corvia-intelligence-release": True,
    }


def test_gate_integral_aceita_somente_total_e_frentes_exatos():
    authorization = {
        "authorized_total": 3,
        "fronts": {"documentos": 2, "evidencias": 1},
    }
    database = {
        "published_total": 3,
        "fronts": {
            "documentos": {"published": 2},
            "evidencias": {"published": 1},
        },
    }

    reconciliation._validate_full_corpus_publication(database, authorization)


def test_gate_integral_falha_fechado_em_publicacao_parcial():
    authorization = {
        "authorized_total": 3,
        "fronts": {"documentos": 2, "evidencias": 1},
    }
    database = {
        "published_total": 2,
        "fronts": {
            "documentos": {"published": 2},
            "evidencias": {"published": 0},
        },
    }

    with pytest.raises(RuntimeError, match="Publicação integral incompleta"):
        reconciliation._validate_full_corpus_publication(database, authorization)


def test_loader_integral_vincula_doencas_e_triagem_as_arvores_compostas(
    tmp_path,
    monkeypatch,
):
    canonical = {
        "doencas_especializadas": {"doenca-canonica"},
        "triagem_sintomas": {"triagem-canonica"},
    }
    sources = {}
    fingerprints = {}
    for front, directory_name, slug in (
        ("doencas_especializadas", "doencas", "doenca-canonica"),
        ("triagem_sintomas", "triagem-sintomas", "triagem-canonica"),
    ):
        directory = tmp_path / directory_name
        directory.mkdir()
        source = directory / "metadados.json"
        source.write_text(
            json.dumps([{"slug": slug, "review_status": "revisado"}]),
            encoding="utf-8",
        )
        sources[front] = source
        fingerprints[front] = build_front_fingerprint(
            directory,
            canonical[front],
            {slug: "revisado"},
        )

    manifest = {
        "schema_version": 1,
        "release": "teste-loader-integrado",
        "decision": FULL_CORPUS_DECISION,
        "scope": FULL_CORPUS_SCOPE,
        "approval_basis": "Teste da composição canônica.",
        "expected_total": 2,
        "inventory_sha256": corpus_inventory_sha256(fingerprints),
        "fronts": fingerprints,
    }
    manifest_path = tmp_path / "full-corpus-release.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(reconciliation, "FRONTS", {
        front: {"model": object}
        for front in canonical
    })
    monkeypatch.setattr(
        reconciliation,
        "FULL_CORPUS_AUTHORIZATION_PATH",
        manifest_path,
    )

    authorized, metadata = reconciliation._load_full_corpus_authorization(
        canonical,
        sources,
    )

    assert authorized == canonical
    assert metadata["authorized_total"] == 2
