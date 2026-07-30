from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Prescription(Base):
    """Prescrição gerada a partir do comparador de medicamentos. Guardada
    para histórico/timeline — sem validade legal por si só, é documento
    pra impressão/assinatura manual até existir integração de assinatura
    digital (fase futura)."""

    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Opcional: o receituário tem destinatário próprio e cifrado, em
    # `prescription_recipients`. Exigir paciente de round para emitir receita
    # obrigaria a criar registro de internação para paciente de ambulatório.
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    items: Mapped[list] = mapped_column(JSONB, default=list)
    # [{"drug_name": str, "presentation": str, "posology": str, "orientation": str}]
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class DocumentTemplate(Base):
    """Modelo reutilizável de atestado/laudo, com variáveis {{nome}} que
    o médico preenche na hora de gerar. Cada usuário cria e mantém os seus —
    exceto os modelos do sistema (`owner_id IS NULL`, acrescentado em
    30/07/2026, Tarefa 30): pesquisados de fonte confiável e disponíveis
    para qualquer médico usar, sem poder editar nem apagar (a checagem de
    posse já existente, `owner_id == user.id`, nunca casa com `None` — não
    precisou de exceção nova no código de edição/exclusão)."""

    __tablename__ = "document_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    doc_type: Mapped[str] = mapped_column(String(30))  # atestado | laudo | outro
    body: Mapped[str] = mapped_column(Text)  # texto com {{variaveis}}
    # Slug estável só para os modelos do sistema, usado no upsert do
    # semeador (para não duplicar a cada rodada). Nulo em modelo de médico.
    slug_sistema: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GeneratedDocument(Base):
    """Registro do documento já preenchido e gerado — pra histórico/timeline,
    não é o template em si (esse fica em DocumentTemplate)."""

    __tablename__ = "generated_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    doc_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    rendered_body: Mapped[str] = mapped_column(Text)
    # Acrescentado em 30/07/2026 (Tarefa 29 — enviar documento por e-mail).
    # Cifrado com o mesmo cofre do receituário — sem entidade "Recipient"
    # própria aqui porque este documento já não tem paciente identificável
    # em nenhum outro campo (`patient_id` aponta pro Patient anonimizado).
    destinatario_email_cifrado: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    # Acrescentado em 30/07/2026 (Tarefa 29 — letterhead). Mesma lógica do
    # campo homônimo em PrescriptionDocument: gravado na geração, não
    # recalculado depois, para o PDF sair idêntico toda vez que for reaberto.
    endereco_exibido: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Appointment(Base):
    """Agenda de consultas — cada profissional só vê a própria agenda.
    Paciente pode ser um já cadastrado no Round, ou só um nome/telefone
    avulso (nem todo agendamento já tem prontuário aberto)."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True)
    patient_name_temp: Mapped[str | None] = mapped_column(String(200), nullable=True)
    patient_phone_temp: Mapped[str | None] = mapped_column(String(30), nullable=True)

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    appointment_type: Mapped[str] = mapped_column(String(40), default="consulta")
    # consulta | retorno | exame | outro
    status: Mapped[str] = mapped_column(String(20), default="confirmado")
    # confirmado | cancelado | realizado | faltou
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
