from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ScientificStudy(Base):
    """Um estudo, ensaio clínico, revisão sistemática ou metanálise catalogado
    — resumo e implicação clínica em texto próprio, nunca cópia do abstract
    original (direito autoral)."""

    __tablename__ = "scientific_studies"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(400))
    study_type: Mapped[str] = mapped_column(String(60))
    # ensaio_clinico | revisao_sistematica | metanalise | consenso | coorte | caso_controle

    # "Sobrenome AB et al." na maioria, mas consenso multissocietário/comitê
    # de diretriz costuma listar autoria completa + sociedades por extenso
    # (registros reais excedem 300 caracteres) — Text desde migração
    # f71q20260812, mesmo padrão de 72abcfc8df81 (drugs.drug_class).
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)  # "Sobrenome AB et al."
    journal: Mapped[str] = mapped_column(String(200))
    year: Mapped[int] = mapped_column(Integer)
    doi: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pmid: Mapped[str | None] = mapped_column(String(20), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    summary: Mapped[str] = mapped_column(Text)  # resumo em texto próprio
    key_findings: Mapped[str] = mapped_column(Text)
    clinical_implications: Mapped[str] = mapped_column(Text)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)

    theme: Mapped[str] = mapped_column(String(80), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    fonte_producao: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
