"""Grafo de conhecimento clínico universal — issue #52 (nova fase).

Camada genérica e persistida, DISTINTA do cruzamento em tempo de consulta já
existente em `app/services/related_content.py` (que casa por `theme`/`tema`
exato, sem persistir nada). As duas coexistem de propósito:

- `related_content.py` continua sendo o cruzamento "por tema", simples e
  rápido, já em produção — não foi tocado nem substituído aqui.
- Este módulo é a abstração genérica pedida explicitamente ("não implementar
  como coluna fixa por tabela — related_medications, related_diseases,
  related_studies espalhados não escala"): duas tabelas, tipos de relação
  catalogados, proveniência/confiança auditáveis, pontuação de relevância,
  e um mecanismo de "backfill" que pode (entre outras fontes) derivar edges
  a partir do mesmo casamento por tema que `related_content.py` já usa —
  sem duplicar aquela lógica de consulta em tempo real, só semeando dados.

## Regra de segurança inegociável (issue #52, seção 26-27)

`knowledge_entities`/`knowledge_relations` são o GRAFO GLOBAL — conteúdo
científico/editorial (documento, evidência, estudo, medicamento, exame,
caso clínico, trilha, checklist, protocolo de emergência, material do
paciente, galeria, calculadora, doença especializada e triagem por sintoma).
NUNCA um `Patient`, `Prescription`, `Appointment`, `GeneratedDocument`,
`ServiceOrder` ou qualquer entidade com dado de paciente/consulta/prescrição
individual pode virar `knowledge_entity` — isso exporia contexto privado de
um paciente como nó público indexável, inclusive entre médicos diferentes
(o mesmo tipo de vazamento que o IDOR/BOLA desta mesma fase corrigiu, agora
pela porta do grafo em vez da porta da rota REST).
`TIPOS_ENTIDADE_PERMITIDOS` abaixo é o allowlist que impõe isso
estruturalmente — `KnowledgeGraphService.registrar_entidade()` rejeita
qualquer `entity_type` fora da lista, não é só documentação.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Allowlist estrutural — só conteúdo global/editorial pode virar nó do grafo.
# Além das frentes já cobertas por `related_content.py`, doenças especializadas
# e fluxos de triagem são conteúdo global versionado/publicável em tabelas
# próprias (`specialty_diseases` e `symptom_triage_guides`) e um nó taxonômico
# interno de tema. Nenhum tipo de
# dado de paciente entra aqui — ver nota de segurança no docstring do módulo.
TIPOS_ENTIDADE_PERMITIDOS = frozenset({
    "documento",
    "fluxograma",
    "evidencia",
    "estudo",
    "medicamento",
    "exame",
    "caso_clinico",
    "trilha",
    "galeria",
    "checklist",
    "material_paciente",
    "protocolo_emergencia",
    "calculadora",
    "doenca",
    "triagem_sintoma",
    # Nó interno de taxonomia. Não é conteúdo clínico nem dado de paciente:
    # permite representar item -> tema em O(N), sem materializar uma malha
    # O(N²) de pares `same_theme`.
    "tema",
})

# Catálogo de tipos de relação — evita a proliferação caótica que o pedido
# pediu para prevenir. Cada relação usa um destes valores; a direção
# (source -> target) é sempre a do verbo, ex.:
# (calculadora) -[recommended_by]-> (evidencia)
# (medicamento) -[treats]-> (documento de doença)
# (doenca) -[differential_for]-> (triagem_sintoma)
TIPOS_RELACAO_PERMITIDOS = frozenset({
    "treats",                       # trata / é indicado para
    "indicated_for",                # indicação clínica formal
    "contraindicated_in",           # contraindicado numa condição/população
    "contraindicated_with",         # contraindicado com outro item (interação)
    "interacts_with",               # interação bidirecional declarada
    "monitor_with",                 # exige monitorização conjunta
    "diagnosed_by",                 # diagnosticado/investigado por exame
    "supported_by",                 # afirmação clínica apoiada por evidência/estudo
    "studied_in",                   # tema estudado num ensaio/estudo
    "recommended_by",               # conduta recomendada por diretriz/evidência
    "associated_with",              # associação genérica, mais fraca que as acima
    "causes",                       # relação causal declarada em fonte
    "may_cause",                    # relação causal possível/efeito adverso
    "alternative_to",               # alternativa terapêutica
    "belongs_to_class",             # pertence à mesma classe/categoria
    "used_in_case",                 # citado/usado num caso clínico
    "mentioned_in",                 # citação/menção textual, sem afirmação clínica forte
    "patient_education_for",        # material de paciente sobre o tema
    "differential_for",             # doença explicitamente listada como diferencial de sintoma/condição
    "same_theme",                   # mesmo tema clínico (proveniência: derivado por tema)
    "belongs_to_topic",             # item associado ao nó canônico do tema
    "derived_from",                 # conteúdo derivado de uma fonte editorial explícita
    "uses_flowchart",               # protocolo usa fluxograma declarado em metadado
    "contains",                     # contêiner curado (trilha) contém item explícito
})

# Proveniência — nunca "confiança implícita". Toda relação carrega qual dos
# três níveis de confiança do pedido (issue #52, seção 24) ela representa.
TIPOS_PROVENIENCIA_PERMITIDOS = frozenset({
    "editorial",             # relação explícita, redigida/revisada por humano
    "structured_metadata",   # derivada de campo estruturado já existente (ex.: mesmo tema)
    "imported",              # trazida de uma migração/backfill de dado legado
    "derived",               # calculada a partir de outras relações já existentes
    "ai_suggested",          # sugerida por IA — NUNCA promovida automaticamente a fato
    "clinical_context",      # inferida do contexto de uso clínico (ex.: navegação)
})

NIVEIS_CONFIANCA_PERMITIDOS = frozenset({"explicit", "derived", "ai_suggested"})

REVIEW_STATUS_RELACAO_PERMITIDOS = frozenset({
    "revisado",           # confirmado por humano/regra determinística confiável
    "pendente_revisao",   # criado (ex.: por backfill) mas ainda não revisado
    "rejeitado",          # revisado e considerado incorreto/irrelevante — mantido para auditoria
})


class KnowledgeEntity(Base):
    """Um nó do grafo — sempre um item de conteúdo global já existente em
    outra tabela (nunca um registro novo de conteúdo: `canonical_id`
    referencia o `id` da tabela de origem, `entity_type` diz qual)."""

    __tablename__ = "knowledge_entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    canonical_id: Mapped[int] = mapped_column(Integer)
    slug: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="ativo")
    # ativo | arquivado — nunca DELETE físico de um nó com relações; arquivar
    # em vez de apagar preserva a auditoria de proveniência das relações que
    # apontam para ele.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # Um nó por (tipo, id de origem) — nunca duplica a mesma evidência/
        # documento/medicamento como dois nós diferentes.
        UniqueConstraint("entity_type", "canonical_id", name="uq_knowledge_entity_origem"),
        Index("ix_knowledge_entities_slug", "slug"),
    )


class KnowledgeRelation(Base):
    """Uma aresta tipada e auditável do grafo."""

    __tablename__ = "knowledge_relations"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_entity_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"), index=True
    )
    target_entity_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"), index=True
    )
    relation_type: Mapped[str] = mapped_column(String(40), index=True)

    relevance_score: Mapped[float] = mapped_column(Float, default=0.5)
    # 0.0-1.0. Nunca alterado por patrocínio — ver nota de módulo e
    # `docs/knowledge-graph.md`, seção de patrocínio.
    confidence: Mapped[str] = mapped_column(String(20), default="derived")
    provenance_type: Mapped[str] = mapped_column(String(30), default="structured_metadata")
    evidence_source: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # PMID/DOI/diretriz quando a relação for uma afirmação científica
    # (treats, contraindicated_in, causes, may_cause, supported_by,
    # recommended_by) — nunca fabricado; None quando a relação for
    # estrutural (ex.: same_theme) e não uma afirmação clínica.
    review_status: Mapped[str] = mapped_column(String(20), default="pendente_revisao", index=True)

    extra: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Metadado livre por relação (ex.: {"tema": "..."} para same_theme) —
    # nunca usado para burlar os campos tipados acima.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    source_entity: Mapped["KnowledgeEntity"] = relationship(foreign_keys=[source_entity_id])
    target_entity: Mapped["KnowledgeEntity"] = relationship(foreign_keys=[target_entity_id])

    __table_args__ = (
        # Mesmo par + mesmo tipo nunca duplica aresta (idempotência de
        # backfill: rodar de novo não cria uma segunda relação idêntica).
        UniqueConstraint(
            "source_entity_id", "target_entity_id", "relation_type",
            name="uq_knowledge_relation_aresta",
        ),
        Index("ix_knowledge_relations_source_type", "source_entity_id", "relation_type"),
        Index("ix_knowledge_relations_target_type", "target_entity_id", "relation_type"),
        Index("ix_knowledge_relations_review_status", "review_status"),
    )
