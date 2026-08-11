"""BPS (Banco de Preços em Saúde) — camada INSTITUCIONAL de preço, issue #52.

Fonte: `GET https://apidadosabertos.saude.gov.br/economia-da-saude/bps` —
API pública do Ministério da Saúde, sem autenticação, sem cadastro,
confirmada funcionando ao vivo nesta sessão (11/08/2026): consulta real por
`codigoCatmat=268856` (losartana potássica 50mg) devolveu preços reais de
compra pública em 2026, com fornecedor/fabricante/instituição/UF/data.

**Regra inegociável: preço do BPS é preço de COMPRA PÚBLICA/institucional —
nunca "preço de varejo", nunca "preço que o paciente paga na farmácia".**
`source_type = "institutional"`, sempre. Um hospital público pagando
R$0,05 por comprimido de losartana em pregão não tem relação com o que uma
farmácia cobra do consumidor final — misturar os dois seria exatamente o
tipo de confusão que este projeto proíbe (ver docs/pricing-architecture.md).

## Limitação real, documentada, não escondida

A API do BPS exige `codigoCatmat` OU `cnpjInstituicao` como filtro
obrigatório — não aceita busca por nome de fármaco nem por
`registroAnvisa` sozinho (esse é só um refinamento opcional). Isso
significa que consultar por `drug_id` exige saber o código CATMAT
correspondente, e **não existe hoje nenhum crosswalk Drug → CATMAT no
catálogo** (não é campo do modelo `Drug`, não está no
`medicamentos/metadados.json`). Construir esse crosswalk em escala exigiria
baixar o Catálogo de Materiais oficial do Ministério da Saúde e casar por
nome — tarefa maior, fora do escopo deste POC.

Por isso, o crosswalk aqui é uma tabela pequena, explícita e 100% de
fármacos com CATMAT verificado nesta sessão (hoje, só 1: losartana
potássica 50mg, CATMAT 268856, confirmado por chamada real à API) — não um
mapeamento amplo. `observations_for()` devolve lista vazia para qualquer
`drug_id` fora do crosswalk, nunca fabrica nem adivinha o código.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.models.drug import Drug
from app.services.pricing.base import PriceObservation

_ENDPOINT = "https://apidadosabertos.saude.gov.br/economia-da-saude/bps"
_TIMEOUT = 10.0

# Crosswalk slug -> código CATMAT, só com código verificado por chamada real
# à API nesta sessão (issue #52) — nunca adivinhado. Ampliar exige o mesmo
# padrão: confirmar o código (ex.: via publicações do Ministério da Saúde
# ou consulta ao próprio BPS) antes de acrescentar uma linha aqui.
CROSSWALK_CATMAT_VERIFICADO: dict[str, str] = {
    "losartana-potassica": "268856",  # LOSARTANA POTÁSSICA, DOSAGEM: 50 MG
}


class BPSProvider:
    source = "bps"
    source_type = "institutional"

    def __init__(self, db: Session, *, tamanho_pagina: int = 20) -> None:
        self._db = db
        self._tamanho_pagina = tamanho_pagina

    def observations_for(self, drug_id: int) -> list[PriceObservation]:
        farmaco = self._db.get(Drug, drug_id)
        if farmaco is None:
            return []
        codigo_catmat = CROSSWALK_CATMAT_VERIFICADO.get(farmaco.slug)
        if not codigo_catmat:
            return []

        try:
            resposta = httpx.get(
                _ENDPOINT,
                params={
                    "codigoCatmat": codigo_catmat,
                    "pagina": 1,
                    "tamanhoPagina": self._tamanho_pagina,
                },
                timeout=_TIMEOUT,
            )
            resposta.raise_for_status()
            corpo = resposta.json()
        except (httpx.HTTPError, ValueError):
            # Fonte externa indisponível/instável — nunca fabrica preço
            # nem propaga exceção para quem só quer "o que existe hoje".
            return []

        linhas = corpo.get("bps") or []
        return [self._observacao(farmaco.id, linha) for linha in linhas if linha.get("precoUnitario") is not None]

    def _observacao(self, drug_id: int, linha: dict[str, Any]) -> PriceObservation:
        data_compra = linha.get("dataCompra")
        try:
            observado_em = datetime.strptime(data_compra, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            observado_em = datetime.now(timezone.utc)

        return PriceObservation(
            source=self.source,
            source_type=self.source_type,
            price_type="institutional_purchase",
            observed_at=observado_em,
            price=Decimal(str(linha["precoUnitario"])),
            presentation_ref=str(linha.get("codigoCatmat") or ""),
            drug_id=drug_id,
            region=linha.get("estado"),
            confidence="official",
            metadata={
                "instituicao_compradora": linha.get("nomeInstituicao"),
                "municipio": linha.get("municipio"),
                "fornecedor": linha.get("nomeFornecedor"),
                "fabricante": linha.get("nomeFabricante"),
                "modalidade": linha.get("modalidade"),
                "tipo_compra": linha.get("tipoCompra"),
                "generico": linha.get("generico"),
                "quantidade_comprada": linha.get("quantidade"),
                "registro_anvisa": linha.get("registroAnvisa"),
                "aviso": (
                    "Preço de compra pública/institucional (BPS, Ministério da Saúde) — "
                    "NÃO é preço de varejo/farmácia ao consumidor."
                ),
            },
        )
