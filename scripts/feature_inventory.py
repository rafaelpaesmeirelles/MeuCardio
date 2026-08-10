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
    "/", "/produto", "/entrar", "/solicitar-acesso", "/esqueci-senha", "/redefinir-senha",
    "/privacidade", "/termos",
    "/corvia-mail", "/apresentacao", "/biblioteca", "/biblioteca/:slug",
    "/doencas", "/doencas/:slug", "/triagem-sintomas",
    "/fluxogramas", "/diretrizes", "/busca", "/calculadoras",
    "/calculadoras/:slug", "/medicamentos", "/interacoes", "/condicoes",
    "/galeria", "/galeria/:slug", "/exames", "/exames/:slug", "/evidencias",
    "/evidencias/:slug", "/estudos", "/estudos/:slug", "/trilhas",
    "/trilhas/timeline",
    "/material-paciente", "/emergencia", "/trilhas/:slug", "/casos-clinicos",
    "/casos-clinicos/:slug", "/checklists", "/checklists/alta/:id",
    "/indicadores", "/cursos", "/cursos/:slug", "/favoritos", "/assistente",
    "/round", "/agenda", "/documentos", "/avaliacao-preoperatoria", "/receituario", "/assinatura",
    "/minha-conta", "/telediagnostico", "/caixa-de-email", "/usuarios-online",
    "/admin", "/fila-telediagnostico", "/admin/usuarios-online",
    # Trabalho 13 (tour guiado) e Trabalho 11/12 (gate de identidade
    # pós-pagamento) — as duas são redirecionamento de gate, não item de
    # menu, por isso não entram em EXPECTED_NAV_ROUTES.
    "/tour", "/verificacao-identidade",
    # Trabalho 16 (07/08/2026): item próprio no menu (seção Gestão).
    "/sincronizacao",
}

EXPECTED_NAV_ROUTES = {
    "/", "/apresentacao", "/agenda", "/condicoes", "/diretrizes", "/assistente", "/doencas",
    "/triagem-sintomas", "/biblioteca", "/busca", "/calculadoras",
    "/casos-clinicos", "/interacoes", "/checklists", "/corvia-mail", "/cursos",
    "/documentos", "/avaliacao-preoperatoria", "/estudos", "/evidencias", "/exames", "/favoritos",
    "/fluxogramas", "/galeria", "/telediagnostico", "/material-paciente",
    "/medicamentos", "/indicadores", "/receituario", "/round", "/trilhas",
    "/usuarios-online", "/minha-conta", "/assinatura", "/admin", "/fila-telediagnostico",
    "/sincronizacao",
}

EXPECTED_BACKEND_ROUTERS = {
    "health.router", "auth.router", "browser_session.router", "password_reset.router",
    "sessions.router", "billing.router", "admin.router", "service_orders.router",
    "partner_courses.router", "email_api.router",
    # CorvIA Mail — renovação/persistência da sessão própria da caixa
    # (commits 866f0caa/940a812c, 09/08/2026). Faltava aqui — lacuna
    # pré-existente à branch de estabilização (issue #52), encontrada e
    # fechada na subfase 8 (Release Candidate), mesmo padrão de
    # `related_content.router` logo abaixo.
    "email_session.router", "documentos_publicos.router",
    "cmed.router", "library.router", "search.router", "calculators.router",
    "drugs.router", "drug_insights.router", "round_api.router", "ai.router",
    "gallery.router", "favorites.router", "lab_tests.router", "evidence.router",
    "studies.router", "prescriptions.router", "documents.router", "appointments.router",
    "timeline.router", "guidelines.router", "guideline_updates.router",
    "mail360_status.router", "presence.router", "indicadores.router",
    "checklists.router", "study_tracks.router", "exportacao.router",
    "emergencia.router", "receituario.router", "clinical_cases.router",
    "specialty_guides.router", "chat.router", "assinatura.router", "agenda_integrada.router",
    "avaliacao_preoperatoria.router", "chat_session.router_ws",
    # Trabalho 11 (06/08/2026): verificação de identidade pós-pagamento (KYC).
    "kyc.router",
    # Tarefa #54 (08/08/2026): Hub "Tudo sobre este tema" (`GET /api/relacionados`).
    # Faltava aqui — lacuna pré-existente encontrada e fechada durante a tarefa
    # #53 (timeline de evolução do conhecimento), sem relação direta com ela.
    "related_content.router",
    # Grafo de Conhecimento Clínico Universal (issue #52, nova fase, 11/08/2026):
    # `GET /api/grafo/relacionados` — camada persistida/tipada, distinta do
    # cruzamento em tempo de consulta de `related_content.router` acima.
    "knowledge_graph.router",
}

EXPECTED_SUPPORT_FILES = {
    "frontend/src/components/ChatFlutuante.tsx",
    "frontend/src/pages/Admin.tsx",
    "frontend/src/pages/Apresentacao.tsx",
    "frontend/src/pages/Assistente.tsx",
    "frontend/src/pages/Assinatura.tsx",
    "frontend/src/pages/AvaliacaoPreOperatoria.tsx",
    "frontend/src/pages/Biblioteca.tsx",
    "frontend/src/pages/CaixaDeEmail.tsx",
    "frontend/src/pages/CorviaMail.tsx",
    "frontend/src/pages/Agenda.tsx",
    "frontend/src/pages/Produto.tsx",
    "frontend/src/pages/PoliticaPrivacidade.tsx",
    "frontend/src/pages/TermosUso.tsx",
    "frontend/src/pages/Emergencia.tsx",
    "frontend/src/pages/GuiaDoencas.tsx",
    "frontend/src/pages/GuiaDoenca.tsx",
    "frontend/src/pages/TriagemSintomas.tsx",
    "frontend/src/pages/Receituario.tsx",
    "frontend/src/pages/Round.tsx",
    "frontend/src/pages/RoundGerenciavel.tsx",
    "frontend/src/pages/Telediagnostico.tsx",
    "frontend/src/pages/UsuariosOnline.tsx",
    "backend/app/api/assinatura.py",
    "backend/app/api/avaliacao_preoperatoria.py",
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
    "backend/app/api/agenda_integrada.py",
    "backend/app/api/specialty_guides.py",
    "backend/app/models/specialty_guide.py",
    "backend/app/models/agenda.py",
    "backend/app/services/perioperative_calculators.py",
    "backend/app/services/agenda_integrada/connectors.py",
    "backend/app/services/agenda_integrada/domain.py",
    "backend/app/services/agenda_integrada/traffic.py",
    "backend/app/services/clinical_rule_engine.py",
    "backend/app/services/carregar_doencas_especializadas.py",
    "backend/app/services/carregar_triagem_sintomas.py",
    "backend/app/commands/reconcile_content.py",
    "backend/migrations/versions/f48a20260805_specialty_guides.py",
    "backend/migrations/versions/f49a20260805_agenda_integrada.py",
    "doencas/metadados.json",
    "triagem-sintomas/metadados.json",
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
        re.findall(r"\b([a-z0-9_]+\.(?:router|router_ws))\b", main_source)
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
    if len(imported_pages) < 51:
        raise AssertionError(
            f"Apenas {len(imported_pages)} páginas registradas no App.tsx; mínimo publicado: 51"
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
