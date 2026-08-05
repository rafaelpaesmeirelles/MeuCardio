from sqlalchemy import Boolean, Float, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Drug(Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    generic_name: Mapped[str] = mapped_column(String(200), index=True)
    brand_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    drug_class: Mapped[str] = mapped_column(String(120), index=True)
    mechanism: Mapped[str | None] = mapped_column(Text, nullable=True)
    presentations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    commercial_presentations: Mapped[list] = mapped_column(JSONB, default=list)
    dosing: Mapped[dict] = mapped_column(JSONB, default=dict)
    renal_adjustment: Mapped[str | None] = mapped_column(Text, nullable=True)
    hepatic_adjustment: Mapped[str | None] = mapped_column(Text, nullable=True)
    contraindications: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    interactions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    monitoring: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    indications: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    adverse_effects: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    notes: Mapped[dict] = mapped_column(JSONB, default=dict)
    pregnancy: Mapped[str | None] = mapped_column(Text, nullable=True)
    lactation: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcomes: Mapped[dict] = mapped_column(JSONB, default=dict)
    cost_reference: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    half_life_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    half_life_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_of_action_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_of_action_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_of_action_source: Mapped[str | None] = mapped_column(String(500), nullable=True)

    sbp_reduction_mmhg: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    dbp_reduction_mmhg: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    bp_evidence_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    references: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    review_status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
