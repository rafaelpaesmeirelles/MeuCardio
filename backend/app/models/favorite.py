from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Favorite(Base):
    """Referência pessoal a conteúdo acessível; nunca copia o conteúdo ou concede acesso."""

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "item_type", "item_id", name="uq_favorito_unico"),
        UniqueConstraint("user_id", "item_type", "item_slug", name="uq_favorito_slug_unico"),
        CheckConstraint("item_id IS NOT NULL OR item_slug IS NOT NULL", name="ck_favorito_identity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[str] = mapped_column(String(30))  # documento | medicamento | imagem | exame | evidencia | estudo
    item_id: Mapped[int | None] = mapped_column(nullable=True)
    item_slug: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
