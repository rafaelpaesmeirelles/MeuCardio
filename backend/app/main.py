from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    account_access_admin, account_sync, admin, admin_user_management, ai, appointments, assinatura, auth, avaliacao_preoperatoria, browser_session,
    calculators, chat, chat_session,
    cmed, documents, documentos_publicos, drug_insights, drugs, email as email_api, email_session, evidence,
    favorites, gallery, guideline_updates, health, kyc, lab_tests, library, mail360_status,
    partner_courses, password_reset, prescriptions, presence, round as round_api, search,
    service_orders, sessions, social_login, specialty_guides, studies, timeline, billing, guidelines, indicadores,
    checklists, study_tracks, exportacao, exportacao_universal, emergencia, receituario, clinical_cases, agenda_integrada,
    related_content, knowledge_graph, patient_profiles,
)
from app.core.canonical_registration import CanonicalRegistrationMiddleware
from app.core.config import settings
from app.core.course_uploads import CourseUploadSecurityMiddleware
from app.core.http_security import HttpSecurityMiddleware
from app.core.oauth_session_recovery import OAuthSessionRecoveryMiddleware
from app.core.observability import ObservabilityMiddleware, configure_observability_logging
from app.core.runtime import validar_configuracao_de_execucao
from app.core.security import assinante_ativo
from app.core.uploads import UploadSecurityMiddleware
from app.services.investidor_demo import InvestidorReadOnlyMiddleware, configurar_modo_investidor
from app.services.investidor_ephemeral_ux import InvestidorEphemeralUxMiddleware

configure_observability_logging()
validar_configuracao_de_execucao(settings)
configurar_modo_investidor()

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
# O round-trip OAuth acontece fora do domínio CorVIA. Depois que o callback
# consumiu com sucesso o state de uso único, reemitimos a sessão HttpOnly da
# mesma conta antes de voltar ao SPA. Isto elimina o retorno indevido a
# /entrar observado com Google/Microsoft sem transformar state em login
# genérico nem aceitar user_id vindo do navegador.
app.add_middleware(OAuthSessionRecoveryMiddleware)
# Barreira fail-closed de produto: qualquer endpoint novo que faça escrita
# nasce bloqueado para User.investidor, inclusive routers "livres" como
# billing/auth/email.
app.add_middleware(InvestidorReadOnlyMiddleware)
# Camada exterior e estritamente efêmera: conclui tour/boas-vindas por cookie
# HttpOnly de sessão vinculado ao token atual, sem persistir flags no banco.
# Também classifica o início de OAuth como ação operacional read-only bloqueada.
app.add_middleware(InvestidorEphemeralUxMiddleware)
# A URL antiga de autocadastro vira um tombstone HTTP: toda conta real criada
# pela interface/API pública precisa fornecer segundo e-mail externo.
app.add_middleware(CanonicalRegistrationMiddleware)

ROUTERS_LIVRES = (
    health.router, auth.router, browser_session.router, social_login.router, password_reset.router,
    sessions.router, billing.router,
    # Precisa preceder admin.router: substitui somente /users/{id}/decidir para
    # acrescentar a notificação transacional sem quebrar o frontend existente.
    account_access_admin.router, admin.router, admin_user_management.router,
    service_orders.router, partner_courses.router, email_api.router, email_session.router,
    documentos_publicos.router, cmed.router, agenda_integrada.oauth_callback_router,
)

ROUTERS_ASSINANTES = (
    library.router, search.router, calculators.router, drugs.router, drug_insights.router,
    round_api.router, ai.router, gallery.router, favorites.router, lab_tests.router,
    evidence.router, studies.router, prescriptions.router, documents.router,
    appointments.router, timeline.router, guidelines.router, guideline_updates.router,
    mail360_status.router, presence.router, indicadores.router, checklists.router,
    study_tracks.router, exportacao.router, exportacao_universal.router, emergencia.router, receituario.router,
    clinical_cases.router, specialty_guides.router, chat.router, assinatura.router,
    # account_sync vem ANTES de agenda_integrada durante a janela de
    # compatibilidade porque expõe também o alias legado /sync-all. Assim os
    # botões antigos da Agenda passam pelo mesmo supervisor capability-aware
    # do /sync-live sem duplicar a regra de sincronização.
    account_sync.router, agenda_integrada.router, kyc.router, avaliacao_preoperatoria.router,
    related_content.router, knowledge_graph.router, patient_profiles.router,
)

for router in ROUTERS_LIVRES:
    app.include_router(router)

for router in ROUTERS_ASSINANTES:
    app.include_router(router, dependencies=[Depends(assinante_ativo)])

app.include_router(chat_session.router_ws)