"""Worker contínuo de sincronização de contas externas e saneamento da agenda.

Mantém conexões e calendário atualizados sem depender de o usuário apertar um
botão. O CorVIA Mail externo continua sendo proxy ao vivo; para ele o worker
faz heartbeat/renovação de credencial. Calendário/contatos usam os cursores
incrementais existentes.

Também tenta completar, em segundo plano, coordenadas ausentes dos locais já
cadastrados. Isso corrige registros antigos que tinham endereço textual mas
ficaram como "GPS pendente". Nenhuma coordenada é inventada: o mesmo serviço
fail-closed de geocodificação é usado e o endereço consultado nunca vai para o
log.

Falha isolada de uma conta ou de um endereço nunca mata o processo. Já falha
estrutural da rodada inteira (por exemplo banco indisponível) é diferente: após
cinco ciclos consecutivos o processo sai com erro para que ``restart:
unless-stopped`` do Docker o recrie.
"""
from __future__ import annotations

import logging
import os
import signal
import time

from sqlalchemy import or_

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.agenda import CalendarIntegration, CalendarLocation
from app.services.account_sync import sincronizar_conta
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.geocoding import GeocodingError, geocode_address

log = logging.getLogger("corvia.agenda_sync_worker")
_PARAR = False
_ESTADOS_ELEGIVEIS = ("connected", "error")
_MAX_FALHAS_FATAL_RODADA = 5


def _parar(_signum, _frame) -> None:  # noqa: ANN001
    global _PARAR
    _PARAR = True


def _intervalo_segundos() -> int:
    bruto = os.getenv("AGENDA_SYNC_INTERVAL_SECONDS", "60")
    try:
        valor = int(bruto)
    except ValueError:
        valor = 60
    return max(15, min(valor, 3600))


def _texto_local(item: CalendarLocation) -> str:
    address = item.address or {}
    keys = (
        "street", "number", "complement", "neighborhood", "district",
        "city", "state", "zip", "postal_code", "country",
    )
    partes = [str(address.get(key) or "").strip() for key in keys]
    partes = [parte for parte in partes if parte]
    if item.name:
        partes.insert(0, item.name.strip())
    return ", ".join(dict.fromkeys(partes))


def _reparar_geocodificacao(db) -> tuple[int, int]:  # noqa: ANN001
    """Completa coordenadas antigas quando houver endereço suficiente.

    Retorna ``(reparadas, pendentes)``. Falhas de provedor ficam pendentes para
    outra rodada; não se loga o endereço nem se bloqueia o restante do worker.
    """
    itens = db.query(CalendarLocation).filter(
        CalendarLocation.active.is_(True),
        or_(CalendarLocation.latitude.is_(None), CalendarLocation.longitude.is_(None)),
    ).order_by(CalendarLocation.id.asc()).all()
    reparadas = 0
    pendentes = 0
    for item in itens:
        consulta = _texto_local(item)
        if len(consulta) < 5:
            pendentes += 1
            continue
        try:
            resultado = geocode_address(consulta)
        except GeocodingError:
            pendentes += 1
            continue
        item.latitude = resultado["latitude"]
        item.longitude = resultado["longitude"]
        reparadas += 1
    if reparadas:
        db.commit()
    return reparadas, pendentes


def sincronizar_rodada() -> dict:
    db = SessionLocal()
    resultado = {
        "sincronizadas": 0,
        "com_pendencia": 0,
        "puladas": 0,
        "locais_geocodificados": 0,
        "locais_gps_pendentes": 0,
    }
    try:
        ids = [
            linha[0]
            for linha in db.query(CalendarIntegration.id).filter(
                CalendarIntegration.enabled.is_(True),
                CalendarIntegration.status.in_(_ESTADOS_ELEGIVEIS),
            ).order_by(CalendarIntegration.id.asc()).all()
        ]
        for integration_id in ids:
            item = db.get(CalendarIntegration, integration_id)
            if item is None:
                continue
            try:
                detalhe = sincronizar_conta(db, item, full=False)
                if detalhe.get("ok"):
                    resultado["sincronizadas"] += 1
                else:
                    resultado["com_pendencia"] += 1
                    log.warning(
                        "agenda-sync pendencia integration_id=%s provider=%s status=%s componentes=%s",
                        item.id, item.provider, detalhe.get("status"), detalhe.get("componentes"),
                    )
            except ConnectorError as exc:
                db.rollback()
                resultado["com_pendencia"] += 1
                log.warning(
                    "agenda-sync falha integration_id=%s provider=%s code=%s: %s",
                    item.id, item.provider, exc.code, exc,
                )
            except Exception:  # noqa: BLE001 — isolamento entre contas
                db.rollback()
                resultado["com_pendencia"] += 1
                log.exception(
                    "agenda-sync falha inesperada integration_id=%s provider=%s",
                    item.id, item.provider,
                )

        resultado["puladas"] = db.query(CalendarIntegration).filter(
            CalendarIntegration.enabled.is_(True),
            ~CalendarIntegration.status.in_(_ESTADOS_ELEGIVEIS),
        ).count()
        reparadas, pendentes = _reparar_geocodificacao(db)
        resultado["locais_geocodificados"] = reparadas
        resultado["locais_gps_pendentes"] = pendentes
        return resultado
    finally:
        db.close()


def executar() -> None:
    signal.signal(signal.SIGTERM, _parar)
    signal.signal(signal.SIGINT, _parar)

    intervalo = _intervalo_segundos()
    falhas_fatais_consecutivas = 0
    log.info(
        "agenda-sync worker iniciado enabled=%s intervalo=%ss",
        settings.agenda_background_sync_enabled,
        intervalo,
    )

    while not _PARAR:
        inicio = time.monotonic()
        if settings.agenda_background_sync_enabled:
            try:
                resultado = sincronizar_rodada()
                falhas_fatais_consecutivas = 0
                log.info(
                    "agenda-sync rodada concluida sincronizadas=%s pendencias=%s puladas=%s locais_geocodificados=%s locais_gps_pendentes=%s",
                    resultado.get("sincronizadas"),
                    resultado.get("com_pendencia"),
                    resultado.get("puladas"),
                    resultado.get("locais_geocodificados"),
                    resultado.get("locais_gps_pendentes"),
                )
            except Exception:  # noqa: BLE001 — erro estrutural da rodada inteira
                falhas_fatais_consecutivas += 1
                log.exception(
                    "agenda-sync rodada falhou inesperadamente (%s/%s)",
                    falhas_fatais_consecutivas,
                    _MAX_FALHAS_FATAL_RODADA,
                )
                if falhas_fatais_consecutivas >= _MAX_FALHAS_FATAL_RODADA:
                    raise RuntimeError(
                        "agenda-sync acumulou falhas estruturais consecutivas; "
                        "encerrando para reinício pelo supervisor Docker"
                    )
        else:
            # Produção força true no compose; se alguém remover essa proteção,
            # o log deixa explícito que a sincronização permanente foi desativada.
            log.warning("agenda-sync está desativado por configuração")

        gasto = time.monotonic() - inicio
        restante = max(1.0, intervalo - gasto)
        limite = time.monotonic() + restante
        while not _PARAR and time.monotonic() < limite:
            time.sleep(min(1.0, limite - time.monotonic()))

    log.info("agenda-sync worker encerrado")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    executar()
