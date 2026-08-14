"""Remove, sob confirmação explícita, a caixa REAL investidor@corvia.med.br.

Uso seguro no servidor:

    python -m app.commands.cleanup_investidor_mail360

é somente leitura e mostra o match exato. Para executar a exclusão já
autorizada pelo proprietário do CorVIA:

    python -m app.commands.cleanup_investidor_mail360 --apply

Fail-closed: nunca usa busca parcial, nunca apaga se houver mais de um match
exato e nunca toca em outro endereço.
"""
from __future__ import annotations

import argparse
from typing import Any

from app.core.db import SessionLocal
from app.models.audit import AuditLog
from app.models.email_account import EmailAccount
from app.services import mail360
from app.services.mail360 import Mail360Error

ALVO = "investidor@corvia.med.br"


def _enderecos(conta: dict[str, Any]) -> set[str]:
    candidatos: set[str] = set()
    for chave in ("email_address", "emailAddress", "emailid", "emailId", "email"):
        valor = conta.get(chave)
        if isinstance(valor, str) and "@" in valor:
            candidatos.add(valor.strip().lower())

    # A listagem do Mail360 também pode expor endereços dentro da coleção
    # `ac`; aceitamos apenas strings que sejam endereços completos ou campos
    # explicitamente nomeados, nunca fuzzy match por nome/local-part.
    ac = conta.get("ac")
    if isinstance(ac, list):
        for item in ac:
            if isinstance(item, str) and "@" in item:
                candidatos.add(item.strip().lower())
            elif isinstance(item, dict):
                for chave in ("email_address", "emailAddress", "emailid", "emailId", "email"):
                    valor = item.get(chave)
                    if isinstance(valor, str) and "@" in valor:
                        candidatos.add(valor.strip().lower())
    return candidatos


def _account_key(conta: dict[str, Any]) -> str | None:
    valor = conta.get("account_key") or conta.get("accountKey") or conta.get("accountId")
    return str(valor).strip() if valor is not None and str(valor).strip() else None


def localizar() -> tuple[list[dict[str, Any]], list[EmailAccount]]:
    dados = mail360._chamar("GET", "/accounts")  # noqa: SLF001 — comando operacional controlado
    contas = dados if isinstance(dados, list) else []
    matches = [conta for conta in contas if ALVO in _enderecos(conta)]

    db = SessionLocal()
    try:
        locais = db.query(EmailAccount).filter(EmailAccount.email_address == ALVO).all()
        # Detach para poder fechar a sessão antes de devolver.
        for item in locais:
            db.expunge(item)
    finally:
        db.close()
    return matches, locais


def executar(apply: bool) -> int:
    try:
        matches, locais = localizar()
    except Mail360Error as exc:
        print(f"ERRO: não foi possível listar contas do Mail360: {exc}")
        return 2

    print(f"Alvo exato: {ALVO}")
    print(f"Matches Mail360: {len(matches)}")
    print(f"Registros locais EmailAccount: {len(locais)}")

    if len(matches) == 0:
        print("OK: nenhuma caixa real com esse endereço existe no Mail360. Nada a excluir.")
        return 0
    if len(matches) != 1:
        print("ABORTADO: mais de um match exato foi retornado. Revisão humana necessária.")
        return 3

    key = _account_key(matches[0])
    if not key:
        print("ABORTADO: match exato sem account_key utilizável.")
        return 4

    print(f"Match exato confirmado: account_key={key}")
    if not apply:
        print("DRY-RUN: nenhuma alteração feita. Use --apply somente após conferir o match acima.")
        return 0

    try:
        mail360._chamar("DELETE", f"/accounts/{key}")  # noqa: SLF001 — exclusão exata autorizada
    except Mail360Error as exc:
        print(f"ERRO: Mail360 recusou a exclusão: {exc}")
        return 5

    # Limpa somente o espelho local do MESMO endereço exato. Não toca em
    # outras caixas e não depende de user_id/flag de investidor para decidir.
    db = SessionLocal()
    try:
        rows = db.query(EmailAccount).filter(EmailAccount.email_address == ALVO).all()
        ids = [row.id for row in rows]
        for row in rows:
            db.delete(row)
        db.add(AuditLog(
            user_id=None,
            action="mail360_investidor_cleanup",
            entity="email_accounts",
            entity_id=key,
            detail={
                "email_address": ALVO,
                "mail360_account_key": key,
                "local_email_account_ids": ids,
                "origem": "comando_operacional_explicito",
            },
        ))
        db.commit()
    finally:
        db.close()

    print(f"OK: caixa real {ALVO} excluída do Mail360 e espelho local exato removido.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpeza segura da caixa real do Investidor no Mail360.")
    parser.add_argument("--apply", action="store_true", help="Executa a exclusão após match exato.")
    args = parser.parse_args()
    raise SystemExit(executar(args.apply))


if __name__ == "__main__":
    main()
