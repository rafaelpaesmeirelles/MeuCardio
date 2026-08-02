"""Envio de material do paciente por e-mail, do endereço do médico (02/08/2026).

Companheira de `DocumentShareLink` no mesmo padrão já usado em
`PrescriptionRecipient`/`Prescription`: o link genérico cuida de token,
validade e contador de acesso; esta tabela guarda o que é específico do
envio ao paciente — e-mail e recado cifrados (mesmo cofre do receituário),
consentimento registrado por envio, e quem enviou.

Por que não juntar tudo em `DocumentShareLink`: esse modelo é
deliberadamente genérico (mesma tabela para receita e documento gerado) e
não tem — nem deve ganhar — colunas específicas de um único tipo de uso. Um
material da biblioteca (`patient_materials`) é item de catálogo compartilhado,
reenviado por médicos diferentes para pacientes diferentes; a identificação do
paciente e o consentimento são por ENVIO, não por material.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PatientMaterialSend(Base):
    __tablename__ = "patient_material_sends"

    id: Mapped[int] = mapped_column(primary_key=True)
    share_link_id: Mapped[int] = mapped_column(
        ForeignKey("document_share_links.id", ondelete="CASCADE"), unique=True, index=True
    )
    material_id: Mapped[int] = mapped_column(ForeignKey("patient_materials.id"), index=True)
    enviado_por: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    paciente_email_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    recado_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    consentimento_confirmado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Como o e-mail saiu: "mail360" (endereço próprio do médico) ou "smtp_corvia"
    # (fallback — não deveria acontecer em produção, já que o botão fica
    # desabilitado sem CorvIA Mail, mas registrar de qual canal saiu ajuda a
    # auditar se isso um dia acontecer por bug).
    canal: Mapped[str] = mapped_column(Text, default="mail360")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
