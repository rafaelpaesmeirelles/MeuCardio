from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import NO_VALUE

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="medico")
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True, index=True)
    profession: Mapped[str | None] = mapped_column(String(80), nullable=True)
    council_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    council_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    council_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rqe: Mapped[str | None] = mapped_column(String(40), nullable=True)
    professional_title: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workplace_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_department: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_role: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    include_workplace_on_documents: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_completion_required: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crm: Mapped[str | None] = mapped_column(String(40), nullable=True)
    document_logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    home_street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    home_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    home_complement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    home_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    home_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)

    practice_street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    practice_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    practice_complement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    practice_neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    practice_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    practice_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    practice_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)
    practice_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="aprovado")
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    boas_vindas_pendente: Mapped[bool] = mapped_column(Boolean, default=False)

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    show_online_status: Mapped[bool] = mapped_column(Boolean, default=False)

    sessions_valid_after: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assinatura_metodo_preferido: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Consentimento específico para o assistente de IA acionar ferramentas
    # (agenda e CorvIA Mail do próprio médico) em vez de só responder texto.
    # Presença de `ia_ferramentas_consent_em` = consentiu; ausência = nunca
    # consentiu ou revogou. Mesmo padrão de MobilityPreference (versão +
    # timestamp), porque também é consentimento sobre ação automatizada
    # sobre dado real, não preferência de exibição.
    ia_ferramentas_consent_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ia_ferramentas_consent_versao: Mapped[str | None] = mapped_column(String(40), nullable=True)


@event.listens_for(User.password_hash, "set")
def _revogar_sessoes_ao_trocar_senha(target, value, oldvalue, initiator) -> None:
    if oldvalue is not NO_VALUE and oldvalue is not None and value != oldvalue:
        target.sessions_valid_after = datetime.now(timezone.utc)
