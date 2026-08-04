#!/usr/bin/env python3
"""Falha a CI quando uma funcionalidade publicada desaparece da aplicação.

Este inventário protege a superfície funcional; ele não substitui testes de
comportamento. Rotas novas exigem revisão explícita do baseline para que menus,
permissões e documentação não se afastem silenciosamente do produto publicado.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "frontend/src/App.tsx"
SHELL = ROOT / "frontend/src/components/Shell.tsx"
MAIN = ROOT / "backend/app/main.py"

EXPECTED_APP_ROUTES = {
    "/", "/entrar", "/solicitar-acesso", "/esqueci-senha", "/redefinir-senha",
    "/corvia-mail", "/apresentacao", "/biblioteca", "/biblioteca/:slug",
    "/fluxogramas", "/diretrizes", "/busca", "/calculadoras",
    "/calculadoras/:slug", "/medicamentos", "/interacoes", "/condicoes",
    "/galeria", "/galeria/:slug", "/exames", "/exames/:slug", "/evidencias",
    "/evidencias/:slug", "/estudos", "/estudos/:slug", "/trilhas",
    "/material-paciente", "/emergencia", "/trilhas/:slug", "/casos-clinicos",
    "/casos-clinicos/:slug", "/checklists", "/checklists/alta/:id",
    "/indicadores", "/cursos", "/cursos/:slug", "/favoritos", "/assistente",
    "/round", "/agenda", "/documentos", "/receituario", "/assinatura",
    "/minha-conta", "/telediagnostico", "/caixa-de-email", "/usuarios-online",
    "/admin", "/fila-telediagnostico", "/admin/usuarios-online",
}

EXPECTED_NAV_ROUTES = {
    "/", "/agenda", "/condicoes", "/diretrizes", "/assistente", "/biblioteca",
    "/busca", "/calculadoras", "/casos-clinicos", "/interacoes", "/checklists",
    "/corvia-mail", "/cursos", "/documentos", "/estudos", "/evidencias",
    "/exames", "/favoritos", "/fluxogramas", "/galeria", "/telediagnostico",
    "/material-paciente", "/medicamentos", "/indicadores", "/receituario",
    "/round", "/trilhas", "/usuarios-online", "/minha-conta", "/admin",
}

EXPECTED_BACKEND_ROUTERS = {
    "health.router", "auth.router", "browser_session.router", "password_reset.router",
    "sessions.router", "billing.router", "admin.router", "service_orders.router",
    "partner_courses.router", "email_api.router", "documentos_publicos.router",
    "cmed.router", "library.router", "search.router", "calculators.router",
    "drugs.router", "drug_insights.router", "round_api.router", "ai.router",
    "gallery.router", "favorites.router", "lab_tests.router", "evidence.router",
    "studies.router", "prescriptions.router", "documents.router", "appointments.router",
    "timeline.router", "guidelines.router", "guideline_updates.router",
    "mail360_status.router", "presence.router", "indicadores.router",
    "checklists.router", "study_tracks.router", "exportacao.router",
    "emergencia.router", "receituario.router", "clinical_cases.router",
    "chat.router", "assinatura.router", "chat_session.router_ws",
}

EXPECTED_SUPPORT_FILES = {
    "frontend/src/components/ChatFlutuante.tsx",
    "frontend/src/pages/Admin.tsx",
    "frontend/src/pages/Apresentacao.tsx",
    "frontend/src/pages/Assistente.tsx",
    "frontend/src/pages/Assinatura.tsx",
    "frontend/src/pages/Biblioteca.tsx",
    "frontend/src/pages/CaixaDeEmail.tsx",
    "frontend/src/pages/CorviaMail.tsx",
    "frontend/src/pages/Emergencia.tsx",
    "frontend/src/pages/Receituario.tsx",
    "frontend/src/pages/Round.tsx",
    "frontend/src/pages/RoundGerenciavel.tsx",
    "frontend/src/pages/Telediagnostico.tsx",
    "frontend/src/pages/UsuariosOnline.tsx",
    "backend/app/api/assinatura.py",
    "backend/app/api/chat.py",
    "backend/app/api/drug_insights.py",
    "backend/app/api/email.py",
    "backend/app/api/emergencia.py",
    "backend/app/api/guideline_updates.py",
    "backend/app/api/mail360_status.py",
    "backend/app/api/presence.py",
    "backend/app/api/receituario.py",
    "backend/app/api/service_orders.py",
    "backend/app/api/clinical_cases.py",
    "backend/app/commands/reconcile_content.py",
    "scripts/release_smoke.py",
    "ops/backup-postgres.sh",
    "ops/restore-postgres.sh",
}


def normalize_route(path: str) -> str:
    if path == "*":
        return path
    return path if path.startswith("/") else f"/{path}"


def assert_exact(label: str, actual: set[str], expected: set[str]) -> None:
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        raise AssertionError(
            f"{label} divergiu. Ausentes={missing}; novos_nao_revisados={unexpected}"
        )


def main() -> int:
    app_source = APP.read_text(encoding="utf-8")
    shell_source = SHELL.read_text(encoding="utf-8")
    main_source = MAIN.read_text(encoding="utf-8")

    route_paths = {
        normalize_route(path)
        for path in re.findall(r'<Route\s+path="([^"]+)"', app_source)
        if path != "*"
    }
    if re.search(r"<Route\s+index\b", app_source):
        route_paths.add("/")
    assert_exact("Rotas React", route_paths, EXPECTED_APP_ROUTES)

    nav_paths = set(re.findall(r'\bto:\s*"([^"]+)"', shell_source))
    assert_exact("Destinos de navegação", nav_paths, EXPECTED_NAV_ROUTES)

    backend_routers = set(
        re.findall(r"\b([a-z_]+\.(?:router|router_ws))\b", main_source)
    )
    assert_exact("Routers FastAPI", backend_routers, EXPECTED_BACKEND_ROUTERS)

    eager_pages = set(
        re.findall(r'import\s+\w+\s+from\s+"\./pages/([^"]+)"', app_source)
    )
    lazy_pages = set(
        re.findall(
            r'lazy\s*\(\s*\(\)\s*=>\s*import\s*\(\s*"\./pages/([^"]+)"\s*\)\s*\)',
            app_source,
        )
    )
    imported_pages = eager_pages | lazy_pages
    missing_pages = sorted(
        page for page in imported_pages
        if not (ROOT / "frontend/src/pages" / f"{page}.tsx").is_file()
    )
    if missing_pages:
        raise AssertionError(f"Páginas importadas ausentes: {missing_pages}")
    if len(imported_pages) < 48:
        raise AssertionError(
            f"Apenas {len(imported_pages)} páginas registradas no App.tsx; mínimo publicado: 48"
        )

    missing_support = sorted(path for path in EXPECTED_SUPPORT_FILES if not (ROOT / path).is_file())
    if missing_support:
        raise AssertionError(f"Arquivos funcionais de suporte ausentes: {missing_support}")

    print(
        "Inventário funcional íntegro: "
        f"{len(route_paths)} rotas React, {len(nav_paths)} destinos de menu, "
        f"{len(backend_routers)} routers FastAPI, {len(imported_pages)} páginas importadas "
        f"e {len(EXPECTED_SUPPORT_FILES)} artefatos críticos."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1)
