"""Ponto único de acesso às tools do Assistente Pessoal — Agenda e CorVIA Mail.

Três travas precisam estar de acordo antes de uma tool produzir efeito:
1. ``settings.ai_assistant_tools_enabled`` — decisão de instalação/admin;
2. ``user.ia_ferramentas_consent_em`` não nulo — consentimento individual;
3. ``user.investidor`` precisa ser falso — conta demo nunca produz efeito.

A seleção das tools pelo modelo continua ocorrendo em ``rag.py``. A checagem de
Investidor vive TAMBÉM aqui, no executor, para que chamadas internas/diretas não
possam contornar o middleware HTTP. Defesa em profundidade, fail-closed.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User
from app.services.entitlement import MENSAGEM_MODO_INVESTIDOR
from app.services.ia.agenda_tools import AGENDA_TOOLS_SCHEMA, executar_tool_agenda
from app.services.ia.assistant_automation_tools import (
    ASSISTANT_AUTOMATION_TOOLS_SCHEMA,
    AUTOMATION_TOOL_NAMES,
    executar_tool_automation,
)
from app.services.ia.assistant_batch_tools import (
    ASSISTANT_BATCH_TOOLS_SCHEMA,
    BATCH_TOOL_NAMES,
    executar_tool_batch,
)
from app.services.ia.mail_tools import MAIL_TOOLS_SCHEMA, executar_tool_mail

ASSISTANT_TOOLS_SCHEMA: list[dict] = [
    *AGENDA_TOOLS_SCHEMA,
    *MAIL_TOOLS_SCHEMA,
    *ASSISTANT_AUTOMATION_TOOLS_SCHEMA,
    *ASSISTANT_BATCH_TOOLS_SCHEMA,
]

# Toda tool que pode persistir dado ou produzir efeito externo entra aqui.
# O AuditLog central registra somente metadados não sensíveis. Endereço,
# coordenada, destinatário, assunto e corpo de e-mail NUNCA entram neste log.
_TOOLS_DE_ESCRITA = {
    "agenda_criar_compromisso",
    "agenda_reagendar_compromisso",
    "agenda_cancelar_compromisso",
    "agenda_resolver_local",
    "agenda_criar_compromisso_inteligente",
    "agenda_criar_rotina_semanal",
    "agenda_criar_compromisso_recorrente",
    "agenda_criar_rotinas_em_lote",
    "mail_enviar_mensagem",
    "mail_responder_mensagem",
}

_ARGUMENTOS_SEGUROS_PARA_AUDITORIA = {
    "agenda_criar_compromisso": ("inicio", "duracao_minutos", "service_id", "location_id", "tipo"),
    "agenda_reagendar_compromisso": ("appointment_id", "novo_inicio", "duracao_minutos"),
    "agenda_cancelar_compromisso": ("appointment_id",),
    # local_nome/endereco são deliberadamente omitidos: podem revelar
    # residência/consultório e não são necessários para provar a ação.
    "agenda_resolver_local": ("location_id", "criar_se_ausente"),
    "agenda_criar_compromisso_inteligente": (
        "inicio", "duracao_minutos", "service_id", "location_id", "tipo",
    ),
    "agenda_criar_rotina_semanal": (
        "dias_semana", "hora_inicio", "hora_fim", "location_id", "service_id",
    ),
    "agenda_criar_compromisso_recorrente": (
        "recorrencia", "intervalo", "data_inicio", "data_final", "location_id",
    ),
    # O lote pode conter endereços e nomes de locais; não registramos o corpo.
    # total_solicitado basta para provar a natureza da ação sem vazar rotina.
    "agenda_criar_rotinas_em_lote": ("total_solicitado",),
    # Não registrar para/cc/cco/assunto/corpo. Para resposta, message_id é um
    # identificador opaco da caixa e é suficiente junto da ação.
    "mail_enviar_mensagem": ("integration_id",),
    "mail_responder_mensagem": ("message_id", "acao"),
}


def executar_tool_assistente(nome: str, argumentos: dict, db: Session, user: User) -> dict:
    argumentos = argumentos or {}

    # Boundary guard explícito. Não delegar esta propriedade somente ao HTTP:
    # o executor é reutilizável por RAG/testes/jobs e deve ser seguro sozinho.
    if bool(getattr(user, "investidor", False)):
        return {
            "erro": "modo_investidor_read_only",
            "mensagem": MENSAGEM_MODO_INVESTIDOR,
        }

    if nome in BATCH_TOOL_NAMES:
        resultado = executar_tool_batch(nome, argumentos, db, user)
    elif nome in AUTOMATION_TOOL_NAMES:
        resultado = executar_tool_automation(nome, argumentos, db, user)
    elif nome.startswith("agenda_"):
        resultado = executar_tool_agenda(nome, argumentos, db, user)
    elif nome.startswith("mail_"):
        resultado = executar_tool_mail(nome, argumentos, db, user)
    else:
        resultado = {
            "erro": "tool_desconhecida",
            "mensagem": f"'{nome}' não é uma ferramenta do assistente.",
        }

    if nome in _TOOLS_DE_ESCRITA:
        campos = _ARGUMENTOS_SEGUROS_PARA_AUDITORIA.get(nome, ())
        argumentos_auditoria = dict(argumentos)
        if nome == "agenda_criar_rotinas_em_lote":
            rotinas = argumentos.get("rotinas")
            argumentos_auditoria = {"total_solicitado": len(rotinas) if isinstance(rotinas, list) else 0}
        db.add(AuditLog(
            user_id=user.id,
            action=f"ia_tool_{nome}",
            entity="ia_assistant_tool",
            entity_id=(
                str(argumentos.get("appointment_id"))
                if argumentos.get("appointment_id") is not None
                else None
            ),
            detail={
                "argumentos": {chave: argumentos_auditoria.get(chave) for chave in campos},
                "sucesso": "erro" not in resultado,
            },
        ))
        db.commit()

    return resultado
