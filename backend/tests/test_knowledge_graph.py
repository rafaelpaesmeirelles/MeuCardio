"""Grafo de Conhecimento Clínico Universal (issue #52, nova fase).

Cobre: registro idempotente de entidade/relação, o allowlist estrutural de
segurança (nunca dado de paciente vira nó público), backfill por tema
(derivado do mesmo casamento exato já usado por related_content.py, agora
persistido) e a consulta paginada/ordenada por relevância.

`drugs`/`documents`/`evidence_records`/... são tabelas de conteúdo, não
cobertas pelo `_banco_limpo` autouse do conftest (de propósito — essa
fixture cobre só as tabelas da suíte do CorvIA Mail), daí o TRUNCATE
explícito aqui, mesmo padrão de `test_relacionados.py`.
"""
from sqlalchemy import select, text

from app.models.content import Document
from app.models.checklist import DischargeChecklist
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.api.study_tracks import ROTA as ROTAS_TRILHA
from app.services import knowledge_graph as kg
from app.services.related_content import buscar_relacionados

TEMA = "Insuficiência cardíaca"

TABELAS = (
    "knowledge_relations", "knowledge_entities",
    "document_revisions", "documents", "evidence_records", "scientific_studies",
    "drugs", "clinical_cases", "study_tracks", "gallery_images", "lab_tests",
    "emergency_protocols", "discharge_checklists", "patient_materials",
    "specialty_diseases", "symptom_triage_guides",
)


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


# ---------------------------------------------------------------------------
# Registro de entidade — idempotência e allowlist de segurança
# ---------------------------------------------------------------------------

def test_registrar_entidade_e_idempotente(db):
    _limpar(db)
    e1 = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a", title="A")
    db.commit()
    e2 = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a", title="A")
    db.commit()

    assert e1.id == e2.id
    total = db.execute(select(KnowledgeEntity)).scalars().all()
    assert len(total) == 1


def test_registrar_entidade_atualiza_slug_e_titulo_quando_mudam(db):
    _limpar(db)
    kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a-antigo", title="Título antigo")
    db.commit()
    atualizado = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a-novo", title="Título novo")
    db.commit()

    assert atualizado.slug == "a-novo"
    assert atualizado.title == "Título novo"
    total = db.execute(select(KnowledgeEntity)).scalars().all()
    assert len(total) == 1


def test_registrar_entidade_rejeita_tipo_fora_do_allowlist(db):
    """Regra de segurança estrutural (issue #52, seção 26-27): dado de
    paciente/consulta/prescrição nunca pode virar nó do grafo global —
    isto não é só documentação, é uma exceção real levantada em código."""
    _limpar(db)
    for tipo_proibido in ("paciente", "prescricao", "consulta", "agendamento", "usuario"):
        try:
            kg.registrar_entidade(db, entity_type=tipo_proibido, canonical_id=1, slug="x", title="X")
            assert False, f"deveria ter rejeitado entity_type={tipo_proibido!r}"
        except kg.TipoEntidadeNaoPermitido:
            pass
    db.rollback()
    total = db.execute(select(KnowledgeEntity)).scalars().all()
    assert total == []


# ---------------------------------------------------------------------------
# Registro de relação — idempotência, catálogo, auto-relação
# ---------------------------------------------------------------------------

def test_registrar_relacao_e_idempotente(db):
    _limpar(db)
    a = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a", title="A")
    b = kg.registrar_entidade(db, entity_type="evidencia", canonical_id=1, slug="b", title="B")
    db.commit()

    r1 = kg.registrar_relacao(
        db, source=a, target=b, relation_type="same_theme",
        provenance_type="structured_metadata", confidence="derived",
    )
    db.commit()
    r2 = kg.registrar_relacao(
        db, source=a, target=b, relation_type="same_theme",
        provenance_type="structured_metadata", confidence="derived",
    )
    db.commit()

    assert r1.id == r2.id
    total = db.execute(select(KnowledgeRelation)).scalars().all()
    assert len(total) == 1


def test_registrar_relacao_devolve_none_para_auto_relacao(db):
    _limpar(db)
    a = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a", title="A")
    db.commit()
    r = kg.registrar_relacao(
        db, source=a, target=a, relation_type="same_theme",
        provenance_type="structured_metadata", confidence="derived",
    )
    assert r is None
    total = db.execute(select(KnowledgeRelation)).scalars().all()
    assert total == []


def test_registrar_relacao_rejeita_tipo_fora_do_catalogo(db):
    _limpar(db)
    a = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="a", title="A")
    b = kg.registrar_entidade(db, entity_type="evidencia", canonical_id=1, slug="b", title="B")
    db.commit()
    try:
        kg.registrar_relacao(
            db, source=a, target=b, relation_type="inventado_qualquer",
            provenance_type="structured_metadata", confidence="derived",
        )
        assert False, "deveria ter rejeitado relation_type fora do catálogo"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# Backfill por tema — derivado, idempotente, não-destrutivo
# ---------------------------------------------------------------------------

