from sqlalchemy import Numeric, String, Text
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
    dosing: Mapped[dict] = mapped_column(JSONB, default=dict)
    renal_adjustment: Mapped[str | None] = mapped_column(Text, nullable=True)
    hepatic_adjustment: Mapped[str | None] = mapped_column(Text, nullable=True)
    contraindications: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    interactions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    monitoring: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    pregnancy: Mapped[str | None] = mapped_column(Text, nullable=True)
    lactation: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcomes: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {"mortalidade": {...}, "hospitalizacao": {...}, "feve": {...}, "pa": {...}}
    cost_reference: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    half_life_hours: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    # Valor único representativo, escolhido por quem revisa a partir da bula/referência
    # farmacocinética. Faixas (ex.: "6-8h") viram o ponto médio ou o valor mais citado —
    # a decisão fica anotada em half_life_note, não escondida.
    half_life_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Redução de PA em dose padrão, sempre com a fonte junto — nunca preenchido
    # automaticamente. Referência sugerida: Wang N et al. Lancet. 2025;406:915-925
    # (padronizado para PAS basal de 154 mmHg) ou Law MR et al. BMJ. 2003;326:1427.
    sbp_reduction_mmhg: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    dbp_reduction_mmhg: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    bp_evidence_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    references: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    review_status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
