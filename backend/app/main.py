from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin, ai, appointments, auth, calculators, documents, drugs, evidence,
    favorites, gallery, health, lab_tests, library, password_reset,
    prescriptions, round as round_api, search, studies, timeline,
)
from app.core.config import settings
from app.services.bootstrap import init_db

app = FastAPI(
    title="MeuCardio — API",
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

for r in (health.router, auth.router, library.router, search.router,
          calculators.router, drugs.router, round_api.router,
          ai.router, admin.router, gallery.router, favorites.router,
          password_reset.router, lab_tests.router, evidence.router, studies.router,
          prescriptions.router, documents.router, appointments.router, timeline.router):
    app.include_router(r)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