def _semear_conteudo_publicado(db):
    db.add(Document(
        slug="ic-doc-1", title="Manejo da IC crônica", kind="modulo", theme=TEMA,
        body_md="corpo", review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-1", theme=TEMA, statement="Beta-bloqueador reduz mortalidade na ICFEr",
        recommendation_class="I", evidence_level="A", society="ESC", year=2021,
        guideline_title="ESC 2021 Heart Failure", reference="ESC 2021, ref completa",
        review_status="revisado", published=True,
    ))
    db.add(Drug(
        slug="carvedilol-teste", generic_name="Carvedilol", drug_class="beta-bloqueador",
        review_status="revisado", published=True,
    ))
    # Item não publicado nunca deve entrar no grafo.
    db.add(Document(
        slug="ic-doc-nao-publicado", title="Rascunho", kind="modulo", theme=TEMA,
        body_md="corpo", review_status="pendente_revisao", published=False,
    ))
    db.commit()


def test_backfill_cria_entidades_e_associacoes_de_tema(db):
    _limpar(db)
    _semear_conteudo_publicado(db)

    resultado = kg.backfill_mesmo_tema(db)

    assert resultado["entidades_criadas_ou_atualizadas"] >= 3
    entidades = db.execute(select(KnowledgeEntity)).scalars().all()
    slugs = {e.slug for e in entidades}
    assert {"ic-doc-1", "ic-ev-1", "carvedilol-teste"} <= slugs
    ids_semeados = {
        e.id for e in entidades
        if e.slug in {"ic-doc-1", "ic-ev-1", "carvedilol-teste"}
    }
    # O item não publicado nunca vira nó — mesma régua de published de toda
    # frente do produto.
    assert "ic-doc-nao-publicado" not in slugs

    relacoes = db.execute(select(KnowledgeRelation)).scalars().all()
    associacoes = [r for r in relacoes if r.relation_type == "belongs_to_topic"]
    assert associacoes
    for r in associacoes:
        assert r.provenance_type == "structured_metadata"
        assert r.confidence == "derived"
        if r.source_entity_id in ids_semeados:
            assert r.extra.get("tema") in (TEMA, "Farmacologia")

    # Documento e evidência compartilham o mesmo nó canônico de tema. Não há
    # malha item↔item: a consulta expande item -> tema <- item em dois saltos.
    doc = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-doc-1")).scalar_one()
    ev = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-ev-1")).scalar_one()
    droga = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "carvedilol-teste")).scalar_one()
    temas_doc = {
        target_id for (target_id,) in db.execute(
            select(KnowledgeRelation.target_entity_id).where(
                KnowledgeRelation.source_entity_id == doc.id,
                KnowledgeRelation.relation_type == "belongs_to_topic",
            )
        )
    }
    temas_ev = {
        target_id for (target_id,) in db.execute(
            select(KnowledgeRelation.target_entity_id).where(
                KnowledgeRelation.source_entity_id == ev.id,
                KnowledgeRelation.relation_type == "belongs_to_topic",
            )
        )
    }
    assert temas_doc & temas_ev
    assert db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == doc.id,
            KnowledgeRelation.target_entity_id == droga.id,
        )
    ).scalar_one_or_none() is None


def test_backfill_e_idempotente_rodar_duas_vezes_nao_duplica(db):
    _limpar(db)
    _semear_conteudo_publicado(db)

    kg.backfill_mesmo_tema(db)
    contagem_entidades_1 = db.execute(select(KnowledgeEntity)).scalars().all()
    contagem_relacoes_1 = db.execute(select(KnowledgeRelation)).scalars().all()

    # Roda de novo, sem nenhuma mudança no conteúdo de origem.
    kg.backfill_mesmo_tema(db)
    contagem_entidades_2 = db.execute(select(KnowledgeEntity)).scalars().all()
    contagem_relacoes_2 = db.execute(select(KnowledgeRelation)).scalars().all()

    assert len(contagem_entidades_1) == len(contagem_entidades_2)
    assert len(contagem_relacoes_1) == len(contagem_relacoes_2)


def test_backfill_nunca_apaga_relacao_existente(db):
    """Não-destrutividade (issue #52, seção 28): uma relação marcada
    'revisado' por curadoria humana sobrevive a uma nova rodada de
    backfill, mesmo que o conteúdo de origem mude depois."""
    _limpar(db)
    _semear_conteudo_publicado(db)
    kg.backfill_mesmo_tema(db)

    doc = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-doc-1")).scalar_one()
    ev = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-ev-1")).scalar_one()
    relacao = kg.registrar_relacao(
        db,
        source=doc,
        target=ev,
        relation_type="associated_with",
        provenance_type="editorial",
        confidence="explicit",
        review_status="revisado",
    )
    db.commit()

    kg.backfill_mesmo_tema(db)

    relacao_depois = db.execute(select(KnowledgeRelation).where(KnowledgeRelation.id == relacao.id)).scalar_one()
    assert relacao_depois.review_status == "revisado"


# ---------------------------------------------------------------------------
# Consulta — agrupada, ordenada por relevância, paginada
# ---------------------------------------------------------------------------

