"""Modo Investidor — demonstração global somente leitura.

O frontend pode esconder/desabilitar ações para UX, mas a barreira real é
servidor-side: investidor navega e conhece o produto sem criar, alterar,
excluir, enviar, conectar, sincronizar, gerar, emitir, assinar ou exportar.

A Agenda merece uma regra adicional: uma conta convertida posteriormente em
Investidor pode possuir compromissos/locais/pacientes reais antigos. Nenhuma
leitura da demo pode consultar esses registros. O middleware intercepta a
superfície GET da Agenda antes dos routers e devolve somente um corpus
sintético conhecido; rota nova não catalogada falha fechada.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy import event, inspect, select, update

from app.core.db import SessionLocal
from app.core.security import AUTH_COOKIE_NAME, hash_password, usuario_por_token_app
from app.models.user import User

SENHA_FIXA_INVESTIDOR = "CorVIAOS"
MENSAGEM_MODO_INVESTIDOR = (
    "Modo investidor: esta conta é somente para visualização da plataforma."
)
MENSAGEM_AGENDA_DEMO = (
    "Modo investidor: esta leitura da Agenda não faz parte do corpus sintético de demonstração."
)

# Login/sessão/logout são infraestrutura de autenticação, não operações do
# produto. Onboarding/boas-vindas NÃO ficam aqui: para Investidor são
# simulados em memória/HTTP abaixo, sem persistir flags no banco.
_ESCRITAS_AUTH_PERMITIDAS = {
    "/api/auth/sessao",
    "/api/auth/login",
    "/api/auth/sair",
}

_ESCRITAS_UX_SIMULADAS = {
    "/api/auth/me/onboarding-concluido": {"onboarding_pendente": False},
    "/api/auth/me/boas-vindas-vista": {"boas_vindas_pendente": False},
}


def _get_com_efeito_colateral(path: str) -> bool:
    """GETs que não são leitura passiva para a conta Investidor."""
    if path.startswith("/api/agenda/oauth/") and path.endswith("/start"):
        return True

    if path.startswith("/api/document-templates/gerados/") and path.endswith("/pdf"):
        return True
    if path.startswith("/api/material-paciente/") and path.endswith("/pdf"):
        return True
    if path.startswith("/api/pedidos/") and path.endswith("/exame"):
        return True
    if path.startswith("/api/prescriptions/") and path.endswith("/imprimir"):
        return True

    partes = [parte for parte in path.split("/") if parte]
    if len(partes) == 5 and partes[:2] == ["api", "cursos"] and partes[3] == "material":
        return True

    return False


def _token_da_requisicao(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return token
    return request.cookies.get(AUTH_COOKIE_NAME)


def _agenda_demo(path: str):
    """Retorna somente dados sintéticos, nunca linhas do tenant.

    IDs negativos reservam um namespace que não colide com PKs reais. Datas
    são próximas ao dia da visualização para a demonstração continuar útil sem
    qualquer job que persista/atualize registros.
    """
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz)
    inicio = agora.replace(hour=8, minute=0, second=0, microsecond=0)
    if inicio < agora:
        inicio += timedelta(days=1)
    fim = inicio + timedelta(minutes=40)
    reuniao = inicio.replace(hour=14) + timedelta(days=1)
    reuniao_fim = reuniao + timedelta(hours=1)

    local = {
        "id": -101,
        "name": "Clínica demonstrativa CorVIA",
        "timezone": "America/Sao_Paulo",
        "address": {
            "street": "Endereço demonstrativo",
            "number": "100",
            "city": "Ribeirão Preto",
            "state": "SP",
        },
        "latitude": None,
        "longitude": None,
        "default_arrival_buffer_minutes": 15,
        "color": "#38CAD5",
        "active": True,
    }
    service = {
        "id": -201,
        "location_id": -101,
        "code": "consulta-demo",
        "name": "Consulta demonstrativa",
        "duration_minutes": 40,
        "visit_mode": "presencial",
        "payment_mode": "nao_informado",
        "private_price_cents": None,
        "allow_extra_slot": False,
        "color": "#38CAD5",
        "active": True,
    }
    appointment = {
        "id": -301,
        "calendar_kind": "appointment",
        "patient_name": "Paciente demonstrativo",
        "patient_phone": None,
        "starts_at": inicio.isoformat(),
        "ends_at": fim.isoformat(),
        "duration_minutes": 40,
        "appointment_type": "consulta",
        "status": "confirmado",
        "notes": "Conteúdo sintético do Modo Demonstração.",
        "location": local,
        "service": service,
        "visit_mode": "presencial",
        "payment_mode": "nao_informado",
        "price_cents": None,
        "source": "demo",
        "integration_id": None,
        "sync_status": "demo",
        "conflict_reason": None,
        "version": 1,
        "color": "#38CAD5",
    }
    commitment = {
        "id": "demo-commitment-1",
        "calendar_kind": "commitment",
        "series_id": -401,
        "occurrence_date": reuniao.date().isoformat(),
        "title": "Reunião demonstrativa",
        "patient_name": None,
        "patient_phone": None,
        "starts_at": reuniao.isoformat(),
        "ends_at": reuniao_fim.isoformat(),
        "duration_minutes": 60,
        "appointment_type": "reuniao",
        "status": "confirmado",
        "notes": "Conteúdo sintético do Modo Demonstração.",
        "location": local,
        "service": None,
        "visit_mode": "presencial",
        "payment_mode": "nao_informado",
        "price_cents": None,
        "source": "corvia_manual",
        "integration_id": None,
        "sync_status": "demo",
        "conflict_reason": None,
        "version": 1,
        "recurrence": "weekly",
        "blocks_scheduling": True,
        "is_exception": False,
        "color": "#A17CF5",
    }

    respostas = {
        "/api/agenda/appointments": [appointment],
        "/api/agenda/locations": [local],
        "/api/agenda/services": [service],
        # Nunca listar integração real nem estado/identificador de provedor.
        "/api/agenda/integrations": [],
        "/api/agenda/capabilities": {
            "integrations_enabled": False,
            "external_writes_enabled": False,
            "traffic_configured": False,
            "traffic_provider": "demo",
            "google_oauth_modo_teste": False,
            "connectors": [],
        },
        "/api/agenda/mobility/preferences": {
            "enabled": False,
            "consent_at": None,
            "automatic_foreground_refresh": False,
            "refresh_interval_minutes": 15,
            "traffic_configured": False,
        },
        "/api/agenda/work-routines": [
            {
                "id": -501,
                "location_id": -101,
                "service_id": -201,
                "weekday": inicio.weekday(),
                "start_time": "08:00:00",
                "end_time": "12:00:00",
                "label": "Rotina demonstrativa",
                "routine_type": "atendimento",
                "visit_mode": "presencial",
                "arrival_buffer_minutes": 15,
                "planning_notes": "Conteúdo sintético.",
                "active": True,
                "location": local,
                "service": service,
            }
        ],
        "/api/agenda/commitment-series": [
            {
                "id": -401,
                "title": "Reunião demonstrativa",
                "category": "reuniao",
                "location_id": -101,
                "location": local,
                "timezone": "America/Sao_Paulo",
                "starts_on": reuniao.date().isoformat(),
                "start_time": "14:00:00",
                "duration_minutes": 60,
                "recurrence": "weekly",
                "recurrence_interval": 1,
                "weekdays": [reuniao.weekday()],
                "month_day": None,
                "ends_on": None,
                "blocks_scheduling": True,
                "color": "#A17CF5",
                "active": True,
            }
        ],
        "/api/agenda/commitments": [commitment],
        "/api/agenda/google-teste/status": {"status": None},
    }
    return respostas.get(path)


class InvestidorReadOnlyMiddleware:
    """Fail-closed para mutações e leituras operacionais futuras."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path
        method = request.method.upper()

        if path.startswith("/api/"):
            token = _token_da_requisicao(request)
            user = None
            db = None
            if token:
                db = SessionLocal()
                try:
                    user = usuario_por_token_app(db, token)
                    investidor = user is not None and bool(getattr(user, "investidor", False))

                    if investidor:
                        # Agenda: interceptação ANTES do router. Uma conta que
                        # já foi normal nunca consegue vazar agenda histórica.
                        if method == "GET" and path.startswith("/api/agenda/"):
                            demo = _agenda_demo(path)
                            response = JSONResponse(
                                status_code=200 if demo is not None else 403,
                                content=demo if demo is not None else {"detail": MENSAGEM_AGENDA_DEMO},
                            )
                            await response(scope, receive, send)
                            return

                        # Flags de UX retornam sucesso sem tocar no modelo/DB.
                        if method not in {"GET", "HEAD", "OPTIONS"} and path in _ESCRITAS_UX_SIMULADAS:
                            response = JSONResponse(status_code=200, content=_ESCRITAS_UX_SIMULADAS[path])
                            await response(scope, receive, send)
                            return

                        mutacao = method not in {"GET", "HEAD", "OPTIONS"}
                        get_operacional = method == "GET" and _get_com_efeito_colateral(path)
                        if (mutacao and path not in _ESCRITAS_AUTH_PERMITIDAS) or get_operacional:
                            response = JSONResponse(
                                status_code=403,
                                content={"detail": MENSAGEM_MODO_INVESTIDOR},
                            )
                            await response(scope, receive, send)
                            return
                finally:
                    if db is not None:
                        db.close()

        await self.app(scope, receive, send)


