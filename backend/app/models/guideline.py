from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Guideline(Base):
    """Uma diretriz publicada, como entidade própria.

    Antes disso, a diretriz de origem existia apenas dentro do texto livre de
    `source_refs` — dava para ler, não para consultar. Sem entidade própria não
    há como responder à pergunta que a Tarefa 9 faz: "a ESC de fibrilação atrial
    foi revisada; que conteúdo do MeuCardio depende dela e quem usa esse
    conteúdo?".

    `superseded_by_id` é o que dispara o alerta. Ele registra que uma diretriz
    nova substituiu esta — e note que isso **não** significa que o conteúdo do
    MeuCardio ficou errado. São coisas diferentes, e a distinção é do próprio
    briefing: o alerta avisa que existe revisão publicada a considerar, não que
    o texto daqui esteja desatualizado. Quem decide isso é a revisão humana.
    """

    __tablename__ = "guidelines"
    __table_args__ = (UniqueConstraint("slug", name="uq_guideline_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), index=True)
    org: Mapped[str] = mapped_column(String(40), index=True)
    # ESC | AHA | ACC | SBC | EACTS | ERS | EAS | SCAI | OMS | outras
    titulo: Mapped[str] = mapped_column(String(300))
    ano: Mapped[int] = mapped_column(Integer, index=True)
    tema: Mapped[str | None] = mapped_column(String(120), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(160), nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    superseded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("guidelines.id"), nullable=True, index=True
    )
    substituida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Momento em que o admin registrou a substituição. Serve para o alerta saber
    # o que é novidade desde a última vez que o assinante foi avisado.

    alerta_enviado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Sem isto, reprocessar a fila reenviaria o mesmo aviso a cada execução.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class GuidelineLink(Base):
    """Liga uma diretriz a um item de conteúdo.

    Genérico em `(item_type, item_id)`, no mesmo padrão de `Favorite`, porque a
    Tarefa 9 fala de protocolo, medicamento e calculadora — e amanhã pode falar
    de fluxograma ou caso clínico. Chave estrangeira por tipo obrigaria uma
    tabela nova a cada frente de conteúdo.
    """

    __tablename__ = "guideline_links"
    __table_args__ = (
        UniqueConstraint("guideline_id", "item_type", "item_id", name="uq_vinculo_diretriz"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    guideline_id: Mapped[int] = mapped_column(
        ForeignKey("guidelines.id", ondelete="CASCADE"), index=True
    )
    item_type: Mapped[str] = mapped_column(String(30), index=True)
    # documento | medicamento | evidencia | estudo | exame | imagem
    item_id: Mapped[int] = mapped_column(index=True)

    # Como o vínculo foi criado. Vínculo extraído automaticamente do texto de
    # `source_refs` é palpite bem-informado, não afirmação conferida — e a
    # diferença precisa sobreviver no banco, senão daqui a seis meses ninguém
    # sabe o que foi lido por uma pessoa e o que foi inferido por regex.
    origem: Mapped[str] = mapped_column(String(20), default="extraido")
    # extraido | confirmado
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    trecho: Mapped[str | None] = mapped_column(Text, nullable=True)
    # A referência original que gerou o vínculo, guardada para conferência.

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
