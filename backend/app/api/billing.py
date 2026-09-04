from datetime import datetime, timedelta, timezone

import logging
import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import ACESSO_LIBERADO, current_user
from app.models.audit import AuditLog
from app.models.subscription import (
    PERIODICIDADE_ANUAL, PERIODICIDADE_MENSAL, PERIODICIDADE_SEMESTRAL,
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

PERIODICIDADES_VALIDAS = {PERIODICIDADE_MENSAL, PERIODICIDADE_SEMESTRAL, PERIODICIDADE_ANUAL}
ROTULO_PERIODICIDADE = {
    PERIODICIDADE_MENSAL: "mês", PERIODICIDADE_SEMESTRAL: "6 meses", PERIODICIDADE_ANUAL: "ano",
}
# Valores fixos por plano+periodicidade, confirmados pelo Rafael em
# 08/08/2026 (mensal sem mudança de valor). Única fonte de verdade sobre
# preço no servidor — o cliente nunca envia valor, só plano+periodicidade,
# e é este dicionário que resolve o centavo, aqui e no e-mail transacional.
PRECO_CENTAVOS = {
    (PLANO_BASICO, PERIODICIDADE_MENSAL): PRECO_BASICO_CENTAVOS,
    (PLANO_BASICO, PERIODICIDADE_SEMESTRAL): 26990,
    (PLANO_BASICO, PERIODICIDADE_ANUAL): 47990,
    (PLANO_COMPLETO, PERIODICIDADE_MENSAL): PRECO_COMPLETO_CENTAVOS,
    (PLANO_COMPLETO, PERIODICIDADE_SEMESTRAL): 32390,
    (PLANO_COMPLETO, PERIODICIDADE_ANUAL): 57590,
}
# Reverso de PRECO_CENTAVOS, usado para inferir o plano a partir do valor
# cobrado que o Stripe confirma no webhook (nunca dos parâmetros que o
# cliente mandou no clique) — chave única porque os seis valores são todos
# distintos entre si.
PLANO_DO_VALOR_CENTAVOS = {v: k[0] for k, v in PRECO_CENTAVOS.items()}

# O prefixo precisa incluir /api: o Caddy usa `handle /api/*` (que, ao contrário
# de `handle_path`, não remove o prefixo antes de repassar ao backend).
router = APIRouter(prefix="/api/billing", tags=["billing"])

stripe.api_key = settings.stripe_secret_key
log = logging.getLogger("meucardio.billing")

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


def _periodicidade_do_price(price) -> str:
    """A partir do `recurring` do Price confirmado pelo Stripe — nunca do que
    o cliente pediu no checkout. `interval_count` só existe nos Prices
    semestrais/anuais criados para esta tarefa; um Price antigo (mensal, sem
    o campo ou com valor 1) cai no `else`, que é o comportamento real de
    100% das assinaturas de antes desta funcionalidade."""
    recurring = _campo(price, "recurring") or {}
    interval = _campo(recurring, "interval")
    interval_count = _campo(recurring, "interval_count") or 1
    if interval == "year":
        return PERIODICIDADE_ANUAL
    if interval == "month" and interval_count and interval_count >= 6:
        return PERIODICIDADE_SEMESTRAL
    return PERIODICIDADE_MENSAL


def _inferir_plano_periodicidade_do_objeto(obj) -> tuple[str | None, str | None]:
    """Lê o valor cobrado e a recorrência do primeiro item da assinatura do
    Stripe e infere plano+periodicidade — nunca do que o cliente pediu no
    checkout ou na troca de plano, só do que o Stripe confirma. Usado tanto
    no evento de assinatura criada/atualizada quanto para reconciliar uma
    troca de plano/periodicidade feita via `stripe.Subscription.modify(...)`
    (endpoint `/trocar-plano`) — a mesma disciplina de "nunca aplicar
    localmente antes da confirmação" que o resto deste arquivo já segue.
    Best-effort: se não der para ler o valor, não adivinha, devolve None."""
    itens = _campo(_campo(obj, "items") or {}, "data") or []
    if not itens:
        return None, None
    price = _campo(itens[0], "price") or {}
    valor = _campo(price, "unit_amount")
    if valor is None:
        return None, None
    plano = PLANO_DO_VALOR_CENTAVOS.get(valor)
    if plano is None:
        return None, None
    return plano, _periodicidade_do_price(price)


def _item_de_preco(plano: str, periodicidade: str) -> dict:
    """Resolve o item de linha (Price existente ou `price_data` inline) para
    um plano+periodicidade — usado tanto no checkout quanto na troca de
    plano de uma assinatura ativa, para não ter duas fontes de verdade sobre
    preço. Nunca aceita preço vindo do cliente: os seis pontos possíveis
    (2 planos × 3 periodicidades) são todos resolvidos aqui, a partir de
    PRECO_CENTAVOS/settings — o cliente só escolhe QUAL dos seis, nunca o
    valor.

    Levanta 503 se a periodicidade pedida ainda não tiver Price configurado
    no `.env` — nunca inventa um price_data com o valor de PRECO_CENTAVOS
    para semestral/anual: o pedido original foi explícito em pedir Price
    OBJECTS de verdade para esses dois, criados uma vez via API, não preço
    inline recriado a cada chamada."""
    if periodicidade == PERIODICIDADE_MENSAL:
        if plano == PLANO_COMPLETO:
            return {
                "price_data": {
                    "currency": "brl",
                    "unit_amount": PRECO_COMPLETO_CENTAVOS,
                    "recurring": {"interval": "month"},
                    "product_data": {"name": "Corvia — Assinatura Completa (Acesso ao Site + CorvIA Mail)"},
                },
            }
        return {"price": settings.stripe_price_id}

    price_id = {
        (PLANO_BASICO, PERIODICIDADE_SEMESTRAL): settings.stripe_price_id_basico_semestral,
        (PLANO_BASICO, PERIODICIDADE_ANUAL): settings.stripe_price_id_basico_anual,
        (PLANO_COMPLETO, PERIODICIDADE_SEMESTRAL): settings.stripe_price_id_completo_semestral,
        (PLANO_COMPLETO, PERIODICIDADE_ANUAL): settings.stripe_price_id_completo_anual,
    }.get((plano, periodicidade))
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail=(
                f"O plano {PLANOS_NOME.get(plano, plano)} a cada {ROTULO_PERIODICIDADE[periodicidade]} "
                "ainda não está disponível para assinatura."
            ),
        )
    return {"price": price_id}


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



