from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

TIPO_MEUCARDIO = "meucardio"
TIPO_CURSO = "curso"
TIPO_EMAIL = "email"  # CorvIA Mail (Tarefa 28) — add-on cobrado à parte, não substitui a assinatura principal

PLANO_BASICO = "basico"     # R$49,90/mês, acesso completo à plataforma, sem CorvIA Mail
PLANO_COMPLETO = "completo"  # R$59,90/mês, acesso completo à plataforma + CorvIA Mail incluso

# Periodicidade da assinatura principal (kind=meucardio) — mensal já existia
# implicitamente; semestral/anual pedidos pelo Rafael em 08/08/2026, com
# valores fixos por plano+periodicidade definidos em app/api/billing.py.
# Não se aplica a kind=email (add-on é sempre mensal) nem kind=curso.
PERIODICIDADE_MENSAL = "mensal"
PERIODICIDADE_SEMESTRAL = "semestral"
PERIODICIDADE_ANUAL = "anual"


class Subscription(Base):
    __tablename__ = "subscriptions"

    # `user_id` era `unique=True`, o que impunha **uma assinatura por médico** no
    # nível do banco. Isso impedia o modelo de cursos parceiros, em que o médico
    # pode ter a assinatura do MeuCardio e mais uma por curso. A unicidade não
    # foi jogada fora, foi movida para onde ela de fato vale: o índice parcial
    # abaixo garante uma única assinatura viva por par médico/curso, e uma única
    # assinatura viva do próprio MeuCardio por médico. Sem esse índice, uma
    # dupla submissão do checkout criaria duas cobranças para a mesma coisa.
    __table_args__ = (
        Index(
            "uq_assinatura_meucardio_por_usuario",
            "user_id",
            unique=True,
            postgresql_where=text("kind = 'meucardio' AND status <> 'cancelado'"),
        ),
        Index(
            "uq_assinatura_curso_por_usuario",
            "user_id",
            "course_id",
            unique=True,
            postgresql_where=text("kind = 'curso' AND status <> 'cancelado'"),
        ),
        # Mesma lógica da assinatura do MeuCardio: uma única assinatura viva de
        # CorvIA Mail por médico. Sem isso, dupla submissão do checkout de
        # e-mail criaria duas cobranças para o mesmo add-on.
        Index(
            "uq_assinatura_email_por_usuario",
            "user_id",
            unique=True,
            postgresql_where=text("kind = 'email' AND status <> 'cancelado'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Discrimina o que está sendo assinado. Antes existia uma linha só por
    # médico e o tipo era implícito; com curso parceiro isso deixou de valer.
    kind: Mapped[str] = mapped_column(String(20), default=TIPO_MEUCARDIO, index=True)
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("partner_courses.id"), nullable=True, index=True
    )
    # Só tem sentido para kind='meucardio' — nas linhas de curso e de CorvIA
    # Mail o campo existe (coluna única na tabela) mas não é lido.
    plano: Mapped[str] = mapped_column(String(20), default=PLANO_BASICO)
    # Idem: só tem sentido para kind='meucardio'. Migração 26751b9d12f0.
    periodicidade: Mapped[str] = mapped_column(String(20), default=PERIODICIDADE_MENSAL)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="inativo")
    # inativo | ativo | teste | pendente | inadimplente | suspenso | cancelado | pausado
    # Traduzido dos status do Stripe em app/api/billing.py (STATUS_STRIPE_PT);
    # quais deles liberam acesso está em app/core/security.py (ACESSO_LIBERADO).
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Momento do último evento de webhook já aplicado, para descartar evento
    # atrasado que sobrescreveria um estado mais novo.
    last_event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
