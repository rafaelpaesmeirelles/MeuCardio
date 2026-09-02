from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.db import Base


class DocumentChunk(Base):
    """Trecho indexado de um documento, com embedding para busca semântica."""

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    ordem: Mapped[int] = mapped_column(Integer)
    titulo_secao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    conteudo: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))
    tokens_aprox: Mapped[int] = mapped_column(Integer, default=0)


class KnowledgeChunk(Base):
    """Trecho indexado de conteúdo global fora de `documents` (auditoria de
    02/09/2026, Parte D da correção coordenada — RAG expandido a todo o
    acervo científico elegível).

    `entity_type` usa o mesmo allowlist estrutural do grafo de conhecimento
    (`app.models.knowledge.TIPOS_ENTIDADE_PERMITIDOS`) e `entity_id` é o `id`
    real da linha na tabela de origem (ou o `_id_estavel(...)` determinístico
    já usado pelo grafo, para o único tipo sem tabela própria: calculadora).
    `documents` continua indexado em `document_chunks`, propositalmente
    intocado — não há necessidade de migrar 1.949 trechos já corretos para
    aqui; `recuperar()` funde os dois na leitura.

    `content_hash` (sha256 do texto fonte) permite detectar conteúdo
    desatualizado sem reprocessar tudo: reindexação seletiva compara o hash
    atual do texto-fonte contra o gravado no chunk mais recente da entidade.
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)
    ordem: Mapped[int] = mapped_column(Integer)
    titulo_secao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    conteudo: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dim))
    tokens_aprox: Mapped[int] = mapped_column(Integer, default=0)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "ordem", name="uq_knowledge_chunk_posicao"),
    )


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    # "clinica" | "pessoal" (Trabalho 15) — separa o histórico dos dois
    # modos do assistente; nunca muda depois de criada (a rota valida isso).
    modo: Mapped[str] = mapped_column(String(20), default="clinica", server_default="clinica", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    mensagens: Mapped[list["AIMessage"]] = relationship(
        back_populates="conversa", cascade="all, delete-orphan"
    )


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True
    )
    papel: Mapped[str] = mapped_column(String(20))  # user | assistant
    conteudo: Mapped[str] = mapped_column(Text)
    fontes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON com slugs citados
    fontes_pubmed: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON com artigos externos citados
    modelo: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tokens_entrada: Mapped[int] = mapped_column(Integer, default=0)
    tokens_saida: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    conversa: Mapped[AIConversation] = relationship(back_populates="mensagens")
