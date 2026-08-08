from datetime import datetime, timedelta, timezone

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import ACESSO_LIBERADO, current_user
from app.models.audit import AuditLog
from app.models.subscription import (
    PLANO_BASICO, PLANO_COMPLETO, TIPO_CURSO, TIPO_EMAIL, TIPO_MEUCARDIO, Subscription,
)
from app.models.user import User
from app.services import emails

PLANOS_VALIDOS = {PLANO_BASICO, PLANO_COMPLETO}
# Preço do plano completo cobrado inline (price_data), no mesmo padrão já usado
# no checkout do CorvIA Mail avulso — evita depender de um segundo Price
# pré-criado no painel do Stripe só para este plano.
PRECO_COMPLETO_CENTAVOS = 5990
# Preço do plano básico — hoje vem de um Price pré-criado no Stripe
# (`settings.stripe_price_id`), não de um valor inline como o completo. O
# valor abaixo é só para compor o e-mail de boas-vindas/confirmação sem uma
# chamada extra à API do Stripe a cada assinatura nova; é o mesmo R$49,90
# documentado em CLAUDE.md e cobrado no painel do Stripe.
PRECO_BASICO_CENTAVOS = 4990
PLANOS_NOME = {PLANO_BASICO: "Assinatura Básica", PLANO_COMPLETO: "Assinatura Completa"}

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


def _aplicar_evento(db: Session, obj, quando: datetime, alteracoes) -> Subscription | None:
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
        return None
    if sub.last_event_at is not None and quando < sub.last_event_at:
        return None
    alteracoes(sub)
    sub.last_event_at = quando
    db.commit()
    if sub.kind == TIPO_EMAIL:
        _sincronizar_caixa_de_email(db, sub)
    return sub


def _inferir_plano_do_objeto(obj) -> str | None:
    """Lê o valor cobrado no primeiro item da assinatura do Stripe e infere
    qual dos dois planos da plataforma é. Best-effort: usado só para detectar
    troca de plano numa assinatura já existente (e-mail de "alteração de
    plano") — se não der para ler o valor, simplesmente não dispara o e-mail,
    nunca adivinha. Como só existem dois planos hoje, comparar contra o valor
    conhecido do Completo já resolve o caso — se um terceiro plano existir um
    dia, esta função precisa ser refeita, não só estendida."""
    itens = _campo(_campo(obj, "items") or {}, "data") or []
    if not itens:
        return None
    price = _campo(itens[0], "price") or {}
    valor = _campo(price, "unit_amount")
    if valor is None:
        return None
    return PLANO_COMPLETO if valor == PRECO_COMPLETO_CENTAVOS else PLANO_BASICO


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

    if user.convidado:
        # Médico convidado (08/08/2026, pedido do Rafael) — mesma tela,
        # mesmo botão "Assinar", mas sem Stripe: a assinatura é liberada
        # direto no banco, sempre no plano Completo (é o que "acesso
        # completo" promete, inclusive CorvIA Mail — que já é incluído sem
        # add-on separado quando `plano == PLANO_COMPLETO`, ver
        # `status_email` mais abaixo). Nunca cria `stripe_customer_id`: sem
        # cliente Stripe, `/billing/portal` e `/billing/faturas` já
        # respondem "sem assinatura para gerenciar"/lista vazia, em vez de
        # tentar falar com uma API que não tem nada para mostrar.
        sub.plano = PLANO_COMPLETO
        sub.status = "ativo"
        db.add(AuditLog(
            user_id=user.id, action="liberar_acesso_convidado", entity="subscription",
            entity_id=str(sub.id), detail={"email": user.email, "plano": PLANO_COMPLETO},
        ))
        db.commit()
        return {
            "checkout_url": None,
            "convidado": True,
            "mensagem": "Médico Convidado — Acesso Completo Liberado.",
        }

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
                "product_data": {"name": "Corvia — Assinatura Completa (Acesso ao Site + CorvIA Mail)"},
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
    # Admin sempre com acesso, mesmo skip do Stripe — mesmo bypass de
    # `assinatura_email_ativa` (core/security.py), aqui refletido na resposta
    # que a tela usa pra decidir entre mostrar "Assinar" ou o formulário de
    # ativação. Decisão do Rafael em 31/07/2026.
    if user.role == "admin":
        return {
            "status": "ativo", "current_period_end": None,
            "preco_definido": settings.corvia_mail_preco_definido,
            "preco_centavos": settings.corvia_mail_preco_centavos,
            "incluido_no_plano": True,
        }

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
            detail="Seu plano atual (Assinatura Completa) já inclui o CorvIA Mail — não é preciso assinar separadamente.",
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


