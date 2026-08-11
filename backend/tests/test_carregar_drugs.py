"""app/services/carregar_drugs.py — carga/upsert de `drugs` a partir do JSON
canônico de medicamentos (issue #52).

Regressão do incidente de deploy de 11/08/2026: `reconcile_content
--publish-reviewed` derrubou o backend em produção com
`TypeError: 'review_note' is an invalid keyword argument for Drug` ao tentar
criar um registro NOVO que trazia `review_note` — campo de documentação já
em uso em `documents`/`evidencias` deste projeto, sem coluna própria em
`Drug`. `Drug(**d)` sem filtro rejeita qualquer kwarg desconhecido; o ramo de
atualização (`setattr`) não tinha o mesmo problema, mas também nunca
persistia o campo — daí o filtro valer para os dois ramos.
"""
import pytest
from sqlalchemy import text

from app.models.drug import Drug
from app.services.carregar_drugs import carregar


@pytest.fixture(autouse=True)
def _limpar_drugs(db):
    # `drugs` é tabela de conteúdo, não coberta pelo `_banco_limpo` autouse
    # do conftest — mesmo padrão de test_pricing_cmed_provider.py.
    db.execute(text("TRUNCATE drugs RESTART IDENTITY CASCADE"))
    db.commit()
    yield


def _escrever_json(tmp_path, registros):
    import json

    caminho = tmp_path / "drugs.json"
    caminho.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")
    return str(caminho)


def test_registro_novo_com_campo_de_documentacao_nao_derruba_a_carga(db, tmp_path):
    caminho = _escrever_json(
        tmp_path,
        [
            {
                "slug": "farmaco-teste-review-note",
                "generic_name": "Fármaco de Teste",
                "brand_names": ["MARCA TESTE"],
                "drug_class": "Classe de teste",
                "review_status": "revisado",
                # Campo de documentação sem coluna em `Drug` — é exatamente
                # o que derrubou o deploy real; a carga não pode quebrar por
                # causa dele, nos dois ramos (novo e atualização).
                "review_note": "Conferido por sessão de teste, sem correspondência de coluna.",
            }
        ],
    )

    resultado = carregar(caminho)

    assert resultado == {"total": 1, "novos": 1, "atualizados": 0}
    farmaco = db.query(Drug).filter(Drug.slug == "farmaco-teste-review-note").first()
    assert farmaco is not None
    assert farmaco.generic_name == "Fármaco de Teste"
    assert farmaco.review_status == "revisado"
    assert not hasattr(farmaco, "review_note") or "review_note" not in Drug.__table__.columns.keys()


def test_atualizacao_com_campo_de_documentacao_tambem_nao_quebra(db, tmp_path):
    db.add(
        Drug(
            slug="farmaco-existente-teste",
            generic_name="Fármaco Existente",
            brand_names=["MARCA ANTIGA"],
            drug_class="Classe antiga",
            review_status="pendente_revisao",
        )
    )
    db.commit()

    caminho = _escrever_json(
        tmp_path,
        [
            {
                "slug": "farmaco-existente-teste",
                "generic_name": "Fármaco Existente Atualizado",
                "brand_names": ["MARCA NOVA"],
                "drug_class": "Classe antiga",
                "review_status": "revisado",
                "review_note": "Atualizado em sessão de teste — não deve quebrar nem persistir.",
            }
        ],
    )

    resultado = carregar(caminho)

    assert resultado == {"total": 1, "novos": 0, "atualizados": 1}
    db.expire_all()
    farmaco = db.query(Drug).filter(Drug.slug == "farmaco-existente-teste").first()
    assert farmaco.generic_name == "Fármaco Existente Atualizado"
    assert farmaco.brand_names == ["MARCA NOVA"]
    # review_status é explicitamente preservado do lado do banco, não do JSON
    # (mesma regra já documentada no projeto para review_status em geral).
    assert farmaco.review_status == "pendente_revisao"


def test_registro_sem_campo_extra_continua_funcionando_normalmente(db, tmp_path):
    caminho = _escrever_json(
        tmp_path,
        [
            {
                "slug": "farmaco-simples-teste",
                "generic_name": "Fármaco Simples",
                "brand_names": ["MARCA SIMPLES"],
                "drug_class": "Classe simples",
                "review_status": "revisado",
            }
        ],
    )

    resultado = carregar(caminho)

    assert resultado == {"total": 1, "novos": 1, "atualizados": 0}
    farmaco = db.query(Drug).filter(Drug.slug == "farmaco-simples-teste").first()
    assert farmaco is not None
    assert farmaco.generic_name == "Fármaco Simples"
