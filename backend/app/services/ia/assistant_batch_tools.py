"""Tools em lote para o Assistente Pessoal.

Objetivo: pedidos reais de rotina costumam descrever vários blocos de trabalho
numa única mensagem (ex.: hospital pela manhã + consultório à tarde em vários
dias). Fazer uma tool por bloco pode consumir todas as rodadas de function
calling antes de o modelo conseguir devolver a confirmação final ao médico.

Esta tool reutiliza a implementação canônica de ``agenda_criar_rotina_semanal``
para cada bloco; não cria um caminho paralelo de persistência.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.ia.assistant_automation_tools import executar_tool_automation


ASSISTANT_BATCH_TOOLS_SCHEMA: list[dict] = [
    {
        "name": "agenda_criar_rotinas_em_lote",
        "description": (
            "Cria vários blocos de rotina semanal em UMA única chamada. Use quando o médico descreveu "
            "uma grade completa de trabalho/atendimento com dois ou mais blocos, por exemplo hospital "
            "segunda e terça de manhã + consultório à tarde + quarta a sexta em outro horário. "
            "Depois que os dias, horários e locais estiverem claros, NÃO volte a pedir os mesmos dados: "
            "execute esta ferramenta e então confirme objetivamente o que foi criado. Cada item aceita "
            "os mesmos campos de agenda_criar_rotina_semanal; não peça location_id, latitude/longitude "
            "nem número de semanas. Rotina sem data final permanece ativa até ser alterada."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rotinas": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 12,
                    "items": {
                        "type": "object",
                        "properties": {
                            "dias_semana": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]},
                            },
                            "hora_inicio": {"type": "string", "description": "HH:MM"},
                            "hora_fim": {"type": "string", "description": "HH:MM"},
                            "titulo": {"type": "string"},
                            "tipo_rotina": {"type": "string", "enum": ["atendimento", "plantao", "telemedicina", "administrativo", "outro"]},
                            "location_id": {"type": "integer"},
                            "local_nome": {"type": "string"},
                            "endereco": {"type": "string"},
                            "service_id": {"type": "integer"},
                            "margem_chegada_minutos": {"type": "integer"},
                            "valido_de": {"type": "string", "description": "YYYY-MM-DD"},
                            "valido_ate": {"type": "string", "description": "YYYY-MM-DD; omitir para sem término"},
                            "observacoes": {"type": "string"},
                        },
                        "required": ["dias_semana", "hora_inicio", "hora_fim", "titulo"],
                    },
                }
            },
            "required": ["rotinas"],
        },
    }
]

BATCH_TOOL_NAMES = {item["name"] for item in ASSISTANT_BATCH_TOOLS_SCHEMA}


def executar_tool_batch(nome: str, argumentos: dict, db: Session, user: User) -> dict:
    if nome != "agenda_criar_rotinas_em_lote":
        return {"erro": "tool_desconhecida", "mensagem": f"'{nome}' não é uma ferramenta em lote."}

    rotinas = argumentos.get("rotinas") if isinstance(argumentos, dict) else None
    if not isinstance(rotinas, list) or not rotinas:
        return {"erro": "rotinas_obrigatorias", "mensagem": "Informe pelo menos um bloco de rotina."}
    if len(rotinas) > 12:
        return {"erro": "lote_excessivo", "mensagem": "Envie no máximo 12 blocos de rotina por operação."}

    resultados: list[dict] = []
    for indice, rotina in enumerate(rotinas, start=1):
        if not isinstance(rotina, dict):
            resultados.append({"indice": indice, "erro": "rotina_invalida", "mensagem": "Bloco de rotina inválido."})
            break
        resultado = executar_tool_automation("agenda_criar_rotina_semanal", rotina, db, user)
        resultados.append({"indice": indice, **resultado})
        if "erro" in resultado:
            break

    criadas = sum(1 for item in resultados if item.get("criado") is True and "erro" not in item)
    erro = next((item for item in resultados if "erro" in item), None)
    resposta = {
        "criado": erro is None and criadas == len(rotinas),
        "total_solicitado": len(rotinas),
        "total_criado": criadas,
        "resultados": resultados,
    }
    if erro is not None:
        resposta["erro"] = "lote_parcial" if criadas else erro.get("erro", "falha_lote")
        resposta["mensagem"] = (
            f"Foram criados {criadas} de {len(rotinas)} blocos; a operação parou no primeiro erro."
            if criadas else erro.get("mensagem", "Não foi possível criar as rotinas.")
        )
    return resposta
