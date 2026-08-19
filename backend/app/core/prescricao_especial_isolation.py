"""Isola prescrições livres especiais das APIs genéricas de documentos.

O fluxo especial tem autorização, revisão e requisitos de assinatura próprios.
Como ele reutiliza ``GeneratedDocument`` para persistência, uma prescrição
criada em nome do prescritor não pode herdar por acidente as rotas genéricas
``/api/document-templates/gerados``. Esta barreira é fail-closed e independe
do frontend.
"""
from __future__ import annotations

import json

from starlette.responses import JSONResponse

from app.core.db import SessionLocal
from app.models.clinical_docs import GeneratedDocument

DOC_TYPE_PRESCRICAO_ESPECIAL = "prescricao_livre_especial"
_PREFIXO = "/api/document-templates/gerados"


class PrescricaoEspecialIsolationMiddleware:
    def __init__(self, app):
        self.app = app

    @staticmethod
    def _gid(path: str) -> int | None:
        if not path.startswith(_PREFIXO + "/"):
            return None
        parte = path[len(_PREFIXO) + 1 :].split("/", 1)[0]
        try:
            return int(parte)
        except ValueError:
            return None

    @staticmethod
    def _eh_especial(gid: int) -> bool:
        db = SessionLocal()
        try:
            return bool(
                db.query(GeneratedDocument.id)
                .filter(
                    GeneratedDocument.id == gid,
                    GeneratedDocument.doc_type == DOC_TYPE_PRESCRICAO_ESPECIAL,
                )
                .first()
            )
        finally:
            db.close()

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or ""
        method = (scope.get("method") or "GET").upper()
        if not path.startswith(_PREFIXO):
            await self.app(scope, receive, send)
            return

        gid = self._gid(path)
        if gid is not None and self._eh_especial(gid):
            response = JSONResponse(status_code=404, content={"detail": "Documento não encontrado."})
            await response(scope, receive, send)
            return

        # A listagem genérica também não deve anunciar esses registros. A
        # filtragem é apenas uma defesa de apresentação; todas as rotas por id
        # já falham fechadas acima, portanto não existe bypass mesmo que uma
        # página antiga tenha sido cacheada pelo cliente.
        if method == "GET" and path.rstrip("/") == _PREFIXO:
            start = None
            body_parts: list[bytes] = []

            async def capture(message):
                nonlocal start
                if message["type"] == "http.response.start":
                    start = message
                    return
                if message["type"] != "http.response.body":
                    await send(message)
                    return
                body_parts.append(message.get("body", b""))
                if message.get("more_body", False):
                    return

                body = b"".join(body_parts)
                headers = list((start or {}).get("headers", []))
                status = int((start or {}).get("status", 200))
                if status == 200:
                    try:
                        payload = json.loads(body)
                        if isinstance(payload, dict) and isinstance(payload.get("items"), list):
                            antes = len(payload["items"])
                            payload["items"] = [
                                item for item in payload["items"]
                                if not (
                                    isinstance(item, dict)
                                    and item.get("doc_type") == DOC_TYPE_PRESCRICAO_ESPECIAL
                                )
                            ]
                            removidos = antes - len(payload["items"])
                            if removidos and isinstance(payload.get("total"), int):
                                payload["total"] = max(0, payload["total"] - removidos)
                            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                    except (TypeError, ValueError, UnicodeDecodeError):
                        pass

                headers = [(k, v) for k, v in headers if k.lower() != b"content-length"]
                headers.append((b"content-length", str(len(body)).encode("ascii")))
                await send({"type": "http.response.start", "status": status, "headers": headers})
                await send({"type": "http.response.body", "body": body, "more_body": False})

            await self.app(scope, receive, capture)
            return

        await self.app(scope, receive, send)
