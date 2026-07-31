from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ChatMessage(Base):
    """Chat entre assinantes (Tarefa de 31/07/2026, pedido do Rafael).

    Sem tabela de "conversa" própria: um par (sender_id, recipient_id) já
    identifica a thread — uma consulta com OR nas duas direções recupera o
    histórico completo entre dois usuários. Simples o bastante para o volume
    esperado (chat 1:1 entre médicos), sem grupo nem broadcast.
    """

    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_par_conversa", "sender_id", "recipient_id", "created_at"),
        Index("ix_chat_messages_nao_lidas", "recipient_id", "read_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # None = não lida. Marcada quando o destinatário abre a conversa.
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
