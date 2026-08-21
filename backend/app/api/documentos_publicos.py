# -*- coding: utf-8 -*-
"""Acesso público controlado a documentos clínicos emitidos pela CorVIA.

Há dois mecanismos independentes:
- `DocumentShareLink.token`: link aleatório e expirável criado para envio ao paciente;
- QR/código de validação: capability HMAC impressa dentro da revisão assinada.

A consulta de autenticidade nunca expõe dados clínicos do paciente. Códigos QR
novos de 128 bits também podem baixar o PDF original ASSINADO da receita; QR
legado de 64 bits permanece somente para validação, preservando compatibilidade
sem transformar um token antigo em credencial de acesso ao conteúdo clínico.
"""
import hashlib
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
        raise HTTPException(status_code=404, detail="Documento não disponível.")

    def _regerar() -> bytes:
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


def _contexto_publico_receita(db: Session, referencia_id: int) -> dict:
    """Somente fatos de emissão/prescritor; nunca nome, documento ou itens do paciente."""
    doc = db.get(PrescriptionDocument, referencia_id)
    if not doc or doc.status != "emitido":
        return {"confirmada_corvia": False, "emitido_em": None, "prescritor": None}
    presc = db.get(Prescription, doc.prescription_id)
    medico = db.get(User, presc.created_by) if presc else None
    prescritor = None
    if medico:
        conselho_nome = medico.council_name_other if medico.council_name == "OUTRO" else medico.council_name
        conselho_uf = medico.council_state_other if medico.council_name == "OUTRO" else medico.council_state
        prescritor = {
            "nome": medico.full_name,
            "conselho": conselho_nome or "CRM",
            "numero": medico.council_number or medico.crm,
            "uf": conselho_uf,
            "rqe": medico.rqe,
        }
    return {
        "confirmada_corvia": True,
        "emitido_em": doc.emitido_em,
        "prescritor": prescritor,
        "tipo_receita": doc.tipo_codigo,
    }


@router.get("/validar/{codigo}")
def validar_documento_publico(codigo: str, db: Session = Depends(get_db)):
    registro = validacao_publica.localizar(db, codigo)
    if registro is None:
        raise HTTPException(status_code=404, detail="Código de validação inválido ou documento não encontrado.")

    resultado = validacao_publica.validar(registro)
    contexto_receita = (
        _contexto_publico_receita(db, registro.referencia_id)
        if registro.tipo == assinatura_emissao.TIPO_RECEITA
        else {"confirmada_corvia": True, "emitido_em": registro.criado_em, "prescritor": None}
    )
    codigo_normalizado = validacao_publica.normalizar_codigo(codigo)
    pdf_original_disponivel = bool(
        registro.tipo == assinatura_emissao.TIPO_RECEITA
        and resultado.valido
        and validacao_publica.codigo_permite_download(codigo_normalizado)
    )
    return {
        "codigo": codigo_normalizado,
        "valido": resultado.valido,
        "tipo": registro.tipo,
        "tipo_receita": contexto_receita.get("tipo_receita"),
        "emissao_confirmada_corvia": contexto_receita["confirmada_corvia"],
        "emitido_em": resultado.registrado_corvia_em,
        "registrado_corvia_em": resultado.registrado_corvia_em,
        "prescritor": contexto_receita["prescritor"],
        "metodo": resultado.metodo_codigo,
        "metodo_nome": resultado.metodo_nome,
        "metodo_familia": resultado.metodo_familia,
        "nivel": registro.nivel,
        "fluxo_assinatura": resultado.fluxo_assinatura,
        "fluxo_assinatura_descricao": resultado.fluxo_assinatura_descricao,
        "integridade_hash": resultado.integridade_hash,
        "assinatura_encontrada": resultado.assinatura_encontrada,
        "assinatura_intacta": resultado.assinatura_intacta,
        "estrutura_valida": resultado.estrutura_valida,
        "cobre_documento_inteiro": resultado.cobre_documento_inteiro,
        "titular": resultado.titular,
        "emissor_certificado": resultado.emissor_certificado,
        "numero_serie_certificado": resultado.numero_serie,
        "certificado_valido_de": resultado.certificado_valido_de,
        "certificado_valido_ate": resultado.certificado_valido_ate,
        "certificado_valido_no_momento_assinatura": resultado.certificado_valido_no_momento_assinatura,
        "politicas_certificado": resultado.politicas_certificado,
        "assinado_em": resultado.assinado_em,
        "qualificada_icp_brasil": resultado.qualificada_icp_brasil,
        "cadeia_confianca_validada": False,
        "sha256": resultado.sha256,
        "pdf_original_disponivel": pdf_original_disponivel,
        "pdf_original_url": (
            f"/api/documentos-publicos/validar/{codigo_normalizado}/pdf"
            if pdf_original_disponivel else None
        ),
        "validacao_independente_url": "https://validar.iti.gov.br/",
        "aviso": (
            "A CorVIA confirmou o artefato persistido, seu SHA-256 e a integridade criptográfica "
            "da assinatura PAdES. A cadeia de confiança e revogação do certificado deve ser "
            "confirmada de forma independente no VALIDAR/ITI ou outro validador confiável."
        ),
    }


@router.get("/validar/{codigo}/pdf")
def baixar_pdf_original_validado(codigo: str, db: Session = Depends(get_db)):
    """Baixa os bytes EXATOS assinados da emissão identificada pela capability."""
    if not validacao_publica.codigo_permite_download(codigo):
        # QR legado continua autenticando metadados, mas não vira credencial de conteúdo.
        raise HTTPException(status_code=404, detail="PDF original indisponível para este código de validação.")
    registro = validacao_publica.localizar(db, codigo)
    if registro is None or registro.tipo != assinatura_emissao.TIPO_RECEITA:
        raise HTTPException(status_code=404, detail="Receita não encontrada.")
    resultado = validacao_publica.validar(registro)
    if not resultado.valido:
        raise HTTPException(
            status_code=409,
            detail="O PDF não será liberado porque a verificação de integridade/assinatura não foi concluída com sucesso.",
        )

    # Não usar `_pdf_receita()` aqui: essa função existe para links históricos e
    # pode procurar por referência/regenerar. A capability nova identifica um
    # DocumentoEmitido específico, então o download deve ler exatamente esse cofre.
    pdf = assinatura_emissao.ler_bytes(registro)
    if hashlib.sha256(pdf).hexdigest() != registro.sha256:
        raise HTTPException(
            status_code=409,
            detail="O PDF persistido diverge do SHA-256 registrado e não será liberado.",
        )
    doc = db.get(PrescriptionDocument, registro.referencia_id)
    nome_arquivo = (
        f"receita-controle-especial-{registro.referencia_id}.pdf"
        if doc and doc.tipo_codigo == "RCE"
        else f"receituario-{registro.referencia_id}.pdf"
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nome_arquivo}"',
            "Cache-Control": "private, no-store, max-age=0",
            "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
        },
    )


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
