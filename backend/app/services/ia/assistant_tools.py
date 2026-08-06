"""Ponto único de acesso às tools do assistente de IA — agenda e CorvIA Mail
do próprio usuário autenticado.

Duas travas precisam estar de acordo antes de uma pergunta sequer OFERECER
estas tools ao modelo (verificado em `rag.py`, não aqui):
1. `settings.ai_assistant_tools_enabled` — decisão de instalação/administrador;
2. `user.ia_ferramentas_consent_em` não nulo — decisão individual do médico,
   revogável a qualquer momento (mesmo padrão de `MobilityPreference`).

Este módulo não repete essa checagem — assume que quem chamou
`executar_tool_assistente` já decidiu que as tools estão autorizadas para
esta pergunta. O que ele garante é o resto: nunca deixar uma exceção subir
para dentro do loop de tool-calling do provedor, e nunca oferecer uma tool
que não exista nos dois catálogos abaixo.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User
from app.services.ia.agenda_tools import AGENDA_TOOLS_SCHEMA, executar_tool_agenda
from app.services.ia.mail_tools import MAIL_TOOLS_SCHEMA, executar_tool_mail

ASSISTANT_TOOLS_SCHEMA: list[dict] = [*AGENDA_TOOLS_SCHEMA, *MAIL_TOOLS_SCHEMA]

# Nomes que alteram dado real (não só leitura) — cada chamada destas é
# auditada com o próprio nome e argumentos não sensíveis, igual a qualquer
# outra escrita da Agenda. As de leitura não geram AuditLog próprio aqui:
# gerariam uma linha por cada "o que eu tenho amanhã?", ruído sem valor de
# auditoria — a leitura de e-mail específica já é registrada dentro de
# `mail_tools.py` quando toca em conteúdo de mensagem.
_TOOLS_DE_ESCRITA = {
    "agenda_criar_compromisso",
    "agenda_reagendar_compromisso",
    "agenda_cancelar_compromisso",
}

_ARGUMENTOS_SEGUROS_PARA_AUDITORIA = {
    "agenda_criar_compromisso": ("inicio", "duracao_minutos", "service_id", "location_id", "tipo"),
    "agenda_reagendar_compromisso": ("appointment_id", "novo_inicio", "duracao_minutos"),
    "agenda_cancelar_compromisso": ("appointment_id",),
}


def executar_tool_assistente(nome: str, argumentos: dict, db: Session, user: User) -> dict:
    if nome.startswith("agenda_"):
        resultado = executar_tool_agenda(nome, argumentos, db, user)
    elif nome.startswith("mail_"):
        resultado = executar_tool_mail(nome, argumentos, db, user)
    else:
        resultado = {"erro": "tool_desconhecida", "mensagem": f"'{nome}' não é uma ferramenta do assistente."}

    if nome in _TOOLS_DE_ESCRITA:
        campos = _ARGUMENTOS_SEGUROS_PARA_AUDITORIA.get(nome, ())
        db.add(AuditLog(
            user_id=user.id, action=f"ia_tool_{nome}", entity="ia_assistant_tool",
            entity_id=str(argumentos.get("appointment_id")) if "appointment_id" in argumentos else None,
            detail={
                "argumentos": {chave: argumentos.get(chave) for chave in campos},
                "sucesso": "erro" not in resultado,
            },
        ))
        db.commit()

    return resultado
