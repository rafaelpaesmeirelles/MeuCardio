from datetime import datetime, timedelta, timezone

from app.api.round import _consultas_ia_hoje
from app.models.audit import AuditLog


def test_conta_apenas_auxilios_do_usuario_no_dia_atual(db, criar_usuario):
    usuario, _ = criar_usuario()
    outro, _ = criar_usuario(email="outro@teste.local")
    agora = datetime(2026, 8, 3, 15, 0, tzinfo=timezone.utc)

    db.add_all([
        AuditLog(
            user_id=usuario.id,
            action="ai_assist_round",
            entity="patient",
            entity_id="1",
            detail={},
            created_at=agora - timedelta(hours=1),
        ),
        AuditLog(
            user_id=usuario.id,
            action="ai_assist_round",
            entity="patient",
            entity_id="1",
            detail={},
            created_at=agora - timedelta(days=1),
        ),
        AuditLog(
            user_id=usuario.id,
            action="outra_acao",
            entity="patient",
            entity_id="1",
            detail={},
            created_at=agora - timedelta(minutes=30),
        ),
        AuditLog(
            user_id=outro.id,
            action="ai_assist_round",
            entity="patient",
            entity_id="2",
            detail={},
            created_at=agora - timedelta(minutes=10),
        ),
    ])
    db.commit()

    assert _consultas_ia_hoje(db, usuario.id, agora=agora) == 1
