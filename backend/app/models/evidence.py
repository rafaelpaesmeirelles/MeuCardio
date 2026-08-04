from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EvidenceRecord(Base):
    """Recomendação pontual com força, resumo clínico e fonte verificável."""

    __tablename__ = "evidence_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    statement: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation_class: Mapped[str] = mapped_column(String(10))
    evidence_level: Mapped[str] = mapped_column(String(5))
    society: Mapped[str] = mapped_column(String(80))
    year: Mapped[int] = mapped_column()
    guideline_title: Mapped[str] = mapped_column(String(400))
    reference: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(160), nullable=True)

    theme: Mapped[str] = mapped_column(String(80), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    document_slug: Mapped[str | None] = mapped_column(String(255), nullable=True)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