def _exigir_assinaturas_habilitadas() -> None:
    if not settings.subscriptions_enabled:
        raise HTTPException(
            status_code=503,
            detail="Assinaturas temporariamente indisponíveis. Conheça o CorVIA no tour.",
        )


@router.post("/checkout")
def criar_checkout(
    plano: str = Query(PLANO_BASICO),
    periodicidade: str = Query(PERIODICIDADE_MENSAL),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    _exigir_assinaturas_habilitadas()
    if plano not in PLANOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Plano inválido.")
    if periodicidade not in PERIODICIDADES_VALIDAS:
        raise HTTPException(status_code=400, detail="Periodicidade inválida.")

    sub = _obter_ou_criar_assinatura(db, user)

    if sub.status in ACESSO_LIBERADO:
        raise HTTPException(
            status_code=409,
            detail=(
                "Você já tem uma assinatura ativa. Para trocar de plano ou periodicidade, use "
                "\"Trocar plano\" na tela de Assinatura, ou cancele pelo portal de assinatura e "
                "assine de novo."
            ),
        )

    if user.investidor:
        # Investidor (issue #52) — nunca precisa passar por aqui, o acesso
        # já é concedido por `tem_acesso_ao_produto()` só pelo flag. Ao
        # contrário do convidado abaixo, deliberadamente NÃO marca
        # `sub.status = "ativo"`: investidor não deve aparecer como
        # assinante em nenhuma métrica que consulte `Subscription.status`,
        # mesmo sem cobrança real. `sub` já existe (criado, pendente, por
        # `_obter_ou_criar_assinatura` acima) mas fica intocado.
        return {
            "checkout_url": None,
            "investidor": True,
            "mensagem": "Acesso concedido administrativamente — não é necessário assinar.",
        }

    if user.convidado:
        # Médico convidado (08/08/2026, pedido do Rafael) — mesma tela,
        # mesmo botão "Assinar", mas sem Stripe: a assinatura é liberada
        # direto no banco. Plano: `convidado_plano_preferido`, escolhido
        # pelo admin na pré-autorização (08/08/2026 — "escolher também se o
        # convidado terá acesso ou não ao CorviaMail"); `None` (convidado
        # marcado direto pelo admin via toggle, sem pré-autorização) cai no
        # padrão PLANO_COMPLETO de sempre, sem mudança de comportamento.
        # CorvIA Mail já é incluído sem add-on separado quando
        # `plano == PLANO_COMPLETO`, ver `status_email` mais abaixo. Nunca
        # cria `stripe_customer_id`: sem cliente Stripe, `/billing/portal` e
        # `/billing/faturas` já respondem "sem assinatura para gerenciar"/
        # lista vazia, em vez de tentar falar com uma API que não tem nada
        # para mostrar.
        plano_convidado = user.convidado_plano_preferido or PLANO_COMPLETO
        sub.plano = plano_convidado
        sub.status = "ativo"
        db.add(AuditLog(
            user_id=user.id, action="liberar_acesso_convidado", entity="subscription",
            entity_id=str(sub.id), detail={"email": user.email, "plano": plano_convidado},
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
    # data de renovação, quem decide o plano/periodicidade é esta chamada,
    # antes de existir qualquer evento do Stripe para esta assinatura.
    sub.plano = plano
    sub.periodicidade = periodicidade
    db.commit()

    line_items = [{**_item_de_preco(plano, periodicidade), "quantity": 1}]

    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=line_items,
        # Pedido do Rafael em 08/08/2026: cupom promocional no checkout —
        # os cupons em si são criados por ele no painel Stripe depois, este
        # campo só habilita o campo de código na tela do Stripe.
        allow_promotion_codes=True,
        subscription_data={
            "metadata": {
                "tipo": "meucardio", "plano": plano, "periodicidade": periodicidade,
                "user_id": str(user.id),
            }
        },
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
    # Convidado (issue #52, "REGRA DEFINITIVA DE ACESSO PARA CONVIDADO"):
    # CorvIA Mail real e completo, sem cobrança — mesmo bypass de
    # `assinatura_email_ativa()` (core/security.py), aqui refletido na
    # resposta que a tela usa pra decidir entre mostrar "Assinar" e o
    # formulário de ativação direto. Sem isto, a tela mostraria "Assine o
    # CorvIA Mail" para quem já pode ativar a caixa de graça.
    if getattr(user, "convidado", False):
        return {
            "status": "ativo", "current_period_end": None,
            "preco_definido": settings.corvia_mail_preco_definido,
            "preco_centavos": settings.corvia_mail_preco_centavos,
            "incluido_no_plano": True,
        }
    # Investidor (issue #52, achado da revisão adversarial): CorvIA Mail
    # nunca é ativável de verdade para essa conta — `preco_definido: False`
    # desabilita o botão de assinar na tela (mesma condição que já existe
    # pra "preço ainda não definido"), reforçando em defesa de profundidade
    # o bloqueio real que já vive em `POST /billing/checkout-email`. Na
    # prática o investidor nunca chega nesta tela — `CorviaMail.tsx` já
    # redireciona pro modo demonstração antes de renderizar esta aba.
    if getattr(user, "investidor", False):
        return {
            "status": "inativo", "current_period_end": None,
            "preco_definido": False,
            "preco_centavos": settings.corvia_mail_preco_centavos,
            "incluido_no_plano": False,
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
    nunca simular um preço que ainda não foi decidido.

    🟠 Achado da revisão adversarial (issue #52): faltava aqui o mesmo
    bloqueio de investidor que `POST /billing/checkout` já tinha — sem ele,
    um investidor conseguia completar um pagamento real no Stripe por um
    CorvIA Mail que `bloquear_investidor_em_operacao_real_de_mail`
    (app/services/entitlement.py) nunca deixa ativar de fato. Não é falha de
    segurança (nenhum dado vaza, nenhum acesso indevido é concedido) — é
    cobrar por algo que estruturalmente nunca funciona para essa conta."""
    _exigir_assinaturas_habilitadas()
    if getattr(user, "investidor", False):
        raise HTTPException(
            status_code=409,
            detail="O CorvIA Mail não está disponível para contas de investidor — o acesso a essa conta é só em modo demonstração.",
        )
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
        # Mesmo motivo do checkout principal, 08/08/2026: habilita o campo de
        # cupom na tela do Stripe — os cupons são criados pelo Rafael.
        allow_promotion_codes=True,
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


def _customer_ids_do_usuario(db: Session, user_id: int) -> list[str]:
    ids: list[str] = []
    for kind in (TIPO_MEUCARDIO, TIPO_EMAIL, TIPO_CURSO):
        rows = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id, Subscription.kind == kind,
                Subscription.stripe_customer_id.isnot(None),
            )
            .order_by(Subscription.id)
            .all()
        )
        for sub in rows:
            customer_id = (sub.stripe_customer_id or "").strip()
            if customer_id and customer_id not in ids:
                ids.append(customer_id)
    return ids


def _customer_id_do_usuario(db: Session, user_id: int) -> str | None:
    ids = _customer_ids_do_usuario(db, user_id)
    return ids[0] if ids else None


@router.post("/portal")
def abrir_portal(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Abre o Customer Portal usando o primeiro cliente Stripe ainda válido.

    Cadastros antigos podem conter um customer id removido no Stripe. Isso não
    pode impedir a conta inteira de usar outro customer id válido já associado.
    """
    customer_ids = _customer_ids_do_usuario(db, user.id)
    if not customer_ids:
        raise HTTPException(status_code=404, detail="Você ainda não tem uma assinatura para gerenciar.")

    encontrou_cliente_valido = False
    for customer_id in customer_ids:
        try:
            stripe.Customer.retrieve(customer_id)
            encontrou_cliente_valido = True
        except stripe.error.InvalidRequestError:
            log.warning("stripe_customer_stale", extra={"user_id": user.id})
            continue
        except stripe.error.StripeError:
            raise HTTPException(status_code=503, detail="O portal de assinatura está indisponível no momento. Tente novamente mais tarde.")
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=f"{settings.public_url}/minha-conta",
            )
            return {"portal_url": session["url"]}
        except stripe.error.InvalidRequestError:
            # Cliente existe: aqui o erro é de configuração do Customer Portal.
            raise HTTPException(status_code=503, detail="O portal de assinatura está indisponível no momento. Tente novamente mais tarde.")
        except stripe.error.StripeError:
            raise HTTPException(status_code=503, detail="O portal de assinatura está indisponível no momento. Tente novamente mais tarde.")

    if not encontrou_cliente_valido:
        raise HTTPException(status_code=404, detail="Seu cadastro de cobrança precisa ser atualizado antes de abrir o portal.")
    raise HTTPException(status_code=503, detail="O portal de assinatura está indisponível no momento. Tente novamente mais tarde.")


@router.post("/trocar-plano")
def trocar_plano(
    plano: str = Query(...), periodicidade: str = Query(...),
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    """Troca plano e/ou periodicidade de uma assinatura JÁ ATIVA (08/08/2026,
    pedido do Rafael) — antes disso, trocar exigia cancelar e reassinar
    manualmente (o 409 em `criar_checkout` acima). Usa
    `stripe.Subscription.modify(...)` trocando o item de preço, com
    `proration_behavior="create_prorations"`: o Stripe credita/debita a
    diferença proporcional ao tempo restante do ciclo atual, em vez de
    cobrar o valor cheio do novo plano imediatamente ou esperar o próximo
    ciclo — é o comportamento que a maioria dos assinantes espera ao trocar
    no meio do período já pago.

    NUNCA aplica o novo plano/periodicidade localmente aqui — só dispara a
    troca no Stripe. Quem grava `sub.plano`/`sub.periodicidade` de verdade é
    sempre o webhook (`customer.subscription.updated`), lendo o que o Stripe
    confirmou — mesma disciplina de "nunca confiar no otimista" que o resto
    deste arquivo já segue (ver `_inferir_plano_periodicidade_do_objeto`)."""
    _exigir_assinaturas_habilitadas()
    if plano not in PLANOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Plano inválido.")
    if periodicidade not in PERIODICIDADES_VALIDAS:
        raise HTTPException(status_code=400, detail="Periodicidade inválida.")

    sub = _assinatura_meucardio(db, user.id)
    if not sub or sub.status not in ACESSO_LIBERADO or not sub.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Você não tem uma assinatura ativa para trocar.")
    if user.convidado:
        # Convidado nunca fala com o Stripe (ver `criar_checkout` acima) —
        # trocar o plano dele é ação de admin (painel Admin/pré-autorização),
        # não desta rota.
        raise HTTPException(status_code=409, detail="Contas de convidado não trocam de plano por aqui.")
    if sub.plano == plano and sub.periodicidade == periodicidade:
        raise HTTPException(status_code=409, detail="Você já está neste plano e periodicidade.")

    item_preco = _item_de_preco(plano, periodicidade)
    stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
    item_atual = _campo(_campo(stripe_sub, "items") or {}, "data")[0]

    stripe.Subscription.modify(
        sub.stripe_subscription_id,
        items=[{"id": item_atual["id"], **item_preco}],
        proration_behavior="create_prorations",
        metadata={"tipo": "meucardio", "plano": plano, "periodicidade": periodicidade, "user_id": str(user.id)},
    )
    db.add(AuditLog(
        user_id=user.id, action="solicitar_troca_plano", entity="subscription",
        entity_id=str(sub.id),
        detail={
            "plano_anterior": sub.plano, "periodicidade_anterior": sub.periodicidade,
            "plano_solicitado": plano, "periodicidade_solicitada": periodicidade,
        },
    ))
    db.commit()
    return {
        "nota": "Troca solicitada — confirmamos assim que o Stripe processar (geralmente na hora).",
    }


@router.get("/faturas")
def listar_faturas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Histórico de cobranças, tolerante a customer ids antigos/removidos.

    Consulta todos os clientes Stripe associados à conta, deduplica as faturas
    e só devolve 503 quando o Stripe falha de fato — um id obsoleto isolado é
    ignorado e não derruba a Minha Conta.
    """
    customer_ids = _customer_ids_do_usuario(db, user.id)
    if not customer_ids:
        return {"faturas": []}

    por_id: dict[str, object] = {}
    consultas_validas = 0
    houve_erro_transitorio = False
    for customer_id in customer_ids:
        try:
            resposta = stripe.Invoice.list(customer=customer_id, limit=24)
            consultas_validas += 1
            for fatura in resposta["data"]:
                por_id[fatura["id"]] = fatura
        except stripe.error.InvalidRequestError:
            log.warning("stripe_customer_stale", extra={"user_id": user.id})
            continue
        except stripe.error.StripeError:
            houve_erro_transitorio = True
            continue

    if consultas_validas == 0 and houve_erro_transitorio:
        raise HTTPException(status_code=503, detail="Não foi possível consultar o histórico de cobranças agora.")

    faturas = sorted(
        por_id.values(), key=lambda item: int(_campo(item, "created") or 0), reverse=True,
    )[:24]
    return {
        "faturas": [
            {
                "id": f["id"], "numero": _campo(f, "number"), "status": _campo(f, "status"),
                "total_centavos": _campo(f, "total"),
                "moeda": (_campo(f, "currency") or "brl").upper(),
                "criada_em": datetime.fromtimestamp(_campo(f, "created"), tz=timezone.utc) if _campo(f, "created") else None,
                "url_fatura": _campo(f, "hosted_invoice_url"), "url_pdf": _campo(f, "invoice_pdf"),
            }
            for f in faturas
        ]
    }


@router.get("/status")
def status_assinatura(db: Session = Depends(get_db), user: User = Depends(current_user)):
    # `acesso_administrativo` (issue #52) é só para a tela de Assinatura
    # decidir o texto certo ("Acesso concedido administrativamente" em vez
    # de "Assine agora"/"Assinatura necessária") quando o acesso do usuário
    # vem de convidado/investidor, não de pagamento — nunca usar este campo
    # como gate, a decisão de acesso é sempre do backend em cada requisição.
    from app.services.entitlement import acesso_administrativo_sem_pagamento

    sub = _assinatura_meucardio(db, user.id)
    if not sub:
        return {
            "status": "inativo", "current_period_end": None, "plano": None, "periodicidade": None,
            "acesso_administrativo": acesso_administrativo_sem_pagamento(user),
        }
    return {
        "status": sub.status, "current_period_end": sub.current_period_end, "plano": sub.plano,
        "periodicidade": sub.periodicidade,
        "acesso_administrativo": acesso_administrativo_sem_pagamento(user),
    }


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
            estado_antes["periodicidade_anterior"] = sub.periodicidade
            sub.stripe_subscription_id = obj["id"]
            sub.status = traduzir_status(obj["status"])
            fim = _fim_do_periodo(obj)
            if fim is not None:
                sub.current_period_end = fim
            if sub.kind == TIPO_MEUCARDIO:
                # Reconciliação SEMPRE pelo que o Stripe confirma neste
                # evento — nunca pelo que `/checkout` ou `/trocar-plano`
                # gravaram otimisticamente antes da confirmação. É assim que
                # uma troca de plano feita via `stripe.Subscription.modify`
                # (endpoint `/trocar-plano`) e uma troca feita pelo próprio
                # Customer Portal do Stripe convergem para o mesmo estado
                # local, sem depender de qual caminho o assinante usou.
                novo_plano, nova_periodicidade = _inferir_plano_periodicidade_do_objeto(obj)
                if novo_plano:
                    sub.plano = novo_plano
                if nova_periodicidade:
                    sub.periodicidade = nova_periodicidade

        sub = _aplicar_evento(db, obj, quando, alterar)

        if sub is not None and sub.kind == TIPO_MEUCARDIO and estado_antes:
            era_nova = estado_antes["era_nova"]
            status_anterior = estado_antes["status_anterior"]
            plano_anterior = estado_antes["plano_anterior"]
            periodicidade_anterior = estado_antes["periodicidade_anterior"]
            valor_do_plano = PRECO_CENTAVOS.get(
                (sub.plano, sub.periodicidade),
                PRECO_COMPLETO_CENTAVOS if sub.plano == PLANO_COMPLETO else PRECO_BASICO_CENTAVOS,
            )

            if era_nova and tipo == "customer.subscription.created":
                background_tasks.add_task(
                    emails.enviar_boas_vindas, sub.user_id, sub.plano, valor_do_plano, sub.current_period_end,
                )
            elif not era_nova and (plano_anterior != sub.plano or periodicidade_anterior != sub.periodicidade):
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
