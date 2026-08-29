"""Elenco do Programa Farmácia Popular do Brasil (PFPB) — camada de acesso/
subsídio, complementar ao preço regulado da CMED (teto legal) e ao K@iros
(preço real de mercado), já cobertos em `app/models/cmed.py` e
`app/services/pricing/kairos_provider.py`.

Gap encontrado por sessão externa (Claude chat), 29/08/2026 (ver CLAUDE.md):
o produto resolvia preço-teto e preço-de-mercado, mas não a terceira
pergunta que o cardiologista faz na prática — "esse fármaco é gratuito pelo
Farmácia Popular?" — que muda a escolha terapêutica em paciente com
restrição financeira.

Arquitetura deliberadamente espelhada em `CmedVersao`/`CmedApresentacao`
(mesmo espírito, não reinvenção): `FarmaciaPopularVersao` existe porque o
elenco do programa também é atualizado periodicamente pelo Ministério da
Saúde, e sem saber de qual conferência veio um item não dá para explicar
por que uma tela mostrou "gratuito" num mês e não no seguinte.
`FarmaciaPopularItem` é por SUBSTÂNCIA/DOSE DE REFERÊNCIA do programa
(o PFPB lista por princípio ativo + dose, não por apresentação comercial
individual como a CMED), casado com `Drug` no import
(`app/services/farmacia_popular.py`) reaproveitando a MESMA normalização
já usada pela CMED (`cmed_precos.palavras_normalizadas`/`eh_match`).

⚠️ Regra de segurança clínica, não relaxar: `elegivel_confirmado` só pode
ser `True` quando `ean` está preenchido E confere contra a lista vigente do
Ministério da Saúde — nunca por match de substância isolado. Um match de
substância sem EAN confirmado é candidato a elegibilidade, não elegibilidade
em si; é informação com peso financeiro real para o paciente (mesmo padrão
de rigor que este projeto já exige para preço, ver CLAUDE.md, "Tarefa A").
Nesta primeira carga (29/08/2026) NENHUM item tem `ean` confirmado — a URL
exata do arquivo/código de barras vigente do MS não foi localizada nesta
sessão (mesma advertência já registrada para a planilha da CMED: a página-
mãe muda o link do arquivo, e tentativa de acesso direto devolveu 404) — por
isso todo item nasce com `elegivel_confirmado = False` até alguém carregar
o EAN real. Ver `app/services/farmacia_popular.py` para o cálculo.
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class FarmaciaPopularVersao(Base):
    """Uma linha por conferência/carga do elenco do PFPB — não é uma versão
    de arquivo baixado e hasheado como `CmedVersao` (não existe hoje um
    arquivo único e estável para isso, ver módulo docstring), e sim o
    registro de quando e contra quais fontes o elenco foi conferido."""

    __tablename__ = "farmacia_popular_versoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Data em que o elenco foi conferido nesta sessão/carga (AAAAMMDD),
    # não a data de publicação de um arquivo — o PFPB não publica um único
    # arquivo versionado e datável como a CMED faz.
    conferido_em: Mapped[str] = mapped_column(String(8), index=True)
    fontes: Mapped[str] = mapped_column(Text)  # citações completas, uma por linha
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    itens: Mapped[int] = mapped_column(Integer)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class FarmaciaPopularItem(Base):
    """Um item do elenco do PFPB (substância + dose de referência), casado
    com `Drug` por normalização de nome. `drug_id` nulo é esperado — parte
    do elenco (contraceptivo, insumo de Parkinson/glaucoma/rinite/
    osteoporose, fralda/absorvente) está fora do escopo cardiológico deste
    catálogo, e a linha ainda é importada para não perder rastreabilidade
    do elenco completo do programa."""

    __tablename__ = "farmacia_popular_itens"

    id: Mapped[int] = mapped_column(primary_key=True)
    farmacia_popular_versao_id: Mapped[int] = mapped_column(
        ForeignKey("farmacia_popular_versoes.id"), index=True
    )
    drug_id: Mapped[int | None] = mapped_column(ForeignKey("drugs.id"), nullable=True, index=True)

    substancia_pfpb: Mapped[str] = mapped_column(Text, index=True)  # texto cru do elenco oficial
    dose_referencia: Mapped[str] = mapped_column(Text)
    categoria: Mapped[str] = mapped_column(String(60), index=True)
    # hipertensao | diabetes | diabetes_cardiovascular | dislipidemia
    indicacao: Mapped[str] = mapped_column(Text)
    criterio_acesso: Mapped[str] = mapped_column(Text)
    # texto livre: "gratuito para qualquer receita" vs. "exige Cartão Bolsa
    # Família ou NIS" — o programa distingue por item, e afirmar "gratuito"
    # sem essa distinção seria impreciso para o paciente.

    ean: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    # Nulo até alguém carregar o código de barras vigente do MS — ver aviso
    # de segurança no topo deste arquivo. Presença de EAN é o único sinal
    # que autoriza `elegivel_confirmado = True` na exposição da API
    # (`app/services/farmacia_popular.py::montar_exposicao`).

    fonte_refs: Mapped[str] = mapped_column(Text)  # citações completas, uma por linha
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    # False quando um item sai do elenco numa conferência futura sem que a
    # linha seja apagada — mesma disciplina de nunca apagar histórico de
    # preço/elenco em silêncio.
