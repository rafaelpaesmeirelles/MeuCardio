from sqlalchemy import text

from app.models.user import User


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_exclusao_definitiva_remove_dependencia_fk_nao_nullable(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-delete-real@teste.local", role="admin")
    alvo, _ = criar_usuario(email="usuario-com-vinculo@teste.local", full_name="Usuario Vinculado")
    user_id = alvo.id
    email = alvo.email

    db.execute(text(
        "CREATE TABLE delete_probe_links ("
        "id INTEGER PRIMARY KEY, "
        "user_id INTEGER NOT NULL REFERENCES users(id), "
        "payload VARCHAR(50)"
        ")"
    ))
    db.execute(
        text("INSERT INTO delete_probe_links (id, user_id, payload) VALUES (1, :uid, 'teste')"),
        {"uid": user_id},
    )
    db.commit()

    resposta = client.request(
        "DELETE",
        f"/api/admin/user-management/{user_id}",
        headers=_headers(token_admin),
        json={"confirmar_email": email, "excluir_corvia_mail": True},
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["excluido"] is True
    db.expire_all()
    assert db.get(User, user_id) is None
    assert db.execute(text("SELECT COUNT(*) FROM delete_probe_links WHERE user_id = :uid"), {"uid": user_id}).scalar() == 0


def test_exclusao_definitiva_anonimiza_fk_nullable(client, db, criar_usuario):
    _, token_admin = criar_usuario(email="admin-delete-nullable@teste.local", role="admin")
    alvo, _ = criar_usuario(email="usuario-nullable@teste.local", full_name="Usuario Nullable")
    user_id = alvo.id
    email = alvo.email

    db.execute(text(
        "CREATE TABLE delete_probe_nullable ("
        "id INTEGER PRIMARY KEY, "
        "user_id INTEGER NULL REFERENCES users(id), "
        "payload VARCHAR(50)"
        ")"
    ))
    db.execute(
        text("INSERT INTO delete_probe_nullable (id, user_id, payload) VALUES (1, :uid, 'preservar')"),
        {"uid": user_id},
    )
    db.commit()

    resposta = client.request(
        "DELETE",
        f"/api/admin/user-management/{user_id}",
        headers=_headers(token_admin),
        json={"confirmar_email": email, "excluir_corvia_mail": True},
    )

    assert resposta.status_code == 200, resposta.text
    db.expire_all()
    assert db.get(User, user_id) is None
    linha = db.execute(text("SELECT user_id, payload FROM delete_probe_nullable WHERE id = 1")).mappings().one()
    assert linha["user_id"] is None
    assert linha["payload"] == "preservar"
