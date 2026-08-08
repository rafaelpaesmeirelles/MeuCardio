from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ConvidadoPreAutorizado(Base):
    """Identificador (e-mail e/ou nome completo) cadastrado por um admin
    ANTES da pessoa se registrar — quando o cadastro em
    `POST /auth/solicitar-acesso` casar com uma linha ainda não usada, o
    novo `User` já nasce com `convidado = True` (08/08/2026, pedido do
    Rafael: "já vamos deixar registrado no sistema que quando ele pedir o
    cadastramento com esse email ele vai seguir pelo caminho que tínhamos
    desenhado").

    Mecanismo genérico e reutilizável — qualquer admin pode pré-autorizar
    qualquer pessoa pelo painel Admin, não é hardcoded para ninguém
    específico. Consumo é único (`usado_em` marcado no primeiro cadastro que
    casar); depois de usada, a pré-autorização não vale mais para ninguém.

    `email` OU `nome_completo` (ou os dois) — o admin nem sempre sabe de
    antemão qual e-mail a pessoa vai escolher no cadastro, então o nome serve
    de identificador alternativo. Um CHECK no banco garante que pelo menos um
    dos dois está preenchido (ver migração f6dn20260808). `email`, quando
    presente, é o critério de match preferido (mais confiável que nome); o
    match por nome só entra em jogo quando não há match por e-mail — ver
    `_pre_autorizacao_de` em `app/api/auth.py`.

    `incluir_corvia_mail` (08/08/2026) — antes todo convidado nascia sempre
    no plano Completo (que inclui CorvIA Mail); agora é escolha por linha,
    lida por `criar_checkout()` via `User.convidado_plano_preferido`.
    """

    __tablename__ = "convidados_pre_autorizados"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    nome_completo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    incluir_corvia_mail: Mapped[bool] = mapped_column(Boolean, default=True)
    observacao: Mapped[str | None] = mapped_column(String(300), nullable=True)
    criado_por: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    usado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    usado_por_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