def _ultimos4_da_fatura(invoice_id: str | None) -> str:
    """Best-effort: o payload do webhook não traz os 4 últimos dígitos do
    cartão por padrão, então busca a fatura expandida. Nunca fabrica o
    valor — qualquer falha (fatura sem cartão, Pix, erro de rede) devolve
    "----", que o template já trata como "não disponível", em vez de
    inventar um número."""
    if not invoice_id:
        return "----"
    try:
        fatura = stripe.Invoice.retrieve(invoice_id, expand=["charge.payment_method_details"])
        charge = _campo(fatura, "charge")
        if not charge:
            return "----"
        detalhes = _campo(charge, "payment_method_details") or {}
        cartao = _campo(detalhes, "card") or {}
        return _campo(cartao, "last4") or "----"
    except Exception:  # noqa: BLE001
        return "----"


@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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

    # Todos os disparos de e-mail abaixo usam BackgroundTasks: a resposta ao
    # Stripe não espera o SMTP, e cada função de `emails.py` abre a própria
    # sessão de banco (não `db` desta rota — ver o comentário no topo de
    # `app/services/emails.py`).
    if tipo in ("customer.subscription.created", "customer.subscription.updated"):
        estado_antes: dict = {}

        def alterar(sub):
            estado_antes["era_nova"] = sub.stripe_subscription_id is None
            estado_antes["status_anterior"] = sub.status
            estado_antes["plano_anterior"] = sub.plano
            sub.stripe_subscription_id = obj["id"]
            sub.status = traduzir_status(obj["status"])
            fim = _fim_do_periodo(obj)
            if fim is not None:
                sub.current_period_end = fim
            if sub.kind == TIPO_MEUCARDIO:
                novo_plano = _inferir_plano_do_objeto(obj)
                if novo_plano:
                    sub.plano = novo_plano

        sub = _aplicar_evento(db, obj, quando, alterar)

        if sub is not None and sub.kind == TIPO_MEUCARDIO and estado_antes:
            era_nova = estado_antes["era_nova"]
            status_anterior = estado_antes["status_anterior"]
            plano_anterior = estado_antes["plano_anterior"]
            valor_do_plano = PRECO_COMPLETO_CENTAVOS if sub.plano == PLANO_COMPLETO else PRECO_BASICO_CENTAVOS

            if era_nova and tipo == "customer.subscription.created":
                background_tasks.add_task(
                    emails.enviar_boas_vindas, sub.user_id, sub.plano, valor_do_plano, sub.current_period_end,
                )
            elif not era_nova and plano_anterior != sub.plano:
                background_tasks.add_task(
                    emails.enviar_alteracao_plano, sub.user_id, plano_anterior, sub.plano,
                    valor_do_plano, sub.current_period_end or quando,
                )

            if not era_nova and status_anterior != "suspenso" and sub.status == "suspenso":
                dados_ate = (sub.current_period_end or quando) + timedelta(
                    days=emails.RETENCAO_DIAS_APOS_CANCELAMENTO
                )
                background_tasks.add_task(
                    emails.enviar_assinatura_suspensa, sub.user_id, dados_ate,
                    f"assinatura_suspensa:{sub.id}:{quando.date().isoformat()}",
                )

    elif tipo == "customer.subscription.deleted":
        sub = _aplicar_evento(db, obj, quando, lambda s: setattr(s, "status", "cancelado"))
        if sub is not None and sub.kind == TIPO_MEUCARDIO:
            tinha_mail = sub.plano == PLANO_COMPLETO or (
                db.query(Subscription)
                .filter(
                    Subscription.user_id == sub.user_id, Subscription.kind == TIPO_EMAIL,
                    Subscription.status.in_(ACESSO_LIBERADO),
                )
                .first()
                is not None
            )
            background_tasks.add_task(
                emails.enviar_assinatura_cancelada, sub.user_id, sub.current_period_end or quando, tinha_mail,
            )

    elif tipo == "invoice.payment_failed":
        estado_antes = {}

        def marcar_inadimplente(s):
            estado_antes["status_anterior"] = s.status
            s.status = "inadimplente"

        sub = _aplicar_evento(db, obj, quando, marcar_inadimplente)
        if (
            sub is not None and sub.kind == TIPO_MEUCARDIO
            and estado_antes.get("status_anterior") != "inadimplente"
        ):
            # Só a PRIMEIRA falha desta assinatura dispara o e-mail. As
            # tentativas seguintes seguem a cadência configurada no painel
            # do Stripe (smart retries); replicar dia-a-dia aqui exigiria
            # guardar a data-limite original em algum lugar, e não há coluna
            # para isso nesta primeira versão — documentado, não fabricado.
            data_limite = quando + timedelta(days=emails.PRAZO_TENTATIVAS_DIAS)
            background_tasks.add_task(
                emails.enviar_pagamento_falhou, sub.user_id, emails.PRAZO_TENTATIVAS_DIAS,
                data_limite, f"{settings.public_url}/minha-conta",
                f"pagamento_falhou:{_campo(obj, 'id')}",
            )

    elif tipo == "invoice.payment_succeeded":
        # Cada fatura paga de assinatura de curso vira um registro com bruto,
        # repasse e margem separados. Registrar no pagamento, e não calcular
        # depois a partir do curso, e o que permite que preco e margem mudem sem
        # reescrever o historico financeiro ja fechado.
        from app.api.partner_courses import registrar_pagamento

        registrar_pagamento(db, obj)

        id_assinatura_fatura = _campo(obj, "subscription")
        if id_assinatura_fatura:
            sub = (
                db.query(Subscription)
                .filter(Subscription.stripe_subscription_id == id_assinatura_fatura)
                .first()
            )
            if sub is not None and sub.kind in (TIPO_MEUCARDIO, TIPO_EMAIL):
                linha = (_campo(_campo(obj, "lines") or {}, "data") or [{}])[0]
                periodo = _campo(linha, "period") or {}
                inicio_ts, fim_ts = _campo(periodo, "start"), _campo(periodo, "end")
                periodo_inicio = datetime.fromtimestamp(inicio_ts, tz=timezone.utc) if inicio_ts else quando
                periodo_fim = datetime.fromtimestamp(fim_ts, tz=timezone.utc) if fim_ts else quando
                plano_nome = PLANOS_NOME.get(sub.plano, "Assinatura") if sub.kind == TIPO_MEUCARDIO else "CorvIA Mail"
                background_tasks.add_task(
                    emails.enviar_pagamento_confirmado, sub.user_id, _campo(obj, "amount_paid") or 0, quando,
                    plano_nome, periodo_inicio, periodo_fim, _ultimos4_da_fatura(_campo(obj, "id")),
                    f"{settings.public_url}/minha-conta", f"pagamento_confirmado:{_campo(obj, 'id')}",
                )

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


