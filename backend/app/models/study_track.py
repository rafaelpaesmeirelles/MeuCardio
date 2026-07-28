from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class StudyTrack(Base):
    """Trilha de estudo: sequência guiada de conteúdo que já existe.

    A Tarefa 11b é explícita em que isto é **curadoria, não conteúdo novo**. O
    que a trilha acrescenta não é texto — é ordem e justificativa: cada etapa
    diz por que vem naquele ponto. Sem o `por_que`, uma trilha é só uma lista de
    links, e o médico não tem motivo para seguir a ordem proposta em vez de ler
    o que quiser.
    """

    __tablename__ = "study_tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    tema: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    objetivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    nivel: Mapped[str | None] = mapped_column(String(30), nullable=True)

    etapas: Mapped[list] = mapped_column(JSONB, default=list)
    # [{"ordem", "item_type", "item_slug", "por_que"}]

    review_status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
    revisao: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class StudyTrackProgress(Base):
    """Onde cada médico parou em cada trilha.

    Guarda a etapa concluída pelo `item_slug`, e não pela posição na lista: se a
    trilha for reordenada ou ganhar uma etapa no meio, o progresso continua
    apontando para o que a pessoa de fato leu. Guardar por índice faria uma
    curadoria futura reescrever o histórico de quem já estudou.
    """

    __tablename__ = "study_track_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "track_id", name="uq_progresso_trilha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("study_tracks.id", ondelete="CASCADE"), index=True)
    concluidas: Mapped[list] = mapped_column(JSONB, default=list)   # item_slug das etapas
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
