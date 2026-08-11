"""Fonte única de verdade sobre acesso ao produto — issue #52, frente de
entitlement de convidados/investidores.

Antes desta função existir, três lugares reimplementavam a mesma pergunta
("este usuário tem acesso pago?") de forma independente e inconsistente:
`assinante_ativo()` (app/core/security.py, o gate central aplicado por
router em app/main.py), `_kyc_required()` e `_onboarding_pendente()`
(app/api/auth.py). Nenhuma das três olhava `User.convidado` — o bypass de
cobrança do convidado vivia só dentro de `criar_checkout()`
(app/api/billing.py), que só roda quando o usuário visita a tela de
Assinatura e clica "Assinar". Um convidado marcado pelo admin que nunca
clicasse era barrado com 402 como um visitante sem conta — bug real,
reportado com a conta `drmarciopeixoto@corvia.med.br`.

Regra: qualquer decisão de "este usuário pode usar o produto sem pagar"
passa por aqui. Não duplicar esta checagem em nenhum outro arquivo.
"""
from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Import direto, não lazy: confirmado (11/08/2026) que app/core/security.py
# não importa este módulo em nível de topo — só dentro do corpo de
# `assinante_ativo()`, em runtime — então não há ciclo de import aqui.
from app.core.security import current_user

ACESSO_LIBERADO = {"ativo", "teste", "inadimplente"}


def tem_acesso_ao_produto(db: Session, user) -> bool:
    """True se o usuário pode usar o produto sem cobrança pendente —
    admin, assinatura paga em dia, convidado ou investidor administrativo.

    Conta desativada nunca passa daqui — na prática isso já é garantido
    antes, porque `usuario_por_token_app()` só resolve usuário com
    `is_active=True`; a checagem aqui é defensiva, para o caso de esta
    função ser chamada a partir de um contexto que não passou por lá.
    """
    if not getattr(user, "is_active", True):
        return False
    if user.role == "admin":
        return True
    if user.convidado or user.investidor:
        return True

    from app.models.subscription import Subscription

    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.kind == "meucardio")
        .order_by(Subscription.id)
        .first()
    )
    return sub is not None and sub.status in ACESSO_LIBERADO


def acesso_administrativo_sem_pagamento(user) -> bool:
    """True quando o acesso do usuário vem de concessão administrativa
    (convidado ou investidor) — não admin, não assinatura paga.

    Uso restrito: só para decidir o que EXIBIR nas telas de assinatura
    ("Acesso concedido administrativamente" em vez de "Assine agora").
    Nunca usar isto como gate de rota — para isso, `tem_acesso_ao_produto`.
    """
    return bool(getattr(user, "is_active", True) and (user.convidado or user.investidor))


# --------------------------------------------------------------------------
# CorvIA Mail — modo demonstração do investidor (issue #52, complemento
# "INVESTIDOR NO CORVIA MAIL")
# --------------------------------------------------------------------------
#
# Regra definitiva, que distingue as duas concessões administrativas:
# CONVIDADO tem CorvIA Mail real e completo — enviar, receber, responder,
# encaminhar, anexo, sincronização, exatamente como assinante pago (ver
# `assinatura_email_ativa()` em app/core/security.py, que concede o add-on
# de e-mail a convidado sem depender de checkout). INVESTIDOR só pode
# NAVEGAR a interface, com conteúdo sintético — nenhuma operação real.
#
# Este bloqueio é aplicado SÓ a investidor, nunca a convidado. É a fonte
# única de verdade no backend: o frontend também desabilita os mesmos
# botões, mas o 403 aqui é o que realmente impede a operação.

MENSAGEM_MODO_INVESTIDOR = "Recurso indisponível no modo investidor."


def bloquear_investidor_em_operacao_real_de_mail(user=Depends(current_user)):
    """Dependency de rota — substitui `Depends(current_user)` em toda rota
    que executa uma operação REAL de e-mail: provisionar caixa, logar na
    sessão da caixa, conectar conta externa (Yahoo/Google/Microsoft/Apple),
    enviar, responder, encaminhar, sincronizar, renovar token. 403 para
    investidor; devolve o usuário normalmente para qualquer outro caso
    (admin, assinante, convidado)."""
    if getattr(user, "investidor", False):
        raise HTTPException(status_code=403, detail=MENSAGEM_MODO_INVESTIDOR)
    return user


def investidor_em_modo_demonstracao(user) -> bool:
    """True quando a interface do CorvIA Mail deve mostrar dado sintético em
    vez de consultar caixa real — hoje, só investidor. Convidado nunca cai
    aqui, porque tem caixa real."""
    return bool(getattr(user, "investidor", False))
