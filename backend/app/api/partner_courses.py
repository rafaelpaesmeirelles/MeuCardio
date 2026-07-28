"""Cursos parceiros: catálogo, material de apoio e assinatura com repasse.

Modelo comercial: o parceiro define o preço dele (X), o MeuCardio cobra
X + margem e repassa X automaticamente pela cobrança, via Stripe Connect. Preço
e margem são por curso e vivem no banco — nunca no código, porque cada parceiro
negocia condições próprias.

A assinatura de curso é **adicional** à do MeuCardio: um médico pode assinar só
a plataforma, ou a plataforma e um ou mais cursos.
"""

from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.audit import AuditLog
from app.models.partner_course import CourseMaterial, CoursePayment, PartnerCourse
from app.models.subscription import TIPO_CURSO, Subscription
from app.models.user import User
from app.services import arquivos_curso

router = APIRouter(prefix="/api/cursos", tags=["cursos parceiros"])

ACESSO_LIBERADO = {"ativo", "teste", "inadimplente"}


def _publico(c: PartnerCourse, assinado: bool = False) -> dict:
    """Os links de aula só saem para quem assinou. Devolvê-los no catálogo
    tornaria a assinatura decorativa: bastaria abrir a listagem para pegar o
    endereço da aula ao vivo."""
    dados = {
        "slug": c.slug, "nome": c.nome, "parceiro": c.parceiro,
        "descricao": c.descricao,
        "frase_destaque": c.frase_destaque,
        "frase_destaque_fonte": c.frase_destaque_fonte,
        "preco_total_centavos": c.preco_total_centavos,
        "ativo": c.ativo, "destaque": c.destaque,
        "trilhas_vinculadas": c.trilhas_vinculadas or [],
        "casos_vinculados": c.casos_vinculados or [],
        "assinado": assinado,
    }
    if assinado:
        dados["link_aula_ao_vivo"] = c.link_aula_ao_vivo
        dados["link_aulas_gravadas"] = c.link_aulas_gravadas
    return dados


def _assinatura_do_curso(db: Session, user_id: int, course_id: int) -> Subscription | None:
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.course_id == course_id,
            Subscription.kind == TIPO_CURSO,
        )
        .order_by(Subscription.id.desc())
        .first()
    )


def _tem_acesso(db: Session, user: User, curso: PartnerCourse) -> bool:
    if user.role == "admin":
        return True
    sub = _assinatura_do_curso(db, user.id, curso.id)
    return sub is not None and sub.status in ACESSO_LIBERADO


class CursoIn(BaseModel):
    slug: str
    nome: str
    parceiro: str
    descricao: str | None = None
    frase_destaque: str | None = None
    frase_destaque_fonte: str | None = None
    link_aula_ao_vivo: str | None = None
    link_aulas_gravadas: str | None = None
    preco_parceiro_centavos: int
    margem_centavos: int
    stripe_account_id: str | None = None
    ativo: bool = False
    destaque: bool = False
    trilhas_vinculadas: list[str] = []
    casos_vinculados: list[str] = []

    @field_validator("preco_parceiro_centavos", "margem_centavos")
    @classmethod
    def _nao_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Preço e margem não podem ser negativos.")
        return v


def _exigir_fonte_da_frase(dados: CursoIn | PartnerCourse) -> None:
    """Frase de destaque sem fonte não entra.

    Índice de aprovação é afirmação de terceiro sobre resultado de curso, e vai
    aparecer no Painel principal, ao lado de conteúdo clínico que este produto
    faz questão de manter rastreável. Número sem procedência ali contamina a
    credibilidade do que está em volta.
    """
    if dados.frase_destaque and not dados.frase_destaque_fonte:
        raise HTTPException(
            status_code=422,
            detail="Frase de destaque exige `frase_destaque_fonte` — quem afirmou o dado "
                   "e quando. Sem isso o número não vai ao Painel.",
        )


