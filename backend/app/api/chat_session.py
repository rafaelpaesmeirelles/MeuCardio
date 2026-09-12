"""WebSocket do chat autenticado por cookie HttpOnly ou Bearer legado.

A rota substitui o handler antigo baseado exclusivamente em `?token=`. O
navegador envia o cookie no handshake sem expor o JWT na URL, histórico ou logs
de proxy. A query continua como fallback para clientes não-browser.
"""

import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.api.chat import _e_assinante, gerenciador
from app.core.db import SessionLocal
from app.core.security import AUTH_COOKIE_NAME, usuario_por_token_app

router_ws = APIRouter(prefix="/api/chat", tags=["chat"])


@router_ws.websocket("/ws")
async def chat_ws_cookie(
    ws: WebSocket,
    token: str | None = Query(default=None),
):
    # Cookie primeiro: o placeholder não secreto mantido pelo frontend não
    # pode sobrepor uma sessão real. Query Bearer só é usada sem cookie.
    session_token = ws.cookies.get(AUTH_COOKIE_NAME) or token

    db = SessionLocal()
    try:
        user = usuario_por_token_app(db, session_token)
        if user is None or not _e_assinante(db, user.id, user.role):
            await ws.close(code=4401)
            return
    finally:
        db.close()

    await gerenciador.conectar(user.id, ws)
    try:
        while True:
            try:
                await asyncio.wait_for(ws.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                pass
            # A fresh session avoids a stale ORM identity map. Revalidate even
            # when the client stops sending pings (maximum interval 30s).
            check = SessionLocal()
            try:
                current = usuario_por_token_app(check, session_token)
                valid = current is not None and _e_assinante(check, current.id, current.role)
            finally:
                check.close()
            if not valid:
                await ws.close(code=4401)
                break
    except WebSocketDisconnect:
        pass
    finally:
        gerenciador.desconectar(user.id, ws)
