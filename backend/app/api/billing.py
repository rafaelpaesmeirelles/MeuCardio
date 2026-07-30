from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import ACESSO_LIBERADO, current_user
from app.models.subscription import (
    PLANO_BASICO, PLANO_COMPLETO, TIPO_CURSO, TIPO_EMAIL, TIPO_MEUCARDIO, Subscription,
)
from app.models.user import User

PLANOS_VALIDOS = {PLANO_BASICO, PLANO_COMPLETO}
# Preço do plano completo cobrado inline (price_data), no mesmo padrão já usado
# no checkout do CorvIA Mail avulso — evita depender de um segundo Price
# pré-criado no painel do Stripe só para este plano.
PRECO_COMPLETO_CENTAVOS = 3000

# O prefixo precisa incluir /api: o Caddy usa `handle /api/*` (que, ao contrário
# de `handle_path`, não remove o prefixo antes de repassar ao backend).
router = APIRouter(prefix="/api/billing", tags=["billing"])

stripe.api_key = settings.stripe_secret_key

# Tradução dos status do Stripe para o vocabulário em português usado no banco
# e na interface. Sem isso o valor cru em inglês vaza para a tela do assinante.
STATUS_STRIPE_PT = {
    "active": "ativo",
    "trialing": "teste",
    "past_due": "inadimplente",   # cobrança falhou, mas ainda em período de tolerância
    "unpaid": "suspenso",         # tolerância esgotada
    "canceled": "cancelado",
    "incomplete": "pendente",
    "incomplete_expired": "inativo",
    "paused": "pausado",
}


def traduzir_status(status_stripe: str) -> str:
    """Status desconhecido (Stripe pode introduzir novos) vira 'pendente' em vez
    de vazar o termo em inglês — pendente não libera acesso, que é o lado seguro."""
    return STATUS_STRIPE_PT.get(status_stripe, "pendente")


def _campo(objeto, chave, padrao=None):
    """Leitura tolerante a campo ausente em objeto do Stripe.

    Objeto do Stripe NÃO é dict: na versão 15 da lib, `.get()` levanta
    `AttributeError: get` — só subscrito e acesso por atributo funcionam, e o
    subscrito levanta KeyError quando o campo não veio. Este helper existe para
    não repetir esse erro, que já custou um 500 em produção no histórico de
    faturas e estava latente no webhook de assinatura."""
    return objeto[chave] if chave in objeto else padrao


def _fim_do_periodo(obj) -> datetime | None:
    """Desde a versão de API 2025-03-31.basil o current_period_end saiu do objeto
    Subscription e passou a viver em cada item da assinatura."""
    itens = _campo(_campo(obj, "items") or {}, "data") or []
    if not itens:
        return None
    fim = _campo(itens[0], "current_period_end")
    if not fim:
        return None
    return datetime.fromtimestamp(fim, tz=timezone.utc)


def _assinatura_meucardio(db: Session, user_id: int) -> Subscription | None:
    """A assinatura da plataforma, e só ela.

    Filtrar por `kind` deixou de ser opcional quando surgiram as assinaturas de
    curso parceiro: um médico passou a poder ter várias linhas, e um
    `filter(user_id == …).first()` devolveria qualquer uma delas. Aplicado a
    `/status` ou ao portal, isso mostraria ao médico o estado de um curso no
    lugar do estado da plataforma.
    """
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.kind == TIPO_MEUCARDIO)
        .order_by(Subscription.id)
        .first()
    )


def _obter_ou_criar_assinatura(db: Session, user: User) -> Subscription:
    sub = _assinatura_meucardio(db, user.id)
    if sub:
        return sub
    sub = Subscription(user_id=user.id, kind=TIPO_MEUCARDIO)
    db.add(sub)
    try:
        db.commit()
    except IntegrityError:
        # Duas chamadas simultâneas de /checkout: a que perdeu a corrida relê a
        # linha criada pela outra em vez de estourar 500 no índice parcial que
        # garante uma assinatura viva da plataforma por médico.
        db.rollback()
        sub = _assinatura_meucardio(db, user.id)
        if sub is None:
            raise
        return sub
    db.refresh(sub)
    return sub


