from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class LabTest(Base):
    """Marcador laboratorial ou exame cardiológico (não-imagem — imagem fica
    na galeria). Ex.: troponina, BNP/NT-proBNP, D-dímero, teste ergométrico."""

    __tablename__ = "lab_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(80), index=True)
    # taxonomia fixa, não usar valor livre: laboratorial | metodo_grafico | imagem
    #   laboratorial   -> biomarcador de sangue/urina (troponina, NT-proBNP, D-dímero...)
    #   metodo_grafico -> exame que gera traçado/registro, sem imagem (ECG, teste
    #                     ergométrico, Holter, MAPA)
    #   imagem         -> exame que gera imagem (eco, TC, RM, radiografia,
    #                     cateterismo) — achado específico fica na Galeria; aqui é
    #                     sobre o exame em si (indicação, preparo, interpretação geral)

    what_it_measures: Mapped[str] = mapped_column(Text)
    reference_range: Mapped[str | None] = mapped_column(Text, nullable=True)
    indications: Mapped[str] = mapped_column(Text)
    interpretation: Mapped[str] = mapped_column(Text)
    limitations: Mapped[str | None] = mapped_column(Text, nullable=True)

    theme: Mapped[str] = mapped_column(String(80), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    source_refs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
