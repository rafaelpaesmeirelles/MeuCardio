from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Favorite(Base):
    """Um documento (ou outro item futuro) marcado como favorito por um usuário."""

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "item_type", "item_id", name="uq_favorito_unico"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[str] = mapped_column(String(30))  # documento | medicamento | imagem | exame | evidencia | estudo
    item_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
