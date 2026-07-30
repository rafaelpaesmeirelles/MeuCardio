from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin, ai, appointments, auth, calculators, documents, documentos_publicos, drugs,
    email as email_api, evidence,
    favorites, gallery, health, lab_tests, library, password_reset,
    prescriptions, round as round_api, search, service_orders, studies,
    timeline, billing, partner_courses, guidelines, indicadores, checklists, study_tracks,
    exportacao, emergencia, receituario,
)
from app.core.config import settings
from app.core.security import assinante_ativo
from app.services.bootstrap import init_db

app = FastAPI(
    title="Corvia — API",
    description=(
        "Idealizador, desenvolvedor, revisor e responsável técnico: "
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

# Acesso livre: entrar, recuperar senha, assinar e o próprio painel de admin
# (que já se restringe por papel). Todo o resto exige assinatura vigente.
# `service_orders` entra aqui, e não entre os routers de assinante, de
# propósito: laudo e consultoria são serviço avulso pago por fora — exigir
# assinatura vigente para comprá-los fecharia a porta justamente para o médico
# que ainda não assina e chegou pelo telediagnóstico.
# `email_api` também entra aqui, e pelo mesmo motivo estrutural: CorvIA Mail
# (Tarefa 28) é add-on cobrado à parte, não benefício da assinatura
# principal — aplicar `assinante_ativo` (que checa kind='meucardio') a este
# router bloquearia justo quem assina só o e-mail. Cada rota do router
# decide sua própria autorização (`current_user` + `assinatura_email_ativa`
# para status/ativação; `current_email_account`, com login e token
# próprios, para pastas e mensagens).
# `documentos_publicos` também entra aqui, mas por um motivo diferente dos
# outros: não é "sem assinatura vigente", é sem conta nenhuma — quem acessa
# é o PACIENTE (Tarefa 29), que nunca terá login na Corvia. A única defesa
# é o token de alta entropia na própria URL, não uma dependência de rota.
ROUTERS_LIVRES = (
    health.router, auth.router, password_reset.router, billing.router, admin.router,
    service_orders.router, partner_courses.router, email_api.router, documentos_publicos.router,
)

ROUTERS_ASSINANTES = (
    library.router, search.router, calculators.router, drugs.router, round_api.router,
    ai.router, gallery.router, favorites.router, lab_tests.router, evidence.router,
    studies.router, prescriptions.router, documents.router, appointments.router,
    timeline.router, guidelines.router, indicadores.router, checklists.router, study_tracks.router,
    exportacao.router, emergencia.router, receituario.router,
)

for r in ROUTERS_LIVRES:
    app.include_router(r)

for r in ROUTERS_ASSINANTES:
    app.include_router(r, dependencies=[Depends(assinante_ativo)])


@app.on_event("startup")
def on_startup() -> None:
    init_db()
