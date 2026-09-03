"""Checagem automática de CRM ativo no Web Service oficial do CFM.

A integração é fail-closed: somente situação regular confirmada diretamente
pelo CFM libera a verificação automática. Falhas de rede/serviço/credencial
seguem para revisão manual e nunca são convertidas em confirmação.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import settings
from app.services.cfm_registry import (
    CFM_NOT_FOUND_CODE,
    CfmWebserviceClient,
    CfmWebserviceError,
)

STATUS_ATIVO_CONFIRMADO = "ativo_confirmado"
STATUS_NAO_CONFIRMADO = "nao_confirmado"
STATUS_ERRO_CHECAGEM = "erro_checagem"


@dataclass
class ResultadoChecagemCrm:
    status: str
    detalhe: str
    verificado_em: datetime


def _consultar_webservice_oficial(numero_crm: str, uf: str) -> ResultadoChecagemCrm:
    agora = datetime.now(timezone.utc)
    try:
        with CfmWebserviceClient() as cliente:
            resultado = cliente.consultar(numero_crm, uf)
    except CfmWebserviceError as exc:
        if exc.codigo == CFM_NOT_FOUND_CODE:
            return ResultadoChecagemCrm(
                status=STATUS_NAO_CONFIRMADO,
                detalhe="CRM/UF não localizado no Web Service oficial do CFM.",
                verificado_em=agora,
            )
        raise

    if resultado.is_regular:
        return ResultadoChecagemCrm(
            status=STATUS_ATIVO_CONFIRMADO,
            detalhe="CRM ativo/regular confirmado no Web Service oficial do CFM.",
            verificado_em=agora,
        )
    situacao = resultado.situacao_texto or resultado.situacao_codigo or "não regular"
    return ResultadoChecagemCrm(
        status=STATUS_NAO_CONFIRMADO,
        detalhe=f"CRM localizado no CFM com situação cadastral: {situacao}.",
        verificado_em=agora,
    )


def checar_crm(numero_crm: str, uf: str) -> ResultadoChecagemCrm:
    agora = datetime.now(timezone.utc)
    # A URL oficial tem fallback seguro no cliente; a única configuração
    # obrigatória é a chave privada recebida do CFM.
    if not settings.cfm_webservice_chave.strip():
        return ResultadoChecagemCrm(
            status=STATUS_ERRO_CHECAGEM,
            detalhe="Checagem automática de CRM ainda não está configurada — a inscrição segue para revisão manual.",
            verificado_em=agora,
        )
    try:
        return _consultar_webservice_oficial(numero_crm, uf)
    except CfmWebserviceError as exc:
        return ResultadoChecagemCrm(
            status=STATUS_ERRO_CHECAGEM,
            detalhe=f"Falha controlada ao consultar o CFM (código {exc.codigo}); encaminhado para revisão manual.",
            verificado_em=agora,
        )
    except Exception:  # noqa: BLE001 — fail-closed; não expõe detalhe/segredo externo
        return ResultadoChecagemCrm(
            status=STATUS_ERRO_CHECAGEM,
            detalhe="Falha inesperada ao consultar o CFM; encaminhado para revisão manual.",
            verificado_em=agora,
        )
