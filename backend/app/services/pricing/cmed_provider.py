"""Adaptador fino: expõe app/services/cmed_precos.py (já existente e em
produção) pelo formato comum PriceObservation — não duplica lógica de
download/parsing/casamento, só traduz o resultado já persistido em
CmedApresentacao para o contrato PriceProvider (issue #52)."""
from __future__ import annotations

from datetime import timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cmed import CmedApresentacao, CmedVersao
from app.services.pricing.base import PriceObservation


class CMEDProvider:
    source = "cmed"
    source_type = "regulatory"

    def __init__(self, db: Session) -> None:
        self._db = db

    def observations_for(self, drug_id: int) -> list[PriceObservation]:
        ultima_versao_id = self._db.execute(
            select(CmedVersao.id).order_by(CmedVersao.id.desc()).limit(1)
        ).scalar_one_or_none()
        if ultima_versao_id is None:
            return []

        linhas = self._db.execute(
            select(CmedApresentacao).where(
                CmedApresentacao.drug_id == drug_id,
                CmedApresentacao.cmed_versao_id == ultima_versao_id,
            )
        ).scalars().all()

        versao = self._db.get(CmedVersao, ultima_versao_id)
        observado_em = versao.baixado_em if versao and versao.baixado_em else None
        if observado_em and observado_em.tzinfo is None:
            observado_em = observado_em.replace(tzinfo=timezone.utc)

        observacoes: list[PriceObservation] = []
        for linha in linhas:
            pmc_por_aliquota = linha.pmc_por_aliquota or {}
            for coluna_aliquota, valor in pmc_por_aliquota.items():
                # `coluna_aliquota` é o texto cru da coluna da planilha da
                # CMED (ex.: "PMC 18%", "PMC 18% ALC", "PMC Sem Impostos") —
                # não um código de UF; a resolução UF->alíquota fica a cargo
                # de quem consome (mesma responsabilidade já documentada em
                # `cmed_precos.preco_pmc`/`_icms_por_uf`, não duplicada aqui).
                if valor is None:
                    continue
                observacoes.append(PriceObservation(
                    source=self.source,
                    source_type=self.source_type,
                    price_type="pmc",
                    observed_at=observado_em or versao.baixado_em,
                    price=Decimal(str(valor)),
                    presentation_ref=linha.ggrem or f"cmed-apresentacao-{linha.id}",
                    drug_id=drug_id,
                    region=coluna_aliquota,
                    confidence="official",
                    metadata={
                        "laboratorio": linha.laboratorio,
                        "produto": linha.produto,
                        "apresentacao": linha.apresentacao,
                        "cmed_versao_publicado_em": versao.publicado_em if versao else None,
                    },
                ))
        return observacoes
