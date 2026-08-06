"""GET /api/auth/me -> kyc_required — gate de KYC obrigatório pós-pagamento
(Trabalho 12, 06/08/2026). Sempre calculado na hora, nunca persistido —
precisa refletir aprovação feita pelo admin sem exigir novo login.
"""
from app.models.kyc import KycVerification
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int, status: str = "ativo") -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status=status))
    db.commit()


def test_admin_nunca_precisa_de_kyc(client, db, criar_usuario):
    _, token = criar_usuario(role="admin")
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.status_code == 200
    assert r.json()["kyc_required"] is False


def test_sem_assinatura_ativa_nao_exige_kyc_ainda(client, db, criar_usuario):
    _, token = criar_usuario()
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is False


def test_assinante_sem_submissao_de_kyc_e_bloqueado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is True


def test_assinante_com_kyc_liberado_sem_checagem_nao_e_bloqueado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    db.add(KycVerification(
        owner_id=user.id, doc_profissional_frente="a", doc_profissional_verso="b", selfie="c",
        status="liberado_sem_checagem",
    ))
    db.commit()
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is False


def test_assinante_com_kyc_aguardando_revisao_continua_bloqueado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    db.add(KycVerification(
        owner_id=user.id, doc_profissional_frente="a", doc_profissional_verso="b", selfie="c",
        status="aguardando_revisao",
    ))
    db.commit()
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is True


def test_assinatura_suspensa_nao_exige_kyc(client, db, criar_usuario):
    """Se a assinatura principal não está ativa, o gate de KYC não é o
    problema mais urgente — outros gates (billing) já cuidam disso."""
    user, token = criar_usuario()
    _subscribe(db, user.id, status="cancelado")
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is False