def _assinatura_email(db: Session, user_id: int) -> Subscription | None:
    """A assinatura de CorvIA Mail (Tarefa 28), e só ela — mesmo cuidado de
    `_assinatura_meucardio`: sem filtrar por `kind`, `.first()` devolveria
    qualquer assinatura do médico, inclusive a da plataforma ou de um curso."""
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.kind == TIPO_EMAIL)
        .order_by(Subscription.id)
        .first()
    )


def _obter_ou_criar_assinatura_email(db: Session, user: User) -> Subscription:
    """Espelha `_obter_ou_criar_assinatura`, para o kind='email' — função
    própria em vez de generalizar a original: a original está em produção há
    meses sustentando a assinatura principal, e não vale o risco de alterar
    seu comportamento para acomodar um caminho novo."""
    sub = _assinatura_email(db, user.id)
    if sub:
        return sub
    sub = Subscription(user_id=user.id, kind=TIPO_EMAIL)
    db.add(sub)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        sub = _assinatura_email(db, user.id)
        if sub is None:
            raise
        return sub
    db.refresh(sub)
    return sub


def _aplicar_evento(db: Session, obj, quando: datetime, alteracoes) -> None:
    """Grava as alterações se o evento for mais novo que o último já aplicado.

    O Stripe reentrega eventos e não garante ordem de chegada, então um evento
    atrasado pode desfazer um estado mais recente (ex.: um cancelamento antigo
    chegando depois de uma reativação)."""
    # Casar pelo id da assinatura no Stripe, não pelo cliente. Um médico com a
    # plataforma e um curso parceiro tem **várias** linhas sob o mesmo
    # `stripe_customer_id`, e o `.first()` que existia aqui devolvia uma
    # qualquer: um evento de curso poderia sobrescrever o estado da assinatura
    # da plataforma, cancelando o acesso de um assinante pagante sem que
    # nenhuma requisição desse erro.
    sub = None
    id_assinatura = obj["id"] if "id" in obj else None
    if id_assinatura:
        sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == id_assinatura
        ).first()
    if sub is None:
        # Primeiro evento de uma assinatura ainda sem id gravado. O metadata diz
        # de qual das duas se trata; sem metadata, é a da plataforma, que é o
        # fluxo antigo e o único que existia antes dos cursos.
        # `.get()` NÃO funciona em objeto do Stripe — levanta AttributeError na
        # lib 15.x. É o mesmo erro que este projeto já documentou e corrigiu uma
        # vez, e que eu reintroduzi aqui ao escrever a discriminação por tipo:
        # como evento real do Stripe SEMPRE traz `metadata`, todo primeiro evento
        # de assinatura nova estourava 500 — ou seja, nenhuma assinatura nova
        # chegaria a ativar. Usar o helper `_campo`, que é para isto.
        metadata = _campo(obj, "metadata") or {}
        tipo_assinatura = _campo(metadata, "tipo")
        consulta = db.query(Subscription).filter(
            Subscription.stripe_customer_id == obj["customer"]
        )
        if tipo_assinatura == "curso":
            curso_id = _campo(metadata, "curso_id")
            consulta = consulta.filter(
                Subscription.kind == TIPO_CURSO,
                Subscription.course_id == (int(curso_id) if curso_id else None),
            )
        elif tipo_assinatura == "email":
            # Sem este ramo, o primeiro evento de uma assinatura de CorvIA
            # Mail cairia no `else` abaixo e seria tratado como assinatura da
            # PLATAFORMA — corrompendo o estado de quem já é assinante do
            # MeuCardio e comprou o e-mail depois. É o mesmo bug que o
            # CLAUDE.md já documenta ter acontecido com `mode` em vez de
            # metadata para os pedidos avulsos de telediagnóstico.
            consulta = consulta.filter(Subscription.kind == TIPO_EMAIL)
        else:
            consulta = consulta.filter(Subscription.kind == TIPO_MEUCARDIO)
        sub = consulta.order_by(Subscription.id.desc()).first()
    if sub is None:
        return
    if sub.last_event_at is not None and quando < sub.last_event_at:
        return
    alteracoes(sub)
    sub.last_event_at = quando
    db.commit()
    if sub.kind == TIPO_EMAIL:
        _sincronizar_caixa_de_email(db, sub)


