from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    entity: Mapped[str] = mapped_column(String(80))
    # 255 para acompanhar `documents.slug`, que e String(255). Enquanto isto era
    # String(80), qualquer documento com slug mais longo quebrava a rota de
    # publicacao com 500 na hora de gravar a auditoria — o `doc.published` ja
    # tinha sido alterado, a transacao inteira revertia, e 16 documentos do
    # acervo simplesmente nao podiam ser publicados nem despublicados.
    entity_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detail: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
