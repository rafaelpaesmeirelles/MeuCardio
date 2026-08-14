"""Modo Investidor — demonstração global somente leitura.

Esta é a barreira central de segurança para contas ``User.investidor``.
O frontend pode esconder/desabilitar ações para melhorar a UX, mas a decisão
real vive aqui: uma conta de demonstração pode navegar e ler o produto, nunca
executar operações reais.

A configuração também substitui, em runtime, a regra antiga de primeiro
acesso que exigia dados pessoais + KYC simplificado do investidor. A conta
investidor agora vai diretamente ao tour e, depois, ao Clinical OS.
"""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy import event, inspect

from app.core.db import SessionLocal
from app.core.security import AUTH_COOKIE_NAME, hash_password, usuario_por_token_app
from app.models.user import User

SENHA_FIXA_INVESTIDOR = "CorVIAOS"
MENSAGEM_MODO_INVESTIDOR = (
    "Modo investidor: esta conta é somente para visualização da plataforma."
)

# Únicas escritas de estado toleradas para a experiência de demonstração.
# Nenhuma delas cria/edita dado clínico, documento, integração, cobrança ou
# conteúdo operacional.
_ESCRITAS_UX_PERMITIDAS = {
    "/api/auth/sessao",
    "/api/auth/login",
    "/api/auth/sair",
    "/api/auth/me/onboarding-concluido",
    "/api/auth/me/boas-vindas-vista",
}

# GETs normalmente são leitura, mas OAuth usa GET para iniciar uma operação
# externa com efeito colateral. Esse caminho precisa ser bloqueado também.
def _get_com_efeito_colateral(path: str) -> bool:
    return path.startswith("/api/agenda/oauth/") and path.endswith("/start")


def _token_da_requisicao(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return token
    return request.cookies.get(AUTH_COOKIE_NAME)


class InvestidorReadOnlyMiddleware:
    """Bloqueia toda mutação real feita por um investidor autenticado.

    A checagem é global de propósito. Assim novos endpoints operacionais
    adicionados no futuro nascem fail-closed para investidor sem depender de
    alguém lembrar de colocar uma checagem específica na rota.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path
        method = request.method.upper()

        # Só inspeciona API. Assets/SPA continuam totalmente passivos.
        if path.startswith("/api/"):
            bloquear_metodo = method not in {"GET", "HEAD", "OPTIONS"}
            bloquear_get = method == "GET" and _get_com_efeito_colateral(path)
            precisa_checar = (
                (bloquear_metodo and path not in _ESCRITAS_UX_PERMITIDAS)
                or bloquear_get
            )

            if precisa_checar:
                token = _token_da_requisicao(request)
                if token:
                    db = SessionLocal()
                    try:
                        user = usuario_por_token_app(db, token)
                        if user is not None and bool(getattr(user, "investidor", False)):
                            response = JSONResponse(
                                status_code=403,
                                content={"detail": MENSAGEM_MODO_INVESTIDOR},
                            )
                            await response(scope, receive, send)
                            return
                    finally:
                        db.close()

        await self.app(scope, receive, send)


_listeners_registrados = False
_patches_aplicados = False


def _preparar_novo_investidor(target: User) -> None:
    """Matriz canônica aplicada ao criar/converter uma conta em investidor."""
    target.investidor = True
    target.convidado = False
    target.is_active = True
    target.status = "aprovado"
    target.profile_completion_required = False
    target.onboarding_visto = False
    target.password_hash = hash_password(SENHA_FIXA_INVESTIDOR)


def _antes_de_inserir(_mapper, _connection, target: User) -> None:
    if bool(getattr(target, "investidor", False)):
        _preparar_novo_investidor(target)


def _antes_de_atualizar(_mapper, _connection, target: User) -> None:
    estado = inspect(target)
    historico_investidor = estado.attrs.investidor.history
    concedendo_agora = bool(target.investidor and historico_investidor.has_changes())

    if concedendo_agora:
        _preparar_novo_investidor(target)
        return

    if not bool(getattr(target, "investidor", False)):
        return

    # Mesmo em registros legados, investidor nunca volta a exigir perfil.
    target.profile_completion_required = False

    # Senha do modo demonstração é fixa. Se qualquer rota antiga/admin tentar
    # trocá-la enquanto a conta continuar investidor, restaura o hash anterior.
    # A conversão inicial é tratada acima e recebe um novo hash de CorVIAOS.
    historico_senha = estado.attrs.password_hash.history
    if historico_senha.has_changes() and historico_senha.deleted:
        target.password_hash = historico_senha.deleted[0]


def _registrar_listeners() -> None:
    global _listeners_registrados
    if _listeners_registrados:
        return
    event.listen(User, "before_insert", _antes_de_inserir)
    event.listen(User, "before_update", _antes_de_atualizar)
    _listeners_registrados = True


def _patch_auth_runtime() -> None:
    """Atualiza os gates já usados por /auth/me sem duplicar o endpoint.

    As funções de ``auth.py`` consultam esses nomes no namespace do módulo em
    tempo de execução. Trocá-los aqui mantém um único endpoint e evita uma
    segunda implementação de perfil/onboarding.
    """
    global _patches_aplicados
    if _patches_aplicados:
        return

    from app.api import auth

    kyc_original = auth._kyc_required
    perfil_original = auth._perfil_completo
    payload_original = auth.profile_payload

    def kyc_required_investidor(db, user):
        if bool(getattr(user, "investidor", False)):
            return False
        return kyc_original(db, user)

    def perfil_completo_investidor(user):
        if bool(getattr(user, "investidor", False)):
            return True
        return perfil_original(user)

    def profile_payload_investidor(user):
        payload = payload_original(user)
        if bool(getattr(user, "investidor", False)):
            payload["profile_completion_required"] = False
        return payload

    auth._kyc_required = kyc_required_investidor
    auth._perfil_completo = perfil_completo_investidor
    auth.profile_payload = profile_payload_investidor
    _patches_aplicados = True


def configurar_modo_investidor() -> None:
    """Chamado uma vez no bootstrap da API."""
    _registrar_listeners()
    _patch_auth_runtime()
