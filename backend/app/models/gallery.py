from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class GalleryImage(Base):
    """Achado de imagem cardiológica (ECG, eco, TC, RM, radiografia, cateterismo).

    Toda imagem precisa ter origem rastreável e licença que permita o uso —
    nunca uma imagem gerada por IA apresentada como achado clínico real."""

    __tablename__ = "gallery_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    modality: Mapped[str] = mapped_column(String(40), index=True)
    # ECG | Ecocardiograma | TC | RM | Radiografia | Cateterismo | Doppler | Patologia
    theme: Mapped[str] = mapped_column(String(80), index=True)  # mesmo vocabulário de Document.theme
    findings: Mapped[str] = mapped_column(Text)  # descrição dos achados, em português, texto próprio
    teaching_points: Mapped[str | None] = mapped_column(Text, nullable=True)

    file_path: Mapped[str] = mapped_column(String(500))  # caminho relativo em /static/galeria/
    thumbnail_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    source_name: Mapped[str] = mapped_column(String(200))  # ex.: "Wikimedia Commons"
    source_url: Mapped[str] = mapped_column(String(500))
    license: Mapped[str] = mapped_column(String(80))  # ex.: "CC BY-SA 4.0", "CC0", "Domínio público"
    attribution: Mapped[str] = mapped_column(Text)  # texto de crédito exigido pela licença

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
