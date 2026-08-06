"""Verificação de identidade pós-pagamento (Trabalho 11, 06/08/2026) —
lado do assinante: submeter documentos/selfie e consultar o próprio status.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.core.uploads import UploadRejected, validate_file
from app.models.kyc import KycVerification
from app.models.user import User
from app.services.kyc import verificacao

router = APIRouter(prefix="/api/kyc", tags=["verificação de identidade"])

TAMANHO_MAXIMO_DOCUMENTO = 8 * 1024 * 1024  # 8 MB — foto de celular cabe folgado


async def _ler(arquivo: UploadFile | None) -> bytes | None:
    """Além do tamanho, valida assinatura de arquivo (magic bytes) — imagem
    ou PDF, mesma política já usada pro exame de paciente (`kind="exam"`
    em `core/uploads.py`), nunca confia só na extensão/Content-Type
    declarado pelo navegador."""
    if arquivo is None:
        return None
    conteudo = await arquivo.read(TAMANHO_MAXIMO_DOCUMENTO + 1)
    if len(conteudo) > TAMANHO_MAXIMO_DOCUMENTO:
        raise HTTPException(status_code=413, detail=f"Arquivo '{arquivo.filename}' maior que 8 MB.")
    if not conteudo:
        return None
    try:
        validate_file(conteudo, arquivo.filename or "documento", "exam")
    except UploadRejected as erro:
        raise HTTPException(status_code=erro.status_code, detail=f"'{arquivo.filename}': {erro.detail}") from None
    return conteudo


def _status_publico(registro: KycVerification | None) -> dict:
    if registro is None:
        return {"status": None, "liberado": False}
    return {
        "status": registro.status,
        "liberado": verificacao.liberado_para_uso(registro),
        "crm_check_status": registro.crm_check_status,
        "criado_em": registro.criado_em,
        "nota_revisao": registro.nota_revisao if registro.status == "rejeitado" else None,
    }


@router.get("/status")
def meu_status(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return _status_publico(verificacao.obter(db, user))


@router.post("/submeter", status_code=201)
async def submeter_verificacao(
    doc_profissional_frente: UploadFile = File(...),
    doc_profissional_verso: UploadFile = File(...),
    selfie: UploadFile = File(...),
    doc_pessoal_frente: UploadFile | None = File(None),
    doc_pessoal_verso: UploadFile | None = File(None),
    doc_pessoal_digital: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    docs = verificacao.DocumentosSubmissao(
        doc_profissional_frente=await _ler(doc_profissional_frente),
        doc_profissional_verso=await _ler(doc_profissional_verso),
        selfie=await _ler(selfie),
        doc_pessoal_frente=await _ler(doc_pessoal_frente),
        doc_pessoal_verso=await _ler(doc_pessoal_verso),
        doc_pessoal_digital=await _ler(doc_pessoal_digital),
    )
    if not docs.doc_profissional_frente or not docs.doc_profissional_verso or not docs.selfie:
        raise HTTPException(status_code=422, detail="Documento profissional (frente e verso) e selfie são obrigatórios.")

    try:
        registro = verificacao.submeter(db, user, docs)
    except verificacao.DocumentoPessoalIncompleto as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    return _status_publico(registro)
