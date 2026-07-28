from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="medico")  # admin|medico|residente|leitor
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- dados profissionais, coletados no cadastro (auto ou pelo admin) -----
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True, index=True)
    profession: Mapped[str | None] = mapped_column(String(80), nullable=True)
    council_name: Mapped[str | None] = mapped_column(String(20), nullable=True)  # CRM, COREN, CRF...
    council_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    council_state: Mapped[str | None] = mapped_column(String(2), nullable=True)  # UF, ex.: SP
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rqe: Mapped[str | None] = mapped_column(String(40), nullable=True)  # registro de qualificação de especialista
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crm: Mapped[str | None] = mapped_column(String(40), nullable=True)  # mantido por compatibilidade

    # --- fila de aprovação -----------------------------------------------
    status: Mapped[str] = mapped_column(String(20), default="aprovado")
    # pendente | aprovado | rejeitado — contas criadas pelo admin nascem aprovadas;
    # contas por autocadastro nascem pendentes e ficam inativas até um admin decidir.
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
