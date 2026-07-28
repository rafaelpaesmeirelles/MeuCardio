from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DischargeChecklist(Base):
    """Modelo de checklist de alta, um por condição.

    Estruturado assim porque o briefing pede que dê para acrescentar checklist a
    um protocolo novo **sem redesenhar a funcionalidade**: a condição, os itens e
    a origem vivem em dado, não em código.

    `documento_origem` não é enfeite. Cada item carrega a seção do protocolo de
    onde veio, e é isso que permite responder "por que este item está aqui?" —
    além de tornar visível, quando o protocolo for revisado, que o checklist
    precisa acompanhar.
    """

    __tablename__ = "discharge_checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    condicao: Mapped[str] = mapped_column(String(200))
    resumo: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)

    documento_origem: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    itens: Mapped[list] = mapped_column(JSONB, default=list)
    # [{"id", "texto", "categoria", "obrigatorio", "origem_secao"}]
    source_refs: Mapped[list] = mapped_column(JSONB, default=list)

    review_status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DischargeChecklistRun(Base):
    """A aplicação do checklist a uma alta concreta.

    Separado do modelo porque são coisas diferentes: o modelo é conteúdo
    curado e versionado; isto é registro de trabalho de um médico com um
    paciente. Guardar a marcação dentro do modelo faria a revisão do conteúdo
    apagar o trabalho de quem estava usando.

    `itens_no_momento` copia os itens como estavam quando a alta foi preenchida.
    Sem isso, revisar o checklist reescreveria retroativamente o que foi
    conferido numa alta já dada — e o registro passaria a dizer que alguém
    marcou um item que ainda não existia.
    """

    __tablename__ = "discharge_checklist_runs"
    __table_args__ = (
        UniqueConstraint("checklist_id", "user_id", "patient_id", "finalizado_em",
                         name="uq_run_checklist"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("discharge_checklists.id"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    identificacao_livre: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Para quem usa o checklist sem ter o paciente cadastrado no Round. Texto
    # curto, de referência do próprio médico — não é prontuário.

    marcados: Mapped[list] = mapped_column(JSONB, default=list)   # ids de item
    itens_no_momento: Mapped[list] = mapped_column(JSONB, default=list)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    finalizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
