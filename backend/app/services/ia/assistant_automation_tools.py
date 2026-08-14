"""Ferramentas avançadas do Assistente Pessoal.

Esta camada resolve as limitações percebidas na primeira versão das tools:
- o médico não precisa saber ``location_id``;
- endereço pode virar local + coordenadas automaticamente;
- rotina semanal e compromisso recorrente são entidades nativas, sem criar N
  eventos manualmente nem perguntar "por quantas semanas?";
- compromisso pontual pode receber nome/endereço do local em linguagem natural;
- CorVIA Mail pode listar contas de envio e, após pedido explícito do médico,
  enviar/responder uma mensagem.

As escritas reaproveitam as funções de rota já usadas pelas telas. Nenhuma tool
aceita ``professional_id``: tudo permanece no tenant do usuário autenticado.
"""
from __future__ import annotations

from datetime import date, datetime, time
from html import escape
from typing import Any, Callable

from fastapi import BackgroundTasks, HTTPException
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.agenda_integrada import (
    AppointmentIn,
    CommitmentSeriesIn,
    LocationIn,
    WorkRoutineIn,
    create_appointment,
    create_commitment_series,
    create_location,
    create_work_routine,
    list_locations,
    update_location,
)
from app.core.config import settings
from app.models.agenda import CalendarIntegration, CalendarLocation
from app.models.email_account import EmailAccount
from app.models.user import User
from app.services.agenda_integrada.geocoding import GeocodingError, geocode_address


