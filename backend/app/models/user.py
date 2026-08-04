from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import NO_VALUE

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="medico")  # admin|medico|residente|leitor
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- dados profissionais, coletados no cadastro (auto ou pelo admin) -----
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True, index=True)
    profession: Mapped[str | None] = mapped_column(String(80), nullable=True)
    council_name: Mapped[str | None] = mapped_column(String(20), nullable=True)  # CRM, COREN, CRF...
    council_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    council_state: Mapped[str | None] = mapped_column(String(2), nullable=True)  # UF, ex.: SP
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rqe: Mapped[str | None] = mapped_column(String(40), nullable=True)  # registro de qualificação de especialista
    professional_title: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workplace_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_department: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_role: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    include_workplace_on_documents: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crm: Mapped[str | None] = mapped_column(String(40), nullable=True)  # mantido por compatibilidade
    # Logo pessoal/do consultório do médico (Tarefa 29, pedido do Rafael em
    # 30/07/2026) — usado JUNTO da logo da Corvia no cabeçalho de receita e
    # documento, não em vez dela. Mesmo padrão de armazenamento de `photo_url`
    # (volume /uploads, servido pelo Caddy em /logos/*), mas endpoint e pasta
    # próprios: são conceitos diferentes (foto de perfil da conta x logo que
    # vai impresso no papel timbrado).
    document_logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- endereços, acrescentados em 30/07/2026 (Tarefa 29) -------------------
    # Dois endereços completos, não um: decisão do Rafael foi deixar o médico
    # escolher, a cada receita/documento emitido, se o cabeçalho/rodapé mostra
    # o residencial ou o profissional (privacidade — nem todo médico quer o
    # endereço de casa impresso num papel que o paciente leva embora). Os dois
    # nascem vazios; nada aparece no PDF até o médico preencher em Minha Conta
    # e escolher qual usar na hora de emitir.
    home_street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    home_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    home_complement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    home_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    home_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    home_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)

    practice_street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    practice_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    practice_complement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    practice_neighborhood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    practice_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    practice_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    practice_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)
    # Exigido por lei especificamente para receita de anabolizantes/hormônios
    # (Lei nº 9.965/2000, art. 1º, parágrafo único: "...o endereço e telefone
    # profissionais..."), verificado direto na fonte em 30/07/2026. Só o
    # profissional — a lei não menciona telefone residencial, e não há
    # necessidade de guardar um.
    practice_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # --- fila de aprovação -----------------------------------------------
    status: Mapped[str] = mapped_column(String(20), default="aprovado")
    # pendente | aprovado | rejeitado — contas criadas pelo admin nascem aprovadas;
    # contas por autocadastro nascem pendentes e ficam inativas até um admin decidir.
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Mensagem de boas-vindas pessoal, mostrada uma vez só no primeiro acesso
    # (pedido do Rafael, 31/07/2026, para o próprio pai). Nasce False pra todo
    # mundo; é setada True manualmente só em quem deve recebê-la, e volta a
    # False assim que a pessoa fecha o popup — não é sistema genérico de
    # avisos, é este recado específico.
    boas_vindas_pendente: Mapped[bool] = mapped_column(Boolean, default=False)

    # Atualizado a cada requisição autenticada (com throttle, ver
    # `current_user` em core/security.py) — base do painel de "usuários
    # online" do admin (Tarefa de 31/07/2026). "Online" é derivado no momento
    # da consulta (últimos 5 minutos), não é um booleano gravado.
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Tokens de aplicação emitidos neste instante ou antes são recusados.
    # Nulo preserva sessões anteriores à implantação até ocorrer troca de senha
    # ou encerramento explícito de todas as sessões.
    sessions_valid_after: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Método de assinatura preferido do médico (Tarefa 4) — código do
    # catálogo em `services/assinatura/catalogo.py` (ex.: "MANUAL", "VIDAAS").
    # Só o DEFAULT sugerido na tela de emissão; o médico ainda escolhe (ou
    # troca) a cada documento. Nulo = usa `settings.assinatura_metodo_padrao`.
    assinatura_metodo_preferido: Mapped[str | None] = mapped_column(String(20), nullable=True)


@event.listens_for(User.password_hash, "set")
def _revogar_sessoes_ao_trocar_senha(target, value, oldvalue, initiator) -> None:
    """Centraliza a invalidação para troca autenticada, reset e ações admin."""
    if oldvalue is not NO_VALUE and oldvalue is not None and value != oldvalue:
        target.sessions_valid_after = datetime.now(timezone.utc)