def test_relacionados_de_agrupa_por_tipo_e_ordena_por_relevancia(db):
    _limpar(db)
    _semear_conteudo_publicado(db)
    kg.backfill_mesmo_tema(db)

    resultado = kg.relacionados_de(
        db,
        entity_type="documento",
        slug="ic-doc-1",
        incluir_contexto_tematico=True,
    )

    assert resultado is not None
    assert resultado["slug"] == "ic-doc-1"
    tipos = {g["tipo"] for g in resultado["grupos"]}
    assert "evidencia" in tipos
    # medicamento fica sob o tema "Farmacologia" (convenção estrutural, ver
    # nota acima) — não aparece como relacionado de um documento de tema
    # "Insuficiência cardíaca", nada fabricado entre temas diferentes.
    assert "medicamento" not in tipos
    # o próprio item nunca aparece na própria lista de relacionados
    for g in resultado["grupos"]:
        for item in g["itens"]:
            assert not (g["tipo"] == "documento" and item["slug"] == "ic-doc-1")


def test_relacionados_de_oculta_por_padrao_vizinhos_apenas_taxonomicos(db):
    _limpar(db)
    _semear_conteudo_publicado(db)
    kg.backfill_mesmo_tema(db)

    resultado = kg.relacionados_de(
        db,
        entity_type="documento",
        slug="ic-doc-1",
    )

    assert resultado is not None
    assert all(
        item["relation_type"] != "belongs_to_topic"
        for grupo in resultado["grupos"]
        for item in grupo["itens"]
    )


def test_relacionados_de_devolve_none_quando_item_nao_esta_no_grafo(db):
    _limpar(db)
    assert kg.relacionados_de(db, entity_type="documento", slug="nao-existe") is None


# ---------------------------------------------------------------------------
# Reconciliação de segurança — conteúdo despublicado nunca continua visível
# ---------------------------------------------------------------------------

def test_preflight_arquiva_entidade_de_conteudo_despublicado(db):
    """Achado de segurança desta fase, mesmo padrão do vazamento histórico
    do RAG (documentado em CLAUDE.md): um item retirado do ar depois de já
    ter sido indexado no grafo não pode continuar aparecendo nas consultas."""
    _limpar(db)
    _semear_conteudo_publicado(db)
    kg.backfill_mesmo_tema(db)

    ainda_visivel = kg.relacionados_de(db, entity_type="documento", slug="ic-doc-1")
    assert ainda_visivel is not None

    doc = db.execute(select(Document).where(Document.slug == "ic-doc-1")).scalar_one()
    doc.published = False
    db.commit()

    arquivadas = kg.arquivar_entidades_de_conteudo_despublicado(db)
    assert arquivadas >= 1

    entidade = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-doc-1")).scalar_one()
    assert entidade.status == "arquivado"
    assert kg.relacionados_de(db, entity_type="documento", slug="ic-doc-1") is None

    # As arestas em si não são apagadas (auditoria de proveniência
    # preservada) — só o nó vira invisível para consulta.
    arestas_preservadas = db.execute(
        select(KnowledgeRelation).where(
            (KnowledgeRelation.source_entity_id == entidade.id)
            | (KnowledgeRelation.target_entity_id == entidade.id)
        )
    ).scalars().all()
    assert arestas_preservadas


def test_tema_em_dois_saltos_nao_trunca_origens_depois_dos_cinco_primeiros(db):
    _limpar(db)
    for indice in range(8):
        db.add(Document(
            slug=f"doc-{indice}", title=f"Documento {indice}", kind="modulo",
            theme=TEMA, body_md="corpo", review_status="revisado", published=True,
        ))
    db.add(EvidenceRecord(
        slug="evidencia-final", theme=TEMA, statement="Evidência final",
        recommendation_class="I", evidence_level="A", society="ESC", year=2026,
        guideline_title="Diretriz", reference="Referência",
        review_status="revisado", published=True,
    ))
    db.commit()

    kg.backfill_mesmo_tema(db)
    resultado = kg.relacionados_de(
        db,
        entity_type="documento",
        slug="doc-7",
        incluir_contexto_tematico=True,
    )

    assert resultado is not None
    grupo = next(g for g in resultado["grupos"] if g["tipo"] == "evidencia")
    assert [item["slug"] for item in grupo["itens"]] == ["evidencia-final"]


