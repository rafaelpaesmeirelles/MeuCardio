from app.services.ia import assistant_batch_tools as batch
from app.services.ia.assistant_tools import ASSISTANT_TOOLS_SCHEMA


def test_catalogo_expoe_tool_de_rotinas_em_lote():
    nomes = {item["name"] for item in ASSISTANT_TOOLS_SCHEMA}
    assert "agenda_criar_rotinas_em_lote" in nomes


def test_lote_executa_varios_blocos_sem_consumir_uma_rodada_por_bloco(monkeypatch):
    chamadas = []

    def fake_exec(nome, argumentos, db, user):
        chamadas.append((nome, argumentos))
        return {"criado": True, "rota_pronta": True}

    monkeypatch.setattr(batch, "executar_tool_automation", fake_exec)
    resultado = batch.executar_tool_batch(
        "agenda_criar_rotinas_em_lote",
        {
            "rotinas": [
                {
                    "dias_semana": ["segunda", "terca"],
                    "hora_inicio": "09:00",
                    "hora_fim": "12:00",
                    "titulo": "Hospital — Enfermaria",
                    "local_nome": "Hospital Beneficência Portuguesa",
                },
                {
                    "dias_semana": ["segunda", "terca"],
                    "hora_inicio": "13:00",
                    "hora_fim": "19:00",
                    "titulo": "Consultório Medclin",
                    "local_nome": "Medclin",
                },
            ]
        },
        db=object(),
        user=object(),
    )

    assert resultado["criado"] is True
    assert resultado["total_solicitado"] == 2
    assert resultado["total_criado"] == 2
    assert [nome for nome, _ in chamadas] == [
        "agenda_criar_rotina_semanal",
        "agenda_criar_rotina_semanal",
    ]


def test_lote_para_no_primeiro_erro_e_reporta_parcial(monkeypatch):
    respostas = iter([
        {"criado": True},
        {"erro": "conflito", "mensagem": "Conflito de agenda."},
        {"criado": True},
    ])

    monkeypatch.setattr(batch, "executar_tool_automation", lambda *args, **kwargs: next(respostas))
    resultado = batch.executar_tool_batch(
        "agenda_criar_rotinas_em_lote",
        {"rotinas": [
            {"dias_semana": ["segunda"], "hora_inicio": "08:00", "hora_fim": "09:00", "titulo": "A"},
            {"dias_semana": ["terca"], "hora_inicio": "08:00", "hora_fim": "09:00", "titulo": "B"},
            {"dias_semana": ["quarta"], "hora_inicio": "08:00", "hora_fim": "09:00", "titulo": "C"},
        ]},
        db=object(),
        user=object(),
    )

    assert resultado["criado"] is False
    assert resultado["erro"] == "lote_parcial"
    assert resultado["total_criado"] == 1
    assert len(resultado["resultados"]) == 2
