from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class ScientificUserDocument(Base):
    """Arquivo científico privado enviado por um assinante.

    O original, texto extraído/traduzido e análise permanecem privados e
    cifrados. A incorporação ao corpus global é uma ação separada, explícita e
    auditável, nunca consequência automática do upload.
    """

    __tablename__ = "scientific_user_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    storage_key: Mapped[str] = mapped_column(String(100), unique=True)
    original_name_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    display_title_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    media_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)

    document_type: Mapped[str] = mapped_column(String(40), default="outro", index=True)
    language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    extracted_text_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    translated_text_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    analysis_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    analysis_status: Mapped[str] = mapped_column(String(24), default="pendente", index=True)
    analysis_error: Mapped[str | None] = mapped_column(String(160), nullable=True)

    incorporation_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    incorporation_status: Mapped[str] = mapped_column(
        String(24), default="nao_avaliado", index=True
    )
    consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    incorporated_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_agora, onupdate=_agora
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "sha256", name="uq_scientific_user_document_owner_sha"),
        CheckConstraint("size_bytes > 0", name="ck_scientific_user_documents_size_positive"),
        CheckConstraint(
            "analysis_status IN ('pendente','processando','concluido','erro')",
            name="ck_scientific_user_documents_analysis_status",
        ),
        CheckConstraint(
            "incorporation_status IN ('nao_avaliado','nao_recomendado','aguardando_consentimento','consentido','incorporado','duplicado')",
            name="ck_scientific_user_documents_incorporation_status",
        ),
    )