ASSISTANT_AUTOMATION_TOOLS_SCHEMA: list[dict] = [
    {
        "name": "agenda_listar_locais",
        "description": (
            "Lista os locais já cadastrados na agenda do próprio médico, incluindo id, nome, endereço "
            "e se já têm coordenadas para rota. Use antes de perguntar ao médico por location_id: ele "
            "não deve precisar conhecer ids internos."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "agenda_resolver_local",
        "description": (
            "Localiza um local existente pelo nome/endereço e, quando necessário, cadastra-o e tenta "
            "geocodificar automaticamente. Use quando o médico disser algo como 'Hospital X, Rua Y'. "
            "NÃO peça latitude/longitude nem location_id ao médico. Se o local já existir sem coordenadas, "
            "a ferramenta tenta completar a geocodificação usando o endereço salvo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "local_nome": {"type": "string", "description": "Nome humano do local, ex.: Hospital Beneficência Portuguesa."},
                "endereco": {"type": "string", "description": "Endereço textual completo quando conhecido."},
                "criar_se_ausente": {"type": "boolean", "description": "Padrão true quando o médico pediu para cadastrar/usar esse local."},
            },
            "required": [],
        },
    },
    {
        "name": "agenda_criar_compromisso_inteligente",
        "description": (
            "Cria um compromisso pontual e resolve o local automaticamente. Aceita location_id, mas o "
            "caminho preferido é local_nome/endereco em linguagem natural; se necessário cria o local e "
            "geocodifica para deixar a função de rota pronta. Não peça location_id ao médico."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "inicio": {"type": "string", "description": "Data/hora ISO 8601 do compromisso."},
                "duracao_minutos": {"type": "integer", "description": "Duração em minutos; padrão 30."},
                "paciente_nome": {"type": "string", "description": "Nome do paciente apenas quando o usuário o informou para este compromisso."},
                "paciente_id": {"type": "integer"},
                "service_id": {"type": "integer"},
                "location_id": {"type": "integer", "description": "Id interno, se já conhecido pela própria ferramenta."},
                "local_nome": {"type": "string", "description": "Nome humano do local."},
                "endereco": {"type": "string", "description": "Endereço completo; será geocodificado automaticamente quando possível."},
                "tipo": {"type": "string", "description": "Ex.: consulta, reunião, trabalho."},
                "observacoes": {"type": "string"},
            },
            "required": ["inicio"],
        },
    },
    {
        "name": "agenda_criar_rotina_semanal",
        "description": (
            "Cria uma rotina semanal real de trabalho/atendimento. Use para frases como 'toda segunda "
            "Hospital 10-12 e Medclin 13-19'. NÃO pergunte por quantas semanas se o médico não informou "
            "data final: a rotina pode ficar sem término até ser alterada. Resolve/cadastra/geocodifica o "
            "local automaticamente, permitindo que o planejamento de deslocamento use essa rotina."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "dias_semana": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]},
                    "description": "Um ou mais dias da semana.",
                },
                "hora_inicio": {"type": "string", "description": "HH:MM."},
                "hora_fim": {"type": "string", "description": "HH:MM."},
                "titulo": {"type": "string", "description": "Ex.: Hospital — Enfermaria."},
                "tipo_rotina": {"type": "string", "enum": ["atendimento", "plantao", "telemedicina", "administrativo", "outro"]},
                "location_id": {"type": "integer"},
                "local_nome": {"type": "string"},
                "endereco": {"type": "string"},
                "service_id": {"type": "integer"},
                "margem_chegada_minutos": {"type": "integer", "description": "Padrão 15."},
                "valido_de": {"type": "string", "description": "Data YYYY-MM-DD; omitir para começar agora."},
                "valido_ate": {"type": "string", "description": "Data final YYYY-MM-DD; omitir para rotina sem término."},
                "observacoes": {"type": "string"},
            },
            "required": ["dias_semana", "hora_inicio", "hora_fim", "titulo"],
        },
    },
    {
        "name": "agenda_criar_compromisso_recorrente",
        "description": (
            "Cria uma série recorrente nativa (diária, semanal ou mensal) para reunião, estudo, plantão, "
            "compromisso pessoal etc. Diferente de criar dezenas de eventos um a um. Se for semanal e "
            "não houver data final, mantenha a série sem término; NÃO pergunte automaticamente quantas "
            "semanas. Para rotina fixa de trabalho, prefira agenda_criar_rotina_semanal."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string"},
                "categoria": {"type": "string", "enum": ["compromisso", "trabalho", "reuniao", "plantao", "estudo", "pessoal", "outro"]},
                "data_inicio": {"type": "string", "description": "YYYY-MM-DD; omitir para iniciar a partir de hoje."},
                "hora_inicio": {"type": "string", "description": "HH:MM."},
                "duracao_minutos": {"type": "integer"},
                "recorrencia": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                "intervalo": {"type": "integer", "description": "Padrão 1; ex.: 2 = a cada 2 semanas."},
                "dias_semana": {"type": "array", "items": {"type": "string", "enum": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]}},
                "dia_do_mes": {"type": "integer"},
                "data_final": {"type": "string", "description": "YYYY-MM-DD; omitir para série sem término."},
                "location_id": {"type": "integer"},
                "local_nome": {"type": "string"},
                "endereco": {"type": "string"},
                "descricao": {"type": "string"},
                "bloqueia_agenda": {"type": "boolean"},
            },
            "required": ["titulo", "hora_inicio", "recorrencia"],
        },
    },
    {
        "name": "mail_listar_contas_envio",
        "description": (
            "Lista quais contas do CorVIA Mail do próprio médico podem ser usadas para ENVIAR mensagem: "
            "caixa nativa e contas externas conectadas com permissão send_mail. Use para escolher a conta "
            "sem pedir ids internos ao médico."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "mail_enviar_mensagem",
        "description": (
            "Envia uma nova mensagem pelo CorVIA Mail. Ação com efeito externo: só use quando o médico "
            "tiver pedido claramente para ENVIAR/MANDAR nesta conversa. Se ele apenas pedir 'escreva um "
            "e-mail', produza o texto no chat e NÃO chame esta ferramenta. confirmacao_usuario deve ser "
            "true somente após uma instrução explícita de envio."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "para": {"type": "string"},
                "assunto": {"type": "string"},
                "corpo": {"type": "string", "description": "Corpo em texto simples; a assinatura configurada é anexada pelo backend."},
                "cc": {"type": "string"},
                "cco": {"type": "string"},
                "integration_id": {"type": "integer", "description": "Omitir para caixa nativa; use id devolvido por mail_listar_contas_envio para conta externa."},
                "confirmacao_usuario": {"type": "boolean"},
            },
            "required": ["para", "assunto", "corpo", "confirmacao_usuario"],
        },
    },
    {
        "name": "mail_responder_mensagem",
        "description": (
            "Responde uma mensagem da caixa nativa CorVIA Mail. Só use depois de o médico pedir "
            "explicitamente para RESPONDER/ENVIAR; se ele pedir apenas uma sugestão de resposta, escreva "
            "no chat e não envie. Nesta primeira versão segura, resposta por tool é restrita à caixa nativa."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string"},
                "assunto": {"type": "string"},
                "corpo": {"type": "string"},
                "acao": {"type": "string", "enum": ["reply", "replyall", "forward"]},
                "para": {"type": "string"},
                "cc": {"type": "string"},
                "cco": {"type": "string"},
                "confirmacao_usuario": {"type": "boolean"},
            },
            "required": ["message_id", "assunto", "corpo", "acao", "confirmacao_usuario"],
        },
    },
]

