"""Operações IMAP comuns usadas pelo CorvIA Mail.

Mantidas fora dos adaptadores Yahoo/iCloud para evitar duplicar a semântica
de mover para a Lixeira. Recebe somente credenciais já cifradas/decifradas
pelo domínio da integração e nunca persiste conteúdo de mensagem.
"""

from __future__ import annotations

import imaplib
from typing import Any, Type


def move_to_trash(
    credentials: dict[str, Any],
    message_id: str,
    *,
    host: str,
    trash_folder: str,
    error_cls: Type[RuntimeError],
) -> None:
    """Move uma mensagem IMAP para a lixeira usando UID.

    Os IDs Yahoo/iCloud no CorvIA são ``pasta:uid``. Se a mensagem já estiver
    na lixeira, a operação a remove definitivamente; fora dela, copia para a
    pasta de lixeira e só depois marca a origem como ``\\Deleted``.
    """
    if ":" not in message_id:
        raise error_cls("Identificador de mensagem inválido.")
    folder, uid = message_id.split(":", 1)
    username = str(credentials.get("username") or "")
    password = str(credentials.get("app_specific_password") or "")
    if not username or not password:
        raise error_cls("Conta sem credencial armazenada — reconecte.")

    try:
        connection = imaplib.IMAP4_SSL(host, 993, timeout=15)
        connection.login(username, password)
    except imaplib.IMAP4.error as exc:
        raise error_cls("Login IMAP recusado — a senha específica de app pode ter expirado.") from exc
    except OSError as exc:
        raise error_cls("Não foi possível conectar ao servidor IMAP.") from exc

    try:
        status, _ = connection.select(f'"{folder}"')
        if status != "OK":
            raise error_cls(f"Pasta '{folder}' não encontrada.")

        if folder != trash_folder:
            status, _ = connection.uid("copy", uid, f'"{trash_folder}"')
            if status != "OK":
                raise error_cls("Não foi possível mover a mensagem para a lixeira.")

        status, _ = connection.uid("store", uid, "+FLAGS", "\\Deleted")
        if status != "OK":
            raise error_cls("Não foi possível remover a mensagem da pasta atual.")
        connection.expunge()
    finally:
        try:
            connection.logout()
        except Exception:
            pass
