"""Pedidos avulsos: laudo e consultoria à distância (pagamento único).

Separado de app/api/billing.py de propósito. São duas naturezas de cobrança
diferentes: billing cuida da assinatura recorrente do MeuCardio, aqui é
pagamento único por pedido, com preço variável. Misturar os dois num fluxo só
levaria a `mode` condicional espalhado pelo código.
"""

from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.service_order import ServiceOrder
from app.models.user import User

router = APIRouter(prefix="/api/pedidos", tags=["pedidos"])

stripe.api_key = settings.stripe_secret_key

SERVICOS = {"consultoria": "Consultoria", "laudo": "Laudo completo assinado"}
URGENCIAS = {"eletivo": "Eletivo (até 12h)", "urgente": "Urgente/Plantão (até 2h)"}
EXAMES = {"ECG": "Eletrocardiograma", "Holter": "Holter 24h", "MAPA": "MAPA",
          "TE": "Teste ergométrico"}

# Tabela de preços em centavos. Fonte única da verdade, no servidor: o cliente
# escolhe a combinação, nunca o valor.
PRECOS_CENTAVOS = {
    ("consultoria", "eletivo"): 4000,
    ("consultoria", "urgente"): 6000,
    ("laudo", "eletivo"): 7000,
    ("laudo", "urgente"): 10000,
}


def preco_de(servico: str, urgencia: str) -> int:
    try:
        return PRECOS_CENTAVOS[(servico, urgencia)]
    except KeyError:
        raise HTTPException(status_code=422, detail="Combinação de serviço e urgência inválida.")


def _dump(p: ServiceOrder) -> dict:
    return {
        "id": p.id,
        "servico": p.servico,
        "servico_rotulo": SERVICOS.get(p.servico, p.servico),
        "urgencia": p.urgencia,
        "urgencia_rotulo": URGENCIAS.get(p.urgencia, p.urgencia),
        "exame": p.exame,
        "preco_centavos": p.preco_centavos,
        "status": p.status,
        "pago_em": p.pago_em,
        "created_at": p.created_at,
    }


@router.get("/precos")
def tabela_de_precos():
    """A interface monta a tabela a partir daqui, em vez de repetir os valores
    no frontend — preço duplicado é preço que sai de sincronia."""
    return {
        "precos": [
            {
                "servico": s, "servico_rotulo": SERVICOS[s],
                "urgencia": u, "urgencia_rotulo": URGENCIAS[u],
                "preco_centavos": valor,
            }
            for (s, u), valor in PRECOS_CENTAVOS.items()
        ],
        "exames_aceitos": [{"codigo": c, "rotulo": r} for c, r in EXAMES.items()],
    }


class NovoPedido(BaseModel):
    servico: str
    urgencia: str
    exame: str | None = None

    @field_validator("servico")
    @classmethod
    def _servico(cls, v: str) -> str:
        if v not in SERVICOS:
            raise ValueError("Serviço inválido.")
        return v

    @field_validator("urgencia")
    @classmethod
    def _urgencia(cls, v: str) -> str:
        if v not in URGENCIAS:
            raise ValueError("Urgência inválida.")
        return v

    @field_validator("exame")
    @classmethod
    def _exame(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if v not in EXAMES:
            raise ValueError("Exame fora do escopo aceito nesta fase.")
        return v


@router.post("/checkout", status_code=201)
def criar_pedido_e_checkout(
    dados: NovoPedido,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    valor = preco_de(dados.servico, dados.urgencia)

    pedido = ServiceOrder(
        user_id=user.id, servico=dados.servico, urgencia=dados.urgencia,
        exame=dados.exame, preco_centavos=valor, status="aguardando_pagamento",
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)

    descricao = f"{SERVICOS[dados.servico]} — {URGENCIAS[dados.urgencia]}"
    if dados.exame:
        descricao += f" — {EXAMES[dados.exame]}"

    try:
        sessao = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "quantity": 1,
                # price_data em vez de produto fixo no Stripe: são quatro
                # combinações e o valor pode mudar; criar produto para cada uma
                # exigiria manter catálogo em dois lugares.
                "price_data": {
                    "currency": "brl",
                    "unit_amount": valor,
                    "product_data": {"name": "MeuCardio — Telediagnóstico",
                                     "description": descricao},
                },
            }],
            customer_email=user.email,
            # O id do pedido volta no webhook: é o que liga o pagamento ao
            # registro no banco sem depender de e-mail nem de ordem de eventos.
            metadata={"pedido_id": str(pedido.id)},
            success_url=f"{settings.public_url}/telediagnostico?pedido={pedido.id}&status=sucesso",
            cancel_url=f"{settings.public_url}/telediagnostico?pedido={pedido.id}&status=cancelado",
        )
    except stripe.error.StripeError:
        # Sem sessão de pagamento o pedido não serve para nada e viraria lixo
        # em "aguardando_pagamento" para sempre.
        db.delete(pedido)
        db.commit()
        raise HTTPException(status_code=503,
                            detail="Não foi possível iniciar o pagamento agora. Tente novamente.")

    pedido.stripe_checkout_session_id = sessao["id"]
    db.commit()
    db.refresh(pedido)

    return {"pedido": _dump(pedido), "checkout_url": sessao["url"]}