def test_backfill_ingere_referencias_explicitas_sem_inferencia_textual(db):
    _limpar(db)
    db.add_all([
        Document(
            slug="doc-origem", title="Documento origem", kind="modulo", theme=TEMA,
            body_md="Veja [o fluxo](/biblioteca/fluxo-alvo).",
            review_status="revisado", published=True,
        ),
        Document(
            slug="fluxo-alvo", title="Fluxo alvo", kind="fluxograma", theme=TEMA,
            body_md="corpo", review_status="revisado", published=True,
        ),
        EvidenceRecord(
            slug="ev-explicita", theme=TEMA, statement="Recomendação",
            recommendation_class="I", evidence_level="A", society="ESC", year=2026,
            guideline_title="Diretriz", reference="Referência",
            document_slug="doc-origem", review_status="revisado", published=True,
        ),
        PatientMaterial(
            slug="material-explicito", titulo="Material", tema=TEMA,
            documento_slug="doc-origem", review_status="revisado", published=True,
        ),
        DischargeChecklist(
            slug="check-explicito", condicao="Condição", theme=TEMA,
            documento_origem="doc-origem", itens=[{"id": "x"}],
            review_status="revisado", published=True,
        ),
        EmergencyProtocol(
            slug="emerg-explicita", titulo="Emergência", ordem=1,
            documento_slug="doc-origem", fluxograma_slug="fluxo-alvo",
            relacionados=["fluxo-alvo"], review_status="revisado", published=True,
        ),
        StudyTrack(
            slug="trilha-explicita", titulo="Trilha", tema=TEMA,
            etapas=[{
                "ordem": 1, "item_type": "documento", "item_slug": "doc-origem",
                "por_que": "Base da trilha",
            }],
            review_status="revisado", published=True,
        ),
    ])
    db.commit()

    resultado = kg.backfill_mesmo_tema(db)
    tipos = set(db.execute(select(KnowledgeRelation.relation_type)).scalars())

    assert resultado["referencias_explicitas_nao_resolvidas"] == 0
    assert {"supported_by", "derived_from", "uses_flowchart", "associated_with",
            "contains", "mentioned_in"} <= tipos


def test_backfill_reconcilia_evidencia_para_estudo_por_slug_explicito(db):
    _limpar(db)
    evidencia = EvidenceRecord(
        slug="ev-com-estudo", theme="Hipertensão", statement="Recomendação",
        recommendation_class="I", evidence_level="A", society="ESC", year=2026,
        guideline_title="Diretriz", reference="Referência",
        review_status="revisado", published=True,
    )
    estudo_a = ScientificStudy(
        slug="estudo-a", title="Estudo A", study_type="ensaio_clinico",
        journal="Journal", year=2025, summary="Resumo A", key_findings="Achados A",
        clinical_implications="Implicações A", theme="Hipertensão",
        review_status="revisado", published=True,
    )
    estudo_b = ScientificStudy(
        slug="estudo-b", title="Estudo B", study_type="metanalise",
        journal="Journal", year=2026, summary="Resumo B", key_findings="Achados B",
        clinical_implications="Implicações B", theme="Hipertensão",
        review_status="revisado", published=True,
    )
    db.add_all([evidencia, estudo_a, estudo_b])
    db.commit()

    # Compatibilidade antecipada: o atributo será mapeado pela migration do
    # loader, mas esta branch do grafo ainda não deve incorporar o schema.
    evidencia.study_slug = estudo_a.slug
    kg.backfill_mesmo_tema(db)

    no_evidencia = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "evidencia",
        KnowledgeEntity.slug == evidencia.slug,
    )).scalar_one()
    no_estudo_a = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "estudo",
        KnowledgeEntity.slug == estudo_a.slug,
    )).scalar_one()
    relacao_a = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == no_evidencia.id,
        KnowledgeRelation.target_entity_id == no_estudo_a.id,
        KnowledgeRelation.relation_type == "supported_by",
    )).scalar_one()

    assert relacao_a.relevance_score == 1.0
    assert relacao_a.provenance_type == "structured_metadata"
    assert relacao_a.confidence == "derived"
    assert relacao_a.review_status == "revisado"
    assert relacao_a.evidence_source == "EvidenceRecord.study_slug"
    assert relacao_a.extra["campo"] == "EvidenceRecord.study_slug"
    assert relacao_a.extra["graph_source_slug"] == evidencia.slug
    assert relacao_a.extra["graph_target_slug"] == estudo_a.slug

    evidencia.study_slug = estudo_b.slug
    kg.backfill_mesmo_tema(db)

    no_estudo_b = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "estudo",
        KnowledgeEntity.slug == estudo_b.slug,
    )).scalar_one()
    relacao_b = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == no_evidencia.id,
        KnowledgeRelation.target_entity_id == no_estudo_b.id,
        KnowledgeRelation.relation_type == "supported_by",
    )).scalar_one()
    db.refresh(relacao_a)

    assert relacao_a.review_status == "rejeitado"
    assert relacao_a.extra["_inactive_reason"] == "source_removed"
    assert relacao_b.review_status == "revisado"
    assert relacao_b.extra["destino_slug"] == estudo_b.slug

    evidencia.study_slug = None
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao_b)

    assert relacao_b.review_status == "rejeitado"
    assert relacao_b.extra["_inactive_reason"] == "source_removed"


