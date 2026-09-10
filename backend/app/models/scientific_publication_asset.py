"""Shared, licensed publication artifacts. Never references private uploads."""
from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ScientificPublicationAsset(Base):
    __tablename__ = 'scientific_publication_assets'
    id: Mapped[int] = mapped_column(primary_key=True)
    source_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    doi: Mapped[str | None] = mapped_column(String(240), nullable=True)
    source_url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default='pending', index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    pmcid: Mapped[str | None] = mapped_column(String(30), nullable=True)
    license_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    original_storage_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    translated_storage_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary_pt: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress: Mapped[dict] = mapped_column(JSONB, default=dict)
    coverage: Mapped[dict] = mapped_column(JSONB, default=dict)
    retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
