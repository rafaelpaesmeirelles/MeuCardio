"""Torna o cadastro com segundo e-mail o único fluxo HTTP canônico.

A função histórica de criação continua reutilizada internamente pelo endpoint
novo para evitar duplicação de regra de negócio, mas a URL pública antiga não
pode permanecer como atalho capaz de criar conta sem canal externo de
recuperação.
"""
from starlette.responses import JSONResponse


class CanonicalRegistrationMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (
            scope.get("type") == "http"
            and str(scope.get("method", "GET")).upper() == "POST"
            and str(scope.get("path", "")) == "/api/auth/solicitar-acesso"
        ):
            response = JSONResponse(
                status_code=410,
                content={
                    "detail": (
                        "Este fluxo de cadastro foi substituído. Use o cadastro atual, "
                        "que exige um segundo e-mail externo para recuperação de acesso."
                    )
                },
                headers={"Cache-Control": "no-store"},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
