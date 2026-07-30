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
    return {"id": t.id, "title": t.title, "doc_type": t.doc_type, "body": t.body}


@router.get("")
def listar_templates(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(DocumentTemplate).filter(DocumentTemplate.owner_id == user.id).order_by(DocumentTemplate.title).all()
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


@router.post("/gerar", status_code=201)
def gerar_documento(dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, dados.template_id)
    if not t or t.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Template não encontrado.")

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

    gerado = GeneratedDocument(
        patient_id=dados.patient_id, template_id=t.id, created_by=user.id,
        doc_type=t.doc_type, title=t.title, rendered_body=corpo,
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
