"""Regressão do incidente `[SMOKE-TESTE] Bloco C` (auditoria de 02/09/2026).

Causa-raiz confirmada: `GET /api/agenda/work-routines` (via `list_rules`) não
filtrava `active`, então uma rotina desativada em 19/08/2026 continuava
aparecendo na Home todo dia da semana correspondente. O marcador reservado
também tinha grafia divergente ("[SMOKE-TESTE]", português) da constante do
filtro do frontend ("[SMOKE-TEST]", inglês), então nem a proteção de nome
pegava o caso. Este teste prova a causa-raiz corrigida: a listagem normal
nunca devolve rotina inativa, independente do rótulo.
"""
from app.models.agenda import AvailabilityRule
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _location(client, token: str) -> dict:
    response = client.post("/api/agenda/locations", headers=_headers(token), json={
        "name": "Hospital Beneficência Portuguesa de Ribeirão Preto",
        "timezone": "America/Sao_Paulo",
        "address": {"city": "Ribeirão Preto", "state": "SP"},
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_disabled_work_routine_disappears_from_normal_listing(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.smoke-incident@teste.local")
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()
    location = _location(client, token)

    created = client.post("/api/agenda/work-routines", headers=_headers(token), json={
        "location_id": location["id"],
        "weekdays": [2],
        "start_time": "07:00:00",
        "end_time": "08:00:00",
        "label": "[SMOKE-TESTE] Bloco C",
        "routine_type": "atendimento",
    })
    assert created.status_code == 201, created.text
    routine_id = created.json()[0]["id"]

    # Enquanto ativa, aparece normalmente — o comportamento correto é
    # depender só de `active`, nunca do texto do rótulo.
    listing = client.get("/api/agenda/work-routines", headers=_headers(token))
    assert routine_id in [item["id"] for item in listing.json()]

    disable = client.delete(f"/api/agenda/work-routines/{routine_id}", headers=_headers(token))
    assert disable.status_code == 204, disable.text
    assert db.query(AvailabilityRule).filter(AvailabilityRule.id == routine_id).one().active is False

    listing_apos_desativar = client.get("/api/agenda/work-routines", headers=_headers(token))
    assert listing_apos_desativar.status_code == 200
    assert routine_id not in [item["id"] for item in listing_apos_desativar.json()]

    occurrences = client.get(
        "/api/agenda/work-routines/occurrences",
        headers=_headers(token),
        params={"start": "2026-09-02", "end": "2026-09-09"},
    )
    assert occurrences.status_code == 200
    assert routine_id not in [item["routine_id"] for item in occurrences.json()]


def test_availability_rules_todas_still_exposes_disabled_routines_for_audit(client, criar_usuario, db):
    user, token = criar_usuario(email="agenda.smoke-audit@teste.local")
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()
    location = _location(client, token)

    created = client.post("/api/agenda/work-routines", headers=_headers(token), json={
        "location_id": location["id"],
        "weekdays": [0],
        "start_time": "07:00:00",
        "end_time": "08:00:00",
        "label": "[SMOKE-TESTE] Bloco A",
        "routine_type": "atendimento",
    })
    routine_id = created.json()[0]["id"]
    client.delete(f"/api/agenda/work-routines/{routine_id}", headers=_headers(token))

    normal = client.get("/api/agenda/availability/rules", headers=_headers(token))
    assert routine_id not in [item["id"] for item in normal.json()]

    auditoria = client.get("/api/agenda/availability/rules/todas", headers=_headers(token))
    assert auditoria.status_code == 200
    encontrada = next(item for item in auditoria.json() if item["id"] == routine_id)
    assert encontrada["active"] is False
    assert encontrada["label"] == "[SMOKE-TESTE] Bloco A"


def test_availability_rules_ids_2_3_4_do_incidente_original_continuam_inativas(db):
    """Não apagar/reativar os registros reais do incidente — só confirmar que
    seguem auditáveis e inativos, como a Parte A exige explicitamente."""
    rotinas = db.query(AvailabilityRule).filter(AvailabilityRule.id.in_([2, 3, 4])).all()
    if not rotinas:
        return  # banco de teste isolado, sem os registros históricos de produção
    for rotina in rotinas:
        assert rotina.active is False
