"""Política de acesso KYC compartilhada entre a sessão e a emissão clínica."""
from fastapi import HTTPException
from app.services.entitlement import eh_socio, tem_acesso_ao_produto
from app.services.kyc import verificacao


def kyc_required(db, user) -> bool:
    if (user.role == "admin" and not eh_socio(user)) or user.investidor:
        return False
    if not tem_acesso_ao_produto(db, user):
        return False
    return not verificacao.liberado_para_uso(verificacao.obter(db, user))


def exigir_liberacao_emissao(db, user) -> None:
    if user.investidor:
        raise HTTPException(status_code=403, detail="Conta de demonstração é somente leitura; a emissão não está disponível.")
    if kyc_required(db, user):
        raise HTTPException(status_code=403, detail="Conclua a verificação de identidade antes de emitir documentos clínicos.")
