"""Regressão: GET /api/gallery/images pagina de verdade (Parte H da correção
coordenada de 02/09/2026 — antes disso, o endpoint aceitava limit/offset mas
nunca devolvia next_offset, e o frontend nunca enviava offset: um lote acima
de 500 imagens ficaria sem forma de o front pedir o restante)."""

import pytest
from sqlalchemy import text

from app.models.gallery import GalleryImage


@pytest.fixture(autouse=True)
def _galeria_limpa(db):
    db.execute(text("TRUNCATE gallery_images RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text("TRUNCATE gallery_images RESTART IDENTITY CASCADE"))
    db.commit()


def _imagem(indice: int) -> GalleryImage:
    return GalleryImage(
        slug=f"achado-paginacao-{indice:03d}",
        title=f"Achado de teste {indice:03d}",
        modality="ECG",
        theme="Arritmias",
        findings="Achado sintético para teste de paginação.",
        file_path=f"/static/galeria/teste-{indice:03d}.jpg",
        source_name="Fonte de teste",
        source_url="https://example.test/imagem",
        license="CC0",
        attribution="Fonte de teste",
        review_status="revisado",
        published=True,
    )


def test_resposta_traz_contrato_completo_de_paginacao(client, db, criar_usuario):
    db.add_all([_imagem(i) for i in range(3)])
    db.commit()
    _, token = criar_usuario(role="admin")

    resposta = client.get("/api/gallery/images", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert corpo["limit"] == 60
    assert corpo["offset"] == 0
    assert corpo["has_more"] is False
    assert corpo["next_offset"] is None
    assert len(corpo["items"]) == 3


def test_offset_percorre_todo_o_acervo_sem_perder_nem_repetir_item(client, db, criar_usuario):
    total_imagens = 7
    db.add_all([_imagem(i) for i in range(total_imagens)])
    db.commit()
    _, token = criar_usuario(role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    vistos: list[str] = []
    offset = 0
    paginas = 0
    while True:
        resposta = client.get(
            "/api/gallery/images", params={"limit": 3, "offset": offset}, headers=headers,
        )
        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["total"] == total_imagens
        vistos.extend(item["slug"] for item in corpo["items"])
        paginas += 1
        if not corpo["has_more"]:
            assert corpo["next_offset"] is None
            break
        offset = corpo["next_offset"]
        assert paginas < 10

    assert paginas == 3  # 7 itens, 3 por página -> 3 páginas (3+3+1)
    assert sorted(vistos) == sorted(f"achado-paginacao-{i:03d}" for i in range(total_imagens))
    assert len(vistos) == len(set(vistos))
