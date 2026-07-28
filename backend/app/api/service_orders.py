"""Pedidos avulsos: laudo e consultoria à distância (pagamento único).

Separado de app/api/billing.py de propósito. São duas naturezas de cobrança
diferentes: billing cuida da assinatura recorrente do MeuCardio, aqui é
pagamento único por pedido, com preço variável. Misturar os dois num fluxo só
levaria a `mode` condicional espalhado pelo código.
"""

from datetime import datetime, timedelta, timezone

import stripe
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import cofre
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.core.validators import cpf_valido, limpar_cpf
from app.models.audit import AuditLog
from app.models.service_order import ServiceOrder, ServiceOrderPatient
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


HORAS_SLA = {"eletivo": 12, "urgente": 2}


def preco_de(servico: str, urgencia: str) -> int:
    try:
        return PRECOS_CENTAVOS[(servico, urgencia)]
    except KeyError:
        raise HTTPException(status_code=422, detail="Combinação de serviço e urgência inválida.")


def calcular_prazo(urgencia: str, a_partir_de: datetime) -> tuple[datetime, str]:
    """Prazo do SLA, contado a partir da confirmação do pagamento.

    Regra do protótipo, confirmada pelo Rafael: Urgente/Plantão vale das 7h às
    22h, todos os dias. Fora dessa janela o pedido é tratado como eletivo —
    quem paga às 3h da manhã não teria plantão para atender em 2 horas.

    Devolve também a urgência efetivamente aplicada, que pode não ser a
    contratada; a interface precisa dizer isso ao solicitante em vez de
    prometer 2 horas e entregar 12.
    """
    try:
        from zoneinfo import ZoneInfo

        local = a_partir_de.astimezone(ZoneInfo(settings.fuso_operacao))
    except Exception:  # noqa: BLE001 — sem base de fusos, não trava o pedido
        local = a_partir_de

    dentro_do_plantao = settings.plantao_inicio_hora <= local.hour < settings.plantao_fim_hora
    efetiva = urgencia if (urgencia == "eletivo" or dentro_do_plantao) else "eletivo"
    return a_partir_de + timedelta(hours=HORAS_SLA[efetiva]), efetiva


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
        "duvida": p.duvida,
        "contato_email": p.contato_email,
        "contato_whatsapp": p.contato_whatsapp,
        "tem_arquivo": p.arquivo_exame is not None,
        "arquivo_nome_original": p.arquivo_nome_original,
        "consentimento_em": p.consentimento_em,
        "prazo_em": p.prazo_em,
        "atendido_em": p.atendido_em,
        "resposta": p.resposta,
    }


def _dump_solicitante(db: Session, user_id: int) -> dict:
    u = db.get(User, user_id)
    if u is None:
        return {}
    return {
        "nome": u.full_name,
        "conselho": f"{u.council_name} {u.council_number}/{u.council_state}"
                    if u.council_name else None,
        "email": u.email,
    }