AUTOMATION_TOOL_NAMES = {item["name"] for item in ASSISTANT_AUTOMATION_TOOLS_SCHEMA}

_DIAS = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}


def _erro(codigo: str, mensagem: str, **extra) -> dict:
    return {"erro": codigo, "mensagem": mensagem, **extra}


def _parse_datetime(valor: str) -> datetime:
    texto = (valor or "").strip()
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    return datetime.fromisoformat(texto)


def _parse_date(valor: str | None, *, default: date | None = None) -> date | None:
    if not valor:
        return default
    return date.fromisoformat(valor.strip())


def _parse_time(valor: str) -> time:
    texto = (valor or "").strip()
    if len(texto) == 5:
        texto += ":00"
    return time.fromisoformat(texto)


def _dump_local(item: CalendarLocation) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "timezone": item.timezone,
        "address": item.address or {},
        "latitude": item.latitude,
        "longitude": item.longitude,
        "rota_pronta": item.latitude is not None and item.longitude is not None,
        "active": item.active,
    }


def _endereco_salvo(item: CalendarLocation) -> str | None:
    endereco = item.address or {}
    if isinstance(endereco, str):
        return endereco.strip() or None
    if not isinstance(endereco, dict):
        return None
    preferidos = [
        endereco.get("formatted"), endereco.get("formatted_address"), endereco.get("full_address"),
        endereco.get("input"), endereco.get("address"),
    ]
    for valor in preferidos:
        if isinstance(valor, str) and valor.strip():
            return valor.strip()
    partes = [str(v).strip() for v in endereco.values() if isinstance(v, (str, int)) and str(v).strip()]
    return ", ".join(partes) if partes else None


def _buscar_local(db: Session, user: User, local_nome: str | None, endereco: str | None) -> CalendarLocation | None:
    query = db.query(CalendarLocation).filter(
        CalendarLocation.owner_id == user.id,
        CalendarLocation.active.is_(True),
    )
    if local_nome:
        nome = " ".join(local_nome.strip().split())
        exato = query.filter(func.lower(CalendarLocation.name) == nome.casefold()).first()
        if exato:
            return exato
        candidatos = query.order_by(CalendarLocation.id.asc()).all()
        alvo = nome.casefold()
        semelhantes = [c for c in candidatos if alvo in c.name.casefold() or c.name.casefold() in alvo]
        if len(semelhantes) == 1:
            return semelhantes[0]
    if endereco:
        alvo = " ".join(endereco.strip().split()).casefold()
        for item in query.order_by(CalendarLocation.id.asc()).all():
            salvo = _endereco_salvo(item)
            if salvo and (alvo in salvo.casefold() or salvo.casefold() in alvo):
                return item
    return None


def _geocodificar_local_existente(
    db: Session, user: User, item: CalendarLocation, endereco: str | None,
) -> tuple[CalendarLocation, str | None]:
    if item.latitude is not None and item.longitude is not None:
        return item, None
    texto = endereco or _endereco_salvo(item)
    if not texto:
        return item, "Local encontrado, mas ainda não há endereço suficiente para habilitar rota automática."
    try:
        geo = geocode_address(texto)
    except GeocodingError as exc:
        return item, str(exc)
    atualizado = LocationIn(
        name=item.name,
        timezone=item.timezone,
        address={
            **(item.address if isinstance(item.address, dict) else {}),
            "formatted": geo["formatted_address"],
            "input": texto,
            "geocoding_provider": geo["provider"],
        },
        phone=item.phone,
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        default_arrival_buffer_minutes=item.default_arrival_buffer_minutes,
        color=item.color,
        active=item.active,
    )
    update_location(item.id, atualizado, professional_id=None, db=db, user=user)
    db.refresh(item)
    return item, None


