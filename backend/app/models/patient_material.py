"""Material educativo entregue ao paciente (Tarefa 12).

É conteúdo próprio, não um recorte do texto técnico. A diferença é de registro:
o documento da biblioteca é escrito para quem prescreve, este é escrito para
quem recebe a explicação — e reescrever é a única forma honesta de mudar de
registro, porque simplificar frase de diretriz costuma trocar precisão por
fluência sem avisar.

Duas regras estruturais, e as duas estão no banco, não só na prosa:

- **Nada de dose, conduta ou recomendação terapêutica individualizada.** O
  material explica a condição; o que fazer com ela é da consulta. O carregador
  recusa o registro que contenha padrão de posologia.
- **Vínculo declarado ao conteúdo técnico** (`documento_slug`), para que a
  explicação leiga e o documento que a sustenta envelheçam juntos. Sem esse
  vínculo, o material do paciente vira uma segunda base de conteúdo clínico
  sem revisão — que é exatamente o que o projeto passou meses removendo.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PatientMaterial(Base):
    __tablename__ = "patient_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(300))
    subtitulo: Mapped[str | None] = mapped_column(String(400), nullable=True)
    tema: Mapped[str] = mapped_column(String(80), index=True)

    # Slug do documento da biblioteca que sustenta esta explicação.
    documento_slug: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # [{"titulo": str, "paragrafos": [str], "itens": [str]}]
    secoes: Mapped[list] = mapped_column(JSONB, default=list)
    # Sinais de alarme: o que faz o paciente procurar atendimento sem esperar.
    sinais_de_alerta: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    # Perguntas que o paciente pode levar à próxima consulta.
    perguntas: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    fontes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    fonte_producao: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    resumo: Mapped[str | None] = mapped_column(Text, nullable=True)
