"""GET /api/auth/me -> onboarding_pendente + POST /api/auth/me/onboarding-
concluido — tour guiado do primeiro acesso (Trabalho 13, 06/08/2026).
"""
from app.models.kyc import KycVerification
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int, status: str = "ativo") -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status=status))
    db.commit()


def _liberar_kyc(db, user_id: int) -> None:
    db.add(KycVerification(
        owner_id=user_id, doc_profissional_frente="a", doc_profissional_verso="b", selfie="c",
        status="liberado_sem_checagem",
    ))
    db.commit()


def test_admin_nunca_ve_onboarding(client, db, criar_usuario):
    _, token = criar_usuario(role="admin")
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["onboarding_pendente"] is False


def test_sem_assinatura_nao_pede_onboarding_ainda(client, db, criar_usuario):
    _, token = criar_usuario()
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["onboarding_pendente"] is False


def test_com_kyc_pendente_onboarding_fica_de_fora(client, db, criar_usuario):
    """As duas telas não podem disputar o mesmo momento — KYC vem primeiro."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is True
    assert r.json()["onboarding_pendente"] is False


def test_assinante_liberado_do_kyc_e_nunca_viu_o_tour_precisa_ver(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _liberar_kyc(db, user.id)
    r = client.get("/api/auth/me", headers=_headers(token))
    assert r.json()["kyc_required"] is False
    assert r.json()["onboarding_pendente"] is True


def test_marcar_concluido_fecha_o_tour_de_vez(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _liberar_kyc(db, user.id)

    antes = client.get("/api/auth/me", headers=_headers(token))
    assert antes.json()["onboarding_pendente"] is True

    concluir = client.post("/api/auth/me/onboarding-concluido", headers=_headers(token))
    assert concluir.status_code == 200
    assert concluir.json()["onboarding_pendente"] is False

    depois = client.get("/api/auth/me", headers=_headers(token))
    assert depois.json()["onboarding_pendente"] is False
