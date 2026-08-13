"""Registro dos módulos auxiliares da API."""

from app.api import agenda_integrada
from app.api import agenda_mobility_targeted

# O endpoint direcionado é uma extensão do router já autenticado da Agenda.
# Isso evita criar um segundo motor de mobilidade ou alterar o registro global
# de routers no `main.py`.
agenda_integrada.router.include_router(agenda_mobility_targeted.router)
