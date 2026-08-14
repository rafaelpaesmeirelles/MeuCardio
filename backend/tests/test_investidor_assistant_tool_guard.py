"""Defesa em profundidade do Assistente Pessoal para conta Investidor."""

from app.models.audit import AuditLog
from app.services.ia import assistant_tools


def test_executor_direto_do_assistente_bloqueia_investidor_sem_side_effect(
    db, criar_usuario, monkeypatch
):
    user, _ = criar_usuario(email="investidor.tools@teste.local")
    user.investidor = True
    db.commit()

    chamadas: list[tuple] = []
    monkeypatch.setattr(
        assistant_tools,
        "executar_tool_automation",
        lambda *args, **kwargs: chamadas.append((args, kwargs)) or {"ok": True},
    )
    monkeypatch.setattr(
        assistant_tools,
        "executar_tool_agenda",
        lambda *args, **kwargs: chamadas.append((args, kwargs)) or {"ok": True},
    )
    monkeypatch.setattr(
        assistant_tools,
        "executar_tool_mail",
        lambda *args, **kwargs: chamadas.append((args, kwargs)) or {"ok": True},
    )

    antes = db.query(AuditLog).count()
    resultado = assistant_tools.executar_tool_assistente(
        "agenda_criar_compromisso_inteligente",
        {"inicio": "2026-08-15T08:00:00-03:00", "paciente_nome": "DADO REAL"},
        db,
        user,
    )

    assert resultado["erro"] == "modo_investidor_read_only"
    assert chamadas == []
    assert db.query(AuditLog).count() == antes
