from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ClinicalCase(Base):
    """Caso clínico interativo (Tarefa 11a).

    Formato fixo, pensado para decisão única e comparável entre casos: um
    enunciado, uma pergunta, um conjunto de opções e uma explicação que cita a
    evidência por trás da conduta correta — nunca a conduta sem a fonte que a
    sustenta, mesmo regra de todo o resto do conteúdo clínico deste produto.

    Não modela caso ramificado (múltiplas decisões em sequência): a Tarefa 11a
    descreve "um caso, a sua decisão, e depois a conduta correta" — um único
    ponto de decisão por caso. Um formato ramificado pode vir depois, como
    extensão, não como redesenho deste.
    """

    __tablename__ = "clinical_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    tema: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    nivel: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # básico | intermediário | avançado — dificuldade declarada, não calculada

    enunciado: Mapped[str] = mapped_column(Text)          # markdown, o caso em si
    pergunta: Mapped[str] = mapped_column(Text)            # a decisão a tomar
    opcoes: Mapped[list] = mapped_column(JSONB, default=list)   # ["texto opção 1", ...]
    resposta_correta: Mapped[int] = mapped_column(Integer)      # índice em `opcoes`
    explicacao: Mapped[str] = mapped_column(Text)          # markdown, por que a resposta certa é certa

    source_refs: Mapped[list] = mapped_column(JSONB, default=list)

    review_status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
    revisao: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ClinicalCaseAttempt(Base):
    """Uma resposta de um médico a um caso.

    Histórico completo (sem chave única por médico+caso): o mesmo caso pode ser
    refeito, e cada tentativa fica registrada — é o que Indicadores soma para
    mostrar taxa de acerto ao longo do tempo, não só o resultado mais recente.
    """

    __tablename__ = "clinical_case_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("clinical_cases.id", ondelete="CASCADE"), index=True)
    opcao_escolhida: Mapped[int] = mapped_column(Integer)
    acertou: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
