import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.compartilhamento import DocumentShareLink
from app.models.round import Patient
from app.services import cofre
from app.services.notificar import tentar_enviar_email

router = APIRouter(prefix="/api/document-templates", tags=["documentos"])

VALIDADE_LINK_DIAS = 7


class TemplateIn(BaseModel):
    title: str
    doc_type: str  # atestado | laudo | outro
    body: str


def _dump_template(t: DocumentTemplate) -> dict:
    return {
        "id": t.id, "title": t.title, "doc_type": t.doc_type, "body": t.body,
        "slug_sistema": t.slug_sistema, "sistema": t.owner_id is None,
    }


@router.get("")
def listar_templates(db: Session = Depends(get_db), user=Depends(current_user)):
    """Modelos do sistema (owner_id nulo — pesquisados de fonte confiável,
    disponíveis a qualquer médico, Tarefa 30) mais os que o próprio médico
    criou. Sistema primeiro, depois os próprios por título."""
    rows = (
        db.query(DocumentTemplate)
        .filter((DocumentTemplate.owner_id == user.id) | (DocumentTemplate.owner_id.is_(None)))
        .order_by(DocumentTemplate.owner_id.is_not(None), DocumentTemplate.title)
        .all()
    )
    return [_dump_template(t) for t in rows]


