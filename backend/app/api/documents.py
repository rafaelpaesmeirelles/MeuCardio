import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.round import Patient

router = APIRouter(prefix="/api/document-templates", tags=["documentos"])


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


@router.post("/gerar", status_code=201)
def gerar_documento(dados: GerarDocumentoIn, db: Session = Depends(get_db), user=Depends(current_user)):
    t = db.get(DocumentTemplate, dados.template_id)
    if not t or t.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Template não encontrado.")

    if dados.patient_id is not None:
        p = db.get(Patient, dados.patient_id)
        if not p or (p.created_by != user.id and user.role != "admin"):
            raise HTTPException(status_code=404, detail="Paciente não encontrado.")

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