def _dump_paciente(db: Session, order_id: int) -> dict | None:
    p = db.query(ServiceOrderPatient).filter(ServiceOrderPatient.order_id == order_id).first()
    return {"nome": p.nome, "cpf": p.cpf} if p else None


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
                    "product_data": {"name": "Corvia — Telediagnóstico",
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


@router.get("/fila")
def fila_de_atendimento(
    incluir_atendidos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Painel de atendimento. Só entra aqui o que já foi pago — é a regra que
    o briefing fixa, e ela vive na query, não na interface: pedido não pago
    não pode aparecer na fila nem por engano de filtro no frontend."""
    query = db.query(ServiceOrder).filter(ServiceOrder.status == "pago")
    if not incluir_atendidos:
        query = query.filter(ServiceOrder.atendido_em.is_(None))

    # Ordena pelo prazo: o mais perto de estourar aparece primeiro.
    pedidos = query.order_by(ServiceOrder.prazo_em.asc().nullslast()).all()
    agora = datetime.now(timezone.utc)

    itens = []
    for p in pedidos:
        d = _dump(p)
        d["atrasado"] = bool(p.prazo_em and not p.atendido_em and p.prazo_em < agora)
        d["minutos_restantes"] = (
            int((p.prazo_em - agora).total_seconds() // 60) if p.prazo_em and not p.atendido_em else None
        )
        d["solicitante"] = _dump_solicitante(db, p.user_id)
        d["paciente"] = _dump_paciente(db, p.id)
        itens.append(d)
    return {"fila": itens, "total": len(itens)}


@router.get("/{pedido_id}")
def ver_pedido(pedido_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    pedido = db.get(ServiceOrder, pedido_id)
    if not pedido or (pedido.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return _dump(pedido)


class DadosClinicos(BaseModel):
    duvida: str | None = None
    contato_email: str | None = None
    contato_whatsapp: str | None = None
    paciente_nome: str | None = None
    paciente_cpf: str | None = None
    consentimento: bool = False


def _meu_pedido(pedido_id: int, db: Session, user: User) -> ServiceOrder:
    pedido = db.get(ServiceOrder, pedido_id)
    if not pedido or pedido.user_id != user.id:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return pedido


@router.patch("/{pedido_id}")
def preencher_pedido(
    pedido_id: int,
    dados: DadosClinicos,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    """Preenche o conteúdo clínico. Só antes do atendimento: depois que o
    laudo foi emitido, mudar a dúvida ou o paciente descreveria um pedido que
    não é o que foi respondido."""
    pedido = _meu_pedido(pedido_id, db, user)
    if pedido.atendido_em is not None:
        raise HTTPException(status_code=409, detail="Pedido já atendido; não pode mais ser alterado.")

    if dados.duvida is not None:
        pedido.duvida = dados.duvida.strip() or None
    if dados.contato_email is not None:
        pedido.contato_email = dados.contato_email.strip() or None
    if dados.contato_whatsapp is not None:
        pedido.contato_whatsapp = dados.contato_whatsapp.strip() or None
    if dados.consentimento:
        pedido.consentimento_em = datetime.now(timezone.utc)

    if dados.paciente_nome or dados.paciente_cpf:
        if not (dados.paciente_nome and dados.paciente_cpf):
            raise HTTPException(status_code=422, detail="Informe nome e CPF do paciente.")
        if not cpf_valido(dados.paciente_cpf):
            raise HTTPException(status_code=422, detail="CPF do paciente inválido.")
        registro = (
            db.query(ServiceOrderPatient)
            .filter(ServiceOrderPatient.order_id == pedido.id)
            .first()
        )
        if registro is None:
            registro = ServiceOrderPatient(order_id=pedido.id, nome="", cpf="")
            db.add(registro)
        registro.nome = dados.paciente_nome.strip()
        registro.cpf = limpar_cpf(dados.paciente_cpf)

    db.commit()
    db.refresh(pedido)
    return _dump(pedido)


# Assinaturas de arquivo aceitas para exame: imagem ou PDF. Mesma lógica da
# foto de perfil — o Content-Type vem do cliente e não prova nada.
ASSINATURAS_EXAME = {b"\xff\xd8\xff": "image/jpeg", b"\x89PNG\r\n\x1a\n": "image/png",
                     b"%PDF-": "application/pdf"}
TAMANHO_MAXIMO_EXAME = 20 * 1024 * 1024  # 20 MB


def _tipo_do_exame(conteudo: bytes) -> str | None:
    for assinatura, tipo in ASSINATURAS_EXAME.items():
        if conteudo.startswith(assinatura):
            return tipo
    return None


@router.post("/{pedido_id}/exame")
async def enviar_exame(
    pedido_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    pedido = _meu_pedido(pedido_id, db, user)
    if pedido.atendido_em is not None:
        raise HTTPException(status_code=409, detail="Pedido já atendido.")

    conteudo = await arquivo.read(TAMANHO_MAXIMO_EXAME + 1)
    if len(conteudo) > TAMANHO_MAXIMO_EXAME:
        raise HTTPException(status_code=413, detail="O arquivo precisa ter no máximo 20 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")

    tipo = _tipo_do_exame(conteudo)
    if tipo is None:
        raise HTTPException(status_code=422, detail="Envie o exame em JPEG, PNG ou PDF.")

    try:
        novo = cofre.guardar(conteudo, pedido.id)
    except cofre.CofreIndisponivel as e:
        # Recusar é melhor do que guardar exame de paciente sem cifrar.
        raise HTTPException(status_code=503, detail=f"Armazenamento seguro indisponível: {e}")

    if pedido.arquivo_exame:
        cofre.apagar(pedido.arquivo_exame)
    pedido.arquivo_exame = novo
    pedido.arquivo_nome_original = (arquivo.filename or "exame")[:255]
    pedido.arquivo_tipo = tipo
    db.add(AuditLog(user_id=user.id, action="enviar_exame", entity="service_order",
                    entity_id=str(pedido.id), detail={"tipo": tipo, "bytes": len(conteudo)}))
    db.commit()
    db.refresh(pedido)
    return _dump(pedido)


@router.get("/{pedido_id}/exame")
def baixar_exame(pedido_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Único caminho de leitura do exame. O arquivo não tem URL pública: o
    volume não é montado no Caddy. Toda leitura vai para o AuditLog — é o
    controle que a cifragem não dá, porque o backend precisa da chave."""
    pedido = db.get(ServiceOrder, pedido_id)
    if not pedido or (pedido.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if not pedido.arquivo_exame:
        raise HTTPException(status_code=404, detail="Este pedido não tem exame anexado.")

    try:
        conteudo = cofre.ler(pedido.arquivo_exame, pedido.id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no armazenamento.")
    except cofre.CofreIndisponivel as e:
        raise HTTPException(status_code=503, detail=str(e))

    db.add(AuditLog(user_id=user.id, action="ler_exame", entity="service_order",
                    entity_id=str(pedido.id), detail={"papel": user.role}))
    db.commit()

    return Response(
        content=conteudo,
        media_type=pedido.arquivo_tipo or "application/octet-stream",
        headers={"Content-Disposition":
                 f'inline; filename="{pedido.arquivo_nome_original or "exame"}"',
                 # Exame de paciente não fica em cache de proxy nem do browser.
                 "Cache-Control": "no-store, private"},
    )


class Resposta(BaseModel):
    resposta: str


@router.post("/{pedido_id}/responder")
def responder(
    pedido_id: int,
    dados: Resposta,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Conclui a consultoria. Para o serviço `laudo`, isto NÃO emite o laudo:
    laudo só existe assinado digitalmente, e a assinatura ainda não está
    integrada — ver a regra transversal nº 3 do briefing. Enquanto isso, o
    pedido de laudo aceita a resposta mas continua sem documento assinado."""
    pedido = db.get(ServiceOrder, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if pedido.status != "pago":
        raise HTTPException(status_code=409, detail="Pedido ainda não foi pago.")

    pedido.resposta = dados.resposta.strip()
    pedido.atendido_em = datetime.now(timezone.utc)
    pedido.respondido_por = user.id
    db.add(AuditLog(user_id=user.id, action="responder", entity="service_order",
                    entity_id=str(pedido.id), detail={"servico": pedido.servico}))
    db.commit()
    db.refresh(pedido)

    resultado = _dump(pedido)
    if pedido.servico == "laudo":
        resultado["aviso"] = (
            "Resposta registrada, mas o laudo assinado digitalmente ainda não "
            "foi emitido: a integração de assinatura (VIDAAS/Gov.br) não está "
            "disponível. VERIFICAÇÃO HUMANA NECESSÁRIA antes de entregar."
        )
    return resultado


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

    agora = datetime.now(timezone.utc)
    pedido.status = "pago"
    pedido.pago_em = agora
    # O prazo só começa a contar quando o pagamento é confirmado — antes disso
    # o pedido não está na fila, então contar antes prometeria tempo que
    # ninguém está usando para atender.
    pedido.prazo_em, _efetiva = calcular_prazo(pedido.urgencia, agora)
    intent = _campo(sessao, "payment_intent")
    if isinstance(intent, str):
        pedido.stripe_payment_intent_id = intent
    db.commit()
