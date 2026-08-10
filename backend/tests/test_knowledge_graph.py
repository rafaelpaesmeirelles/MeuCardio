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
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.services import knowledge_graph as kg

TEMA = "Insuficiência cardíaca"

TABELAS = (
    "knowledge_relations", "knowledge_entities",
    "document_revisions", "documents", "evidence_records", "scientific_studies",
    "drugs", "clinical_cases", "study_tracks", "gallery_images", "lab_tests",
    "emergency_protocols", "discharge_checklists", "patient_materials",
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


def test_backfill_cria_entidades_e_arestas_same_theme(db):
    _limpar(db)
    _semear_conteudo_publicado(db)

    resultado = kg.backfill_mesmo_tema(db)

    assert resultado["entidades_criadas_ou_atualizadas"] >= 3
    entidades = db.execute(select(KnowledgeEntity)).scalars().all()
    slugs = {e.slug for e in entidades}
    assert {"ic-doc-1", "ic-ev-1", "carvedilol-teste"} <= slugs
    # O item não publicado nunca vira nó — mesma régua de published de toda
    # frente do produto.
    assert "ic-doc-nao-publicado" not in slugs

    relacoes = db.execute(select(KnowledgeRelation)).scalars().all()
    assert len(relacoes) > 0
    for r in relacoes:
        assert r.relation_type == "same_theme"
        assert r.provenance_type == "structured_metadata"
        assert r.confidence == "derived"
        # Medicamento entra sob "Farmacologia" (convenção já documentada em
        # related_content.py — drugs não tem campo de tema próprio), então
        # nem toda aresta é do tema da IC; o que importa é que cada aresta
        # tem ALGUM tema de origem registrado, nunca vazio/fabricado.
        assert r.extra.get("tema") in (TEMA, "Farmacologia")

    # O documento e a evidência (mesmo tema real, "Insuficiência cardíaca")
    # ficam conectados por same_theme — é a aresta que a convenção de
    # medicamento->Farmacologia deliberadamente NÃO cria com o medicamento.
    doc = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-doc-1")).scalar_one()
    ev = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-ev-1")).scalar_one()
    droga = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "carvedilol-teste")).scalar_one()
    assert db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == doc.id,
            KnowledgeRelation.target_entity_id == ev.id,
        )
    ).scalar_one_or_none() is not None
    # Documento (tema IC) e medicamento (tema Farmacologia) não são ligados
    # por same_theme — são temas estruturalmente diferentes, nada fabricado.
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
    relacao = db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == doc.id,
            KnowledgeRelation.target_entity_id == ev.id,
        )
    ).scalar_one()
    relacao.review_status = "revisado"
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

    resultado = kg.relacionados_de(db, entity_type="documento", slug="ic-doc-1")

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


def test_relacionados_de_devolve_none_quando_item_nao_esta_no_grafo(db):
    _limpar(db)
    assert kg.relacionados_de(db, entity_type="documento", slug="nao-existe") is None


# ---------------------------------------------------------------------------
# Reconciliação de segurança — conteúdo despublicado nunca continua visível
# ---------------------------------------------------------------------------

def test_backfill_arquiva_entidade_de_conteudo_despublicado(db):
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

    resultado = kg.backfill_mesmo_tema(db)
    assert resultado["entidades_arquivadas"] >= 1

    entidade = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-doc-1")).scalar_one()
    assert entidade.status == "arquivado"
    assert kg.relacionados_de(db, entity_type="documento", slug="ic-doc-1") is None

    # As arestas em si não são apagadas (auditoria de proveniência
    # preservada) — só o nó vira invisível para consulta.
    ev = db.execute(select(KnowledgeEntity).where(KnowledgeEntity.slug == "ic-ev-1")).scalar_one()
    aresta_preservada = db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == entidade.id,
            KnowledgeRelation.target_entity_id == ev.id,
        )
    ).scalar_one_or_none()
    assert aresta_preservada is not None


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
            db, source=origem, target=alvo, relation_type="same_theme",
            provenance_type="structured_metadata", confidence="derived",
            relevance_score=i / 10,
        )
    db.commit()

    resultado = kg.relacionados_de(db, entity_type="documento", slug="origem", limite_por_tipo=3)

    grupo_evidencia = next(g for g in resultado["grupos"] if g["tipo"] == "evidencia")
    assert len(grupo_evidencia["itens"]) == 3
    assert grupo_evidencia["total_disponivel"] == 10
    # ordenado por relevância decrescente — os 3 primeiros são ev-9, ev-8, ev-7
    assert [i["slug"] for i in grupo_evidencia["itens"]] == ["ev-9", "ev-8", "ev-7"]
