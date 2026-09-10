from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ClinicalChangeProposal(Base):
    __tablename__ = "clinical_change_proposals"
    __table_args__ = (
        UniqueConstraint("guideline_id", "fingerprint", name="uq_clinical_proposal_source_payload"),
        CheckConstraint("status IN ('pending','approved','rejected')", name="ck_clinical_proposal_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    guideline_id: Mapped[int] = mapped_column(ForeignKey("guidelines.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    fingerprint: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(2000), nullable=True)
