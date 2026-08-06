"""Verificação de identidade pós-pagamento (Trabalho 11, 06/08/2026).

Diferente do gate de aprovação de CONTA que já existe (`User.status`,
`app/api/auth.py::solicitar_acesso` + `app/api/admin.py::decidir`) — aquele
é texto (nome, CRM, especialidade), decidido ANTES de existir assinatura
paga. Este é depois: assinante já pagou, precisa enviar foto do documento
profissional (frente/verso), documento de identificação pessoal
(frente/verso, ou PDF de documento digital gov.br/CNH Digital) e uma selfie
capturada ao vivo pela câmera — e só tem liberação plena depois de revisão
humana definitiva, mesmo que a checagem automática de CRM já tenha
liberado o uso na hora.

Arquivos ficam cifrados no cofre já existente (`services/cofre.py`), nunca
em coluna, nunca com URL alcançável — PII de identidade é dado tão sensível
quanto exame de paciente ou chave privada de certificado.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class KycVerification(Base):
    __tablename__ = "kyc_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    doc_profissional_frente: Mapped[str] = mapped_column(String(120))
    doc_profissional_verso: Mapped[str] = mapped_column(String(120))
    # Documento pessoal: OU as duas fotos, OU o PDF do documento digital —
    # nunca os dois conjuntos, a rota decide qual veio e zera o outro par.
    doc_pessoal_frente: Mapped[str | None] = mapped_column(String(120), nullable=True)
    doc_pessoal_verso: Mapped[str | None] = mapped_column(String(120), nullable=True)
    doc_pessoal_digital: Mapped[str | None] = mapped_column(String(120), nullable=True)
    selfie: Mapped[str] = mapped_column(String(120))

    # "aguardando_revisao" (padrão) | "liberado_conselho_ok" (checagem
    # automática confirmou registro ativo — hoje só existe para CRM) |
    # "liberado_sem_checagem" (não-médico: nenhuma checagem automática
    # existe para o conselho dele, liberado por decisão do Rafael em
    # 06/08/2026 — ver `app/services/kyc/verificacao.py`) | "aprovado" |
    # "rejeitado"
    status: Mapped[str] = mapped_column(String(30), default="aguardando_revisao", index=True)

    # "ativo_confirmado" | "nao_confirmado" | "erro_checagem" |
    # "indisponivel_para_conselho" — melhor esforço; hoje só o CRM tem
    # webservice em potencial (CFM, pago, sem credencial ainda). Nenhum
    # outro conselho (CRO/CRBM/COREN/CRF/CREFITO/CRN/CRP/CREF/CRESS) tem
    # API pública documentada — ver `app/services/kyc/council_check.py`.
    conselho_check_status: Mapped[str] = mapped_column(String(30), default="nao_verificado")
    conselho_check_detalhe: Mapped[str | None] = mapped_column(String(500), nullable=True)
    conselho_check_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    liberado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    aprovado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    aprovado_por: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    nota_revisao: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)
