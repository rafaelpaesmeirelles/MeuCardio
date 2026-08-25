"""Regressão: o catálogo deve aceitar busca por nome comercial."""

import pytest
from sqlalchemy import text

from app.models.drug import Drug


@pytest.fixture(autouse=True)
def _drugs_limpos(db):
    db.execute(text("TRUNCATE drugs RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text("TRUNCATE drugs RESTART IDENTITY CASCADE"))
    db.commit()


def test_lista_busca_nome_comercial_e_mantem_apenas_publicados(
    client, db, criar_usuario,
):
    db.add_all([
        Drug(
            slug="metoprolol-marca-teste",
            generic_name="Metoprolol",
            brand_names=["Lopressor"],
            drug_class="Betabloqueador",
            review_status="revisado",
            published=True,
        ),
        Drug(
            slug="farmaco-rascunho-marca-teste",
            generic_name="Fármaco em revisão",
            brand_names=["Lopressor oculto"],
            drug_class="Classe de teste",
            review_status="pendente_revisao",
            published=False,
        ),
    ])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get(
        "/api/drugs",
        params={"q": "lopressor"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resposta.status_code == 200
    assert [item["slug"] for item in resposta.json()] == ["metoprolol-marca-teste"]
