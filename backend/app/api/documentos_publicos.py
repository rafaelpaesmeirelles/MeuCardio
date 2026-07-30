# -*- coding: utf-8 -*-
"""Download público de PDF clínico por link — Tarefa 29 (30/07/2026).

Rota SEM autenticação, de propósito: quem acessa é o paciente, que não tem
(nem deveria precisar de) conta na Corvia. A única defesa é o token — 32
bytes aleatórios (`DocumentShareLink.token`, gerado por `secrets.
token_urlsafe`), o mesmo padrão já usado em `password_reset_tokens`.

Por isso este router fica fora de `ROUTERS_ASSINANTES`, mas TAMBÉM fora do
espírito de `ROUTERS_LIVRES` como estava documentado em `main.py` até aqui
(entrar, recuperar senha, assinar, admin) — é a primeira rota do sistema
pensada para alguém que nunca terá login. Continua registrada em
`ROUTERS_LIVRES` porque a lista já é "sem `assinante_ativo`", que é o que
importa; o comentário de lá foi atualizado para refletir isso.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.clinical_docs import GeneratedDocument, Prescription
from app.models.compartilhamento import DocumentShareLink
from app.models.receituario import PrescriptionDocument, PrescriptionRecipient
from app.models.user import User
from app.services import cofre

router = APIRouter(prefix="/api/documentos-publicos", tags=["documentos públicos"])


def _pdf_receita(db: Session, referencia_id: int) -> tuple[bytes, str]:
    from app.services.pdf_documento import receituario_comum, resolver_endereco

    doc = db.get(PrescriptionDocument, referencia_id)
    if not doc or doc.status != "emitido":
        # Link pode ter sido criado e o documento nunca chegou a ser emitido
        # (não deveria acontecer, dado que `enviar_email` exige emitido, mas
        # o link sobrevive ao documento em teoria — mais seguro checar de novo
        # aqui do que confiar só na checagem de quando o link foi criado).
        raise HTTPException(status_code=404, detail="Documento não disponível.")
    presc = db.get(Prescription, doc.prescription_id)
    if not presc:
        raise HTTPException(status_code=404, detail="Documento não disponível.")
    medico = db.get(User, presc.created_by)

    dest = db.query(PrescriptionRecipient).filter(
        PrescriptionRecipient.prescription_id == presc.id).first()
    destinatario = {}
    if dest:
        destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
        if dest.endereco_cifrado:
            destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)

    pdf = receituario_comum(
        destinatario=destinatario, itens=doc.itens, observacoes=presc.notes or "",
        medico={
            "full_name": medico.full_name if medico else "",
            "council_name": medico.council_name if medico else None,
            "council_number": medico.council_number if medico else None,
            "council_state": medico.council_state if medico else None,
            "rqe": medico.rqe if medico else None,
            "specialty": medico.specialty if medico else None,
            "document_logo_url": medico.document_logo_url if medico else None,
        },
        endereco=resolver_endereco(medico, doc.endereco_exibido) if medico else None,
    )
    return pdf, f"receituario-{doc.id}.pdf"


def _pdf_documento(db: Session, referencia_id: int) -> tuple[bytes, str]:
    from app.services.pdf_documento import documento_generico, resolver_endereco

    g = db.get(GeneratedDocument, referencia_id)
    if not g:
        raise HTTPException(status_code=404, detail="Documento não disponível.")
    emissor = db.get(User, g.created_by)
    titulo = {"atestado": "Atestado", "laudo": "Laudo"}.get(g.doc_type, g.title)
    pdf = documento_generico(
        titulo=titulo, corpo=g.rendered_body,
        medico={
            "full_name": emissor.full_name if emissor else "",
            "council_name": emissor.council_name if emissor else None,
            "council_number": emissor.council_number if emissor else None,
            "council_state": emissor.council_state if emissor else None,
            "rqe": emissor.rqe if emissor else None,
            "specialty": emissor.specialty if emissor else None,
            "document_logo_url": emissor.document_logo_url if emissor else None,
        },
        endereco=resolver_endereco(emissor, g.endereco_exibido) if emissor else None,
    )
    return pdf, f"documento-{g.id}.pdf"


@router.get("/{token}")
def baixar_por_token(token: str, db: Session = Depends(get_db)):
    link = db.query(DocumentShareLink).filter(DocumentShareLink.token == token).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link inválido.")

    agora = datetime.now(timezone.utc)
    if agora > link.expires_at:
        raise HTTPException(status_code=410, detail="Este link expirou. Peça ao seu médico para enviar de novo.")

    if link.tipo == "prescription_document":
        pdf, nome_arquivo = _pdf_receita(db, link.referencia_id)
    elif link.tipo == "generated_document":
        pdf, nome_arquivo = _pdf_documento(db, link.referencia_id)
    else:
        raise HTTPException(status_code=500, detail="Tipo de link desconhecido.")

    link.acessos += 1
    if link.primeiro_acesso_em is None:
        link.primeiro_acesso_em = agora
    db.commit()

    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="{nome_arquivo}"'})
