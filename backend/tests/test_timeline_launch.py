from sqlalchemy import text

from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy

TABELAS = ("evidence_records", "scientific_studies")


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_timeline_expoe_eixos_de_investigacao_tratamento_e_proveniencia(client, db, criar_usuario):
    _limpar(db)
    db.add(ScientificStudy(
        slug="eco-diagnostico-ic", title="Ecocardiografia no diagnóstico da insuficiência cardíaca",
        study_type="coorte", authors="Autor A et al.", journal="JACC", year=2001,
        doi="10.1000/eco.2001", pmid="12345678", url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
        summary="Avaliação ecocardiográfica diagnóstica.", key_findings="Achados de imagem.",
        clinical_implications="A ecocardiografia integra a investigação diagnóstica.",
        theme="Insuficiência cardíaca", tags=["diagnóstico", "imagem"],
        review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug="terapia-ic", title="Terapia farmacológica na ICFEr",
        study_type="ensaio_clinico", authors="Autor B et al.", journal="NEJM", year=2014,
        doi="10.1000/therapy.2014", pmid="87654321", url="https://pubmed.ncbi.nlm.nih.gov/87654321/",
        summary="Ensaio de tratamento medicamentoso.", key_findings="Benefício clínico.",
        clinical_implications="Tratamento farmacológico da insuficiência cardíaca.",
        theme="Insuficiência cardíaca", tags=["farmacologia", "tratamento"],
        review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="diretriz-ic", statement="Recomendação de tratamento farmacológico da ICFEr.",
        summary="Recomendação terapêutica.", recommendation_class="I", evidence_level="A",
        society="ESC", year=2021, guideline_title="ESC Heart Failure 2021",
        reference="ESC 2021 referência completa", source_url="https://example.org/esc",
        doi="10.1000/guideline.2021", theme="Insuficiência cardíaca",
        tags=["tratamento", "farmacologia"], review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(
        "/api/trilhas/timeline?tema=Insufici%C3%AAncia%20card%C3%ADaca",
        headers=_headers(criar_usuario),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["primeiro_ano"] == 2001
    assert body["ultimo_ano"] == 2021
    assert {item["eixo"] for item in body["eixos"]} >= {
        "Investigação e diagnóstico", "Tratamento farmacológico"
    }

    by_slug = {item["slug"]: item for item in body["marcos"]}
    diagnostic = by_slug["eco-diagnostico-ic"]
    assert diagnostic["eixo"] == "Investigação e diagnóstico"
    assert diagnostic["doi"] == "10.1000/eco.2001"
    assert diagnostic["pmid"] == "12345678"
    assert diagnostic["source_url"].startswith("https://pubmed.ncbi.nlm.nih.gov/")

    therapy = by_slug["terapia-ic"]
    assert therapy["eixo"] == "Tratamento farmacológico"
    assert therapy["subtipo"] == "ensaio_clinico"

    recommendation = by_slug["diretriz-ic"]
    assert recommendation["tipo"] == "diretriz"
    assert recommendation["referencia"] == "ESC 2021 referência completa"
    assert recommendation["source_url"] == "https://example.org/esc"


def test_timeline_funde_alias_historico_no_mesmo_tema_canonico(client, db, criar_usuario):
    _limpar(db)
    db.add(ScientificStudy(
        slug="dac-canonico", title="Estudo coronariano canônico", study_type="coorte",
        journal="Heart", year=2000, summary="resumo", key_findings="achados",
        clinical_implications="implicação", theme="Doença coronariana",
        review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug="dac-alias", title="Estudo coronariano em rótulo legado", study_type="coorte",
        journal="Heart", year=2005, summary="resumo", key_findings="achados",
        clinical_implications="implicação", theme="Doença arterial coronariana",
        review_status="revisado", published=True,
    ))
    db.commit()

    headers = _headers(criar_usuario)
    topics = client.get("/api/trilhas/timeline/temas", headers=headers).json()
    coronary = [item for item in topics if item["tema"] == "Doença coronariana"]
    assert coronary == [{"tema": "Doença coronariana", "total_marcos": 2}]
    assert not any(item["tema"] == "Doença arterial coronariana" for item in topics)

    timeline = client.get(
        "/api/trilhas/timeline?tema=Doen%C3%A7a%20arterial%20coronariana", headers=headers
    ).json()
    assert timeline["tema"] == "Doença coronariana"
    assert {item["slug"] for item in timeline["marcos"]} == {"dac-canonico", "dac-alias"}


def test_timeline_sem_pista_semantica_nao_inventa_eixo_especifico(client, db, criar_usuario):
    _limpar(db)
    db.add(ScientificStudy(
        slug="estudo-neutro", title="Estudo observacional histórico", study_type="coorte",
        journal="Journal", year=1990, summary="descrição geral", key_findings="achados gerais",
        clinical_implications="contribuição clínica geral", theme="Arritmias", tags=[],
        review_status="revisado", published=True,
    ))
    db.commit()

    body = client.get(
        "/api/trilhas/timeline?tema=Arritmias", headers=_headers(criar_usuario)
    ).json()
    assert body["marcos"][0]["eixo"] == "Evidência clínica"
