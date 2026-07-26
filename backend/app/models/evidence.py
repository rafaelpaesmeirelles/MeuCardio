from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EvidenceRecord(Base):
    """Uma recomendação pontual, com classe/nível de evidência — não é o
    documento inteiro, é a afirmação específica que carrega essa força.
    Ex.: 'Sacubitril-valsartana é recomendado em vez de IECA em ICFEr
    sintomática — Classe I, Nível A'."""

    __tablename__ = "evidence_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    statement: Mapped[str] = mapped_column(Text)  # a recomendação em si, texto próprio
    recommendation_class: Mapped[str] = mapped_column(String(10))  # I | IIa | IIb | III
    evidence_level: Mapped[str] = mapped_column(String(5))  # A | B | C
    society: Mapped[str] = mapped_column(String(80))  # ESC | AHA/ACC | SBC | ...
    year: Mapped[int] = mapped_column()
    guideline_title: Mapped[str] = mapped_column(String(400))
    reference: Mapped[str] = mapped_column(Text)  # citação completa

    theme: Mapped[str] = mapped_column(String(80), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    document_slug: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # referência solta ao slug do documento relacionado na Biblioteca, se existir — sem FK
    # rígida porque documentos são geridos por arquivo, não é garantido que o slug já exista.

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
