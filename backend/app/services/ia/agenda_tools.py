"""Tools (function-calling) do assistente de IA para a Agenda Integrada.

Reaproveita as MESMAS funções de rota de `app/api/agenda_integrada.py` —
mesma validação, mesma resolução de dono (`_owner_for`), mesmo cálculo de
conflito, mesma fila de sincronização externa (`queue_external_operation`) e
mesmo `AuditLog`. O assistente não fala com o banco por um caminho paralelo:
ele aciona exatamente o que a tela de Agenda aciona.

Escopo deliberadamente conservador nesta primeira versão:
- toda ação é sempre sobre a PRÓPRIA agenda do usuário autenticado
  (nunca passamos `professional_id` vindo do modelo — delegação continua
  sendo decisão humana, feita pela tela, não pelo assistente);
- criar/reagendar/cancelar nunca envia e-mail ao paciente a partir daqui
  (não passamos `patient_email`/`email_consent`) — comunicação com paciente
  iniciada por IA é o tipo de mudança que o handoff de produção exige
  revisão humana explícita antes de existir;
- toda escrita usa a MESMA trava de conflito de horário que a tela usa
  (`find_conflicts`); o assistente não pode empurrar um encaixe sem que o
  serviço permita (`allow_extra_slot`), porque não expomos esse parâmetro;
- se o compromisso pertence a uma integração `external_authoritative`, a
  própria função de rota já recusa com 409 — o assistente herda essa regra
  sem precisar reimplementá-la.

Nenhuma função aqui levanta exceção para o chamador do loop de tool-calling:
toda falha (autorização, conflito, validação, provedor externo indisponível)
vira um dicionário `{"erro": "<codigo>", "mensagem": "..."}"`, porque isto
roda dentro de uma conversa com um modelo de linguagem — deixar uma exceção
não tratada subir quebraria a resposta inteira em vez de deixar o modelo
explicar a indisponibilidade ao médico.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import BackgroundTasks, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.agenda_integrada import (
    AppointmentIn,
    CancelIn,
    CommuteIn,
    RescheduleIn,
    cancel_appointment,
    commute,
    create_appointment,
    list_appointments,
    next_locations,
    reschedule_appointment,
    workday_plan,
)
from app.models.user import User

AGENDA_TOOLS_SCHEMA: list[dict] = [
    {
        "name": "agenda_listar_compromissos",
        "description": (
            "Lista os compromissos da agenda do próprio médico autenticado, num "
            "intervalo de datas. Use para responder 'o que tenho hoje/essa semana', "
            "'quando é a minha próxima consulta com fulano', etc. Não lista a "
            "agenda de outro profissional."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "inicio": {
                    "type": "string",
                    "description": "Data/hora inicial em ISO 8601 (ex.: 2026-08-06T00:00:00). Omitir para não filtrar pelo início.",
                },
                "fim": {
                    "type": "string",
                    "description": "Data/hora final em ISO 8601. Omitir para não filtrar pelo fim.",
                },
                "status": {
                    "type": "string",
                    "description": "Filtrar por status exato (ex.: confirmado, cancelado, realizado). Omitir para todos.",
                },
                "limite": {
                    "type": "integer",
                    "description": "Máximo de compromissos a devolver (padrão 20, máximo 100).",
                },
            },
            "required": [],
        },
    },
    {
        "name": "agenda_criar_compromisso",
        "description": (
            "Cria um novo compromisso na agenda do próprio médico. Sempre local ao "
            "Corvia primeiro (a sincronização com calendário externo, se houver, "
            "acontece depois, de forma assíncrona). Nunca envia e-mail ao paciente "
            "a partir desta ferramenta. Recusa automaticamente se houver conflito "
            "de horário — nesse caso, informe o conflito ao médico em vez de tentar de novo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "inicio": {"type": "string", "description": "Data/hora de início em ISO 8601. Obrigatório."},
                "paciente_nome": {"type": "string", "description": "Nome do paciente (texto livre), quando não houver patient_id cadastrado."},
                "paciente_id": {"type": "integer", "description": "Id de paciente já cadastrado no Round, se aplicável."},
                "duracao_minutos": {"type": "integer", "description": "Duração em minutos (padrão 30, ou a duração do serviço se service_id for informado)."},
                "service_id": {"type": "integer", "description": "Id do serviço/tipo de atendimento já cadastrado, se aplicável."},
                "location_id": {"type": "integer", "description": "Id do local já cadastrado, se aplicável."},
                "tipo": {"type": "string", "description": "Tipo do compromisso (padrão 'consulta')."},
                "observacoes": {"type": "string", "description": "Observações livres, até 4000 caracteres."},
            },
            "required": ["inicio"],
        },
    },
    {
        "name": "agenda_reagendar_compromisso",
        "description": (
            "Reagenda (move de horário) um compromisso já existente do próprio "
            "médico. Recusa se houver conflito de horário no novo horário, ou se "
            "o compromisso vier de um calendário externo autoritativo (nesse "
            "caso o reagendamento precisa ser feito na origem)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "integer", "description": "Id do compromisso a reagendar."},
                "novo_inicio": {"type": "string", "description": "Novo início em ISO 8601."},
                "duracao_minutos": {"type": "integer", "description": "Nova duração em minutos; omitir para manter a atual."},
            },
            "required": ["appointment_id", "novo_inicio"],
        },
    },
    {
        "name": "agenda_cancelar_compromisso",
        "description": (
            "Cancela (desmarca) um compromisso já existente do próprio médico. "
            "Sempre exige um motivo curto, que fica registrado. Não apaga o "
            "registro — ele continua no histórico como cancelado."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "integer", "description": "Id do compromisso a cancelar."},
                "motivo": {"type": "string", "description": "Motivo do cancelamento, mínimo 3 caracteres."},
            },
            "required": ["appointment_id", "motivo"],
        },
    },
    {
        "name": "agenda_plano_do_dia",
        "description": (
            "Devolve o plano de trabalho do médico nos próximos N dias: rotinas "
            "de atendimento, compromissos confirmados e avisos (ex.: local sem "
            "coordenada geocodificada, sobreposição entre dois locais diferentes)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "dias": {"type": "integer", "description": "Horizonte em dias (padrão 7, máximo 31)."},
            },
            "required": [],
        },
    },
    {
        "name": "agenda_proximo_deslocamento",
        "description": (
            "Informa o próximo local de trabalho do médico e, se as coordenadas "
            "atuais forem fornecidas E o consentimento de localização já tiver "
            "sido dado na conta, calcula distância, tempo de percurso, condição "
            "de trânsito e rotas alternativas até lá. Sem coordenadas, ou sem "
            "consentimento ativo, devolve só o próximo local (sem rota) e explica "
            "o motivo — nunca inventa distância, trânsito ou tempo de percurso."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origem_latitude": {"type": "number", "description": "Latitude atual do médico, se disponível (-90 a 90)."},
                "origem_longitude": {"type": "number", "description": "Longitude atual do médico, se disponível (-180 a 180)."},
            },
            "required": [],
        },
    },
]


def _erro(codigo: str, mensagem: str) -> dict:
    return {"erro": codigo, "mensagem": mensagem}


def _parse_datetime(valor: str, campo: str) -> datetime:
    texto = valor.strip()
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    return datetime.fromisoformat(texto)


def _tool_agenda_listar_compromissos(argumentos: dict, db: Session, user: User) -> dict:
    limite = min(max(int(argumentos.get("limite") or 20), 1), 100)
    try:
        inicio = _parse_datetime(argumentos["inicio"], "inicio") if argumentos.get("inicio") else None
        fim = _parse_datetime(argumentos["fim"], "fim") if argumentos.get("fim") else None
    except (ValueError, KeyError):
        return _erro("data_invalida", "Datas devem estar em ISO 8601 (ex.: 2026-08-06T14:00:00).")
    itens = list_appointments(
        start=inicio, end=fim, status=argumentos.get("status"), source=None,
        location_id=None, service_id=None, search=None, professional_id=None,
        db=db, user=user,
    )
    return {"total": len(itens), "compromissos": itens[:limite]}


def _tool_agenda_criar_compromisso(argumentos: dict, db: Session, user: User) -> dict:
    try:
        dados = AppointmentIn(
            starts_at=_parse_datetime(argumentos["inicio"], "inicio"),
            patient_name=argumentos.get("paciente_nome"),
            patient_id=argumentos.get("paciente_id"),
            duration_minutes=argumentos.get("duracao_minutos"),
            service_id=argumentos.get("service_id"),
            location_id=argumentos.get("location_id"),
            appointment_type=argumentos.get("tipo") or "consulta",
            notes=argumentos.get("observacoes"),
        )
    except (ValidationError, KeyError, ValueError) as exc:
        return _erro("dados_invalidos", str(exc))
    try:
        item = create_appointment(dados, BackgroundTasks(), db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {"criado": True, "compromisso": item}


def _tool_agenda_reagendar_compromisso(argumentos: dict, db: Session, user: User) -> dict:
    try:
        appointment_id = int(argumentos["appointment_id"])
        dados = RescheduleIn(
            starts_at=_parse_datetime(argumentos["novo_inicio"], "novo_inicio"),
            duration_minutes=argumentos.get("duracao_minutos"),
        )
    except (ValidationError, KeyError, ValueError) as exc:
        return _erro("dados_invalidos", str(exc))
    try:
        item = reschedule_appointment(appointment_id, dados, professional_id=None, db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {"reagendado": True, "compromisso": item}


def _tool_agenda_cancelar_compromisso(argumentos: dict, db: Session, user: User) -> dict:
    try:
        appointment_id = int(argumentos["appointment_id"])
        dados = CancelIn(reason=argumentos["motivo"])
    except (ValidationError, KeyError, ValueError) as exc:
        return _erro("dados_invalidos", str(exc))
    try:
        item = cancel_appointment(appointment_id, dados, professional_id=None, db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {"cancelado": True, "compromisso": item}


def _tool_agenda_plano_do_dia(argumentos: dict, db: Session, user: User) -> dict:
    dias = min(max(int(argumentos.get("dias") or 7), 1), 31)
    try:
        return workday_plan(days=dias, professional_id=None, db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))


def _tool_agenda_proximo_deslocamento(argumentos: dict, db: Session, user: User) -> dict:
    latitude = argumentos.get("origem_latitude")
    longitude = argumentos.get("origem_longitude")
    if latitude is None or longitude is None:
        destinos = next_locations(limit=1, professional_id=None, db=db, user=user)
        if not destinos:
            return {"status": "sem_proximo_compromisso", "destino": None}
        return {
            "status": "sem_coordenadas_de_origem",
            "mensagem": "Sem a localização atual, só é possível informar o próximo local — não o trajeto.",
            "destino": destinos[0],
        }
    try:
        dados = CommuteIn(latitude=float(latitude), longitude=float(longitude))
    except ValidationError as exc:
        return _erro("coordenadas_invalidas", str(exc))
    try:
        resultado = commute(dados, db=db, user=user)
    except HTTPException as exc:
        detail = exc.detail
        if isinstance(detail, dict):
            return _erro(detail.get("code", "indisponivel"), detail.get("message", "Serviço de trânsito indisponível."))
        if exc.status_code == 403:
            # Falta consentimento de localização na conta (MobilityPreference) —
            # negação de autorização, não indisponibilidade de provedor externo.
            return _erro("recusado", str(detail))
        return _erro("indisponivel", str(detail))
    return resultado


_DESPACHO = {
    "agenda_listar_compromissos": _tool_agenda_listar_compromissos,
    "agenda_criar_compromisso": _tool_agenda_criar_compromisso,
    "agenda_reagendar_compromisso": _tool_agenda_reagendar_compromisso,
    "agenda_cancelar_compromisso": _tool_agenda_cancelar_compromisso,
    "agenda_plano_do_dia": _tool_agenda_plano_do_dia,
    "agenda_proximo_deslocamento": _tool_agenda_proximo_deslocamento,
}


def executar_tool_agenda(nome: str, argumentos: dict, db: Session, user: User) -> dict[str, Any]:
    """Ponto único de entrada: nunca deixa exceção subir para o loop de tool-calling."""
    funcao = _DESPACHO.get(nome)
    if funcao is None:
        return _erro("tool_desconhecida", f"'{nome}' não é uma ferramenta de agenda válida.")
    try:
        return funcao(argumentos, db, user)
    except Exception as exc:  # noqa: BLE001 — fronteira com o modelo de IA, nunca propaga
        return _erro("falha_interna", f"Não foi possível concluir ({type(exc).__name__}).")
