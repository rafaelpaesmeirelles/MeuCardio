"""`GET /api/trilhas/timeline` e `/api/trilhas/timeline/temas` — timeline de
evolução do conhecimento por doença, dentro de Trilhas de estudo (tarefa #53).

Cobre:
1. marcos de evidência e de estudo do mesmo tema, em ordem cronológica;
2. item não publicado nunca aparece;
3. `documento_relacionado` só aparece quando o `document_slug` da evidência
   existe e está publicado;
4. tema sem nenhum marco devolve lista vazia sem erro (nunca 404/500);
5. `/temas` nunca lista tema sem conteúdo, e soma evidência + estudo;
6. a rota `/timeline` não é engolida pelo catch-all `/{slug}` da trilha.
"""

from sqlalchemy import event, text

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services.timeline_conhecimento import montar_timeline

TEMA = "Insuficiência cardíaca"

TABELAS = ("document_revisions", "documents", "evidence_records", "scientific_studies", "study_tracks")


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_marcos_de_evidencia_e_estudo_em_ordem_cronologica(client, db, criar_usuario):
    _limpar(db)
    db.add(EvidenceRecord(
        slug="ic-ev-recente", statement="Sacubitril-valsartana reduz mortalidade na ICFEr.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2021,
        guideline_title="ESC 2021 Heart Failure", reference="ESC 2021, ref completa",
        theme=TEMA, review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug="paradigm-hf", title="PARADIGM-HF", study_type="ensaio_clinico",
        journal="NEJM", year=2014, summary="resumo", key_findings="achados",
        clinical_implications="Reduz mortalidade e hospitalização na ICFEr.",
        theme=TEMA, review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-antiga", statement="Enalapril reduz mortalidade na ICFEr.",
        recommendation_class="I", evidence_level="A", society="AHA", year=1991,
        guideline_title="SOLVD", reference="AHA, ref completa",
        theme=TEMA, review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/trilhas/timeline?tema={TEMA}", headers=_headers(criar_usuario))
    assert r.status_code == 200
    body = r.json()
    assert body["tema"] == TEMA
    assert body["total"] == 3
    anos = [m["ano"] for m in body["marcos"]]
    assert anos == sorted(anos)          # ordem cronológica
    assert anos[0] == 1991 and anos[-1] == 2021

    tipos = {m["slug"]: m["tipo"] for m in body["marcos"]}
    assert tipos["ic-ev-antiga"] == "diretriz"
    assert tipos["paradigm-hf"] == "estudo"

    marco_estudo = next(m for m in body["marcos"] if m["slug"] == "paradigm-hf")
    assert marco_estudo["rota"] == "/estudos/paradigm-hf"
    assert "NEJM" in marco_estudo["fonte"]


def test_item_nao_publicado_nunca_aparece(client, db, criar_usuario):
    _limpar(db)
    db.add(EvidenceRecord(
        slug="ic-ev-pendente", statement="Recomendação ainda em revisão.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2024,
        guideline_title="Rascunho", reference="ref",
        theme=TEMA, review_status="pendente_revisao", published=False,
    ))
    db.commit()

    r = client.get(f"/api/trilhas/timeline?tema={TEMA}", headers=_headers(criar_usuario))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["marcos"] == []


def test_flag_publicado_sem_revisao_nao_abre_conteudo_cientifico(client, db, criar_usuario):
    _limpar(db)
    db.add(EvidenceRecord(
        slug="ic-ev-publicada-por-engano", statement="Recomendação ainda sem revisão.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2024,
        guideline_title="Rascunho", reference="ref", theme=TEMA,
        review_status="pendente_revisao", published=True,
    ))
    db.commit()

    headers = _headers(criar_usuario)
    timeline = client.get(f"/api/trilhas/timeline?tema={TEMA}", headers=headers)
    topics = client.get("/api/trilhas/timeline/temas", headers=headers)

    assert timeline.status_code == 200
    assert timeline.json()["marcos"] == []
    assert not any(item["tema"] == TEMA for item in topics.json())


def test_documento_relacionado_so_quando_publicado(client, db, criar_usuario):
    _limpar(db)
    db.add(Document(
        slug="ic-doc-origem", title="Manejo da IC crônica", kind="modulo", theme=TEMA,
        body_md="conteúdo", source_tier="A", review_status="revisado", published=True,
    ))
    db.add(Document(
        slug="ic-doc-rascunho", title="Rascunho ainda não publicado", kind="modulo",
        theme=TEMA, body_md="conteúdo", source_tier="A",
        review_status="pendente_revisao", published=False,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-com-doc", statement="Recomendação com documento de origem publicado.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2021,
        guideline_title="ESC 2021", reference="ref", theme=TEMA,
        document_slug="ic-doc-origem", review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-doc-nao-publicado", statement="Recomendação cujo documento de origem não está no ar.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2022,
        guideline_title="ESC 2022", reference="ref", theme=TEMA,
        document_slug="ic-doc-rascunho", review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/trilhas/timeline?tema={TEMA}", headers=_headers(criar_usuario))
    assert r.status_code == 200
    por_slug = {m["slug"]: m for m in r.json()["marcos"]}

    assert por_slug["ic-ev-com-doc"]["documento"] == {
        "slug": "ic-doc-origem", "titulo": "Manejo da IC crônica", "rota": "/biblioteca/ic-doc-origem",
    }
    assert por_slug["ic-ev-doc-nao-publicado"]["documento"] is None


def test_documentos_relacionados_sao_buscados_em_lote(db):
    _limpar(db)
    for index in range(3):
        doc_slug = f"ic-doc-lote-{index}"
        db.add(Document(
            slug=doc_slug, title=f"Documento {index}", kind="modulo", theme=TEMA,
            body_md="conteúdo", review_status="revisado", published=True,
        ))
        db.add(EvidenceRecord(
            slug=f"ic-ev-lote-{index}", statement=f"Recomendação {index}.",
            recommendation_class="I", evidence_level="A", society="ESC",
            year=2020 + index, guideline_title=f"ESC {2020 + index}",
            reference="ref", theme=TEMA, document_slug=doc_slug,
            review_status="revisado", published=True,
        ))
    db.commit()

    document_selects: list[str] = []

    def capture(_conn, _cursor, statement, _parameters, _context, _executemany):
        normalized = " ".join(statement.lower().split())
        if normalized.startswith("select") and " from documents" in normalized:
            document_selects.append(statement)

    event.listen(db.bind, "before_cursor_execute", capture)
    try:
        timeline = montar_timeline(db, TEMA)
    finally:
        event.remove(db.bind, "before_cursor_execute", capture)

    assert timeline["total"] == 3
    assert len(document_selects) == 1


def test_tema_sem_marco_devolve_lista_vazia_sem_erro(client, db, criar_usuario):
    _limpar(db)
    r = client.get("/api/trilhas/timeline?tema=Tema+Sem+Nenhum+Conteudo", headers=_headers(criar_usuario))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["marcos"] == []


def test_temas_soma_evidencia_e_estudo_e_ignora_tema_vazio(client, db, criar_usuario):
    _limpar(db)
    db.add(EvidenceRecord(
        slug="fa-ev-1", statement="Anticoagulação na FA não valvar.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2020,
        guideline_title="ESC 2020 FA", reference="ref", theme="Fibrilação atrial",
        review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug="fa-est-1", title="ARISTOTLE", study_type="ensaio_clinico",
        journal="NEJM", year=2011, summary="resumo", key_findings="achados",
        clinical_implications="implicação", theme="Fibrilação atrial",
        review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug="dac-est-1", title="ISCHEMIA", study_type="ensaio_clinico",
        journal="NEJM", year=2020, summary="resumo", key_findings="achados",
        clinical_implications="implicação", theme="Doença coronariana",
        review_status="revisado", published=True,
    ))
    # não publicado — não deve contar nem aparecer em /temas
    db.add(EvidenceRecord(
        slug="tema-fantasma-ev", statement="Nunca publicada.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2024,
        guideline_title="rascunho", reference="ref", theme="Tema Fantasma",
        review_status="pendente_revisao", published=False,
    ))
    db.commit()

    r = client.get("/api/trilhas/timeline/temas", headers=_headers(criar_usuario))
    assert r.status_code == 200
    por_tema = {t["tema"]: t["total_marcos"] for t in r.json()}

    assert por_tema["Fibrilação atrial"] == 2   # 1 evidência + 1 estudo
    assert por_tema["Doença coronariana"] == 1
    assert "Tema Fantasma" not in por_tema

    temas = [t["tema"] for t in r.json()]
    assert temas == sorted(temas, key=str.lower)


def test_rota_timeline_nao_e_engolida_pelo_catch_all_de_slug(client, db, criar_usuario):
    """Garante a ordem de declaração: uma trilha real chamada por coincidência
    não pode interceptar `/api/trilhas/timeline`."""
    _limpar(db)
    db.add(StudyTrack(
        slug="timeline", titulo="Trilha cujo slug colide com a rota",
        tema=TEMA, objetivo="objetivo", nivel="iniciante",
        etapas=[], review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-rota", statement="Marco de verdade.",
        recommendation_class="I", evidence_level="A", society="ESC", year=2020,
        guideline_title="ESC 2020", reference="ref", theme=TEMA,
        review_status="revisado", published=True,
    ))
    db.commit()

    r = client.get(f"/api/trilhas/timeline?tema={TEMA}", headers=_headers(criar_usuario))
    assert r.status_code == 200
    body = r.json()
    # é a resposta da timeline (tem "marcos"), não a de uma trilha (teria "etapas")
    assert "marcos" in body
    assert body["total"] == 1
