from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
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

    # --- conteúdo clínico do pedido ---------------------------------------
    duvida: Mapped[str | None] = mapped_column(Text, nullable=True)
    contato_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contato_whatsapp: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Nome do arquivo cifrado no cofre (UUID), não o nome original enviado.
    arquivo_exame: Mapped[str | None] = mapped_column(String(80), nullable=True)
    arquivo_nome_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
    arquivo_tipo: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Consentimento declarado pelo médico solicitante, conforme o TCLE. Guarda
    # o momento: "declarou" sem quando não serve de nada numa auditoria.
    consentimento_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- fila de atendimento ----------------------------------------------
    prazo_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    atendido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Quem respondeu. Hoje é sempre o Rafael, único com papel de admin, então
    # o campo parece redundante — e é exatamente por isso que precisa existir
    # antes do segundo respondente, e não depois. O painel de indicadores fala
    # em 'receita gerada' e 'meus laudos emitidos': sem este campo, esses
    # números não têm dono, e a primeira contratação de um segundo cardiologista
    # exigiria migrar dado histórico sem ter como saber quem fez o quê.
    respondido_por: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    # Resposta da consultoria (texto). O laudo assinado é outra coisa e só
    # existe depois da assinatura digital — ver Tarefa 4/5 do briefing.
    resposta: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ServiceOrderPatient(Base):
    """Dados do paciente, obrigatórios só quando o serviço é laudo assinado.

    Em tabela separada de propósito: a fila de atendimento e o histórico do
    solicitante consultam `service_orders` o tempo todo, e não há motivo para
    carregar nome e CPF de paciente em toda listagem. Separar reduz a
    superfície de exposição do dado mais sensível do sistema.
    """

    __tablename__ = "service_order_patient"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("service_orders.id", ondelete="CASCADE"), unique=True, index=True
    )
    nome: Mapped[str] = mapped_column(String(255))
    cpf: Mapped[str] = mapped_column(String(14))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
