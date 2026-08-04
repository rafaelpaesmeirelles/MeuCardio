from fastapi.routing import iter_route_contexts

from app.core.security import (
    assinante_ativo,
    current_email_account,
    current_user,
    oauth2_scheme,
    require_admin,
)
from app.main import app

AUTH_CALLS = {
    assinante_ativo,
    current_email_account,
    current_user,
    oauth2_scheme,
    require_admin,
}

# A chave é a superfície pública aprovada; o valor explica por que a rota não
# pode exigir uma sessão autenticada. Qualquer rota nova sem gate estrutural
# quebra a CI até ser protegida ou adicionada conscientemente a este inventário.
PUBLIC_ROUTE_RATIONALES: dict[tuple[str, str], str] = {
    ("GET", "/api/health"): "Liveness do processo para orquestrador e proxy.",
    ("GET", "/api/ready"): "Readiness sem segredos, usado pelo healthcheck do backend.",
    ("GET", "/api/version"): (
        "Comprovação externa do deploy; retorna somente o SHA Git injetado, sem configuração."
    ),
    ("GET", "/api/pedidos/precos"): "Catálogo comercial necessário antes de login ou assinatura.",
    ("GET", "/api/documentos-publicos/{token}"): (
        "Download destinado ao paciente, autorizado por token de alta entropia na URL."
    ),
    ("POST", "/api/auth/login"): "Emissão Bearer para integrações e clientes externos.",
    ("POST", "/api/auth/sessao"): "Emissão da sessão web em cookie HttpOnly antes da autenticação.",
    ("POST", "/api/auth/sair"): (
        "Limpeza idempotente do cookie HttpOnly mesmo quando expirado ou revogado."
    ),
    ("POST", "/api/auth/solicitar-acesso"): "Autocadastro anterior à autenticação.",
    ("POST", "/api/auth/esqueci-senha"): "Início da recuperação de credencial.",
    ("POST", "/api/auth/redefinir-senha"): "Conclusão da recuperação por token descartável.",
    ("POST", "/api/auth/reenviar-ativacao"): "Reenvio de ativação para conta ainda sem sessão.",
    ("POST", "/api/email/entrar"): "Emissão inicial da sessão separada da caixa de e-mail.",
    ("POST", "/api/email/esqueci-senha"): "Recuperação da senha própria da caixa de e-mail.",
    ("POST", "/api/billing/webhook"): (
        "Recepção servidor-a-servidor protegida pela assinatura criptográfica do Stripe."
    ),
}

EXPECTED_PUBLIC_ROUTES = set(PUBLIC_ROUTE_RATIONALES)


def _dependency_tree_contains_auth(dependant) -> bool:
    for dependency in getattr(dependant, "dependencies", ()):
        if dependency.call in AUTH_CALLS:
            return True
        if _dependency_tree_contains_auth(dependency):
            return True
    return False


def _public_routes() -> set[tuple[str, str]]:
    """Inventaria a superfície HTTP efetiva, inclusive routers incluídos.

    Desde o FastAPI 0.137, ``router.routes`` forma uma árvore e a API pública
    ``iter_route_contexts`` materializa prefixos e dependências herdados de
    ``include_router``. O ponto de entrada correto é ``app.router.routes``;
    ``app.routes`` é uma compatibilidade herdada do Starlette e não representa
    necessariamente a árvore efetiva do router FastAPI.
    """
    routes: set[tuple[str, str]] = set()
    for route_context in iter_route_contexts(app.router.routes):
        path = route_context.path
        methods = route_context.methods
        dependant = getattr(route_context, "dependant", None)
        if not path or not methods or dependant is None:
            continue
        if _dependency_tree_contains_auth(dependant):
            continue
        for method in methods:
            if method not in {"HEAD", "OPTIONS"}:
                routes.add((method, path))
    return routes


def test_public_routes_are_explicitly_allowlisted():
    actual = _public_routes()
    assert actual == EXPECTED_PUBLIC_ROUTES, (
        "Inventário de rotas públicas mudou. Revise cada rota e atualize a "
        f"allowlist conscientemente. Encontradas: {sorted(actual)}"
    )


def test_every_public_route_has_a_reviewable_rationale():
    assert all(reason.strip() for reason in PUBLIC_ROUTE_RATIONALES.values())
