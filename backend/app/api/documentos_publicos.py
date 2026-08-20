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
from app.services.assinatura import emissao as assinatura_emissao
from app.services.assinatura import validacao_publica
from app.services.professional_profile import document_identity

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

    def _regerar() -> bytes:
        # Só roda para documento emitido ANTES da Tarefa 4 (sem
        # `DocumentoEmitido`) — reproduz o PDF exatamente como saía antes:
        # sempre "MANUAL", com a data de quando foi de fato emitido.
        presc = db.get(Prescription, doc.prescription_id)
        if not presc:
            raise HTTPException(status_code=404, detail="Documento não disponível.")
        medico = db.get(User, presc.created_by)

        dest = db.query(PrescriptionRecipient).filter(
            PrescriptionRecipient.prescription_id == presc.id).first()
        destinatario = {"nome": "", "endereco": "", "documento": ""}
        if dest:
            destinatario["nome"] = cofre.decifrar_campo(dest.nome_cifrado, presc.id)
            if dest.endereco_cifrado:
                destinatario["endereco"] = cofre.decifrar_campo(dest.endereco_cifrado, presc.id)
            if dest.documento_cifrado:
                destinatario["documento"] = cofre.decifrar_campo(dest.documento_cifrado, presc.id)

        identidade = document_identity(medico) if medico else {"full_name": ""}
        endereco = resolver_endereco(medico, doc.endereco_exibido) if medico else None
        if doc.tipo_codigo == "RCE":
            from app.services.receita_controle_especial import receita_controle_especial

            identidade = dict(identidade)
            identidade["cpf"] = medico.cpf if medico else None
            return receita_controle_especial(
                destinatario=destinatario,
                itens=doc.itens,
                observacoes=presc.notes or "",
                medico=identidade,
                endereco_profissional=endereco,
                data_emissao=doc.emitido_em,
                cid=doc.cid,
            )

        return receituario_comum(
            destinatario=destinatario, itens=doc.itens, observacoes=presc.notes or "",
            medico=identidade, endereco=endereco, data_emissao=doc.emitido_em,
        )

    pdf = assinatura_emissao.servir_ou_regerar(
        db, tipo=assinatura_emissao.TIPO_RECEITA, referencia_id=doc.id, regerar=_regerar)
    nome = (
        f"receita-controle-especial-{doc.id}.pdf"
        if doc.tipo_codigo == "RCE" else f"receituario-{doc.id}.pdf"
    )
    return pdf, nome


def _pdf_material_paciente(db: Session, referencia_id: int, criado_por: int) -> tuple[bytes, str]:
    """Reaproveita `svc_material.gerar` — o mesmo gerador de PDF já usado em
    `GET /api/material-paciente/{slug}/pdf` (Tarefa 12). O papel timbrado
    sai com os dados de `criado_por` (quem gerou o link, sempre o médico que
    disparou o envio), não de um médico genérico — é a ele que o paciente
    volta com dúvida, mesma lógica já documentada em `exportacao.py`."""
    from app.models.patient_material import PatientMaterial
    from app.services import material_paciente as svc_material

    m = db.get(PatientMaterial, referencia_id)
    if not m or not m.published:
        raise HTTPException(status_code=404, detail="Material não disponível.")
    medico = db.get(User, criado_por)
    pdf = svc_material.gerar(m, document_identity(medico) if medico else {"full_name": ""})
    return pdf, f"material-{m.slug}.pdf"


def _pdf_documento(db: Session, referencia_id: int) -> tuple[bytes, str]:
    from app.services.pdf_documento import documento_generico, resolver_endereco

    g = db.get(GeneratedDocument, referencia_id)
    if not g:
        raise HTTPException(status_code=404, detail="Documento não disponível.")

    def _regerar() -> bytes:
        # Só roda para documento gerado ANTES da Tarefa 4 (sem
        # `DocumentoEmitido` — o primeiro download via `GET .../pdf` de
        # `documents.py` passou a emitir e persistir). "MANUAL" e
        # `g.created_at` reproduzem o que já saía antes, determinístico.
        emissor = db.get(User, g.created_by)
        titulo = {"atestado": "Atestado", "laudo": "Laudo"}.get(g.doc_type, g.title)
        return documento_generico(
            titulo=titulo, corpo=g.rendered_body,
            medico=document_identity(emissor) if emissor else {"full_name": ""},
            endereco=resolver_endereco(emissor, g.endereco_exibido) if emissor else None,
            data_emissao=g.created_at,
        )

    pdf = assinatura_emissao.servir_ou_regerar(
        db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=g.id, regerar=_regerar)
    return pdf, f"documento-{g.id}.pdf"


@router.get("/validar/{codigo}")
def validar_documento_publico(codigo: str, db: Session = Depends(get_db)):
    registro = validacao_publica.localizar(db, codigo)
    if registro is None:
        raise HTTPException(status_code=404, detail="Código de validação inválido ou documento não encontrado.")

    resultado = validacao_publica.validar(registro)
    return {
        "codigo": validacao_publica.codigo_documento(
            tipo=registro.tipo, referencia_id=registro.referencia_id, criado_por=registro.criado_por,
        ),
        "valido": resultado.valido,
        "tipo": registro.tipo,
        "metodo": registro.metodo,
        "nivel": registro.nivel,
        "integridade_hash": resultado.integridade_hash,
        "assinatura_encontrada": resultado.assinatura_encontrada,
        "assinatura_intacta": resultado.assinatura_intacta,
        "estrutura_valida": resultado.estrutura_valida,
        "cobre_documento_inteiro": resultado.cobre_documento_inteiro,
        "titular": resultado.titular,
        "emissor_certificado": resultado.emissor_certificado,
        "assinado_em": resultado.assinado_em,
        "qualificada_icp_brasil": resultado.qualificada_icp_brasil,
        "sha256": resultado.sha256,
        "aviso": (
            "A CorVIA confirmou os bytes persistidos e a integridade criptográfica da assinatura "
            "embutida no PDF. A validação oficial de cadeia de confiança, revogação e requisitos "
            "adicionais pode ser complementada pelo validador oficial do ITI/ICP-Brasil."
        ),
    }


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
    elif link.tipo == "patient_material":
        pdf, nome_arquivo = _pdf_material_paciente(db, link.referencia_id, link.criado_por)
    else:
        raise HTTPException(status_code=500, detail="Tipo de link desconhecido.")

    link.acessos += 1
    if link.primeiro_acesso_em is None:
        link.primeiro_acesso_em = agora
    db.commit()

    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'inline; filename="{nome_arquivo}"'})
