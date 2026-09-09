"""Payment records survive chat deletion and retain their original price."""
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AICreditPurchase(Base):
    __tablename__ = "ai_credit_purchases"
    __table_args__ = (
        UniqueConstraint("user_id", "request_key", name="uq_ai_credit_purchase_request"),
        CheckConstraint("amount_centavos > 0", name="ck_ai_purchase_amount"),
        CheckConstraint("reversed_centavos >= 0 AND reversed_centavos <= amount_centavos", name="ck_ai_purchase_reversed"),
        CheckConstraint("refunded_centavos >= 0 AND refunded_centavos <= amount_centavos AND disputed_centavos >= 0 AND disputed_centavos <= amount_centavos", name="ck_ai_purchase_reversals"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    request_key: Mapped[str] = mapped_column(String(36))
    amount_centavos: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="brl")
    status: Mapped[str] = mapped_column(String(24), default="pending")
    checkout_session_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    payment_intent_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    checkout_url: Mapped[str | None] = mapped_column(String(2048))
    # Cumulative withdrawal prevents refund and dispute events double-debiting.
    reversed_centavos: Mapped[int] = mapped_column(Integer, default=0)
    refunded_centavos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    disputed_centavos: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    dispute_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    dispute_status: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
