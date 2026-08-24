from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from app.core.config import settings
from app.models.patient_profile import PatientProfile
from app.models.prontuario import PatientECGRecord
from app.models.user import User
from app.services import cofre


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


def test_exclusao_definitiva_remove_arquivo_cifrado_de_ecg(
    client, db, criar_usuario, monkeypatch, tmp_path,
):
    monkeypatch.setattr(settings, "exames_dir", str(tmp_path / "ecgs"))
    _, token_admin = criar_usuario(email="admin-delete-ecg@teste.local", role="admin")
    alvo, _ = criar_usuario(email="usuario-com-ecg@teste.local", full_name="Usuario ECG")
    perfil = PatientProfile(owner_id=alvo.id, full_name_cifrado=b"nome-cifrado")
    db.add(perfil)
    db.flush()
    registro = PatientECGRecord(
        owner_id=alvo.id,
        author_id=alvo.id,
        patient_profile_id=perfil.id,
        performed_at=datetime.now(timezone.utc),
        storage_key="pendente",
        original_name_cifrado=b"nome-cifrado",
        media_type="image/png",
        size_bytes=8,
    )
    db.add(registro)
    db.flush()
    registro.storage_key = cofre.guardar(b"ecg-test", registro.id)
    storage_path = Path(settings.exames_dir) / registro.storage_key
    db.commit()
    assert storage_path.exists()

    resposta = client.request(
        "DELETE",
        f"/api/admin/user-management/{alvo.id}",
        headers=_headers(token_admin),
        json={"confirmar_email": alvo.email, "excluir_corvia_mail": True},
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["arquivos_ecg_removidos"] == 1
    assert resposta.json()["arquivos_ecg_pendentes"] == 0
    assert not storage_path.exists()
