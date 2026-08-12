"""Cadastro de paciente REUTILIZÁVEL entre documentos (12/08/2026, pedido do
Rafael) — nome, CPF, nascimento, sexo, telefone, e-mail e endereço, cifrados
em repouso com o mesmo cofre AES-256-GCM já usado em
`PrescriptionRecipient`/`GeneratedDocument` (ver `app.services.cofre`).

Deliberadamente uma entidade SEPARADA do `Patient` do round hospitalar
(`app/models/round.py`), que continua anonimizado por decisão de
29/07/2026 (iniciais + número de prontuário, nunca nome/documento/endereço
— ver histórico em CLAUDE.md). Este cadastro é a contraparte identificável,
escopada por médico (`owner_id`, mesmo padrão de posse de
`DocumentTemplate.owner_id`/`Patient.created_by`), pensada para reaproveitar
dados de contato do paciente em QUALQUER fluxo de documento (modelo,
atestado rápido, solicitação de exames, documento em branco) sem reabrir o
debate de anonimizar o round.

Nada aqui é lido "ao vivo" para reconstruir um documento já emitido —
`GeneratedDocument.patient_snapshot_cifrado` congela o que foi de fato usado
no momento da emissão (regra permanente do projeto: documento histórico
nunca muda retroativamente, mesmo princípio do `pmc_snapshot`/`itens` da
Tarefa B/27)."""
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    full_name_cifrado: Mapped[bytes] = mapped_column(LargeBinary)
    cpf_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    # Não cifrados, mesmo padrão de `Patient.birth_date`/`Patient.sex` no
    # round — nunca foram tratados como campo cifrado neste projeto.
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(1), nullable=True)
    phone_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    email_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    # JSON cifrado de um blob só — {"logradouro","numero","complemento",
    # "bairro","cidade","uf","cep"} — em vez de 7 colunas cifradas
    # separadas: mais simples, e decifra tudo com uma chamada só.
    endereco_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
