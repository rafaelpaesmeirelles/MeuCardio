"""Curadoria do Modo Emergência (Tarefa 15).

**Este modelo não guarda conteúdo clínico.** Ele guarda uma seleção: qual
documento já publicado e já verificado entra no modo emergência, em que ordem,
e sob qual gatilho de reconhecimento. O texto continua vivendo em `documents`,
com uma cópia só — se o protocolo for corrigido lá, o modo emergência serve a
correção no mesmo instante, porque não tem texto próprio para envelhecer.

Foi a decisão de desenho mais importante da tarefa. A alternativa — copiar o
trecho crítico de cada protocolo para uma tabela própria, mais curta e mais
rápida de ler — criaria uma segunda versão do mesmo conteúdo clínico, que
divergiria da primeira na primeira correção que alguém fizesse. Numa tela usada
sob pressão, servir a versão desatualizada é o pior desfecho possível.

`gatilho` é o único texto próprio daqui, e é deliberadamente **não prescritivo**:
descreve o quadro que faz o médico abrir aquele protocolo, não o que fazer.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EmergencyProtocol(Base):
    __tablename__ = "emergency_protocols"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(300))
    # Sinal de reconhecimento — o que faz abrir este protocolo, não a conduta.
    gatilho: Mapped[str | None] = mapped_column(String(400), nullable=True)
    ordem: Mapped[int] = mapped_column(Integer, default=99, index=True)

    documento_slug: Mapped[str] = mapped_column(String(255), index=True)
    fluxograma_slug: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relacionados: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    review_status: Mapped[str] = mapped_column(String(40), default="pendente_revisao")
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
