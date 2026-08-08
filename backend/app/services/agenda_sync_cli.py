"""Sincronização periódica automática das contas externas de Agenda.

Pedido do Rafael em 08/08/2026: "faca com que as contas permanecam sempre
conectadas automaticamente e sempre sincronizadas e com o conteudo
sincronizado sempre atualizado no sistema automaticamente". Até aqui, a
sincronização só acontecia em dois momentos: no instante em que a conta era
conectada (`_oauth_callback`) e quando o próprio médico clicava em
"Sincronizar agora" na tela. Sem nenhum gatilho automático entre esses dois
pontos, uma conta conectada há dias sem ninguém clicar em nada fica com
`last_sync_finished_at` parado — foi exatamente o que apareceu no print do
Rafael: a conta Microsoft mostrava "connected" mas a última sincronização
era de mais de 30 horas atrás.

Este script roda via cron (ver `infra/agenda_sync_cron.sh`, mesmo padrão já
usado para `cmed_precos_cli`/`guideline_discovery_cli`) e varre toda
integração `enabled=True` e `status='connected'`, sincronizando agenda e,
quando habilitado, contatos. Isso também tem um efeito colateral importante:
`sync_integration`/`sync_contacts` chamam `ensure_fresh_credentials()`, que
renova o access token do Google/Microsoft usando o refresh token sempre que
ele está a menos de 90s de expirar — rodando isso a cada poucos minutos, o
token nunca fica muito tempo sem ser usado/renovado, o que reduz (não
elimina) o risco de o refresh token expirar por inatividade prolongada em
alguns provedores.

O que este script NUNCA resolve, e não deve fingir que resolve: se o próprio
usuário revogar o acesso pelo painel do provedor (Google/Microsoft/Apple),
ou se o provedor invalidar o token por segurança, a integração vai para
`status='reauth_required'`/`'disconnected'` e PRECISA de um novo consentimento
manual — nenhuma rotina automática pode contornar isso, é a proteção de
segurança do próprio OAuth funcionando como desenhado. O script detecta esse
caso, registra o erro no próprio registro (`last_error_code`) e segue para a
próxima conta, sem tentar "forçar" reconexão nem inventar sucesso.
"""

from __future__ import annotations

import logging
import sys

from app.core.db import SessionLocal
from app.models.agenda import CalendarIntegration
from app.services.agenda_integrada.connectors import ConnectorError
from app.services.agenda_integrada.contacts import sync_contacts
from app.services.agenda_integrada.domain import sync_integration

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agenda_sync_cli")


def sincronizar_todas() -> dict:
    db = SessionLocal()
    resultado = {"sincronizadas": 0, "falharam": 0, "puladas": 0, "detalhe": []}
    try:
        integracoes = (
            db.query(CalendarIntegration)
            .filter(CalendarIntegration.enabled.is_(True), CalendarIntegration.status == "connected")
            .all()
        )
        for item in integracoes:
            rotulo = f"{item.provider}:{item.display_name or item.id}"
            # Calendário e contatos são independentes de propósito — mesmo
            # princípio do fix de conexão do Apple (08/08/2026): uma falha
            # isolada de contatos não pode apagar/mascarar um calendário que
            # sincronizou com sucesso, nem o inverso. Cada um grava seu
            # próprio resultado; a conta só conta como "falhou" no resumo se
            # NENHUM dos dois teve sucesso.
            calendario = contatos = None
            erro_calendario = erro_contatos = None
            # "não aplicável" é diferente de "falhou" — uma conta só de e-mail
            # (ex.: Yahoo neste catálogo) nunca terá `read_appointments`, e
            # isso não é uma falha a contar/alarmar a cada rodada do cron.
            calendario_aplicavel = True
            try:
                calendario = sync_integration(db, item, full=False)
                db.commit()
            except ConnectorError as exc:
                db.rollback()
                if exc.code == "read_not_supported":
                    calendario_aplicavel = False
                else:
                    erro_calendario = exc.code
                    item = db.get(CalendarIntegration, item.id) or item
                    item.last_error_code = exc.code
                    item.last_error_message = str(exc)[:500]
                    db.commit()
            except Exception:  # noqa: BLE001 - uma conta com erro inesperado não pode travar as outras
                db.rollback()
                erro_calendario = "erro_inesperado"
                log.exception("Erro inesperado sincronizando calendário de %s", rotulo)

            contatos_aplicavel = bool(item.contacts_enabled)
            if contatos_aplicavel:
                item = db.get(CalendarIntegration, item.id) or item
                try:
                    contatos = sync_contacts(db, item, full=False)
                    db.commit()
                except ConnectorError as exc:
                    db.rollback()
                    erro_contatos = exc.code
                    # De propósito, NÃO grava em `last_error_code` da
                    # integração: esse campo alimenta o aviso de "Reconectar"
                    # na tela de Sincronização, e uma falha isolada de
                    # contatos (ex.: Apple, ver connectors.py) não deve fazer
                    # uma conta que sincroniza calendário/e-mail normalmente
                    # aparecer como quebrada. O erro fica só no log do cron.
                except Exception:  # noqa: BLE001
                    db.rollback()
                    erro_contatos = "erro_inesperado"
                    log.exception("Erro inesperado sincronizando contatos de %s", rotulo)

            # "Sucesso" exige que toda frente REALMENTE APLICÁVEL a esta conta
            # tenha ido bem. Frente não aplicável (Yahoo não tem calendário;
            # contatos desligado pelo médico) não conta nem a favor nem contra.
            calendario_ok = (not calendario_aplicavel) or erro_calendario is None
            contatos_ok = (not contatos_aplicavel) or erro_contatos is None
            ok = calendario_ok and contatos_ok
            if ok:
                resultado["sincronizadas"] += 1
                log.info("OK %s — calendario=%s contatos=%s", rotulo, calendario, contatos)
            else:
                resultado["falharam"] += 1
                log.warning("FALHOU %s — calendario=%s contatos=%s", rotulo, erro_calendario, erro_contatos)
            resultado["detalhe"].append({
                "conta": rotulo, "ok": ok,
                "calendario": calendario, "erro_calendario": erro_calendario,
                "contatos": contatos, "erro_contatos": erro_contatos,
            })

        total_desconectadas = (
            db.query(CalendarIntegration)
            .filter(CalendarIntegration.enabled.is_(True), CalendarIntegration.status != "connected")
            .count()
        )
        resultado["puladas"] = total_desconectadas
        return resultado
    finally:
        db.close()


if __name__ == "__main__":
    r = sincronizar_todas()
    log.info(
        "Resumo: %d sincronizadas, %d falharam, %d puladas (desconectadas/precisam reconectar)",
        r["sincronizadas"], r["falharam"], r["puladas"],
    )
    sys.exit(0)