_listeners_registrados = False


def _preparar_investidor(target: User) -> None:
    """Matriz aplicada ao criar ou converter uma conta para Investidor."""
    target.investidor = True
    target.convidado = False
    target.is_active = True
    target.status = "aprovado"
    target.profile_completion_required = False
    target.onboarding_visto = False
    target.password_hash = hash_password(SENHA_FIXA_INVESTIDOR)


def _neutralizar_integracao_real(target) -> None:
    """Mantém qualquer integração externa inerte enquanto o dono for Investidor."""
    target.enabled = False
    target.write_enabled = False
    target.contacts_enabled = False
    target.sync_calendar = False
    target.sync_mail = False


def _owner_e_investidor(connection, owner_id: int | None) -> bool:
    if owner_id is None:
        return False
    return bool(
        connection.execute(
            select(User.investidor).where(User.id == owner_id)
        ).scalar_one_or_none()
    )


def _quarentenar_integracoes_existentes(connection, owner_id: int | None) -> None:
    """Desativa integrações reais já existentes ao converter uma conta."""
    if owner_id is None:
        return
    from app.models.agenda import CalendarIntegration

    connection.execute(
        update(CalendarIntegration)
        .where(CalendarIntegration.owner_id == owner_id)
        .values(
            enabled=False,
            write_enabled=False,
            contacts_enabled=False,
            sync_calendar=False,
            sync_mail=False,
        )
    )