def test_backfill_publica_vinculo_estudo_so_com_dupla_revisao(db):
    _limpar(db)
    evidencia = EvidenceRecord(
        slug="ev-pendente", theme="Hipertensão", statement="Recomendação",
        recommendation_class="IIa", evidence_level="B", society="ESC", year=2026,
        guideline_title="Diretriz", reference="Referência",
        review_status="pendente_revisao", published=True,
    )
    estudo = ScientificStudy(
        slug="estudo-revisao", title="Estudo em revisão", study_type="coorte",
        journal="Journal", year=2026, summary="Resumo", key_findings="Achados",
        clinical_implications="Implicações", theme="Hipertensão",
        review_status="revisado", published=True,
    )
    db.add_all([evidencia, estudo])
    db.commit()
    evidencia.study_slug = estudo.slug

    kg.backfill_mesmo_tema(db)
    assert db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.relation_type == "supported_by",
        KnowledgeRelation.extra["campo"].astext == "EvidenceRecord.study_slug",
    )).scalars().all() == []

    evidencia.review_status = "revisado"
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    relacao = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.relation_type == "supported_by",
        KnowledgeRelation.extra["campo"].astext == "EvidenceRecord.study_slug",
    )).scalar_one()
    assert relacao.review_status == "revisado"

    evidencia.review_status = "pendente_revisao"
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)
    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "source_removed"

    evidencia.review_status = "revisado"
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)
    assert relacao.review_status == "revisado"

    evidencia.published = False
    db.commit()
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)
    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "source_removed"

    evidencia.published = True
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)
    assert relacao.review_status == "revisado"

    estudo.review_status = "pendente_revisao"
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)

    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "source_removed"

    estudo.review_status = "revisado"
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)
    assert relacao.review_status == "revisado"

    estudo.published = False
    db.commit()
    evidencia.study_slug = estudo.slug
    kg.backfill_mesmo_tema(db)
    db.refresh(relacao)
    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "source_removed"


def test_backfill_reativa_entidade_de_conteudo_republicado(db):
    _limpar(db)
    _semear_conteudo_publicado(db)
    kg.backfill_mesmo_tema(db)

    doc = db.execute(select(Document).where(Document.slug == "ic-doc-1")).scalar_one()
    doc.published = False
    db.commit()
    kg.backfill_mesmo_tema(db)
    assert kg.relacionados_de(db, entity_type="documento", slug="ic-doc-1") is None

    doc.published = True
    db.commit()
    kg.backfill_mesmo_tema(db)

    entidade = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-doc-1")).scalar_one()
    assert entidade.status == "ativo"
    assert kg.relacionados_de(db, entity_type="documento", slug="ic-doc-1") is not None


def test_relacionados_de_respeita_limite_por_tipo(db):
    _limpar(db)
    origem = kg.registrar_entidade(db, entity_type="documento", canonical_id=1, slug="origem", title="Origem")
    for i in range(10):
        alvo = kg.registrar_entidade(
            db, entity_type="evidencia", canonical_id=i, slug=f"ev-{i}", title=f"Evidência {i}"
        )
        kg.registrar_relacao(
            db, source=origem, target=alvo, relation_type="supported_by",
            provenance_type="editorial", confidence="explicit",
            relevance_score=i / 10,
            evidence_source=f"curadoria:ev-{i}", review_status="revisado",
        )
    db.commit()

    resultado = kg.relacionados_de(db, entity_type="documento", slug="origem", limite_por_tipo=3)

    grupo_evidencia = next(g for g in resultado["grupos"] if g["tipo"] == "evidencia")
    assert len(grupo_evidencia["itens"]) == 3
    assert grupo_evidencia["total_disponivel"] == 10
    # ordenado por relevância decrescente — os 3 primeiros são ev-9, ev-8, ev-7
    assert [i["slug"] for i in grupo_evidencia["itens"]] == ["ev-9", "ev-8", "ev-7"]


def test_relacionados_de_nao_publica_same_theme_como_relacao_clinica(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="origem-tema", title="Origem",
    )
    alvo = kg.registrar_entidade(
        db, entity_type="evidencia", canonical_id=1, slug="alvo-tema", title="Alvo",
    )
    kg.registrar_relacao(
        db, source=origem, target=alvo, relation_type="same_theme",
        provenance_type="structured_metadata", confidence="derived",
        relevance_score=0.35,
    )
    db.commit()

    resultado = kg.relacionados_de(db, entity_type="documento", slug="origem-tema")

    assert resultado is not None
    assert resultado["grupos"] == []
    assert resultado["total"] == 0


def test_reconciliacao_atualiza_e_desativa_somente_relacao_automatica(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="origem", title="Origem",
    )
    alvo = kg.registrar_entidade(
        db, entity_type="evidencia", canonical_id=1, slug="alvo", title="Alvo",
    )
    db.flush()
    lote = kg._LoteRelacoes(existentes={}, desejadas=set())
    assert kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="mentioned_in",
        relevance_score=0.8, extra={"ordem": 1}, lote=lote,
    ) == 1
    db.commit()

    relacao = db.execute(select(KnowledgeRelation)).scalar_one()
    lote_atualizacao = kg._LoteRelacoes(
        existentes={(origem.id, alvo.id, "mentioned_in"): relacao}, desejadas=set(),
    )
    assert kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="mentioned_in",
        relevance_score=0.9, extra={"ordem": 2}, lote=lote_atualizacao,
    ) == 0
    assert relacao.relevance_score == 0.9
    assert relacao.extra["ordem"] == 2

    lote_ausente = kg._LoteRelacoes(
        existentes={(origem.id, alvo.id, "mentioned_in"): relacao}, desejadas=set(),
    )
    assert kg._rejeitar_relacoes_automaticas_ausentes(lote_ausente) == 1
    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "source_removed"

    lote_retorno = kg._LoteRelacoes(
        existentes={(origem.id, alvo.id, "mentioned_in"): relacao}, desejadas=set(),
    )
    kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="mentioned_in",
        relevance_score=0.9, extra={"ordem": 2}, lote=lote_retorno,
    )
    assert relacao.review_status == "pendente_revisao"
    assert "_inactive_reason" not in relacao.extra


