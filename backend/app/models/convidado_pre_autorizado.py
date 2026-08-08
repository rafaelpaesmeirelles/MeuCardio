from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ConvidadoPreAutorizado(Base):
    """E-mail cadastrado por um admin ANTES da pessoa se registrar — quando
    esse e-mail passa por `POST /auth/solicitar-acesso`, o novo `User` já
    nasce com `convidado = True` (08/08/2026, pedido do Rafael: "já vamos
    deixar registrado no sistema que quando ele pedir o cadastramento com
    esse email ele vai seguir pelo caminho que tínhamos desenhado").

    Mecanismo genérico e reutilizável — qualquer admin pode pré-autorizar
    qualquer e-mail, não é hardcoded para nenhuma pessoa específica. Consumo
    é único (`usado_em` marcado no primeiro cadastro que casar o e-mail);
    depois de usada, a pré-autorização não vale mais para ninguém, inclusive
    se a mesma pessoa tentar se cadastrar de novo com outro e-mail.
    """

    __tablename__ = "convidados_pre_autorizados"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    observacao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    criado_por: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    usado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
