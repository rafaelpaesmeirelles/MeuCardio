#!/usr/bin/env python3
"""Falha a CI quando uma funcionalidade publicada desaparece da aplicação.

O inventário protege tanto a existência das rotas quanto a discoverability nas
navegações CANÔNICAS que o usuário realmente vê. Não é permitido validar uma
sidebar legada escondida por CSS e concluir, por engano, que a feature continua
acessível.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "frontend/src/App.tsx"
DESKTOP_NAV = ROOT / "frontend/src/components/ClinicalDesktopNav.tsx"
MOBILE_NAV = ROOT / "frontend/src/components/ClinicalMobileNav.tsx"
MAIN = ROOT / "backend/app/main.py"

EXPECTED_APP_ROUTES = {
    "/", "/produto", "/entrar", "/solicitar-acesso", "/esqueci-senha", "/redefinir-senha",
    "/privacidade", "/termos", "/validar", "/validar/:codigo",
    "/corvia-mail", "/apresentacao", "/biblioteca", "/biblioteca/:slug",
    "/doencas", "/doencas/:slug", "/triagem-sintomas",
    "/fluxogramas", "/diretrizes", "/busca", "/calculadoras",
    "/calculadoras/:slug", "/cardiologia-intensiva", "/medicamentos", "/interacoes", "/condicoes",
    "/galeria", "/galeria/:slug", "/exames", "/exames/:slug", "/evidencias",
    "/evidencias/:slug", "/estudos", "/estudos/:slug", "/trilhas",
    "/trilhas/timeline",
    "/material-paciente", "/material-paciente/:slug", "/emergencia",
    "/trilhas/:slug", "/casos-clinicos", "/casos-clinicos/:slug",
    "/checklists", "/checklists/:slug", "/checklists/alta/:id",
    "/indicadores", "/cursos", "/cursos/:slug", "/favoritos", "/assistente",
    "/round", "/prontuario", "/ecg-ia", "/exames-ia", "/agenda", "/documentos", "/exportar", "/avaliacao-preoperatoria", "/receituario", "/assinatura",
    "/minha-conta", "/excluir-conta", "/telediagnostico", "/caixa-de-email", "/usuarios-online",
    "/admin", "/fila-telediagnostico", "/receitas-para-assinatura", "/admin/usuarios-online",
    "/admin/usuarios", "/admin/usuarios/:id", "/admin/usuarios/:id/gerenciar",
    "/tour", "/em-breve", "/verificacao-identidade",
    "/sincronizacao",
}

EXPECTED_NAV_ROUTES = {
    "/", "/apresentacao", "/agenda", "/condicoes", "/diretrizes", "/assistente", "/doencas",
    "/triagem-sintomas", "/biblioteca", "/busca", "/busca?modo=tudo-com-tudo", "/calculadoras", "/emergencia",
    "/cardiologia-intensiva",
    "/casos-clinicos", "/interacoes", "/checklists", "/corvia-mail", "/cursos",
    "/documentos", "/exportar", "/avaliacao-preoperatoria", "/estudos", "/evidencias", "/exames", "/favoritos",
    "/fluxogramas", "/galeria", "/telediagnostico", "/material-paciente",
    "/medicamentos", "/indicadores", "/receituario", "/round", "/prontuario", "/exames-ia", "/trilhas", "/trilhas/timeline",
    "/usuarios-online", "/minha-conta", "/excluir-conta", "/privacidade", "/termos", "/admin", "/fila-telediagnostico", "/receitas-para-assinatura",
    "/sincronizacao", "/admin/usuarios", "/tour", "/tour?origem=assinatura&modo=quick",
}

EXPECTED_BACKEND_ROUTERS = {
    "health.router", "auth.router", "browser_session.router", "social_login.router", "password_reset.router",
    "sessions.router", "billing.router", "account_access_admin.router", "admin.router", "admin_user_management.router", "service_orders.router",
    "partner_courses.router", "email_api.router", "email_session.router", "documentos_publicos.router",
    "cmed.router", "library.router", "search.router", "calculators.router",
    "drugs.router", "drug_insights.router", "round_api.router", "ai.router",
    "gallery.router", "favorites.router", "lab_tests.router", "evidence.router",
    "studies.router", "prescriptions.router", "prescricao_especial.router", "documents.router", "appointments.router",
    "timeline.router", "guidelines.router", "guideline_updates.router",
    "mail360_status.router", "presence.router", "indicadores.router",
    "checklists.router", "study_tracks.router", "exportacao.router", "exportacao_universal.router",
    "emergencia.router", "receituario.router", "clinical_cases.router",
    "specialty_guides.router", "chat.router", "assinatura.router", "agenda_integrada.router", "agenda_clinica.router",
    "encounter_artifacts.router", "avaliacao_preoperatoria.router", "chat_session.router_ws", "kyc.router",
    "related_content.router", "knowledge_graph.router", "patient_profiles.router", "patient_timeline.router",
    "account_sync.router", "ecg_quick.router", "cardiovascular_exam_ai.router",
}

EXPECTED_SUPPORT_FILES = {
    ".github/workflows/release-final-dispatch.yml",
    "frontend/src/components/ChatFlutuante.tsx",
    "frontend/src/components/PersonalAssistantPanel.tsx",
    "frontend/src/components/ShellClinicalOSLaunch.tsx",
    "frontend/src/components/ClinicalDesktopNav.tsx",
    "frontend/src/components/ClinicalMobileNav.tsx",
    "frontend/src/pages/PainelClinicalOS.tsx",
    "frontend/src/pages/TourClinicalOS.tsx",
    "frontend/src/pages/EmBreve.tsx",
    "frontend/src/pages/ECGQuickOpinion.tsx",
    "frontend/src/pages/CardiovascularExamAI.tsx",
    "frontend/src/pages/Admin.tsx",
    "frontend/src/pages/AdminGerenciarUsuario.tsx",
    "frontend/src/pages/Apresentacao.tsx",
    "frontend/src/pages/Assistente.tsx",
    "frontend/src/pages/Assinatura.tsx",
    "frontend/src/pages/AvaliacaoPreOperatoria.tsx",
    "frontend/src/pages/Biblioteca.tsx",
    "frontend/src/pages/CaixaDeEmail.tsx",
    "frontend/src/pages/CorviaMail.tsx",
    "frontend/src/pages/ValidarDocumento.tsx",
    "frontend/src/pages/Agenda.tsx",
    "frontend/src/pages/ExportarConteudo.tsx",
    "frontend/src/pages/Produto.tsx",
    "frontend/src/pages/PoliticaPrivacidade.tsx",
    "frontend/src/pages/TermosUso.tsx",
    "frontend/src/pages/Emergencia.tsx",
    "frontend/src/pages/CardiologiaIntensiva.tsx",
    "frontend/src/pages/ChecklistModelo.tsx",
    "frontend/src/pages/MaterialPacienteDetalhe.tsx",
    "frontend/src/pages/GuiaDoencas.tsx",
    "frontend/src/pages/GuiaDoenca.tsx",
    "frontend/src/pages/TriagemSintomas.tsx",
    "frontend/src/pages/Receituario.tsx",
    "frontend/src/pages/Round.tsx",
    "frontend/src/pages/RoundGerenciavel.tsx",
    "frontend/src/pages/Telediagnostico.tsx",
    "frontend/src/pages/UsuariosOnline.tsx",
    "backend/app/api/account_access_admin.py",
    "backend/app/api/admin_user_management.py",
    "backend/app/api/assinatura.py",
    "backend/app/api/avaliacao_preoperatoria.py",
    "backend/app/api/chat.py",
    "backend/app/api/drug_insights.py",
    "backend/app/api/email.py",
    "backend/app/api/emergencia.py",
    "backend/app/api/ecg_quick.py",
    "backend/app/api/cardiovascular_exam_ai.py",
    "backend/app/api/exportacao_universal.py",
    "backend/app/api/guideline_updates.py",
    "backend/app/api/mail360_status.py",
    "backend/app/api/presence.py",
    "backend/app/api/receituario.py",
    "backend/app/api/service_orders.py",
    "backend/app/api/clinical_cases.py",
    "backend/app/api/account_sync.py",
    "backend/app/api/agenda_integrada.py",
    "backend/app/api/social_login.py",
    "backend/app/api/specialty_guides.py",
    "backend/app/models/account_recovery.py",
    "backend/app/models/specialty_guide.py",
    "backend/app/models/agenda.py",
    "backend/app/services/account_recovery.py",
    "backend/app/services/release_certification.py",
    "backend/app/services/perioperative_calculators.py",
    "backend/app/services/intensive_care_calculators.py",
    "backend/app/services/account_sync.py",
    "backend/tests/test_account_recovery_email.py",
    "backend/tests/test_investidor_agenda_synthetic.py",
    "backend/tests/test_investidor_assistant_tool_guard.py",
    "backend/tests/test_account_sync_realtime.py",
    "backend/app/services/agenda_integrada/connectors.py",
    "backend/app/services/agenda_integrada/domain.py",
    "backend/app/services/agenda_integrada/traffic.py",
    "backend/app/services/clinical_rule_engine.py",
    "backend/app/services/carregar_doencas_especializadas.py",
    "backend/app/services/carregar_triagem_sintomas.py",
    "backend/app/commands/reconcile_content.py",
    "backend/migrations/versions/f48a20260805_specialty_guides.py",
    "backend/migrations/versions/f49a20260805_agenda_integrada.py",
    "backend/migrations/versions/f75a20260814_account_recovery_email.py",
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
        raise AssertionError(f"{label} divergiu. Ausentes={missing}; novos_nao_revisados={unexpected}")


def _navigation_paths(*sources: str) -> set[str]:
    """Inventaria destinos das navegações canônicas visíveis desktop/mobile."""
    paths: set[str] = set()
    for source in sources:
        paths.update(re.findall(r'\bto:\s*"([^"]+)"', source))
        paths.update(re.findall(r'<NavLink\s+to="([^"]+)"', source))
        paths.update(re.findall(r'<Link\s+to="([^"]+)"', source))
    return {normalize_route(path) for path in paths}


def main() -> int:
    app_source = APP.read_text(encoding="utf-8")
    desktop_nav_source = DESKTOP_NAV.read_text(encoding="utf-8")
    mobile_nav_source = MOBILE_NAV.read_text(encoding="utf-8")
    main_source = MAIN.read_text(encoding="utf-8")

    route_paths = {
        normalize_route(path)
        for path in re.findall(r'<Route\s+path="([^"]+)"', app_source)
        if path != "*"
    }
    if re.search(r"<Route\s+index\b", app_source):
        route_paths.add("/")
    assert_exact("Rotas React", route_paths, EXPECTED_APP_ROUTES)

    nav_paths = _navigation_paths(desktop_nav_source, mobile_nav_source)
    assert_exact("Destinos da navegação canônica visível", nav_paths, EXPECTED_NAV_ROUTES)

    backend_routers = set(re.findall(r"\b([a-z0-9_]+\.(?:router|router_ws))\b", main_source))
    assert_exact("Routers FastAPI", backend_routers, EXPECTED_BACKEND_ROUTERS)

    eager_pages = set(re.findall(r'import\s+\w+\s+from\s+"\./pages/([^"]+)"', app_source))
    lazy_pages = set(re.findall(r'lazy\s*\(\s*\(\)\s*=>\s*import\s*\(\s*"\./pages/([^"]+)"\s*\)\s*\)', app_source))
    imported_pages = eager_pages | lazy_pages
    missing_pages = sorted(page for page in imported_pages if not (ROOT / "frontend/src/pages" / f"{page}.tsx").is_file())
    if missing_pages:
        raise AssertionError(f"Páginas importadas ausentes: {missing_pages}")
    if len(imported_pages) < 51:
        raise AssertionError(f"Apenas {len(imported_pages)} páginas registradas no App.tsx; mínimo publicado: 51")

    missing_support = sorted(path for path in EXPECTED_SUPPORT_FILES if not (ROOT / path).is_file())
    if missing_support:
        raise AssertionError(f"Arquivos funcionais de suporte ausentes: {missing_support}")

    print(
        "Inventário funcional íntegro e discoverable: "
        f"{len(route_paths)} rotas React, {len(nav_paths)} destinos nas navegações canônicas visíveis, "
        f"{len(backend_routers)} routers FastAPI, {len(imported_pages)} páginas importadas "
        f"e {len(EXPECTED_SUPPORT_FILES)} artefatos críticos. "
        "(baseline certificado anterior: 63 rotas React, 39 destinos de menu, 50 routers FastAPI)."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1)