def test_reconciliacao_adota_legado_sem_apagar_revisao_humana(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="origem", title="Origem",
    )
    alvo = kg.registrar_entidade(
        db, entity_type="evidencia", canonical_id=1, slug="alvo", title="Alvo",
    )
    relacao = kg.registrar_relacao(
        db, source=origem, target=alvo, relation_type="supported_by",
        provenance_type="structured_metadata", confidence="derived",
        relevance_score=0.95, review_status="revisado",
        extra={
            "campo": "EvidenceRecord.document_slug",
            "nota_curadoria": "manter esta observação",
        },
    )
    db.commit()

    lote = kg._LoteRelacoes(
        existentes={(origem.id, alvo.id, "supported_by"): relacao}, desejadas=set(),
    )
    kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="supported_by",
        relevance_score=0.95,
        extra={"campo": "EvidenceRecord.document_slug"}, lote=lote,
    )

    assert relacao.review_status == "revisado"
    assert relacao.extra["_producer"] == kg._PRODUTOR_BACKFILL
    assert relacao.extra["_fingerprint"]
    assert relacao.extra["nota_curadoria"] == "manter esta observação"


def test_fingerprint_novo_nao_reativa_rejeicao_humana(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="origem", title="Origem",
    )
    alvo = kg.registrar_entidade(
        db, entity_type="evidencia", canonical_id=1, slug="alvo", title="Alvo",
    )
    db.flush()
    lote = kg._LoteRelacoes(existentes={}, desejadas=set())
    kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="supported_by",
        relevance_score=0.95, extra={"campo": "EvidenceRecord.document_slug"}, lote=lote,
    )
    relacao = next(iter(lote.existentes.values()))
    relacao.review_status = "rejeitado"
    db.commit()

    lote_novo = kg._LoteRelacoes(
        existentes={(origem.id, alvo.id, "supported_by"): relacao}, desejadas=set(),
    )
    kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="supported_by",
        relevance_score=0.95,
        extra={"campo": "EvidenceRecord.document_slug", "versao": 2}, lote=lote_novo,
    )

    assert relacao.review_status == "rejeitado"
    assert "_inactive_reason" not in relacao.extra


def test_motivo_de_inativacao_editorial_nao_e_reativado(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="origem", title="Origem",
    )
    alvo = kg.registrar_entidade(
        db, entity_type="evidencia", canonical_id=1, slug="alvo", title="Alvo",
    )
    db.flush()
    lote = kg._LoteRelacoes(existentes={}, desejadas=set())
    kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="supported_by",
        relevance_score=0.95, extra={"campo": "EvidenceRecord.document_slug"}, lote=lote,
    )
    relacao = next(iter(lote.existentes.values()))
    relacao.review_status = "rejeitado"
    relacao.extra = {**relacao.extra, "_inactive_reason": "decisao_editorial"}
    db.commit()

    lote_novo = kg._LoteRelacoes(
        existentes={(origem.id, alvo.id, "supported_by"): relacao}, desejadas=set(),
    )
    kg._registrar_relacao_estruturada(
        db, source=origem, target=alvo, relation_type="supported_by",
        relevance_score=0.96,
        extra={"campo": "EvidenceRecord.document_slug"}, lote=lote_novo,
    )

    assert relacao.review_status == "rejeitado"
    assert relacao.extra["_inactive_reason"] == "decisao_editorial"


def test_assinatura_legada_incompativel_nao_e_adotada(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="origem", title="Origem",
    )
    alvo = kg.registrar_entidade(
        db, entity_type="evidencia", canonical_id=1, slug="alvo", title="Alvo",
    )
    relacao = kg.registrar_relacao(
        db, source=origem, target=alvo, relation_type="recommended_by",
        provenance_type="editorial", confidence="explicit", review_status="revisado",
        extra={"campo": "EvidenceRecord.document_slug"},
    )
    db.commit()

    assert kg._relacao_pertence_ao_backfill(relacao) is False