def _sincronizar_caixa_de_email(db: Session, sub: Subscription) -> None:
    """Quando a assinatura de CorvIA Mail muda de estado (cancelamento,
    inadimplência, reativação), a caixa em `email_accounts` precisa
    acompanhar — senão um médico que cancelou continua lendo e-mail de
    graça, sem que a assinatura vencida bloqueie nada."""
    from app.models.email_account import EmailAccount

    conta = db.query(EmailAccount).filter(EmailAccount.user_id == sub.user_id).first()
    if not conta:
        return
    novo_status = "ativa" if sub.status in ACESSO_LIBERADO else "suspensa"
    if conta.status != novo_status:
        conta.status = novo_status
        db.commit()


@router.post("/checkout")
def criar_checkout(
    plano: str = Query(PLANO_BASICO),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if plano not in PLANOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Plano inválido.")

    sub = _obter_ou_criar_assinatura(db, user)

    if sub.status in ACESSO_LIBERADO:
        raise HTTPException(
            status_code=409,
            detail="Você já tem uma assinatura ativa. Para trocar de plano, cancele a atual pelo portal de assinatura e assine o novo plano.",
        )

    if not sub.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.full_name)
        sub.stripe_customer_id = customer["id"]

    # Gravado aqui, não deduzido do webhook: o webhook só confirma status e
    # data de renovação, quem decide o plano é esta chamada, antes de existir
    # qualquer evento do Stripe para esta assinatura.
    sub.plano = plano
    db.commit()

    if plano == PLANO_COMPLETO:
        line_items = [{
            "price_data": {
                "currency": "brl",
                "unit_amount": PRECO_COMPLETO_CENTAVOS,
                "recurring": {"interval": "month"},
                "product_data": {"name": "Corvia — Acesso Completo à Plataforma + CorvIA Mail"},
            },
            "quantity": 1,
        }]
    else:
        line_items = [{"price": settings.stripe_price_id, "quantity": 1}]

    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=line_items,
        subscription_data={"metadata": {"tipo": "meucardio", "plano": plano, "user_id": str(user.id)}},
        success_url=f"{settings.public_url}/assinatura?status=sucesso",
        cancel_url=f"{settings.public_url}/assinatura?status=cancelado",
    )
    return {"checkout_url": session["url"]}


@router.get("/status-email")
def status_email(db: Session = Depends(get_db), user: User = Depends(current_user)):
    sub = _assinatura_email(db, user.id)
    if sub and sub.status in ACESSO_LIBERADO:
        return {
            "status": sub.status, "current_period_end": sub.current_period_end,
            "preco_definido": settings.corvia_mail_preco_definido,
            "preco_centavos": settings.corvia_mail_preco_centavos,
            "incluido_no_plano": False,
        }

    # Sem add-on avulso ativo — mas o plano completo já inclui CorvIA Mail.
    # Sem esta checagem, quem pagou o plano completo veria "Assinar o CorvIA
    # Mail" na tela, e um clique nele seria recusado pelo checkout (409).
    principal = _assinatura_meucardio(db, user.id)
    if principal and principal.status in ACESSO_LIBERADO and principal.plano == PLANO_COMPLETO:
        return {
            "status": principal.status, "current_period_end": principal.current_period_end,
            "preco_definido": settings.corvia_mail_preco_definido,
            "preco_centavos": settings.corvia_mail_preco_centavos,
            "incluido_no_plano": True,
        }

    return {
        "status": sub.status if sub else "inativo",
        "current_period_end": sub.current_period_end if sub else None,
        "preco_definido": settings.corvia_mail_preco_definido,
        "preco_centavos": settings.corvia_mail_preco_centavos,
        "incluido_no_plano": False,
    }