def _resolver_local(
    argumentos: dict,
    db: Session,
    user: User,
    *,
    criar_padrao: bool = True,
) -> tuple[CalendarLocation | None, str | None]:
    location_id = argumentos.get("location_id")
    local_nome = str(argumentos.get("local_nome") or "").strip() or None
    endereco = str(argumentos.get("endereco") or "").strip() or None

    if location_id is not None:
        item = db.query(CalendarLocation).filter(
            CalendarLocation.id == int(location_id),
            CalendarLocation.owner_id == user.id,
            CalendarLocation.active.is_(True),
        ).first()
        if item is None:
            return None, "O local informado não existe na sua agenda."
        return _geocodificar_local_existente(db, user, item, endereco)

    item = _buscar_local(db, user, local_nome, endereco)
    if item is not None:
        return _geocodificar_local_existente(db, user, item, endereco)

    criar = bool(argumentos.get("criar_se_ausente", criar_padrao))
    if not criar:
        return None, "Local não encontrado."
    if not endereco:
        return None, "Não encontrei esse local e preciso do endereço textual para cadastrá-lo automaticamente."

    aviso: str | None = None
    try:
        geo = geocode_address(endereco)
        latitude = geo["latitude"]
        longitude = geo["longitude"]
        formatted = geo["formatted_address"]
        provider = geo["provider"]
    except GeocodingError as exc:
        # O compromisso pode continuar existindo; a rota fica explicitamente
        # pendente, nunca com coordenada inventada.
        latitude = None
        longitude = None
        formatted = endereco
        provider = None
        aviso = str(exc)

    nome = local_nome or formatted.split(",", 1)[0].strip() or "Local"
    dados = LocationIn(
        name=nome[:160],
        address={
            "formatted": formatted,
            "input": endereco,
            **({"geocoding_provider": provider} if provider else {}),
        },
        latitude=latitude,
        longitude=longitude,
    )
    criado = create_location(dados, professional_id=None, db=db, user=user)
    item = db.query(CalendarLocation).filter(
        CalendarLocation.id == int(criado["id"]), CalendarLocation.owner_id == user.id,
    ).first()
    return item, aviso


def _tool_agenda_listar_locais(argumentos: dict, db: Session, user: User) -> dict:
    itens = list_locations(professional_id=None, db=db, user=user)
    return {
        "total": len(itens),
        "locais": [
            {**item, "rota_pronta": item.get("latitude") is not None and item.get("longitude") is not None}
            for item in itens
        ],
    }


def _tool_agenda_resolver_local(argumentos: dict, db: Session, user: User) -> dict:
    item, aviso = _resolver_local(argumentos, db, user, criar_padrao=True)
    if item is None:
        return _erro("local_nao_resolvido", aviso or "Não foi possível resolver o local.")
    return {"resolvido": True, "local": _dump_local(item), "aviso": aviso}