def test_calculadora_duplicada_preserva_relacao_manual_no_no_canonico(db):
    _limpar(db)
    documento = Document(
        slug="alvo-manual", title="Alvo manual", kind="modulo", theme=TEMA,
        body_md="corpo", review_status="revisado", published=True,
    )
    db.add(documento)
    db.flush()
    calculadora = next(c for c in kg.calc.REGISTRY.values() if c.status == "implementada")
    id_estavel = kg._id_estavel("calculadora", calculadora.slug)
    canonica = KnowledgeEntity(
        entity_type="calculadora", canonical_id=id_estavel,
        slug=calculadora.slug, title=calculadora.name, status="ativo",
    )
    duplicada = KnowledgeEntity(
        entity_type="calculadora", canonical_id=id_estavel + 1,
        slug=calculadora.slug, title=calculadora.name, status="ativo",
    )
    alvo = KnowledgeEntity(
        entity_type="documento", canonical_id=documento.id,
        slug="alvo-manual", title="Alvo manual", status="ativo",
    )
    db.add_all([canonica, duplicada, alvo])
    db.flush()
    db.add_all([
        KnowledgeRelation(
            source_entity_id=canonica.id, target_entity_id=alvo.id,
            relation_type="recommended_by", provenance_type="structured_metadata",
            confidence="derived", relevance_score=0.3, review_status="pendente_revisao",
            extra={"_producer": kg._PRODUTOR_BACKFILL},
        ),
        KnowledgeRelation(
            source_entity_id=duplicada.id, target_entity_id=alvo.id,
            relation_type="recommended_by", provenance_type="editorial",
            confidence="explicit", relevance_score=1.0, review_status="revisado",
            extra={"curadoria": "manual"},
        ),
    ])
    db.commit()

    resultado = kg.backfill_mesmo_tema(db)

    db.refresh(duplicada)
    assert duplicada.status == "arquivado"
    assert resultado["relacoes_manuais_calculadora_migradas"] == 1
    migrada = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == canonica.id,
        KnowledgeRelation.target_entity_id == alvo.id,
        KnowledgeRelation.relation_type == "recommended_by",
    )).scalar_one()
    assert migrada.review_status == "revisado"
    assert migrada.provenance_type == "editorial"
    assert migrada.extra["_migrated_from_entity_ids"] == [duplicada.id]
    relacionados = kg.relacionados_de(
        db, entity_type="calculadora", slug=calculadora.slug,
    )
    assert "alvo-manual" in {
        item["slug"] for grupo in relacionados["grupos"] for item in grupo["itens"]
    }

    migrada.extra = {
        **migrada.extra,
        "_producer": kg._PRODUTOR_BACKFILL,
        "nota_pos_migracao": "decisão mantida",
    }
    migrada.review_status = "rejeitado"
    db.commit()
    segunda_rodada = kg.backfill_mesmo_tema(db)
    db.refresh(migrada)
    assert segunda_rodada["relacoes_manuais_calculadora_migradas"] == 0
    assert migrada.review_status == "rejeitado"
    assert migrada.extra["nota_pos_migracao"] == "decisão mantida"


def test_calculadoras_duplicadas_migram_os_dois_endpoints(db):
    _limpar(db)
    calculadoras = [c for c in kg.calc.REGISTRY.values() if c.status == "implementada"][:2]
    assert len(calculadoras) == 2
    canonicas = []
    duplicadas = []
    for indice, calculadora in enumerate(calculadoras):
        id_estavel = kg._id_estavel("calculadora", calculadora.slug)
        canonicas.append(KnowledgeEntity(
            entity_type="calculadora", canonical_id=id_estavel,
            slug=calculadora.slug, title=calculadora.name, status="ativo",
        ))
        duplicadas.append(KnowledgeEntity(
            entity_type="calculadora", canonical_id=id_estavel + 10_000 + indice,
            slug=calculadora.slug, title=calculadora.name, status="ativo",
        ))
    db.add_all([*canonicas, *duplicadas])
    db.flush()
    db.add(KnowledgeRelation(
        source_entity_id=duplicadas[0].id, target_entity_id=duplicadas[1].id,
        relation_type="alternative_to", provenance_type="editorial",
        confidence="explicit", relevance_score=1.0, review_status="revisado",
        extra={"curadoria": "manual"},
    ))
    db.commit()

    kg.backfill_mesmo_tema(db)

    migrada = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == canonicas[0].id,
        KnowledgeRelation.target_entity_id == canonicas[1].id,
        KnowledgeRelation.relation_type == "alternative_to",
    )).scalar_one()
    assert migrada.review_status == "revisado"
    assert migrada.extra["_migrated_from_entity_ids"] == sorted(
        [duplicadas[0].id, duplicadas[1].id]
    )


def test_parser_markdown_ignora_url_externa_e_trecho_de_codigo():
    assert kg._slug_de_link_markdown("https://exemplo.org/documento.md") is None
    assert kg._slug_de_link_markdown("//exemplo.org/documento.md") is None
    assert kg._slug_de_link_markdown("/biblioteca/documento-interno") == "documento-interno"
    corpo = """[válido](/biblioteca/valido)\n```md\n[falso](/biblioteca/falso)\n```"""
    destinos = kg._LINK_MARKDOWN.findall(kg._markdown_sem_codigo(corpo))
    assert destinos == ["/biblioteca/valido"]


