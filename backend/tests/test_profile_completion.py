from app.models.user import User
from app.services.professional_profile import profile_payload


def test_profile_payload_expõe_bloqueio_de_complementação():
    user = User(
        email="nova@teste.local", full_name="Nova Usuária", password_hash="x",
        profile_completion_required=True,
    )
    user.professional_title = None
    user.workplace_name = None
    user.workplace_department = None
    user.workplace_role = None
    user.workplace_notes = None
    user.include_workplace_on_documents = False
    user.document_logo_url = None
    assert profile_payload(user)["profile_completion_required"] is True
