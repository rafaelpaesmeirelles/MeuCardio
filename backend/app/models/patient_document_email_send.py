# -*- coding: utf-8 -*-
"""Auditoria da oferta de envio ao paciente por e-mail, pós-geração/assinatura
(pedido do Rafael, 08/08/2026): depois de concluir a assinatura digital de uma
prescrição/documento, ou de gerar um item de Material ao Paciente, o assinante
com CorvIA Mail ativo pode mandar o arquivo ao paciente sem sair da tela —
escolhendo entre o envio automático (Corvia, `contato@corvia.med.br`) ou o
envio pela própria caixa do CorvIA Mail (compositor pré-preenchido).

Uma tabela só, genérica pelos três `tipo_origem`, em vez de reescrever
`PatientMaterialSend` três vezes para uma diferença que é só de rótulo —
mesmo raciocínio já usado em `DocumentShareLink.tipo`/`DocumentoEmitido.tipo`.
Nunca decifra sozinha: `paciente_email_cifrado` usa o mesmo cofre AES-256-GCM
do resto do projeto (`app/services/cofre.py`), com o próprio id como dado
autenticado.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# Vocabulário igual ao de `DocumentShareLink.tipo`/`assinatura/emissao.py`.
TIPO_DOCUMENTO_GERADO = "generated_document"
TIPO_RECEITA = "prescription_document"
TIPO_MATERIAL = "patient_material"

CANAL_AUTO_CONTATO_CORVIA = "auto_contato_corvia"
CANAL_PROPRIO_CORVIA_MAIL = "proprio_corvia_mail"


class PatientDocumentEmailSend(Base):
    __tablename__ = "patient_document_email_sends"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo_origem: Mapped[str] = mapped_column(String(30), index=True)
    referencia_id: Mapped[int] = mapped_column(Integer, index=True)
    # "auto_contato_corvia" (SMTP, link seguro de 7/14 dias — nunca anexo) ou
    # "proprio_corvia_mail" (Mail360 da própria caixa do médico, com o PDF
    # anexado de verdade no compositor — decisão registrada no commit desta
    # tabela e em CLAUDE.md).
    canal: Mapped[str] = mapped_column(String(30))
    # Só existe quando `canal == auto_contato_corvia` (o envio pela própria
    # caixa não gera link — o anexo já é o próprio arquivo).
    share_link_id: Mapped[int | None] = mapped_column(
        ForeignKey("document_share_links.id"), nullable=True
    )
    enviado_por: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    paciente_email_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    # Se a frase de confirmação de assinatura (ver `assinatura/divulgacao_
    # email.py`) foi incluída no corpo/sugestão — só é possível quando o
    # documento tem `DocumentoEmitido.nivel == "qualificada"`.
    assinatura_confirmada: Mapped[bool] = mapped_column(Boolean, default=False)
    # Só é significativo para `canal == auto_contato_corvia` (envio síncrono,
    # sabe na hora se saiu). Para `proprio_corvia_mail`, o envio de fato só
    # acontece depois, quando o médico confirma no compositor do CorvIA Mail
    # — este registro marca só que o anexo foi preparado com sucesso.
    sucesso: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
