from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ServiceOrder(Base):
    """Pedido avulso de laudo ou consultoria à distância.

    Esta tabela nasce cobrindo só a camada de cobrança (Tarefa 7 do briefing):
    o que foi pedido, quanto custa e se já foi pago. O conteúdo clínico do
    pedido — arquivo do exame, dados do paciente, consentimento, prazo de SLA e
    entrega do laudo — entra na Tarefa 5, sobre esta mesma tabela.

    A regra que amarra as duas: o pedido só entra na fila de atendimento depois
    que o webhook do Stripe confirma o pagamento. Por isso `status` nasce em
    `aguardando_pagamento` e nada além do webhook o move para `pago`.
    """

    __tablename__ = "service_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Vocabulário igual ao do protótipo `solicitar.html`, para o formulário da
    # Tarefa 5 não precisar traduzir nada.
    servico: Mapped[str] = mapped_column(String(20))    # consultoria | laudo
    urgencia: Mapped[str] = mapped_column(String(20))   # eletivo | urgente
    exame: Mapped[str | None] = mapped_column(String(20), nullable=True)  # ECG | Holter | MAPA | TE

    # Preço em centavos, sempre calculado no servidor a partir da combinação
    # serviço × urgência. Nunca vem do cliente — é o que impede alguém de
    # pedir um laudo urgente pagando o preço de consultoria eletiva.
    preco_centavos: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(30), default="aguardando_pagamento", index=True)
    # aguardando_pagamento | pago | cancelado
    # Os estados da fila de atendimento entram na Tarefa 5.

    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    pago_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
