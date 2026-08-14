"""Modo Investidor — demonstração global somente leitura.

O frontend pode esconder/desabilitar ações para UX, mas a barreira real é
servidor-side: investidor navega e conhece o produto sem criar, alterar,
excluir, enviar, conectar, sincronizar, gerar, emitir, assinar ou exportar.
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

# Únicas escritas persistentes necessárias à própria experiência de entrada.
_ESCRITAS_UX_PERMITIDAS = {
    "/api/auth/sessao",
    "/api/auth/login",
    "/api/auth/sair",
    "/api/auth/me/onboarding-concluido",
    "/api/auth/me/boas-vindas-vista",
}


def _get_com_efeito_colateral(path: str) -> bool:
    """GETs que não são leitura passiva para a conta Investidor.

    Além do OAuth (que cria estado/conexão), algumas rotas GET entregam um
    artefato operacional pronto para uso fora da plataforma. A conta demo pode
    conhecer a superfície, mas não pode baixar exame/material real, emitir PDF
    nem obter uma prescrição pronta para impressão.
    """
    if path.startswith("/api/agenda/oauth/") and path.endswith("/start"):
        return True

    if path.startswith("/api/document-templates/gerados/") and path.endswith("/pdf"):
        return True
    if path.startswith("/api/material-paciente/") and path.endswith("/pdf"):
        return True
    if path.startswith("/api/pedidos/") and path.endswith("/exame"):
        return True
    if path.startswith("/api/prescriptions/") and path.endswith("/imprimir"):
        return True

    # Materiais de cursos são anexos para download. A página/ementa do curso
    # continua navegável; só a exportação do arquivo é bloqueada.
    partes = [parte for parte in path.split("/") if parte]
    if len(partes) == 5 and partes[:2] == ["api", "cursos"] and partes[3] == "material":
        return True

    return False


def _token_da_requisicao(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return token
    return request.cookies.get(AUTH_COOKIE_NAME)


class InvestidorReadOnlyMiddleware:
    """Fail-closed para qualquer mutação futura da API.

    POST/PUT/PATCH/DELETE novos ficam automaticamente bloqueados para
    investidor, sem depender de o autor do endpoint lembrar da regra.
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

        if path.startswith("/api/"):
            mutacao = method not in {"GET", "HEAD", "OPTIONS"}
            get_operacional = method == "GET" and _get_com_efeito_colateral(path)
            precisa_checar = (
                (mutacao and path not in _ESCRITAS_UX_PERMITIDAS)
                or get_operacional
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


def _preparar_investidor(target: User) -> None:
    """Matriz aplicada ao criar ou converter uma conta para Investidor."""
    target.investidor = True
    target.convidado = False
    target.is_active = True
    target.status = "aprovado"
    target.profile_completion_required = False
    target.onboarding_visto = False
    target.password_hash = hash_password(SENHA_FIXA_INVESTIDOR)


def _antes_de_inserir(_mapper, _connection, target: User) -> None:
    if bool(getattr(target, "investidor", False)):
        _preparar_investidor(target)


def _restaurar_valor_anterior(estado, atributo: str, target: User) -> None:
    historico = estado.attrs[atributo].history
    if historico.has_changes() and historico.deleted:
        setattr(target, atributo, historico.deleted[0])


def _antes_de_atualizar(_mapper, _connection, target: User) -> None:
    estado = inspect(target)
    historico_investidor = estado.attrs.investidor.history
    concedendo_agora = bool(target.investidor and historico_investidor.has_changes())

    if concedendo_agora:
        _preparar_investidor(target)
        return

    if not bool(getattr(target, "investidor", False)):
        return

    # Enquanto for Investidor, não pode simultaneamente voltar a Convidado e
    # nunca deve reabrir gate de perfil/KYC por dado legado.
    target.convidado = False
    target.profile_completion_required = False

    # Navegar pela demo faz current_user atualizar last_seen_at como telemetria
    # normal do produto. Para o Investidor isso também precisa ser passivo:
    # restaura o valor anterior antes do flush, sem alterar o core compartilhado
    # de autenticação/presença dos demais usuários.
    _restaurar_valor_anterior(estado, "last_seen_at", target)

    # Senha fixa: qualquer rota antiga, reset público ou edição administrativa
    # que tente trocar a senha é neutralizada no modelo. Também restauramos o
    # marco de revogação que o listener de User.password_hash teria alterado,
    # evitando invalidar a sessão por uma troca que não aconteceu.
    estado_senha = estado.attrs.password_hash.history
    if estado_senha.has_changes() and estado_senha.deleted:
        target.password_hash = estado_senha.deleted[0]
        _restaurar_valor_anterior(estado, "sessions_valid_after", target)


def _registrar_listeners() -> None:
    global _listeners_registrados
    if _listeners_registrados:
        return
    event.listen(User, "before_insert", _antes_de_inserir)
    event.listen(User, "before_update", _antes_de_atualizar)
    _listeners_registrados = True


def configurar_modo_investidor() -> None:
    """Registra invariantes de modelo; gates de auth vivem em app/api/auth.py."""
    _registrar_listeners()