def _tool_agenda_criar_compromisso_inteligente(argumentos: dict, db: Session, user: User) -> dict:
    local, aviso = _resolver_local(argumentos, db, user, criar_padrao=True)
    if any(argumentos.get(chave) for chave in ("location_id", "local_nome", "endereco")) and local is None:
        return _erro("local_nao_resolvido", aviso or "Não foi possível resolver o local.")
    try:
        dados = AppointmentIn(
            starts_at=_parse_datetime(argumentos["inicio"]),
            patient_name=argumentos.get("paciente_nome"),
            patient_id=argumentos.get("paciente_id"),
            duration_minutes=argumentos.get("duracao_minutos") or 30,
            service_id=argumentos.get("service_id"),
            location_id=local.id if local else None,
            appointment_type=argumentos.get("tipo") or "compromisso",
            notes=argumentos.get("observacoes"),
        )
    except (ValidationError, ValueError, KeyError) as exc:
        return _erro("dados_invalidos", str(exc))
    try:
        item = create_appointment(dados, BackgroundTasks(), db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {
        "criado": True,
        "compromisso": item,
        "local": _dump_local(local) if local else None,
        "rota_pronta": bool(local and local.latitude is not None and local.longitude is not None),
        "aviso": aviso,
    }


def _weekdays(valores: list[str]) -> list[int]:
    dias: list[int] = []
    for valor in valores or []:
        chave = str(valor).strip().casefold()
        if chave not in _DIAS:
            raise ValueError(f"Dia da semana inválido: {valor}")
        dias.append(_DIAS[chave])
    return sorted(set(dias))


def _tool_agenda_criar_rotina_semanal(argumentos: dict, db: Session, user: User) -> dict:
    local, aviso = _resolver_local(argumentos, db, user, criar_padrao=True)
    if local is None:
        return _erro("local_nao_resolvido", aviso or "Informe um local para a rotina.")
    try:
        dados = WorkRoutineIn(
            location_id=local.id,
            service_id=argumentos.get("service_id"),
            weekdays=_weekdays(argumentos["dias_semana"]),
            start_time=_parse_time(argumentos["hora_inicio"]),
            end_time=_parse_time(argumentos["hora_fim"]),
            label=argumentos["titulo"],
            routine_type=argumentos.get("tipo_rotina") or "atendimento",
            arrival_buffer_minutes=argumentos.get("margem_chegada_minutos") or 15,
            planning_notes=argumentos.get("observacoes"),
            valid_from=_parse_date(argumentos.get("valido_de"), default=date.today()),
            valid_until=_parse_date(argumentos.get("valido_ate")),
            allow_overlap=False,
        )
    except (ValidationError, ValueError, KeyError) as exc:
        return _erro("dados_invalidos", str(exc))
    try:
        itens = create_work_routine(dados, professional_id=None, db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {
        "criado": True,
        "rotina": itens,
        "sem_data_final": dados.valid_until is None,
        "local": _dump_local(local),
        "rota_pronta": local.latitude is not None and local.longitude is not None,
        "aviso": aviso,
    }


def _tool_agenda_criar_compromisso_recorrente(argumentos: dict, db: Session, user: User) -> dict:
    local, aviso = _resolver_local(argumentos, db, user, criar_padrao=True)
    if any(argumentos.get(chave) for chave in ("location_id", "local_nome", "endereco")) and local is None:
        return _erro("local_nao_resolvido", aviso or "Não foi possível resolver o local.")
    try:
        recorrencia = argumentos["recorrencia"]
        dias = _weekdays(argumentos.get("dias_semana") or [])
        dados = CommitmentSeriesIn(
            title=argumentos["titulo"],
            category=argumentos.get("categoria") or "compromisso",
            description=argumentos.get("descricao"),
            location_id=local.id if local else None,
            starts_on=_parse_date(argumentos.get("data_inicio"), default=date.today()),
            start_time=_parse_time(argumentos["hora_inicio"]),
            duration_minutes=argumentos.get("duracao_minutos") or 30,
            recurrence=recorrencia,
            recurrence_interval=argumentos.get("intervalo") or 1,
            weekdays=dias,
            month_day=argumentos.get("dia_do_mes"),
            ends_on=_parse_date(argumentos.get("data_final")),
            blocks_scheduling=argumentos.get("bloqueia_agenda", True),
        )
    except (ValidationError, ValueError, KeyError) as exc:
        return _erro("dados_invalidos", str(exc))
    try:
        item = create_commitment_series(dados, professional_id=None, db=db, user=user)
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {
        "criado": True,
        "serie": item,
        "sem_data_final": dados.ends_on is None,
        "local": _dump_local(local) if local else None,
        "rota_pronta": bool(local and local.latitude is not None and local.longitude is not None),
        "aviso": aviso,
    }


def _conta_nativa(db: Session, user: User) -> EmailAccount | None:
    return db.query(EmailAccount).filter(
        EmailAccount.user_id == user.id,
        EmailAccount.status == "ativa",
    ).first()


def _tool_mail_listar_contas_envio(argumentos: dict, db: Session, user: User) -> dict:
    contas: list[dict] = []
    nativa = _conta_nativa(db, user)
    if nativa is not None and settings.mail360_configurado:
        contas.append({
            "tipo": "nativo",
            "integration_id": None,
            "nome": "CorVIA Mail",
            "endereco": nativa.email_address,
            "pode_enviar": True,
        })
    integracoes = db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == user.id,
        CalendarIntegration.enabled.is_(True),
        CalendarIntegration.status == "connected",
    ).order_by(CalendarIntegration.id.asc()).all()
    for item in integracoes:
        capacidades = item.capabilities or {}
        if capacidades.get("send_mail"):
            contas.append({
                "tipo": "externo",
                "integration_id": item.id,
                "provider": item.provider,
                "nome": item.display_name,
                "pode_enviar": True,
            })
    return {"total": len(contas), "contas": contas}


def _texto_para_html(texto: str) -> str:
    seguro = escape(texto or "")
    paragrafos = [p.strip() for p in seguro.split("\n\n") if p.strip()]
    if not paragrafos:
        return ""
    return "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragrafos)


def _tool_mail_enviar_mensagem(argumentos: dict, db: Session, user: User) -> dict:
    if argumentos.get("confirmacao_usuario") is not True:
        return _erro(
            "confirmacao_necessaria",
            "O e-mail não foi enviado. Só envie depois de uma instrução explícita do médico para mandar/enviar.",
        )
    conta = _conta_nativa(db, user)
    if conta is None:
        return _erro("sem_caixa_ativa", "Não há uma caixa CorVIA Mail ativa para autorizar o envio.")
    try:
        from app.api import email as email_api

        dados = email_api.NovaMensagem(
            para=argumentos["para"],
            cc=argumentos.get("cc"),
            cco=argumentos.get("cco"),
            assunto=argumentos["assunto"],
            corpo_html=_texto_para_html(argumentos["corpo"]),
            anexos=[],
        )
        integration_id = argumentos.get("integration_id")
        if integration_id is None:
            resultado = email_api.enviar(dados, db=db, conta=conta)
            origem = "nativo"
        else:
            resultado = email_api.enviar_mensagem_externa(int(integration_id), dados, db=db, conta=conta)
            origem = f"integracao:{int(integration_id)}"
    except (ValidationError, KeyError, ValueError) as exc:
        return _erro("dados_invalidos", str(exc))
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {"enviado": True, "origem": origem, "resultado": resultado}


def _tool_mail_responder_mensagem(argumentos: dict, db: Session, user: User) -> dict:
    if argumentos.get("confirmacao_usuario") is not True:
        return _erro(
            "confirmacao_necessaria",
            "A resposta não foi enviada. Só responda depois de uma instrução explícita do médico.",
        )
    conta = _conta_nativa(db, user)
    if conta is None:
        return _erro("sem_caixa_ativa", "Não há uma caixa CorVIA Mail nativa ativa.")
    try:
        from app.api import email as email_api

        dados = email_api.ResponderMensagem(
            acao=argumentos["acao"],
            assunto=argumentos["assunto"],
            conteudo=_texto_para_html(argumentos["corpo"]),
            para=argumentos.get("para"),
            cc=argumentos.get("cc"),
            cco=argumentos.get("cco"),
            anexos=[],
        )
        resultado = email_api.responder(
            argumentos["message_id"], dados, db=db, conta=conta,
        )
    except (ValidationError, KeyError, ValueError) as exc:
        return _erro("dados_invalidos", str(exc))
    except HTTPException as exc:
        return _erro("recusado", exc.detail if isinstance(exc.detail, str) else str(exc.detail))
    return {"enviado": True, "origem": "nativo", "resultado": resultado}


_HANDLERS: dict[str, Callable[[dict, Session, User], dict]] = {
    "agenda_listar_locais": _tool_agenda_listar_locais,
    "agenda_resolver_local": _tool_agenda_resolver_local,
    "agenda_criar_compromisso_inteligente": _tool_agenda_criar_compromisso_inteligente,
    "agenda_criar_rotina_semanal": _tool_agenda_criar_rotina_semanal,
    "agenda_criar_compromisso_recorrente": _tool_agenda_criar_compromisso_recorrente,
    "mail_listar_contas_envio": _tool_mail_listar_contas_envio,
    "mail_enviar_mensagem": _tool_mail_enviar_mensagem,
    "mail_responder_mensagem": _tool_mail_responder_mensagem,
}


def executar_tool_automation(nome: str, argumentos: dict, db: Session, user: User) -> dict[str, Any]:
    handler = _HANDLERS.get(nome)
    if handler is None:
        return _erro("tool_desconhecida", f"'{nome}' não é uma ferramenta avançada válida.")
    try:
        return handler(argumentos or {}, db, user)
    except Exception as exc:  # noqa: BLE001 — fronteira do function-calling
        return _erro("falha_interna", f"Não foi possível concluir ({type(exc).__name__}).")
