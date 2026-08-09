from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin, ai, appointments, assinatura, auth, avaliacao_preoperatoria, browser_session,
    calculators, chat, chat_session,
    cmed, documents, documentos_publicos, drug_insights, drugs, email as email_api, email_session, evidence,
    favorites, gallery, guideline_updates, health, kyc, lab_tests, library, mail360_status,
    partner_courses, password_reset, prescriptions, presence, round as round_api, search,
    service_orders, sessions, specialty_guides, studies, timeline, billing, guidelines, indicadores,
    checklists, study_tracks, exportacao, emergencia, receituario, clinical_cases, agenda_integrada,
    related_content,
)
from app.core.config import settings
from app.core.course_uploads import CourseUploadSecurityMiddleware
from app.core.http_security import HttpSecurityMiddleware
from app.core.observability import ObservabilityMiddleware, configure_observability_logging
from app.core.runtime import validar_configuracao_de_execucao
from app.core.security import assinante_ativo
from app.core.uploads import UploadSecurityMiddleware

configure_observability_logging()
validar_configuracao_de_execucao(settings)

app = FastAPI(
    title="Corvia — API",
    description=(
        "Idealizador, Desenvolvedor e Revisor: "
        "Dr. Rafael Paes Meirelles — CRM-SP 138266 · RQE 134798 em Cardiologia"
    ),
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(UploadSecurityMiddleware)
app.add_middleware(CourseUploadSecurityMiddleware)
app.add_middleware(HttpSecurityMiddleware)
app.add_middleware(ObservabilityMiddleware)

ROUTERS_LIVRES = (
    health.router, auth.router, browser_session.router, password_reset.router,
    sessions.router, billing.router, admin.router, service_orders.router,
    partner_courses.router, email_api.router, email_session.router, documentos_publicos.router, cmed.router,
    agenda_integrada.oauth_callback_router,
)

ROUTERS_ASSINANTES = (
    library.router, search.router, calculators.router, drugs.router, drug_insights.router,
    round_api.router, ai.router, gallery.router, favorites.router, lab_tests.router,
    evidence.router, studies.router, prescriptions.router, documents.router,
    appointments.router, timeline.router, guidelines.router, guideline_updates.router,
    mail360_status.router, presence.router, indicadores.router, checklists.router,
    study_tracks.router, exportacao.router, emergencia.router, receituario.router,
    clinical_cases.router, specialty_guides.router, chat.router, assinatura.router,
    agenda_integrada.router, kyc.router, avaliacao_preoperatoria.router,
    related_content.router,
)

for router in ROUTERS_LIVRES:
    app.include_router(router)

for router in ROUTERS_ASSINANTES:
    app.include_router(router, dependencies=[Depends(assinante_ativo)])

app.include_router(chat_session.router_ws)