def _antes_de_salvar_integracao(_mapper, connection, target) -> None:
    """Defesa em profundidade contra criação/reativação interna para Investidor."""
    if _owner_e_investidor(connection, getattr(target, "owner_id", None)):
        _neutralizar_integracao_real(target)


def _antes_de_inserir(_mapper, _connection, target: User) -> None:
    if bool(getattr(target, "investidor", False)):
        _preparar_investidor(target)


def _restaurar_valor_anterior(estado, atributo: str, target: User) -> None:
    historico = estado.attrs[atributo].history
    if historico.has_changes() and historico.deleted:
        setattr(target, atributo, historico.deleted[0])


def _antes_de_atualizar(_mapper, _connection, target: User) -> None:
    estado = inspect(target)
    historico_investidor = estado.attrs.investidor.history
    concedendo_agora = bool(target.investidor and historico_investidor.has_changes())

    if concedendo_agora:
        _preparar_investidor(target)
        _quarentenar_integracoes_existentes(_connection, target.id)
        return

    if not bool(getattr(target, "investidor", False)):
        return

    target.convidado = False
    target.profile_completion_required = False

    # Telemetria e senha continuam passivas na demo.
    _restaurar_valor_anterior(estado, "last_seen_at", target)

    estado_senha = estado.attrs.password_hash.history
    if estado_senha.has_changes() and estado_senha.deleted:
        target.password_hash = estado_senha.deleted[0]
        _restaurar_valor_anterior(estado, "sessions_valid_after", target)


def _registrar_listeners() -> None:
    global _listeners_registrados
    if _listeners_registrados:
        return
    from app.models.agenda import CalendarIntegration

    event.listen(User, "before_insert", _antes_de_inserir)
    event.listen(User, "before_update", _antes_de_atualizar)
    event.listen(CalendarIntegration, "before_insert", _antes_de_salvar_integracao)
    event.listen(CalendarIntegration, "before_update", _antes_de_salvar_integracao)
    _listeners_registrados = True


def configurar_modo_investidor() -> None:
    """Registra invariantes de modelo; gates de auth vivem em app/api/auth.py."""
    _registrar_listeners()