@router.post("", status_code=201)
def criar_template(dados: TemplateIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if dados.doc_type not in {"atestado", "laudo", "outro"}:
        raise HTTPException(status_code=422, detail="Tipo inválido.")
    t = DocumentTemplate(owner_id=user.id, title=dados.title, doc_type=dados.doc_type, body=dados.body)
    db.add(t)
    db.commit()
    db.refresh(t)
    return _dump_template(t)


@router.put("/{tid}")
def editar_template(tid: int, dados: TemplateIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, tid)
    if not t or t.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Template não encontrado.")
    t.title, t.doc_type, t.body = dados.title, dados.doc_type, dados.body
    db.commit()
    return _dump_template(t)


@router.delete("/{tid}", status_code=204)
def apagar_template(tid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    db.query(DocumentTemplate).filter(DocumentTemplate.id == tid, DocumentTemplate.owner_id == user.id).delete()
    db.commit()


class GerarDocumentoIn(BaseModel):
    template_id: int
    patient_id: int | None = None
    variables: dict[str, str] = {}
    # 'residencial' | 'profissional' | None — mesma escolha do receituário
    # (Tarefa 29), gravada aqui porque o PDF é gerado sob demanda depois
    # (GET .../pdf, ou pelo link público) e precisa sair sempre igual.
    endereco: str | None = None
    # Só para o modelo do sistema "documento em branco" (Tarefa 30) — título
    # livre por geração, já que o do template ("Documento em branco") não
    # serve como título final impresso.
    titulo_customizado: str | None = None


@router.post("/gerar", status_code=201)
def gerar_documento(dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, dados.template_id)
    # Modelo do sistema (owner_id nulo, Tarefa 30) é liberado pra qualquer
    # médico; modelo próprio continua exigindo posse.
    if not t or (t.owner_id is not None and t.owner_id != user.id):
        raise HTTPException(status_code=404, detail="Template não encontrado.")

    if t.slug_sistema == "avaliacao-risco-cirurgico":
        raise HTTPException(
            status_code=422,
            detail="Use POST /document-templates/avaliacao-preoperatoria para este modelo — "
                   "ele calcula o risco a partir dos dados clínicos, não substitui variáveis.",
        )

    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or (p.created_by != user.id and user.role != "admin"):
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    corpo = t.body
    faltando = []
    for variavel in set(re.findall(r"\{\{(\w+)\}\}", corpo)):
        valor = dados.variables.get(variavel)
        if valor is None or valor == "":
            faltando.append(variavel)
        else:
            corpo = corpo.replace(f"{{{{{variavel}}}}}", valor)
    if faltando:
        raise HTTPException(status_code=422, detail=f"Faltam variáveis: {', '.join(faltando)}")

    titulo = t.title
    if t.slug_sistema == "documento-em-branco" and dados.titulo_customizado:
        titulo = dados.titulo_customizado

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=t.id, created_by=user.id,
        doc_type=t.doc_type, title=titulo, rendered_body=corpo,
        endereco_exibido=dados.endereco,
    )
    db.add(gerado)
    db.commit()
    db.refresh(gerado)
    return {
        "id": gerado.id, "title": gerado.title, "doc_type": gerado.doc_type,
        "rendered_body": gerado.rendered_body, "created_at": gerado.created_at,
        "medico": {"full_name": user.full_name, "council_name": user.council_name,
                   "council_number": user.council_number, "council_state": user.council_state,
                   "rqe": user.rqe, "specialty": user.specialty},
    }


class AvaliacaoPreOpIn(BaseModel):
    """Dados clínicos da avaliação de risco cirúrgico (Tarefa 30). Nenhum campo
    é obrigatório sozinho — o rascunho é montado com o que estiver preenchido,
    e o médico completa/corrige antes de emitir."""
    # Procedimento planejado — usado para classificar o risco cirúrgico
    # pela Tabela 5 da ESC/ESAIC 2022.
    procedimento_planejado: str = ""
    categoria_risco_cirurgico: str | None = None  # baixo | intermediario | alto

    # RCRI — os 6 critérios do Índice de Lee.
    cirurgia_alto_risco: bool = False
    doenca_arterial_coronariana: bool = False
    insuficiencia_cardiaca_congestiva: bool = False
    doenca_cerebrovascular: bool = False
    diabetes_insulinodependente: bool = False
    creatinina_maior_2: bool = False

    # Capacidade funcional: se algum item do DASI abaixo vier marcado, ele
    # prevalece (é o método estruturado que ESC/ESAIC 2022 e ACC/AHA 2024
    # preferem); senão cai na seleção simples.
    capacidade_funcional: str = "indeterminada"  # boa | reduzida | indeterminada
    cuidar_de_si: bool = False
    caminhar_dentro_de_casa: bool = False
    caminhar_200m_plano: bool = False
    subir_um_lance_escada: bool = False
    correr_curta_distancia: bool = False
    trabalho_domestico_leve: bool = False
    trabalho_domestico_moderado: bool = False
    trabalho_domestico_pesado: bool = False
    jardinagem: bool = False
    relacoes_sexuais: bool = False
    recreacao_moderada: bool = False
    esporte_extenuante: bool = False

    # Gupta MICA — coletadas, sem cálculo automático (ver app/services/preop.py).
    gupta_idade: str | None = None
    gupta_status_funcional: str | None = None
    gupta_asa: str | None = None
    gupta_creatinina_elevada: bool = False
    gupta_tipo_procedimento: str | None = None

    observacoes_adicionais: str | None = None


@router.post("/avaliacao-preoperatoria/rascunho")
def rascunho_avaliacao_preoperatoria(dados: AvaliacaoPreOpIn, user=Depends(current_user)):
    """Só calcula e monta o texto — não grava nada. O médico revisa/edita no
    frontend antes de confirmar a emissão (endpoint abaixo)."""
    from app.services import preop

    if dados.categoria_risco_cirurgico not in (None, "baixo", "intermediario", "alto"):
        raise HTTPException(status_code=422, detail="categoria_risco_cirurgico inválida.")
    if dados.capacidade_funcional not in ("boa", "reduzida", "indeterminada"):
        raise HTTPException(status_code=422, detail="capacidade_funcional inválida.")

    texto, resultado_rcri = preop.montar_rascunho(dados.model_dump())
    return {"rascunho": texto, "rcri": resultado_rcri["result"]}


class ConfirmarAvaliacaoPreOpIn(BaseModel):
    corpo: str = Field(min_length=1)
    patient_id: int | None = None
    endereco: str | None = None


@router.post("/avaliacao-preoperatoria", status_code=201)
def confirmar_avaliacao_preoperatoria(
    dados: ConfirmarAvaliacaoPreOpIn, db: Session = Depends(get_db), user=Depends(current_user)
):
    """Grava a avaliação com o texto JÁ revisado pelo médico (`corpo` é o que
    veio do rascunho, editado ou não) — mesmo modelo de `GeneratedDocument`
    usado pelos outros documentos, então PDF/e-mail/link público reaproveitam
    tudo que já existe para atestado e laudo."""
    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or (p.created_by != user.id and user.role != "admin"):
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    if dados.endereco not in (None, "residencial", "profissional"):
        raise HTTPException(status_code=422, detail="endereco precisa ser 'residencial', 'profissional' ou omitido.")

    template = db.query(DocumentTemplate).filter(
        DocumentTemplate.slug_sistema == "avaliacao-risco-cirurgico").first()

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=template.id if template else None,
        created_by=user.id, doc_type="laudo",
        title="Avaliação cardiológica de risco cirúrgico", rendered_body=dados.corpo,
        endereco_exibido=dados.endereco,
    )
    db.add(gerado)
    db.commit()
    db.refresh(gerado)
    return {"id": gerado.id, "title": gerado.title, "created_at": gerado.created_at}


