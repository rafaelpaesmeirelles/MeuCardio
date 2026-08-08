# -*- coding: utf-8 -*-
"""Prepara o anexo do documento/material para o compositor do CorvIA Mail,
quando o médico escolhe enviar do próprio e-mail em vez do envio automático
pela Corvia (pedido do Rafael, 08/08/2026 — ver `app/models/patient_document_
email_send.py` para o desenho completo dos dois canais).

Sobe o PDF para o Mail360 usando a caixa NATIVA do próprio médico
(`EmailAccount`), lendo o `account_key` direto do banco — sem depender do
token de sessão separado da caixa de e-mail (`scope="email"`, ver
`core/security.py`), porque quem chama esta função já está autenticado na
sessão comum da Corvia (`current_user`) no momento em que o documento acabou
de ser gerado/assinado. O médico só entra na "sessão email" de fato quando
o frontend navega para `/caixa-de-email` — o anexo já estará pronto lá,
referenciado pelo `file_id` que o Mail360 devolveu aqui.

Diferente de `app/api/email.py::enviar_anexo` (upload multipart pela sessão
de e-mail, usado quando o médico anexa algo manualmente dentro da caixa),
esta função nunca é chamada com um arquivo arbitrário do usuário — sempre
com o PDF do próprio documento clínico que passou pelas mesmas checagens de
posse/assinatura da rota que a invoca."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.email_account import EmailAccount
from app.services import mail360
from app.services.mail360 import Mail360Error


class AnexoIndisponivel(Exception):
    """Sem caixa nativa do CorvIA Mail ativa, ou falha ao subir o anexo no
    Mail360 — quem chama decide o código HTTP (409 no primeiro caso, 502 no
    segundo)."""


@dataclass
class AnexoPreparado:
    file_id: str
    nome: str


def obter_conta_nativa_ativa(db: Session, user) -> EmailAccount:
    conta = db.query(EmailAccount).filter(EmailAccount.user_id == user.id).first()
    if not conta or conta.status != "ativa":
        raise AnexoIndisponivel("Sua caixa do CorvIA Mail não está ativa.")
    return conta


def preparar(db: Session, user, *, nome_arquivo: str, conteudo: bytes) -> AnexoPreparado:
    conta = obter_conta_nativa_ativa(db, user)
    try:
        file_id = mail360.upload_anexo(conta.mail360_account_key, nome_arquivo, conteudo)
    except Mail360Error as e:
        raise AnexoIndisponivel(str(e)) from e
    return AnexoPreparado(file_id=file_id, nome=nome_arquivo)
