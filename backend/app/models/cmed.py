"""Preço regulado de medicamento via lista da CMED (Tarefa A, CLAUDE.md).

Fonte obrigatória e única: lista de preços da CMED em
`gov.br/anvisa/pt-br/assuntos/medicamentos/cmed/precos` — nenhum preço de
outra origem. `CmedVersao` existe porque a lista muda todo mês: sem saber de
qual versão um preço veio, não dá para explicar por que um relatório antigo
mostra número diferente do de hoje (ver Tarefa B, `pmc_snapshot`).

`CmedApresentacao` é por APRESENTAÇÃO COMERCIAL (marca + dosagem + embalagem
específica), não por substância — a mesma substância tem várias linhas, uma
por produto/laboratório/apresentação, exatamente como a planilha da CMED
lista. O casamento com `Drug` é feito no import (`services/cmed_importer.py`)
por nome de substância normalizado; ver ali a regra de match e por que é
assimétrica.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CmedVersao(Base):
    __tablename__ = "cmed_versoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Data embutida no nome do arquivo da ANVISA (xls_..._<AAAAMMDD>_<ms>.xlsx)
    # — é a data de publicação da lista, não a data em que baixamos.
    publicado_em: Mapped[str] = mapped_column(String(8), index=True)
    arquivo_url: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    linhas: Mapped[int] = mapped_column(Integer)
    baixado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CmedApresentacao(Base):
    __tablename__ = "cmed_apresentacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    cmed_versao_id: Mapped[int] = mapped_column(ForeignKey("cmed_versoes.id"), index=True)
    drug_id: Mapped[int | None] = mapped_column(ForeignKey("drugs.id"), nullable=True, index=True)
    # Nulo quando a substância da CMED não bate com nenhum `Drug` do catálogo
    # (ex.: fora do escopo de cardiologia) — a linha ainda é importada, só não
    # aparece em nenhuma tela; existe para não precisar reimportar ao ampliar
    # o catálogo depois.

    substancia_cmed: Mapped[str] = mapped_column(Text, index=True)  # texto cru da coluna SUBSTÂNCIA
    laboratorio: Mapped[str] = mapped_column(Text)
    produto: Mapped[str] = mapped_column(Text)  # marca
    apresentacao: Mapped[str] = mapped_column(Text)
    ggrem: Mapped[str] = mapped_column(String(30), index=True)
    registro: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ean1: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tarja: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tipo_produto: Mapped[str | None] = mapped_column(Text, nullable=True)
    classe_terapeutica: Mapped[str | None] = mapped_column(Text, nullable=True)
    restricao_hospitalar: Mapped[bool] = mapped_column(Boolean, default=False)
    # Todas as colunas de PMC por alíquota, cruas — {"PMC Sem Impostos": 12.34,
    # "PMC 0%": ..., "PMC 12%": ..., "PMC 12% ALC": ..., ...}. Valor None onde a
    # planilha vem em branco (comum em `restricao_hospitalar`, Resolução CMED
    # nº 3/2009 — apresentação de uso hospitalar não tem PMC nenhum, por norma,
    # não por falha de dado).
    pmc_por_aliquota: Mapped[dict] = mapped_column(JSONB, default=dict)
