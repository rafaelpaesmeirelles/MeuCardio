"""Checagem automática de CRM ativo — Trabalho 11 (06/08/2026).

O CFM tem um webservice OFICIAL de consulta por CRM+UF (Resolução CFM
2.129/15, sistemas.cfm.org.br/listamedicos), atualizado diariamente — mas
é **pago para empresa privada** e exige credencial cadastrada com eles.
Pedida, sem retorno até 06/08/2026 (mesmo padrão de pendência já registrado
pra VIDaaS/Bird ID/etc. — ver `docs/adr-assinatura-provedores` se existir,
ou o histórico da sessão).

A busca PÚBLICA do site (`portal.cfm.org.br/busca-medicos`) existe, mas é
carregada via JavaScript sem endpoint documentado — tentar reverse-
engineering de uma API não documentada de um portal de governo é
exatamente o tipo de dependência frágil e não verificável que este projeto
evita (`CLAUDE.md`: "tratar toda dependência externa como indisponível até
prova real"). Por isso este módulo NÃO tenta raspar o site.

Comportamento atual, honesto: sem `settings.cfm_webservice_configurado`,
toda chamada devolve `"erro_checagem"` — nunca finge confirmar. Quando a
credencial oficial chegar, só a função `_consultar_webservice_oficial`
precisa ganhar corpo real; o resto do fluxo (rota de KYC, liberação
automática) já está pronto para usar o resultado.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings

STATUS_ATIVO_CONFIRMADO = "ativo_confirmado"
STATUS_NAO_CONFIRMADO = "nao_confirmado"
STATUS_ERRO_CHECAGEM = "erro_checagem"


@dataclass
class ResultadoChecagemCrm:
    status: str  # um dos STATUS_* acima
    detalhe: str
    verificado_em: datetime


def _consultar_webservice_oficial(numero_crm: str, uf: str) -> ResultadoChecagemCrm:
    """Corpo real só entra quando `cfm_webservice_configurado` for True —
    ainda não escrito porque não há credencial pra testar contra, e este
    projeto não escreve integração não testável contra a API real (mesma
    regra que barrou stub de VIDaaS)."""
    raise NotImplementedError(
        "cfm_webservice_configurado ficou True, mas a chamada real ao "
        "webservice do CFM ainda não foi escrita — sem credencial pra testar."
    )


def checar_crm(numero_crm: str, uf: str) -> ResultadoChecagemCrm:
    agora = datetime.now(timezone.utc)
    if not settings.cfm_webservice_configurado:
        return ResultadoChecagemCrm(
            status=STATUS_ERRO_CHECAGEM,
            detalhe="Checagem automática de CRM ainda não está configurada — a inscrição segue para revisão manual.",
            verificado_em=agora,
        )
    try:
        return _consultar_webservice_oficial(numero_crm, uf)
    except Exception as exc:  # noqa: BLE001 — qualquer falha aqui cai em revisão manual, nunca trava nem finge confirmar
        return ResultadoChecagemCrm(
            status=STATUS_ERRO_CHECAGEM,
            detalhe=f"Falha ao consultar o CFM: {exc}",
            verificado_em=agora,
        )