@router.post("/verificar-retencao")
def verificar_retencao(db: Session = Depends(get_db), admin: User = Depends(current_user)):
    """Item 10 do spec de e-mails transacionais: aviso adicional no 25º dia
    de retenção de uma assinatura suspensa (5 dias antes da exclusão
    definitiva). Não há agendador embutido no projeto — este endpoint serve
    tanto a chamada manual do admin quanto um cron externo diário (mesmo
    padrão já documentado no CLAUDE.md para a atualização mensal da CMED: um
    único caminho de código, chamado das duas formas)."""
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Só administradores.")

    agora = datetime.now(timezone.utc)
    limite = agora - timedelta(days=emails.RETENCAO_DIAS_APOS_CANCELAMENTO - 5)
    candidatas = (
        db.query(Subscription)
        .filter(
            Subscription.kind == TIPO_MEUCARDIO, Subscription.status == "suspenso",
            Subscription.last_event_at.isnot(None), Subscription.last_event_at <= limite,
        )
        .all()
    )

    avisos_enviados = 0
    for sub in candidatas:
        dias_desde_suspensao = (agora - sub.last_event_at).days
        dias_restantes = max(emails.RETENCAO_DIAS_APOS_CANCELAMENTO - dias_desde_suspensao, 0)
        chave = f"aviso_exclusao:{sub.id}:{sub.last_event_at.date().isoformat()}"
        if emails.enviar_assinatura_suspensa_aviso_exclusao(sub.user_id, dias_restantes, chave):
            avisos_enviados += 1

    return {"assinaturas_verificadas": len(candidatas), "avisos_enviados": avisos_enviados}
