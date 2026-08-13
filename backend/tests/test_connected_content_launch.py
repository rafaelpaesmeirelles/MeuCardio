"""Launch invariants for CorVIA's "Tudo com Tudo".

These tests protect the product rule that connected content must be complete
within a topic but must never become a generic similarity feed.
"""
from sqlalchemy import text

from app.models.content import Document
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord

TABELAS = ("document_revisions", "documents", "evidence_records", "drugs")


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_alias_historico_e_canonicalizado_sem_perder_conteudo(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="dac-canonico", title="Doença coronariana crônica", kind="modulo",
        theme="Doença coronariana", body_md="conteúdo", source_tier="A",
        review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="dac-alias", statement="Recomendação coronariana publicada sob rótulo legado.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2024,
        guideline_title="ESC 2024", reference="ref",
        theme="Doença arterial coronariana", review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(
        "/api/relacionados?tema=Doen%C3%A7a%20arterial%20coronariana",
        headers=_headers(criar_usuario),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["tema"] == "Doença coronariana"
    por_tipo = {group["tipo"]: group["itens"] for group in body["grupos"]}
    assert {item["slug"] for item in por_tipo["documento"]} == {"dac-canonico"}
    assert {item["slug"] for item in por_tipo["evidencia"]} == {"dac-alias"}


def test_tema_clinico_recebe_so_medicamento_com_indicacao_explicita(client, db, criar_usuario):
    _limpar(db)
    db.add(Drug(
        slug="sacubitril-valsartana", generic_name="Sacubitril/Valsartana", drug_class="ARNI",
        indications=["Tratamento da insuficiência cardíaca com fração de ejeção reduzida (ICFEr)."],
        review_status="revisado", published=True,
    ))
    db.add(Drug(
        slug="apixabana", generic_name="Apixabana", drug_class="Anticoagulante",
        indications=["Prevenção de AVC na fibrilação atrial não valvar."],
        review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(
        "/api/relacionados?tema=Insufici%C3%AAncia%20card%C3%ADaca",
        headers=_headers(criar_usuario),
    )
    assert r.status_code == 200
    meds = next(group["itens"] for group in r.json()["grupos"] if group["tipo"] == "medicamento")
    assert [item["slug"] for item in meds] == ["sacubitril-valsartana"]


def test_pagina_de_medicamento_agrega_so_tematicas_clinicas_sustentadas(client, db, criar_usuario):
    _limpar(db)
    db.add(Drug(
        slug="apixabana", generic_name="Apixabana", drug_class="Anticoagulante",
        indications=[
            "Prevenção de AVC na fibrilação atrial não valvar.",
            "Tratamento de tromboembolismo venoso e trombose venosa profunda.",
        ],
        review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="fa-doc", title="Fibrilação atrial", kind="modulo", theme="Fibrilação atrial",
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="tev-doc", title="Tromboembolismo venoso", kind="modulo", theme="Tromboembolismo",
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="ic-irrelevante", title="Insuficiência cardíaca", kind="modulo",
        theme="Insuficiência cardíaca", body_md="conteúdo", source_tier="A",
        review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(
        "/api/relacionados/medicamento/apixabana", headers=_headers(criar_usuario)
    )
    assert r.status_code == 200
    body = r.json()
    assert body["medicamento"]["slug"] == "apixabana"
    assert body["temas"] == ["Fibrilação atrial", "Tromboembolismo"]
    docs = next(group["itens"] for group in body["grupos"] if group["tipo"] == "documento")
    slugs = {item["slug"] for item in docs}
    assert slugs == {"fa-doc", "tev-doc"}
    assert "ic-irrelevante" not in slugs


def test_medicamento_sem_tema_clinico_seguro_nao_recebe_ruido(client, db, criar_usuario):
    _limpar(db)
    db.add(Drug(
        slug="farmaco-sem-indicacao", generic_name="Fármaco sem indicação estruturada",
        drug_class="Outro", indications=[], review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="qualquer-doc", title="Documento qualquer", kind="modulo", theme="Hipertensão",
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(
        "/api/relacionados/medicamento/farmaco-sem-indicacao",
        headers=_headers(criar_usuario),
    )
    assert r.status_code == 200
    assert r.json()["temas"] == []
    assert r.json()["total"] == 0
    assert r.json()["grupos"] == []