def test_relacao_clinica_forte_pendente_nao_e_publicada(db):
    _limpar(db)
    origem = kg.registrar_entidade(
        db, entity_type="medicamento", canonical_id=1, slug="farmaco", title="Fármaco",
    )
    pendente = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=1, slug="condicao", title="Condição",
    )
    navegacao = kg.registrar_entidade(
        db, entity_type="documento", canonical_id=2, slug="referencia", title="Referência",
    )
    kg.registrar_relacao(
        db, source=origem, target=pendente, relation_type="treats",
        provenance_type="structured_metadata", confidence="derived",
        review_status="pendente_revisao",
    )
    kg.registrar_relacao(
        db, source=navegacao, target=origem, relation_type="mentioned_in",
        provenance_type="structured_metadata", confidence="derived",
        review_status="pendente_revisao",
    )
    kg.registrar_relacao(
        db, source=origem, target=pendente, relation_type="associated_with",
        provenance_type="ai_suggested", confidence="ai_suggested",
        review_status="pendente_revisao",
    )
    db.commit()

    resultado = kg.relacionados_de(db, entity_type="medicamento", slug="farmaco")
    slugs = {item["slug"] for grupo in resultado["grupos"] for item in grupo["itens"]}
    assert "condicao" not in slugs
    assert "referencia" in slugs


def test_area_estruturada_cobre_doenca_e_todos_os_topicos_da_triagem(db):
    _limpar(db)
    db.add(SpecialtyDisease(
        slug="doenca-gravidez", name="Doença da gravidez", area="gravidez",
        category="teste", summary="Resumo", review_status="revisado", published=True,
    ))
    db.add(SymptomTriageGuide(
        slug="triagem-multipla", name="Triagem múltipla",
        areas=["geral", "gravidez"], summary="Resumo",
        review_status="revisado", published=True,
    ))
    db.commit()

    kg.backfill_mesmo_tema(db)
    doenca = db.execute(
        select(KnowledgeEntity).where(KnowledgeEntity.slug == "doenca-gravidez")
    ).scalar_one()
    triagem = db.execute(
        select(KnowledgeEntity).where(KnowledgeEntity.slug == "triagem-multipla")
    ).scalar_one()

    def _temas(no):
        return set(db.execute(
            select(KnowledgeEntity.title)
            .join(KnowledgeRelation, KnowledgeRelation.target_entity_id == KnowledgeEntity.id)
            .where(
                KnowledgeRelation.source_entity_id == no.id,
                KnowledgeRelation.relation_type == "belongs_to_topic",
            )
        ).scalars())

    assert _temas(doenca) == {"Gravidez"}
    assert _temas(triagem) == {"Geral", "Gravidez"}


def test_conteudo_publicado_sem_tema_permanece_no_grafo(db):
    _limpar(db)
    db.add(Document(
        slug="documento-sem-tema", title="Documento sem tema", kind="modulo",
        theme="", body_md="corpo", review_status="revisado", published=True,
    ))
    db.add(EmergencyProtocol(
        slug="protocolo-sem-documento", titulo="Protocolo sem documento resolvido",
        ordem=1, documento_slug="documento-ainda-ausente",
        review_status="revisado", published=True,
    ))
    db.commit()

    resultado = kg.backfill_mesmo_tema(db)

    documento = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "documento",
        KnowledgeEntity.slug == "documento-sem-tema",
    )).scalar_one()
    protocolo = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "protocolo_emergencia",
        KnowledgeEntity.slug == "protocolo-sem-documento",
    )).scalar_one()
    assert documento.status == "ativo"
    assert protocolo.status == "ativo"
    assert resultado["referencias_explicitas_nao_resolvidas"] >= 1
    assert db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == documento.id,
        KnowledgeRelation.relation_type == "belongs_to_topic",
    )).scalars().all() == []


def test_rotas_relacionadas_abrem_o_item_especifico(db):
    _limpar(db)
    db.add_all([
        Document(
            slug="doc-rota", title="Documento", kind="modulo", theme=TEMA,
            body_md="corpo", review_status="revisado", published=True,
        ),
        EmergencyProtocol(
            slug="emerg-rota", titulo="Emergência", ordem=1,
            documento_slug="doc-rota", review_status="revisado", published=True,
        ),
        DischargeChecklist(
            slug="check-rota", condicao="Checklist", theme=TEMA,
            itens=[{"id": "x", "texto": "Item"}],
            review_status="revisado", published=True,
        ),
        PatientMaterial(
            slug="material-rota", titulo="Material", tema=TEMA,
            review_status="revisado", published=True,
        ),
    ])
    db.commit()

    resposta = buscar_relacionados(db, TEMA)
    rotas = {
        item["slug"]: item["rota"]
        for grupo in resposta["grupos"]
        for item in grupo["itens"]
    }
    assert ROTAS_TRILHA["checklist"].format(slug="check-rota") == "/checklists/check-rota"
    assert rotas["emerg-rota"] == "/emergencia?protocolo=emerg-rota"
    assert rotas["check-rota"] == "/checklists/check-rota"
    assert rotas["material-rota"] == "/material-paciente/material-rota"
