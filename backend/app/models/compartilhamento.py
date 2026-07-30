"""Link de acesso público a PDF clínico — Tarefa 29 (30/07/2026).

Arquivo próprio, separado de `receituario.py`: embora o primeiro uso seja
para receita, o modelo é deliberadamente genérico (também serve documento
gerado a partir de modelo, `generated_documents`) — não é conceito do
domínio de receituário (Portaria 344/98), é infraestrutura compartilhada.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.password_reset import gerar_token


class DocumentShareLink(Base):
    """Link de acesso público e temporário a um PDF clínico (receita ou
    documento gerado a partir de modelo). Decisão do Rafael em 30/07/2026:
    o e-mail ao paciente leva só este link, nunca o PDF anexado — o
    conteúdo clínico nunca passa pela infraestrutura de terceiro (Zoho), só
    a notificação neutra ("seu médico disponibilizou um documento") vai por
    e-mail, pelo SMTP da própria Corvia.

    `tipo`/`referencia_id` seguem o padrão genérico já usado em
    `AuditLog.entity`/`entity_id`, em vez de duas FKs opcionais — evita abrir
    a discussão de referência polimórfica que o RAG já registrou como
    decisão de esquema cara (CLAUDE.md, item 7 de "Trabalho novo").
    `tipo` vale "prescription_document" ou "generated_document".

    Não é uso único de propósito: um paciente pode querer abrir o PDF mais
    de uma vez (celular, depois computador). Quem controla o acesso é só a
    validade (`expires_at`) — token de alta entropia (32 bytes) é a única
    defesa, então a validade curta importa mais do que reuso único.
    """

    __tablename__ = "document_share_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=gerar_token)
    tipo: Mapped[str] = mapped_column(String(30), index=True)
    referencia_id: Mapped[int] = mapped_column(Integer, index=True)
    criado_por: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    primeiro_acesso_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acessos: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
