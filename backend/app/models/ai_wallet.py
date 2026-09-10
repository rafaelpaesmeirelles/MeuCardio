"""Persistent AI balances; deliberately independent of conversations/cases."""
from datetime import date, datetime, timezone

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def utcnow():
    return datetime.now(timezone.utc)


class AIWalletAccount(Base):
    __tablename__ = "ai_wallet_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    principal_key: Mapped[str] = mapped_column(String(120), unique=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    budget_credit_micros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    paid_credit_micros: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    paid_spent_micros: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    paid_reserved_micros: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    billing_blocked: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("paid_spent_micros >= 0 AND paid_reserved_micros >= 0", name="ck_ai_wallet_paid_nonnegative"),
                     CheckConstraint("budget_credit_micros IS NULL OR budget_credit_micros >= 0", name="ck_ai_wallet_budget_nonnegative"))


class AIWalletPeriod(Base):
    __tablename__ = "ai_wallet_periods"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("ai_wallet_accounts.id", ondelete="RESTRICT"), index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    pricing_version: Mapped[str] = mapped_column(String(80))
    markup_bps: Mapped[int] = mapped_column(BigInteger)
    grant_credit_micros: Mapped[int] = mapped_column(BigInteger)
    cost_ceiling_micros: Mapped[int] = mapped_column(BigInteger)
    spent_credit_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    reserved_credit_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    spent_cost_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    reserved_cost_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    paid_spent_credit_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    paid_reserved_credit_micros: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (
        UniqueConstraint("account_id", "period_start", name="uq_ai_wallet_account_period"),
        CheckConstraint("markup_bps >= 10000 AND grant_credit_micros >= 0 AND cost_ceiling_micros >= 0", name="ck_ai_wallet_period_limits"),
        CheckConstraint("spent_credit_micros >= 0 AND reserved_credit_micros >= 0 AND spent_cost_micros >= 0 AND reserved_cost_micros >= 0 AND paid_spent_credit_micros >= 0 AND paid_reserved_credit_micros >= 0", name="ck_ai_wallet_period_balances"),
    )


class AIWalletOperation(Base):
    __tablename__ = "ai_wallet_operations"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("ai_wallet_accounts.id", ondelete="RESTRICT"), index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("ai_wallet_periods.id", ondelete="RESTRICT"), index=True)
    operation_key: Mapped[str] = mapped_column(String(180))
    feature: Mapped[str] = mapped_column(String(80))
    cost_center: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_name: Mapped[str] = mapped_column(String(160))
    pricing_version: Mapped[str] = mapped_column(String(80))
    fingerprint: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(30), default="reserved")
    reserved_cost_micros: Mapped[int] = mapped_column(BigInteger)
    reserved_credit_micros: Mapped[int] = mapped_column(BigInteger)
    included_reserved_cost_micros: Mapped[int] = mapped_column(BigInteger)
    included_reserved_credit_micros: Mapped[int] = mapped_column(BigInteger)
    paid_reserved_credit_micros: Mapped[int] = mapped_column(BigInteger)
    actual_cost_micros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    actual_credit_micros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tokens_input: Mapped[int] = mapped_column(BigInteger, default=0)
    tokens_output: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        UniqueConstraint("account_id", "operation_key", name="uq_ai_wallet_operation_key"),
        CheckConstraint("state IN ('reserved','unknown','settled','released','settled_overrun')", name="ck_ai_wallet_operation_state"),
        CheckConstraint("reserved_cost_micros >= 0 AND reserved_credit_micros >= 0 AND included_reserved_cost_micros >= 0 AND included_reserved_credit_micros >= 0 AND paid_reserved_credit_micros >= 0", name="ck_ai_wallet_operation_reserved"),
        CheckConstraint("(actual_cost_micros IS NULL OR actual_cost_micros >= 0) AND (actual_credit_micros IS NULL OR actual_credit_micros >= 0) AND tokens_input >= 0 AND tokens_output >= 0", name="ck_ai_wallet_operation_actual"),
    )


class AIWalletCreditGrant(Base):
    __tablename__ = "ai_wallet_credit_grants"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("ai_wallet_accounts.id", ondelete="RESTRICT"), index=True)
    reference: Mapped[str] = mapped_column(String(180), unique=True)
    original_reference: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    credit_micros: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (CheckConstraint("credit_micros <> 0", name="ck_ai_wallet_grant_nonzero"),)
