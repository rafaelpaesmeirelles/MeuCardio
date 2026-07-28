"""Painel de indicadores pessoais (Tarefa 10).

Agregação sobre dado que já existe — fila de atendimento, `service_orders` e os
pagamentos confirmados pelo Stripe. Nada aqui captura informação nova.

Regra que atravessa o arquivo inteiro: **cada médico vê apenas os próprios
números**. Não há parâmetro de usuário em nenhuma rota; o recorte sai sempre do
token. Um `?user_id=` aqui seria a forma mais fácil de transformar um painel
pessoal em vigilância de produtividade alheia.
"""

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.service_order import ServiceOrder
from app.models.user import User

router = APIRouter(prefix="/api/indicadores", tags=["indicadores"])


def _janela(dias: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=dias)


def _horas(inicio: datetime | None, fim: datetime | None) -> float | None:
    if not inicio or not fim:
        return None
    return round((fim - inicio).total_seconds() / 3600, 1)


@router.get("/meus")
def meus_indicadores(
    dias: int = Query(30, ge=1, le=365, description="janela em dias"),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    """Atividade do próprio médico na janela pedida.

    Devolve duas seções, e cada uma só aparece se fizer sentido para quem
    pergunta:

    - **como solicitante**: pedidos que ele abriu, o que gastou e se o prazo
      prometido foi cumprido com ele;
    - **como respondente**: o que ele atendeu, o tempo médio contra o SLA e a
      receita que gerou.

    A segunda seção existe para quem responde pedidos. Enquanto houver um único
    respondente, ela é o painel do Rafael — mas o recorte é por
    `respondido_por`, não por papel de admin, para que o número continue certo
    quando existir um segundo cardiologista.
    """
    desde = _janela(dias)

    # ---------------------------------------------------------- solicitante
    meus = db.query(ServiceOrder).filter(
        ServiceOrder.user_id == user.id, ServiceOrder.created_at >= desde
    ).all()
    pagos = [p for p in meus if p.pago_em is not None]
    atendidos_para_mim = [p for p in pagos if p.atendido_em is not None]

    prazos_cumpridos = sum(
        1 for p in atendidos_para_mim if p.prazo_em and p.atendido_em <= p.prazo_em
    )
    solicitante = {
        "pedidos_abertos": len(meus),
        "pedidos_pagos": len(pagos),
        "pedidos_atendidos": len(atendidos_para_mim),
        "aguardando": len([p for p in pagos if p.atendido_em is None]),
        "gasto_centavos": sum(p.preco_centavos for p in pagos),
        "prazo_cumprido": prazos_cumpridos,
        "prazo_estourado": len(atendidos_para_mim) - prazos_cumpridos,
        "por_servico": _contar(meus, "servico"),
        "por_urgencia": _contar(meus, "urgencia"),
    }

    # ---------------------------------------------------------- respondente
    respondidos = db.query(ServiceOrder).filter(
        ServiceOrder.respondido_por == user.id, ServiceOrder.atendido_em >= desde
    ).all()

    tempos = [h for h in (_horas(p.pago_em, p.atendido_em) for p in respondidos) if h is not None]
    dentro = sum(1 for p in respondidos if p.prazo_em and p.atendido_em <= p.prazo_em)
    folgas = [
        round((p.prazo_em - p.atendido_em).total_seconds() / 3600, 1)
        for p in respondidos if p.prazo_em and p.atendido_em
    ]

    respondente = {
        "atendidos": len(respondidos),
        "por_servico": _contar(respondidos, "servico"),
        "por_urgencia": _contar(respondidos, "urgencia"),
        "por_exame": _contar(respondidos, "exame"),
        "tempo_medio_resposta_horas": round(sum(tempos) / len(tempos), 1) if tempos else None,
        "tempo_maior_resposta_horas": max(tempos) if tempos else None,
        "dentro_do_prazo": dentro,
        "fora_do_prazo": len(respondidos) - dentro,
        "folga_mediana_horas": _mediana(folgas),
        "receita_centavos": sum(p.preco_centavos for p in respondidos),
        "fila_aberta_agora": db.query(func.count(ServiceOrder.id)).filter(
            ServiceOrder.pago_em.isnot(None), ServiceOrder.atendido_em.is_(None)
        ).scalar() or 0,
    }

    return {
        "janela_dias": dias,
        "desde": desde.date().isoformat(),
        "ate": date.today().isoformat(),
        "como_solicitante": solicitante,
        "como_respondente": respondente,
        "notas": [
            "O tempo de resposta conta do pagamento confirmado até o atendimento, "
            "que é como o prazo do serviço é definido — não da criação do pedido.",
            "Receita é o valor cobrado dos pedidos que você atendeu no período. "
            "Não desconta taxa do Stripe nem imposto.",
            "Pedidos atendidos antes de existir o registro de quem respondeu não "
            "aparecem em 'como respondente' — o campo passou a ser gravado a partir "
            "da Tarefa 10 e não foi retroagido, porque não havia como saber.",
        ],
    }


def _contar(pedidos: list[ServiceOrder], campo: str) -> dict:
    saida: dict[str, int] = {}
    for p in pedidos:
        chave = getattr(p, campo) or "não informado"
        saida[chave] = saida.get(chave, 0) + 1
    return dict(sorted(saida.items(), key=lambda x: -x[1]))


def _mediana(valores: list[float]) -> float | None:
    """Mediana, não média, para a folga de prazo: um único atendimento muito
    adiantado distorce a média e faz parecer que há folga onde não há."""
    if not valores:
        return None
    v = sorted(valores)
    meio = len(v) // 2
    return v[meio] if len(v) % 2 else round((v[meio - 1] + v[meio]) / 2, 1)
