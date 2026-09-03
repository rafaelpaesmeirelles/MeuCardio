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
from app.services.investidor_demo import MENSAGEM_MODO_INVESTIDOR
from app.services.kyc import auto_flow, verificacao

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


def _status_publico(registro: KycVerification | None, *, waivers: dict[str, bool] | None = None) -> dict:
    extras = {}
    if waivers is not None:
        extras = {
            "waivers": waivers,
            "requirements": {campo: not ativo for campo, ativo in waivers.items()},
        }
    if registro is None:
        return {"status": None, "liberado": False, **extras}
    return {
        "status": registro.status,
        "liberado": verificacao.liberado_para_uso(registro),
        "conselho_check_status": registro.conselho_check_status,
        "criado_em": registro.criado_em,
        # A justificativa interna da validação automática fica restrita ao
        # admin. O assinante recebe nota apenas quando há uma decisão humana
        # explícita de rejeição/reenvio, como já ocorria antes.
        "nota_revisao": (
            registro.nota_revisao if registro.status in ("rejeitado", "reenvio_solicitado") else None
        ),
        **extras,
    }


@router.get("/status")
def meu_status(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return _status_publico(
        verificacao.obter(db, user),
        waivers=verificacao.dispensas_aplicaveis(db, user) if user.convidado else None,
    )


@router.post("/submeter", status_code=201)
async def submeter_verificacao(
    selfie: UploadFile | None = File(None),
    doc_profissional_frente: UploadFile | None = File(None),
    doc_profissional_verso: UploadFile | None = File(None),
    doc_pessoal_frente: UploadFile | None = File(None),
    doc_pessoal_verso: UploadFile | None = File(None),
    doc_pessoal_digital: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    """Submete KYC apenas para contas reais.

    Para médico CRM normal, a mesma requisição consulta o CFM e compara
    cadastro + documentos. Só uma validação inequívoca termina em ``aprovado``
    e libera o uso. Negativo ou inconclusivo permanece bloqueado e cai na
    fila administrativa com todos os arquivos cifrados disponíveis ao admin.
    """
    if user.investidor:
        raise HTTPException(status_code=403, detail=MENSAGEM_MODO_INVESTIDOR)

    docs = verificacao.DocumentosSubmissao(
        doc_profissional_frente=await _ler(doc_profissional_frente),
        doc_profissional_verso=await _ler(doc_profissional_verso),
        selfie=await _ler(selfie),
        doc_pessoal_frente=await _ler(doc_pessoal_frente),
        doc_pessoal_verso=await _ler(doc_pessoal_verso),
        doc_pessoal_digital=await _ler(doc_pessoal_digital),
    )
    try:
        registro = auto_flow.submeter_com_auto_validacao(db, user, docs)
    except (
        verificacao.DocumentoPessoalIncompleto,
        verificacao.DocumentoProfissionalIncompleto,
        verificacao.SelfieObrigatoria,
    ) as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    return _status_publico(
        registro,
        waivers=verificacao.dispensas_aplicaveis(db, user) if user.convidado else None,
    )