@router.get("")
def listar_meus_pedidos(db: Session = Depends(get_db), user: User = Depends(current_user)):
    pedidos = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.user_id == user.id)
        .order_by(ServiceOrder.created_at.desc())
        .all()
    )
    return {"pedidos": [_dump(p) for p in pedidos]}


@router.get("/{pedido_id}")
def ver_pedido(pedido_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    pedido = db.get(ServiceOrder, pedido_id)
    if not pedido or (pedido.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return _dump(pedido)


@router.post("/{pedido_id}/reconciliar")
def reconciliar(pedido_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Rede de segurança para webhook perdido: consulta a sessão no Stripe e
    confirma o pagamento se ele de fato ocorreu.

    Não substitui o webhook — a fonte da verdade continua sendo o Stripe, e não
    o cliente, que aqui só informa qual pedido conferir. Existe porque webhook
    é entrega assíncrona: pode falhar, atrasar ou não estar configurado para o
    modo em uso, e nesse caso um pagamento real ficaria preso em
    `aguardando_pagamento` sem ninguém perceber."""
    pedido = db.get(ServiceOrder, pedido_id)
    if not pedido or (pedido.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if pedido.status == "pago":
        return _dump(pedido)
    if not pedido.stripe_checkout_session_id:
        raise HTTPException(status_code=409, detail="Pedido sem sessão de pagamento.")

    try:
        sessao = stripe.checkout.Session.retrieve(pedido.stripe_checkout_session_id)
    except stripe.error.StripeError:
        raise HTTPException(status_code=503, detail="Não foi possível consultar o pagamento agora.")

    from app.api.billing import _campo

    if _campo(sessao, "payment_status") == "paid":
        confirmar_pagamento(db, sessao)
        db.refresh(pedido)
    return _dump(pedido)


def confirmar_pagamento(db: Session, sessao) -> None:
    """Chamado pelo webhook de billing quando chega checkout.session.completed
    de uma sessão em modo `payment`. Idempotente: o Stripe reentrega eventos, e
    marcar duas vezes não pode duplicar nada nem reabrir prazo."""
    from app.api.billing import _campo

    pedido_id = _campo(_campo(sessao, "metadata") or {}, "pedido_id")
    pedido = db.get(ServiceOrder, int(pedido_id)) if pedido_id else None
    if pedido is None:
        pedido = (
            db.query(ServiceOrder)
            .filter(ServiceOrder.stripe_checkout_session_id == _campo(sessao, "id"))
            .first()
        )
    if pedido is None or pedido.status == "pago":
        return

    pedido.status = "pago"
    pedido.pago_em = datetime.now(timezone.utc)
    intent = _campo(sessao, "payment_intent")
    if isinstance(intent, str):
        pedido.stripe_payment_intent_id = intent
    db.commit()
