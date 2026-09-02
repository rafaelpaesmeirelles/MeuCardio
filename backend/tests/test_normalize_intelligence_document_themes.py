"""Regressão do comando da Parte C (correção coordenada de 02/09/2026):
normaliza tema não-canônico só em documentos publicados, sem hardcode de
slug, e não toca em documentos já com tema canônico."""

import pytest
from sqlalchemy import text

from app.commands.normalize_intelligence_document_themes_20260902 import normalizar
from app.models.content import Document


@pytest.fixture(autouse=True)
def _documentos_limpos(db):
    db.execute(text("TRUNCATE documents RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text("TRUNCATE documents RESTART IDENTITY CASCADE"))
    db.commit()


def _documento(slug: str, title: str, theme: str, published: bool = True) -> Document:
    return Document(
        slug=slug, title=title, kind="diretriz", theme=theme,
        body_md="Corpo de teste.", source_tier="A",
        review_status="revisado", published=published,
    )


def test_normaliza_publicado_com_tema_livre_e_ignora_o_resto(db):
    db.add_all([
        _documento(
            "corvia-intelligence-teste-diabetes",
            "Semaglutida e desfechos cardiovasculares em diabetes tipo 2",
            "Uma frase inteira sobre diabetes que não é um tema canônico",
        ),
        _documento("doc-ja-canonico", "Documento normal", "Farmacologia"),
        _documento(
            "corvia-intelligence-nao-publicado",
            "Rascunho não publicado", "Frase livre não canônica", published=False,
        ),
    ])
    db.commit()

    alterados = normalizar()

    assert [a["slug"] for a in alterados] == ["corvia-intelligence-teste-diabetes"]
    assert alterados[0]["tema_novo"] == "Diabetes e cardiologia"

    ajustado = db.query(Document).filter(Document.slug == "corvia-intelligence-teste-diabetes").one()
    assert ajustado.theme == "Diabetes e cardiologia"

    inalterado = db.query(Document).filter(Document.slug == "doc-ja-canonico").one()
    assert inalterado.theme == "Farmacologia"

    nao_publicado = db.query(Document).filter(Document.slug == "corvia-intelligence-nao-publicado").one()
    assert nao_publicado.theme == "Frase livre não canônica"  # não tocado: não está publicado


def test_idempotente(db):
    db.add(_documento(
        "corvia-intelligence-teste-oncologia",
        "Cardiotoxicidade por antraciclina em paciente oncológico",
        "Tratamento sistêmico do carcinoma e segurança cardiovascular",
    ))
    db.commit()

    primeira = normalizar()
    segunda = normalizar()

    assert len(primeira) == 1
    assert len(segunda) == 0  # já canônico, nada mais para normalizar
