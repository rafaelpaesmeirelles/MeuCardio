"""Tools de agenda do assistente — chamam as MESMAS funções da rota HTTP,
então o essencial (conflito, autorização) já é coberto por
`test_agenda_integrada.py`. Aqui testamos a camada de tradução: parsing de
argumento vindo do modelo, nunca deixar exceção subir, e isolamento entre
usuários pela mesma ferramenta.
"""
from datetime import datetime, timedelta, timezone

from app.models.subscription import Subscription
from app.services.ia.agenda_tools import executar_tool_agenda


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def test_tool_desconhecida_nao_lanca_excecao(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.desconhecida@teste.local")
    resultado = executar_tool_agenda("agenda_nao_existe", {}, db, user)
    assert resultado["erro"] == "tool_desconhecida"


def test_listar_compromissos_data_invalida_nao_lanca_excecao(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.data-invalida@teste.local")
    resultado = executar_tool_agenda(
        "agenda_listar_compromissos", {"inicio": "não é uma data"}, db, user
    )
    assert resultado["erro"] == "data_invalida"


def test_listar_compromissos_vazio(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.vazio@teste.local")
    _subscribe(db, user.id)
    resultado = executar_tool_agenda("agenda_listar_compromissos", {}, db, user)
    assert resultado["total"] == 0
    assert resultado["compromissos"] == []


def test_criar_e_listar_compromisso_via_tool(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.criar@teste.local")
    _subscribe(db, user.id)
    inicio = (datetime.now(timezone.utc) + timedelta(days=2)).replace(minute=0, second=0, microsecond=0)

    criado = executar_tool_agenda(
        "agenda_criar_compromisso",
        {"inicio": inicio.isoformat(), "paciente_nome": "Paciente da Tool"},
        db, user,
    )
    assert criado.get("criado") is True, criado
    appointment_id = criado["compromisso"]["id"]

    listado = executar_tool_agenda("agenda_listar_compromissos", {}, db, user)
    assert listado["total"] == 1
    assert listado["compromissos"][0]["id"] == appointment_id


def test_criar_compromisso_sem_paciente_e_recusado_sem_excecao(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.sem-paciente@teste.local")
    _subscribe(db, user.id)
    inicio = datetime.now(timezone.utc) + timedelta(days=2)
    resultado = executar_tool_agenda(
        "agenda_criar_compromisso", {"inicio": inicio.isoformat()}, db, user
    )
    assert resultado["erro"] == "recusado"


def test_criar_compromisso_com_conflito_e_recusado_sem_excecao(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.conflito@teste.local")
    _subscribe(db, user.id)
    inicio = (datetime.now(timezone.utc) + timedelta(days=2)).replace(minute=0, second=0, microsecond=0)
    argumentos = {"inicio": inicio.isoformat(), "paciente_nome": "Primeiro"}
    primeiro = executar_tool_agenda("agenda_criar_compromisso", argumentos, db, user)
    assert primeiro.get("criado") is True, primeiro

    segundo = executar_tool_agenda(
        "agenda_criar_compromisso",
        {"inicio": inicio.isoformat(), "paciente_nome": "Segundo"},
        db, user,
    )
    assert segundo["erro"] == "recusado"


def test_reagendar_e_cancelar_via_tool(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.reagendar@teste.local")
    _subscribe(db, user.id)
    inicio = (datetime.now(timezone.utc) + timedelta(days=2)).replace(minute=0, second=0, microsecond=0)
    criado = executar_tool_agenda(
        "agenda_criar_compromisso",
        {"inicio": inicio.isoformat(), "paciente_nome": "Paciente Reagendado"},
        db, user,
    )
    appointment_id = criado["compromisso"]["id"]

    novo_inicio = inicio + timedelta(hours=3)
    reagendado = executar_tool_agenda(
        "agenda_reagendar_compromisso",
        {"appointment_id": appointment_id, "novo_inicio": novo_inicio.isoformat()},
        db, user,
    )
    assert reagendado.get("reagendado") is True, reagendado

    cancelado = executar_tool_agenda(
        "agenda_cancelar_compromisso",
        {"appointment_id": appointment_id, "motivo": "Paciente remarcou por telefone."},
        db, user,
    )
    assert cancelado.get("cancelado") is True, cancelado
    assert cancelado["compromisso"]["status"] == "cancelado"


def test_reagendar_compromisso_de_outro_usuario_e_recusado(db, criar_usuario):
    dono, _ = criar_usuario(email="agenda.tool.dono@teste.local")
    intruso, _ = criar_usuario(email="agenda.tool.intruso@teste.local")
    _subscribe(db, dono.id)
    _subscribe(db, intruso.id)
    inicio = (datetime.now(timezone.utc) + timedelta(days=2)).replace(minute=0, second=0, microsecond=0)
    criado = executar_tool_agenda(
        "agenda_criar_compromisso",
        {"inicio": inicio.isoformat(), "paciente_nome": "Paciente do Dono"},
        db, dono,
    )
    appointment_id = criado["compromisso"]["id"]

    tentativa = executar_tool_agenda(
        "agenda_cancelar_compromisso",
        {"appointment_id": appointment_id, "motivo": "Tentativa indevida"},
        db, intruso,
    )
    assert tentativa["erro"] == "recusado"


def test_plano_do_dia_nao_lanca_excecao(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.plano@teste.local")
    _subscribe(db, user.id)
    resultado = executar_tool_agenda("agenda_plano_do_dia", {"dias": 400}, db, user)
    assert "erro" not in resultado
    assert resultado["horizon_days"] == 31  # clampado ao máximo


def test_proximo_deslocamento_sem_coordenadas_nao_inventa_rota(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.deslocamento@teste.local")
    _subscribe(db, user.id)
    resultado = executar_tool_agenda("agenda_proximo_deslocamento", {}, db, user)
    assert resultado["status"] in ("sem_proximo_compromisso", "sem_coordenadas_de_origem")
    assert "rota" not in resultado and "routes" not in resultado


def test_proximo_deslocamento_sem_consentimento_e_recusado_sem_excecao(db, criar_usuario):
    user, _ = criar_usuario(email="agenda.tool.deslocamento-consent@teste.local")
    _subscribe(db, user.id)
    resultado = executar_tool_agenda(
        "agenda_proximo_deslocamento",
        {"origem_latitude": -23.5, "origem_longitude": -46.6},
        db, user,
    )
    # Sem MobilityPreference.enabled=True, commute() recusa com 403 —
    # a tool tem que devolver erro tratado, nunca lançar.
    assert resultado["erro"] == "recusado"
