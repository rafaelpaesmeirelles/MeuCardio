from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PartnerCourse(Base):
    """Curso de parceiro externo revendido dentro do MeuCardio.

    O que este modelo NÃO guarda: vídeo. Aula ao vivo e gravada continuam no
    ambiente do parceiro, e aqui ficam só os links de acesso. O que ele guarda
    de verdade é o material de apoio (em `CourseMaterial`) e as condições
    comerciais.
    """

    __tablename__ = "partner_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(200))
    parceiro: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Frase de destaque exibida no Painel. `frase_destaque_fonte` é obrigatória
    # sempre que houver frase: índice de aprovação é afirmação de terceiro sobre
    # resultado de curso, e a régua do produto é a mesma do conteúdo clínico —
    # ou o parceiro fornece o dado e ele aparece atribuído a ele, ou não aparece.
    # A rota de cadastro recusa frase sem fonte, para o número não chegar ao
    # Painel sem procedência.
    frase_destaque: Mapped[str | None] = mapped_column(String(300), nullable=True)
    frase_destaque_fonte: Mapped[str | None] = mapped_column(String(300), nullable=True)

    link_aula_ao_vivo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    link_aulas_gravadas: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Centavos, sempre. Guardar dinheiro em float é como este projeto não faz.
    preco_parceiro_centavos: Mapped[int] = mapped_column(Integer)
    margem_centavos: Mapped[int] = mapped_column(Integer)
    # Preço e margem são por curso, nunca fixos no código: cada parceiro negocia
    # o seu. O valor cobrado do médico é a soma dos dois, calculada no servidor.

    # Conta conectada do parceiro no Stripe. Sem ela não há repasse automático,
    # e a rota de checkout recusa a venda em vez de cobrar sem ter como repassar.
    stripe_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    destaque: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # `destaque` escolhe qual curso aparece no cartão do Painel. Trocar é mudar
    # esta coluna em dois registros — sem deploy, sem mexer em código.

    # Vínculo com trilha de estudo e caso clínico da Tarefa 11. Fica como lista
    # de slugs em JSONB de propósito: as tabelas de trilha e de caso clínico
    # ainda não existem, e uma chave estrangeira para tabela inexistente
    # impediria a migração de rodar. Quando a Tarefa 11 chegar, isto vira
    # relacionamento de verdade sem perder o que já foi cadastrado.
    trilhas_vinculadas: Mapped[list] = mapped_column(JSONB, default=list)
    casos_vinculados: Mapped[list] = mapped_column(JSONB, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def preco_total_centavos(self) -> int:
        """O que o médico paga. Calculado, nunca recebido do cliente — mesma
        regra já adotada no preço do telediagnóstico."""
        return self.preco_parceiro_centavos + self.margem_centavos


class CourseMaterial(Base):
    """Apostila ou documento de apoio enviado pelo curso.

    Fica em volume próprio, **não montado no Caddy**, servido por rota
    autenticada — mesmo raciocínio do cofre de exames: arquivo que só quem pagou
    pode abrir não pode ter URL alcançável de fora. Sem a cifragem do cofre, que
    existe lá porque aquilo é dado de paciente; aqui é material didático.
    """

    __tablename__ = "course_materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("partner_courses.id", ondelete="CASCADE"), index=True
    )
    titulo: Mapped[str] = mapped_column(String(200))
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    caminho: Mapped[str] = mapped_column(String(500))
    tamanho_bytes: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(100))
    enviado_por: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CoursePayment(Base):
    """Uma cobrança de assinatura de curso, com os três valores separados.

    A separação existe por causa da contabilidade: só a margem é receita do
    MeuCardio. O repasse é dinheiro de terceiro que apenas transita por aqui, e
    somá-lo ao faturamento infla a receita com valor que nunca foi nosso — que é
    exatamente o que o contador precisa conseguir reconciliar, e o que a emissão
    de nota fiscal dos dois lados vai exigir separado.
    """

    __tablename__ = "course_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("partner_courses.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    stripe_invoice_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    bruto_centavos: Mapped[int] = mapped_column(Integer)       # cobrado do médico
    repasse_centavos: Mapped[int] = mapped_column(Integer)     # passivo com o parceiro
    margem_centavos: Mapped[int] = mapped_column(Integer)      # receita própria
    moeda: Mapped[str] = mapped_column(String(3), default="brl")

    competencia: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
