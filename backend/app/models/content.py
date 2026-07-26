from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Document(Base):
    """Unidade de conteúdo científico (módulo, protocolo, diretriz, estudo)."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    kind: Mapped[str] = mapped_column(String(50), default="modulo")
    # modulo | protocolo | diretriz | estudo | consenso | calculadora | farmacologia
    theme: Mapped[str] = mapped_column(String(80), index=True)  # IC, DAC, FA, CDI...
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_md: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    source_refs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    evidence_level: Mapped[str | None] = mapped_column(String(40), nullable=True)

    source_tier: Mapped[str] = mapped_column(String(12), default="sem_fonte", index=True)
    # A = diretriz/sociedade/agência/periódico indexado
    # B = secundária institucional revisada (guia farmacêutico hospitalar, Cochrane, UpToDate)
    # C = terciária (blog, e-commerce de farmácia, vídeo, agregador de bula)
    # sem_fonte = nenhuma referência rastreável

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    # pendente_revisao | revisado | lacuna_declarada
    # fonte_terciaria_revisar | sem_fonte_rastreavel

    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # Só o que está publicado aparece para a equipe assistencial e alimenta a IA.

    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    gaps: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    # Campos que o próprio módulo declara como VERIFICAÇÃO HUMANA NECESSÁRIA.
    version: Mapped[int] = mapped_column(Integer, default=1)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    revisions: Mapped[list["DocumentRevision"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentRevision(Base):
    __tablename__ = "document_revisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    body_md: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    document: Mapped[Document] = relationship(back_populates="revisions")