@router.get("")
def listar(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Catálogo dos cursos ativos. Acesso livre a assinante da Corvia e a
    quem ainda não assina — é vitrine de venda."""
    cursos = db.query(PartnerCourse).filter(PartnerCourse.ativo.is_(True)).order_by(
        PartnerCourse.nome
    ).all()
    return [_publico(c, _tem_acesso(db, user, c)) for c in cursos]


@router.get("/destaque")
def curso_em_destaque(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Alimenta o cartão do Painel principal.

    Devolve `null` quando não há curso ativo em destaque, e é isso que faz o
    espaço sumir por inteiro em vez de deixar moldura vazia — a decisão fica no
    servidor, não numa flag esquecida no frontend.
    """
    c = (
        db.query(PartnerCourse)
        .filter(PartnerCourse.ativo.is_(True), PartnerCourse.destaque.is_(True))
        .order_by(PartnerCourse.updated_at.desc())
        .first()
    )
    if c is None:
        return {"curso": None}
    return {"curso": _publico(c, _tem_acesso(db, user, c))}


@router.get("/{slug}")
def detalhe(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.query(PartnerCourse).filter(PartnerCourse.slug == slug).first()
    if c is None or not c.ativo:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")
    acesso = _tem_acesso(db, user, c)
    dados = _publico(c, acesso)
    dados["materiais"] = [
        {"id": m.id, "titulo": m.titulo, "nome_arquivo": m.nome_arquivo,
         "tamanho_bytes": m.tamanho_bytes}
        for m in db.query(CourseMaterial).filter(CourseMaterial.course_id == c.id)
        .order_by(CourseMaterial.created_at).all()
    ] if acesso else []
    return dados


@router.post("/{slug}/assinar")
def assinar(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Checkout da assinatura do curso, com repasse automático ao parceiro."""
    curso = db.query(PartnerCourse).filter(PartnerCourse.slug == slug).first()
    if curso is None or not curso.ativo:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    if not curso.stripe_account_id:
        # Cobrar sem ter como repassar criaria uma dívida com o parceiro a ser
        # resolvida por transferência manual — exatamente o que o modelo de
        # Connect existe para evitar. Melhor recusar a venda.
        raise HTTPException(
            status_code=409,
            detail="Este curso ainda não tem conta conectada do parceiro no Stripe. "
                   "A venda fica bloqueada até o repasse automático estar configurado.",
        )

    existente = _assinatura_do_curso(db, user.id, curso.id)
    if existente is not None and existente.status in ACESSO_LIBERADO:
        raise HTTPException(status_code=409, detail="Você já assina este curso.")

    # O cliente Stripe é o mesmo do médico, reaproveitado da assinatura do
    # MeuCardio quando existir: dois clientes para a mesma pessoa quebram o
    # portal de cobrança e o histórico de faturas.
    principal = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.stripe_customer_id.isnot(None))
        .first()
    )
    customer_id = principal.stripe_customer_id if principal else None
    if not customer_id:
        customer_id = stripe.Customer.create(email=user.email, name=user.full_name)["id"]

    if existente is None:
        existente = Subscription(
            user_id=user.id, kind=TIPO_CURSO, course_id=curso.id,
            stripe_customer_id=customer_id, status="pendente",
        )
        db.add(existente)
    else:
        existente.stripe_customer_id = customer_id
        existente.status = "pendente"
    db.commit()

    sessao = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "brl",
                "unit_amount": curso.preco_total_centavos,
                "recurring": {"interval": "month"},
                "product_data": {"name": f"{curso.nome} — {curso.parceiro}"},
            },
            "quantity": 1,
        }],
        subscription_data={
            # O repasse acontece na própria cobrança: a margem fica na conta do
            # MeuCardio como application fee e o restante vai para o parceiro.
            "application_fee_percent": _percentual_de_margem(curso),
            "transfer_data": {"destination": curso.stripe_account_id},
            "metadata": {"tipo": "curso", "curso_id": str(curso.id), "user_id": str(user.id)},
        },
        # O metadata da sessão e o da assinatura são campos diferentes; o webhook
        # de customer.subscription.* só enxerga o da assinatura.
        metadata={"tipo": "curso", "curso_id": str(curso.id), "user_id": str(user.id)},
        success_url=f"{settings.public_url}/cursos/{curso.slug}?status=sucesso",
        cancel_url=f"{settings.public_url}/cursos/{curso.slug}?status=cancelado",
    )
    return {"checkout_url": sessao["url"]}


def _percentual_de_margem(curso: PartnerCourse) -> float:
    """O Stripe cobra a taxa de aplicação em percentual na assinatura, não em
    centavos. Converte a margem configurada, que é em centavos porque é assim
    que se negocia com o parceiro, arredondando a duas casas."""
    total = curso.preco_total_centavos
    if total <= 0:
        return 0.0
    return round(curso.margem_centavos * 100 / total, 2)


@router.get("/{slug}/material/{material_id}")
def baixar_material(
    slug: str, material_id: int,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    curso = db.query(PartnerCourse).filter(PartnerCourse.slug == slug).first()
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")
    if not _tem_acesso(db, user, curso):
        raise HTTPException(status_code=402, detail="Assinatura deste curso necessária.")

    material = db.query(CourseMaterial).filter(
        CourseMaterial.id == material_id, CourseMaterial.course_id == curso.id
    ).first()
    if material is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    try:
        conteudo = arquivos_curso.ler(material.caminho)
    except arquivos_curso.ArquivoRecusado as e:
        raise HTTPException(status_code=410, detail=str(e))

    db.add(AuditLog(user_id=user.id, action="baixar_material_curso",
                    entity="course_material", entity_id=str(material.id),
                    detail={"curso": curso.slug}))
    db.commit()
    return Response(
        content=conteudo, media_type=material.content_type,
        headers={"Content-Disposition": f'attachment; filename="{material.nome_arquivo}"'},
    )


# ---------------------------------------------------------------- administração

@router.post("/admin", status_code=201)
def criar_curso(dados: CursoIn, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Cadastro manual do curso. Não existe autocadastro para o parceiro por
    decisão de escopo: enquanto não houver contrato fechado, quem cadastra é o
    administrador."""
    _exigir_fonte_da_frase(dados)
    if db.query(PartnerCourse).filter(PartnerCourse.slug == dados.slug).first():
        raise HTTPException(status_code=409, detail="Já existe curso com este slug.")

    curso = PartnerCourse(**dados.model_dump())
    if curso.destaque:
        _tirar_destaque_dos_outros(db, manter=None)
    db.add(curso)
    db.commit()
    db.refresh(curso)
    db.add(AuditLog(user_id=admin.id, action="criar_curso_parceiro",
                    entity="partner_course", entity_id=curso.slug,
                    detail={"preco_total_centavos": curso.preco_total_centavos}))
    db.commit()
    return _publico(curso)


@router.patch("/admin/{slug}")
def editar_curso(slug: str, dados: dict, db: Session = Depends(get_db), admin=Depends(require_admin)):
    curso = db.query(PartnerCourse).filter(PartnerCourse.slug == slug).first()
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    permitidos = set(CursoIn.model_fields) - {"slug"}
    for campo, valor in dados.items():
        if campo in permitidos:
            setattr(curso, campo, valor)
    _exigir_fonte_da_frase(curso)

    if curso.destaque:
        _tirar_destaque_dos_outros(db, manter=curso.id)
    db.commit()
    db.add(AuditLog(user_id=admin.id, action="editar_curso_parceiro",
                    entity="partner_course", entity_id=curso.slug,
                    detail={"campos": sorted(set(dados) & permitidos)}))
    db.commit()
    return _publico(curso)


def _tirar_destaque_dos_outros(db: Session, manter: int | None) -> None:
    """Só um curso em destaque por vez. Dois cartões no Painel não é decisão de
    layout, é sintoma de configuração inconsistente."""
    q = db.query(PartnerCourse).filter(PartnerCourse.destaque.is_(True))
    if manter is not None:
        q = q.filter(PartnerCourse.id != manter)
    for outro in q.all():
        outro.destaque = False


@router.post("/admin/{slug}/material", status_code=201)
async def enviar_material(
    slug: str, titulo: str = "", arquivo: UploadFile = File(...),
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    curso = db.query(PartnerCourse).filter(PartnerCourse.slug == slug).first()
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")

    conteudo = await arquivo.read()
    try:
        guardado = arquivos_curso.guardar(conteudo, arquivo.filename or "material", curso.id)
    except arquivos_curso.ArquivoRecusado as e:
        raise HTTPException(status_code=422, detail=str(e))

    material = CourseMaterial(
        course_id=curso.id,
        titulo=(titulo or guardado["nome_arquivo"])[:200],
        nome_arquivo=guardado["nome_arquivo"],
        caminho=guardado["caminho"],
        tamanho_bytes=guardado["tamanho_bytes"],
        content_type=arquivo.content_type or "application/octet-stream",
        enviado_por=admin.id,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return {"id": material.id, "titulo": material.titulo,
            "tamanho_bytes": material.tamanho_bytes}


@router.delete("/admin/{slug}/material/{material_id}", status_code=204)
def remover_material(
    slug: str, material_id: int,
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    curso = db.query(PartnerCourse).filter(PartnerCourse.slug == slug).first()
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso não encontrado.")
    material = db.query(CourseMaterial).filter(
        CourseMaterial.id == material_id, CourseMaterial.course_id == curso.id
    ).first()
    if material is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    arquivos_curso.apagar(material.caminho)
    db.delete(material)
    db.commit()
    return Response(status_code=204)


@router.get("/admin/financeiro/resumo")
def resumo_financeiro(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Separa o que é receita do MeuCardio do que é dinheiro de terceiro.

    Somar o bruto ao faturamento infla a receita com valor que só transita por
    aqui. É essa separação que a emissão de nota fiscal dos dois lados vai
    exigir, e o que o contador precisa conseguir reconciliar.
    """
    from sqlalchemy import func

    linhas = (
        db.query(
            PartnerCourse.slug, PartnerCourse.nome,
            func.count(CoursePayment.id),
            func.coalesce(func.sum(CoursePayment.bruto_centavos), 0),
            func.coalesce(func.sum(CoursePayment.repasse_centavos), 0),
            func.coalesce(func.sum(CoursePayment.margem_centavos), 0),
        )
        .join(CoursePayment, CoursePayment.course_id == PartnerCourse.id)
        .group_by(PartnerCourse.slug, PartnerCourse.nome)
        .all()
    )
    por_curso = [
        {"slug": s, "nome": n, "cobrancas": q,
         "bruto_centavos": b, "repasse_a_terceiro_centavos": r, "receita_propria_centavos": m}
        for s, n, q, b, r, m in linhas
    ]
    return {
        "por_curso": por_curso,
        "totais": {
            "bruto_centavos": sum(l["bruto_centavos"] for l in por_curso),
            "repasse_a_terceiro_centavos": sum(l["repasse_a_terceiro_centavos"] for l in por_curso),
            "receita_propria_centavos": sum(l["receita_propria_centavos"] for l in por_curso),
        },
        "nota": "Receita própria é só a margem. O repasse é passivo com o parceiro e "
                "não deve entrar no faturamento da Corvia.",
    }


def registrar_pagamento(db: Session, invoice) -> None:
    """Chamada pelo webhook a cada fatura paga de assinatura de curso.

    Guarda os três valores separados no momento do pagamento, e não recalcula a
    partir do curso depois: preço e margem podem mudar, e um relatório de junho
    não pode ser reescrito pela tabela de agosto.
    """
    def campo(obj, chave, padrao=None):
        return obj[chave] if chave in obj else padrao

    assinatura_id = campo(invoice, "subscription")
    if not assinatura_id:
        return
    sub = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == assinatura_id,
                Subscription.kind == TIPO_CURSO)
        .first()
    )
    if sub is None or sub.course_id is None:
        return
    curso = db.query(PartnerCourse).filter(PartnerCourse.id == sub.course_id).first()
    if curso is None:
        return

    invoice_id = campo(invoice, "id")
    if db.query(CoursePayment).filter(CoursePayment.stripe_invoice_id == invoice_id).first():
        return  # o Stripe reentrega eventos; a fatura já foi registrada

    bruto = campo(invoice, "amount_paid") or curso.preco_total_centavos
    margem = round(bruto * curso.margem_centavos / curso.preco_total_centavos) \
        if curso.preco_total_centavos else 0
    db.add(CoursePayment(
        course_id=curso.id, user_id=sub.user_id,
        stripe_invoice_id=invoice_id, stripe_subscription_id=assinatura_id,
        bruto_centavos=bruto, repasse_centavos=bruto - margem, margem_centavos=margem,
        moeda=(campo(invoice, "currency") or "brl"),
        competencia=datetime.now(timezone.utc),
    ))
    db.commit()
