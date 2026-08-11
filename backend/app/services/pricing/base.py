"""Abstração de fonte de preço — issue #52, nova fase (Medicamentos +
inteligência regulatória/preços).

Três camadas que nunca se misturam (ver docs/pricing-architecture.md):
regulatória (CMED), inteligência de mercado (ex.: Kairos, quando/se
licenciada), e varejo/parceiro observado (nenhuma fonte legítima
disponível hoje). Cada fonte concreta implementa `PriceProvider` e
devolve `PriceObservation` — nunca um preço "definitivo" fabricado por
combinação arbitrária (ex.: PMC × desconto médio nacional).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class PriceObservation:
    source: str
    """Identificador curto da fonte: "cmed", "kairos", "market_partner", "pbm"."""

    source_type: str
    """"regulatory" | "market_intelligence" | "retail" | "pbm" | "institutional" —
    nunca livre; é o que impede a UI/API de tratar preço observado como
    regulatório. "institutional" é preço de COMPRA PÚBLICA/institucional
    (ex.: BPS) — nunca deve ser rotulado como preço de varejo/consumidor."""

    price_type: str
    """"pf" | "pmc" | "observed" | "pbm" — o TIPO do valor, não a fonte."""

    observed_at: datetime
    price: Decimal
    presentation_ref: str
    """Identifica a apresentação de origem (ex.: GGREM da CMED) — nunca o
    nome comercial sozinho, que pode repetir entre apresentações."""

    drug_id: int | None = None
    currency: str = "BRL"
    region: str | None = None
    """UF, quando a fonte diferencia por alíquota/região — None = nacional."""

    confidence: str = "official"
    """"official" (fonte regulatória primária) | "high" | "medium" |
    "estimated" (nunca usado para exibir como preço de produto individual,
    só para contexto analítico agregado, sempre rotulado como estimativa)."""

    metadata: dict = field(default_factory=dict)


class PriceProvider(Protocol):
    """Contrato que toda fonte de preço implementa. Ver
    docs/pricing-architecture.md antes de adicionar uma nova fonte —
    scraping frágil/não licenciado não é uma implementação aceitável."""

    source: str
    source_type: str

    def observations_for(self, drug_id: int) -> list[PriceObservation]:
        """Devolve as observações de preço mais recentes conhecidas por
        esta fonte para o fármaco. Lista vazia é uma resposta válida
        (fonte não tem dado para este fármaco) — nunca levanta exceção
        para "sem dado", só para falha real de acesso à fonte."""
        ...
