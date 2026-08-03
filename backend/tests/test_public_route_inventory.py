from fastapi.routing import APIRoute

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
    ("GET", "/api/pedidos/precos"): "Catálogo comercial necessário antes de login ou assinatura.",
    ("GET", "/api/documentos-publicos/{token}"): (
        "Download destinado ao paciente, autorizado por token de alta entropia na URL."
    ),
    ("POST", "/api/auth/login"): "Emissão inicial da sessão da plataforma.",
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
    for dependency in dependant.dependencies:
        if dependency.call in AUTH_CALLS:
            return True
        if _dependency_tree_contains_auth(dependency):
            return True
    return False


def _public_routes() -> set[tuple[str, str]]:
    routes: set[tuple[str, str]] = set()
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if _dependency_tree_contains_auth(route.dependant):
            continue
        for method in route.methods or set():
            if method not in {"HEAD", "OPTIONS"}:
                routes.add((method, route.path))
    return routes


def test_public_routes_are_explicitly_allowlisted():
    actual = _public_routes()
    assert actual == EXPECTED_PUBLIC_ROUTES, (
        "Inventário de rotas públicas mudou. Revise cada rota e atualize a "
        f"allowlist conscientemente. Encontradas: {sorted(actual)}"
    )


def test_every_public_route_has_a_reviewable_rationale():
    assert all(reason.strip() for reason in PUBLIC_ROUTE_RATIONALES.values())
