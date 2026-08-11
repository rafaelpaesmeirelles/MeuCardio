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
    role: Mapped[str] = mapped_column(String(30), default="medico")
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), unique=True, nullable=True, index=True)
    profession: Mapped[str | None] = mapped_column(String(80), nullable=True)
    council_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    council_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    council_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    # Preenchidos só quando council_name == "OUTRO" (08/08/2026, pedido do
    # Rafael) — o nome real do conselho e o estado/região em texto livre,
    # já que "OUTRO" sozinho não identifica o conselho e a UF de 2 letras
    # não serve pra região não-brasileira. council_name continua "OUTRO"
    # literal (é o que escopo_profissional.escopo_de() usa pro fail-closed
    # do escopo de prescrição) — estes dois campos são só para EXIBIÇÃO,
    # nunca para decisão de escopo/permissão.
    council_name_other: Mapped[str | None] = mapped_column(String(120), nullable=True)
    council_state_other: Mapped[str | None] = mapped_column(String(60), nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rqe: Mapped[str | None] = mapped_column(String(40), nullable=True)
    professional_title: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workplace_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_department: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_role: Mapped[str | None] = mapped_column(String(180), nullable=True)
    workplace_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    include_workplace_on_documents: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_completion_required: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crm: Mapped[str | None] = mapped_column(String(40), nullable=True)
    document_logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

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
    practice_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="aprovado")
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    boas_vindas_pendente: Mapped[bool] = mapped_column(Boolean, default=False)
    # Tour guiado do primeiro acesso já com assinatura ativa (Trabalho 13,
    # 06/08/2026) — coluna já existia desde a migração b3f8a1d92e64
    # (03/08/2026, funil público→assinante), nunca tinha sido exposta no
    # model nem usada por código nenhum até agora.
    onboarding_visto: Mapped[bool] = mapped_column(Boolean, default=False)

    # Médico convidado — acesso cortesia completo (08/08/2026, pedido do
    # Rafael). Passa pelo fluxo real de cadastro/KYC/pagamento, mas:
    # `criar_checkout` (app/api/billing.py) libera a assinatura sem cobrar
    # e sem redirecionar ao Stripe; `verificacao.submeter` (KYC) aprova
    # automaticamente em vez de cair na fila de revisão manual. Ligado só
    # por admin, via `PATCH /api/admin/users/{id}/convidado` — nunca pelo
    # próprio usuário.
    convidado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Investidor — acesso cortesia de demonstração (issue #52, frente de
    # entitlement). Mesmo espírito do `convidado` acima, mas identidade
    # distinta de propósito: não é um médico real passando pelo fluxo de
    # KYC/cadastro profissional, é uma conta de avaliação do produto.
    # `tem_acesso_ao_produto()` (app/services/entitlement.py) trata os dois
    # como fontes de acesso administrativo equivalentes, mas o KYC nunca é
    # exigido de investidor (`_kyc_required`), e a tela de Assinatura
    # distingue a origem só para efeito de texto exibido. Ligado só por
    # admin, via `PATCH /api/admin/users/{id}/investidor` — nunca pelo
    # próprio usuário. Migração 66717ca01f2d.
    investidor: Mapped[bool] = mapped_column(Boolean, default=False)

    # Plano que o convidado deve receber ao assinar, quando o cadastro veio
    # de uma pré-autorização (08/08/2026, pedido do Rafael — admin escolhe
    # por linha se aquele convidado tem CorvIA Mail ou não). None significa
    # "sem preferência registrada": tanto convidado marcado direto pelo
    # admin (toggle, sem pré-autorização) quanto pré-autorização antiga sem
    # esse campo caem no padrão PLANO_COMPLETO já usado por
    # `criar_checkout()` — nenhuma mudança de comportamento pra quem já
    # usava o caminho antigo.
    convidado_plano_preferido: Mapped[str | None] = mapped_column(String(20), nullable=True)

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    show_online_status: Mapped[bool] = mapped_column(Boolean, default=False)

    sessions_valid_after: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assinatura_metodo_preferido: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Consentimento específico para o assistente de IA acionar ferramentas
    # (agenda e CorvIA Mail do próprio médico) em vez de só responder texto.
    # Presença de `ia_ferramentas_consent_em` = consentiu; ausência = nunca
    # consentiu ou revogou. Mesmo padrão de MobilityPreference (versão +
    # timestamp), porque também é consentimento sobre ação automatizada
    # sobre dado real, não preferência de exibição.
    ia_ferramentas_consent_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ia_ferramentas_consent_versao: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Assinatura de e-mail (logo Corvia + logo/dados profissionais) anexada
    # ao final de todo e-mail enviado pelo CorvIA Mail — nativo ou contas
    # externas conectadas. Desligada por padrão (opt-in). Telefone e endereço
    # profissional são sub-opções independentes: o médico pode querer nome/
    # CRM/logo na assinatura sem publicar telefone ou endereço do consultório.
    email_assinatura_ativa: Mapped[bool] = mapped_column(Boolean, default=False)
    email_assinatura_incluir_telefone: Mapped[bool] = mapped_column(Boolean, default=False)
    email_assinatura_incluir_endereco: Mapped[bool] = mapped_column(Boolean, default=False)

    # Conta usada por padrão ao abrir o CorvIA Mail para escrever uma
    # mensagem nova (Trabalho 9, painel "Administre suas contas"). Guarda o
    # mesmo `id` que o frontend já usa em ContaEmail — "corvia" para a caixa
    # nativa, ou o id (string) da CalendarIntegration para conta externa.
    # None = comportamento de sempre, abre na caixa nativa. Não é FK: o id
    # pode apontar pra uma integração que foi desconectada depois, e nesse
    # caso o frontend cai de volta pro nativo em vez de quebrar.
    email_conta_padrao_envio: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Instagram opcional no cadastro (tarefa #43, 08/08/2026) — campo livre
    # que o próprio médico digita se quiser; NUNCA buscado/adivinhado pelo
    # sistema por nome ou e-mail (correlação automática foi rejeitada por
    # LGPD/ToS da plataforma, decisão já tomada com o Rafael). Sem "@" na
    # frente (normalizado em SolicitacaoAcesso). instagram_photo_url é
    # preenchido em segundo plano, melhor esforço, a partir DESSE handle
    # específico — ver app/services/instagram_profile.py; fica None se a
    # busca falhar, o perfil for privado ou não existir.
    instagram_handle: Mapped[str | None] = mapped_column(String(60), nullable=True)
    instagram_photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)


@event.listens_for(User.password_hash, "set")
def _revogar_sessoes_ao_trocar_senha(target, value, oldvalue, initiator) -> None:
    if oldvalue is not NO_VALUE and oldvalue is not None and value != oldvalue:
        target.sessions_valid_after = datetime.now(timezone.utc)
