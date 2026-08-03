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

# Preenchida após o primeiro inventário automatizado. Qualquer rota nova sem
# autenticação precisa ser adicionada conscientemente aqui e revisada no diff.
EXPECTED_PUBLIC_ROUTES: set[tuple[str, str]] = set()


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
