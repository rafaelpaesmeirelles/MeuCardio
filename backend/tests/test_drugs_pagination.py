"""Regressão: GET /api/drugs pagina de verdade (Parte G da correção coordenada
de 02/09/2026 — antes disso, `.limit(300)` era fixo, sem offset/total, e o
301º medicamento futuro ficaria invisível sem aviso nenhum)."""

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


def _farmaco(indice: int) -> Drug:
    return Drug(
        slug=f"farmaco-paginacao-{indice:03d}",
        generic_name=f"Fármaco de Teste {indice:03d}",
        drug_class="Classe de teste",
        review_status="revisado",
        published=True,
    )


def test_resposta_traz_contrato_completo_de_paginacao(client, db, criar_usuario):
    db.add_all([_farmaco(i) for i in range(3)])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get("/api/drugs", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert corpo["offset"] == 0
    assert corpo["has_more"] is False
    assert corpo["next_offset"] is None
    assert len(corpo["items"]) == 3


def test_offset_e_limit_percorrem_o_catalogo_inteiro_sem_perder_nem_repetir_item(
    client, db, criar_usuario,
):
    # 205 é deliberadamente maior que o antigo limit(300) NÃO é o ponto — o
    # ponto é provar que limit pequeno + paginação continua encontrando o
    # último item, o que o limite fixo antigo nunca permitiria pedir.
    total_farmacos = 12
    db.add_all([_farmaco(i) for i in range(total_farmacos)])
    db.commit()
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    vistos: list[str] = []
    offset = 0
    paginas = 0
    while True:
        resposta = client.get(
            "/api/drugs", params={"limit": 5, "offset": offset}, headers=headers,
        )
        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["total"] == total_farmacos
        vistos.extend(item["slug"] for item in corpo["items"])
        paginas += 1
        if not corpo["has_more"]:
            assert corpo["next_offset"] is None
            break
        offset = corpo["next_offset"]
        assert paginas < 10  # trava de segurança contra loop infinito

    assert paginas == 3  # 12 itens, 5 por página -> 3 páginas (5+5+2)
    assert sorted(vistos) == sorted(f.slug for f in [_farmaco(i) for i in range(total_farmacos)])
    assert len(vistos) == len(set(vistos))  # nenhum item repetido entre páginas


def test_limit_padrao_ainda_cobre_o_catalogo_atual_de_206_em_uma_pagina_so(
    client, db, criar_usuario,
):
    """Preserva o comportamento observado hoje: sem parâmetro nenhum, o
    catálogo inteiro (206 publicados em produção, < 500) continua vindo numa
    chamada só — telas existentes que ainda não percorrem páginas não quebram
    enquanto o acervo estiver abaixo do novo limite padrão."""
    db.add_all([_farmaco(i) for i in range(206)])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get("/api/drugs", headers={"Authorization": f"Bearer {token}"})
    corpo = resposta.json()
    assert corpo["total"] == 206
    assert corpo["has_more"] is False
    assert len(corpo["items"]) == 206