@router.post("/checkout-email")
def criar_checkout_email(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Checkout do CorvIA Mail — add-on cobrado à parte da assinatura
    principal (decisão do Rafael, 30/07/2026). Preço inline (`price_data`),
    não um Price pré-criado no painel: enquanto `corvia_mail_preco_centavos`
    for 0 ("em branco"), a rota recusa em vez de cobrar um valor inventado —
    nunca simular um preço que ainda não foi decidido."""
    if not settings.corvia_mail_preco_definido:
        raise HTTPException(
            status_code=409,
            detail="O preço do CorvIA Mail ainda não foi definido. Assinatura indisponível no momento.",
        )

    principal = _assinatura_meucardio(db, user.id)
    if principal and principal.status in ACESSO_LIBERADO and principal.plano == PLANO_COMPLETO:
        raise HTTPException(
            status_code=409,
            detail="Seu plano atual (Acesso Completo + CorvIA Mail) já inclui o CorvIA Mail — não é preciso assinar separadamente.",
        )

    sub = _obter_ou_criar_assinatura_email(db, user)
    if sub.status in ACESSO_LIBERADO:
        raise HTTPException(status_code=409, detail="Você já assina o CorvIA Mail.")

    # Reaproveita o cliente Stripe da assinatura principal quando existir —
    # dois clientes para a mesma pessoa quebram o portal de cobrança e o
    # histórico de faturas (mesmo cuidado já tomado nos cursos parceiros).
    if not sub.stripe_customer_id:
        principal = _assinatura_meucardio(db, user.id)
        sub.stripe_customer_id = (
            principal.stripe_customer_id if principal and principal.stripe_customer_id
            else stripe.Customer.create(email=user.email, name=user.full_name)["id"]
        )
        db.commit()

    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode="subscription",
        # Pedido do Rafael em 30/07/2026: cobrar em Pix OU cartão. Pix
        # recorrente no Stripe (Pix Automático) exige mandate_options com
        # amount_type="fixed" — sem isso, o padrão é "maximum" (um TETO de
        # cobrança variável, não o valor fixo mensal que queremos). O mandato
        # do Pix leva alguns dias pra ser autorizado pelo banco do assinante
        # antes da primeira cobrança recorrente valer — diferente do cartão,
        # que cobra na hora. Depende também de o Pix estar habilitado nas
        # configurações de pagamento da conta Stripe (fora do código).
        payment_method_types=["card", "pix"],
        payment_method_options={
            "pix": {
                "mandate_options": {
                    "amount_type": "fixed",
                    "amount": settings.corvia_mail_preco_centavos,
                    "payment_schedule": "monthly",
                    "reference": "CorvIA Mail",
                },
            },
        },
        line_items=[{
            "price_data": {
                "currency": "brl",
                "unit_amount": settings.corvia_mail_preco_centavos,
                "recurring": {"interval": "month"},
                "product_data": {"name": "CorvIA Mail"},
            },
            "quantity": 1,
        }],
        subscription_data={"metadata": {"tipo": "email", "user_id": str(user.id)}},
        # O metadata da sessão e o da assinatura são campos diferentes; o
        # webhook de customer.subscription.* só enxerga o da assinatura.
        metadata={"tipo": "email", "user_id": str(user.id)},
        success_url=f"{settings.public_url}/corvia-mail?status=sucesso",
        cancel_url=f"{settings.public_url}/corvia-mail?status=cancelado",
    )
    return {"checkout_url": session["url"]}


def _customer_id_do_usuario(db: Session, user_id: int) -> str | None:
    """O primeiro `stripe_customer_id` não nulo entre as assinaturas do
    médico — plataforma, CorvIA Mail ou curso, nessa ordem.

    Existe porque `abrir_portal`/`listar_faturas` olhavam só para
    `_assinatura_meucardio`: um médico que assina SÓ o CorvIA Mail (o
    add-on foi desenhado em 30/07/2026 para não depender da assinatura
    principal — ver Tarefa 28) nunca teria `sub.stripe_customer_id` ali, e
    o botão "Gerenciar assinatura" da Minha Conta devolvia 404 sempre,
    mesmo com uma assinatura de e-mail paga e ativa. `criar_checkout_email`
    já reaproveita o cliente Stripe da assinatura principal quando ela
    existe, então na prática quem tem as duas continua caindo no mesmo
    `customer_id` — o portal do Stripe lista todas as assinaturas ativas de
    um cliente na mesma tela, então um único portal já basta para gerenciar
    as duas."""
    for kind in (TIPO_MEUCARDIO, TIPO_EMAIL, TIPO_CURSO):
        sub = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id, Subscription.kind == kind,
                Subscription.stripe_customer_id.isnot(None),
            )
            .order_by(Subscription.id)
            .first()
        )
        if sub:
            return sub.stripe_customer_id
    return None


@router.post("/portal")
def abrir_portal(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Customer Portal do Stripe: é por ele que o assinante troca o cartão,
    baixa recibo e cancela. Diferente do Checkout, que só serve pra assinar."""
    customer_id = _customer_id_do_usuario(db, user.id)
    if not customer_id:
        raise HTTPException(
            status_code=404,
            detail="Você ainda não tem uma assinatura para gerenciar.",
        )
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.public_url}/minha-conta",
        )
    except stripe.error.InvalidRequestError:
        # Caso clássico: o portal ainda não teve as configurações salvas no
        # painel do Stripe. É erro de configuração nossa, não do assinante.
        raise HTTPException(
            status_code=503,
            detail="O portal de assinatura está indisponível no momento. Tente novamente mais tarde.",
        )
    return {"portal_url": session["url"]}