def _obter_gerado(gid: int, db: Session, user) -> GeneratedDocument:
    g = db.get(GeneratedDocument, gid)
    if not g or (g.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return g


@router.get("/gerados")
def listar_gerados(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = (
        db.query(GeneratedDocument)
        .filter(GeneratedDocument.created_by == user.id)
        .order_by(GeneratedDocument.created_at.desc())
        .limit(200)
        .all()
    )
    return [
        {"id": g.id, "title": g.title, "doc_type": g.doc_type, "created_at": g.created_at}
        for g in rows
    ]


@router.get("/gerados/{gid}")
def obter_gerado(gid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    g = _obter_gerado(gid, db, user)
    return {
        "id": g.id, "title": g.title, "doc_type": g.doc_type,
        "rendered_body": g.rendered_body, "created_at": g.created_at,
        "tem_email_destinatario": g.destinatario_email_cifrado is not None,
    }


@router.get("/gerados/{gid}/pdf")
def baixar_pdf_gerado(gid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    from app.models.user import User
    from app.services.pdf_documento import documento_generico, resolver_endereco

    g = _obter_gerado(gid, db, user)
    # O cabeçalho do PDF tem que trazer o médico que EMITIU o documento, não
    # quem está baixando agora — um admin vendo o documento de outro médico
    # não pode aparecer como se fosse o emissor.
    emissor = db.get(User, g.created_by) or user
    titulo = {"atestado": "Atestado", "laudo": "Laudo"}.get(g.doc_type, g.title)
    pdf = documento_generico(
        titulo=titulo, corpo=g.rendered_body,
        medico={"full_name": emissor.full_name, "council_name": emissor.council_name,
                "council_number": emissor.council_number, "council_state": emissor.council_state,
                "rqe": emissor.rqe, "specialty": emissor.specialty,
                "document_logo_url": emissor.document_logo_url},
        endereco=resolver_endereco(emissor, g.endereco_exibido),
    )
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="documento-{g.id}.pdf"'})


class EnviarEmailIn(BaseModel):
    email: str = Field(min_length=5)


@router.post("/gerados/{gid}/enviar-email")
def enviar_email_gerado(gid: int, dados: EnviarEmailIn, db: Session = Depends(get_db), user=Depends(current_user)):
    """Mesma decisão do receituário (30/07/2026): manda ao paciente um LINK,
    nunca o PDF anexado — atestado/laudo também é dado clínico, e a caixa de
    e-mail (CorvIA Mail) tem termo LGPD que proíbe isso. Diferente de
    `_obter_gerado` (que permite admin ver documento de outro médico), esta
    rota exige ser o próprio autor: mandar e-mail a um paciente em nome de
    outro médico não é ação que um admin deva poder disparar."""
    g = db.get(GeneratedDocument, gid)
    if not g or g.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    g.destinatario_email_cifrado = cofre.cifrar_campo(dados.email, g.id)

    link = DocumentShareLink(
        tipo="generated_document", referencia_id=g.id, criado_por=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=VALIDADE_LINK_DIAS),
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    url = f"{settings.public_url}/api/documentos-publicos/{link.token}"
    enviado = tentar_enviar_email(
        destinatario=dados.email,
        assunto="Corvia — documento do seu médico disponível",
        corpo=(
            f"Dr(a). {user.full_name} disponibilizou um documento para você na Corvia.\n\n"
            f"Acesse pelo link abaixo (válido por {VALIDADE_LINK_DIAS} dias): {url}\n\n"
            f"Este link é pessoal — não compartilhe."
        ),
    )
    return {"enviado": enviado, "link": None if enviado else url}