@router.get("/faturas")
def listar_faturas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Histórico de cobranças. Lê direto do Stripe em vez de espelhar faturas no
    banco: o Stripe é a fonte da verdade sobre cobrança, e espelhar criaria uma
    segunda versão que sai de sincronia no primeiro estorno ou ajuste."""
    customer_id = _customer_id_do_usuario(db, user.id)
    if not customer_id:
        return {"faturas": []}

    try:
        faturas = stripe.Invoice.list(customer=customer_id, limit=24)
    except stripe.error.StripeError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível consultar o histórico de cobranças agora.",
        )

    return {
        "faturas": [
            {
                "id": f["id"],
                "numero": _campo(f, "number"),
                "status": _campo(f, "status"),
                "total_centavos": _campo(f, "total"),
                "moeda": (_campo(f, "currency") or "brl").upper(),
                "criada_em": datetime.fromtimestamp(_campo(f, "created"), tz=timezone.utc)
                if _campo(f, "created") else None,
                "url_fatura": _campo(f, "hosted_invoice_url"),
                "url_pdf": _campo(f, "invoice_pdf"),
            }
            for f in faturas["data"]
        ]
    }


@router.get("/status")
def status_assinatura(db: Session = Depends(get_db), user: User = Depends(current_user)):
    sub = _assinatura_meucardio(db, user.id)
    if not sub:
        return {"status": "inativo", "current_period_end": None, "plano": None}
    return {"status": sub.status, "current_period_end": sub.current_period_end, "plano": sub.plano}


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Tenta cada secret configurado. Durante a migração de domínio há dois
    # endpoints ativos no Stripe, um por domínio, com secrets distintos — validar
    # contra um só faria todo evento do outro voltar 400, e o Stripe reenfileira
    # sem que nada aqui acuse o problema.
    event = None
    for secret in settings.stripe_webhook_secrets:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
            break
        except (ValueError, stripe.error.SignatureVerificationError):
            continue
    if event is None:
        raise HTTPException(status_code=400, detail="Assinatura de webhook inválida.")

    tipo = event["type"]
    obj = event["data"]["object"]
    quando = datetime.fromtimestamp(event["created"], tz=timezone.utc)

    if tipo in ("customer.subscription.created", "customer.subscription.updated"):
        def alterar(sub):
            sub.stripe_subscription_id = obj["id"]
            sub.status = traduzir_status(obj["status"])
            fim = _fim_do_periodo(obj)
            if fim is not None:
                sub.current_period_end = fim

        _aplicar_evento(db, obj, quando, alterar)

    elif tipo == "customer.subscription.deleted":
        _aplicar_evento(db, obj, quando, lambda sub: setattr(sub, "status", "cancelado"))

    elif tipo == "invoice.payment_failed":
        _aplicar_evento(db, obj, quando, lambda sub: setattr(sub, "status", "inadimplente"))

    elif tipo == "invoice.payment_succeeded":
        # Cada fatura paga de assinatura de curso vira um registro com bruto,
        # repasse e margem separados. Registrar no pagamento, e não calcular
        # depois a partir do curso, e o que permite que preco e margem mudem sem
        # reescrever o historico financeiro ja fechado.
        from app.api.partner_courses import registrar_pagamento

        registrar_pagamento(db, obj)

    elif tipo == "checkout.session.completed":
        # A mesma rota recebe os dois fluxos de cobrança. O `mode` separa:
        # `subscription` já é tratado pelos eventos de customer.subscription,
        # então aqui só interessa `payment`, que é o pedido avulso de laudo ou
        # consultoria. Sem esse filtro, uma assinatura nova cairia no caminho
        # do pedido e não acharia nenhum ServiceOrder.
        if _campo(obj, "mode") == "payment":
            from app.api.service_orders import confirmar_pagamento

            confirmar_pagamento(db, obj)

    return {"received": True}
