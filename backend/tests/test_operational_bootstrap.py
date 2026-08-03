from sqlalchemy import text

from app.main import app
from app.models.user import User
from app.services.bootstrap import create_admin_if_absent


def test_api_import_has_no_startup_database_mutation():
    assert app.router.on_startup == []


def test_admin_bootstrap_is_explicit_and_idempotent(db):
    first, created_first = create_admin_if_absent(
        db,
        email=" Admin.Explicito@Teste.Local ",
        password="senha-inicial-segura-123",
        full_name="Admin de Teste",
    )
    original_hash = first.password_hash

    second, created_second = create_admin_if_absent(
        db,
        email="admin.explicito@teste.local",
        password="senha-que-nao-deve-substituir-456",
        full_name="Outro Nome",
    )

    assert created_first is True
    assert created_second is False
    assert second.id == first.id
    assert second.email == "admin.explicito@teste.local"
    assert second.password_hash == original_hash
    assert db.query(User).filter(User.email == second.email).count() == 1


def test_search_infrastructure_is_owned_by_migrations(db):
    extensions = set(
        db.execute(text("SELECT extname FROM pg_extension")).scalars().all()
    )
    assert {"vector", "pg_trgm", "unaccent"}.issubset(extensions)

    triggers = set(
        db.execute(
            text("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal")
        ).scalars().all()
    )
    assert {
        "documents_search_vector_trg",
        "gallery_search_vector_trg",
        "lab_tests_search_vector_trg",
        "evidence_search_vector_trg",
        "studies_search_vector_trg",
    }.issubset(triggers)

    indexes = set(
        db.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE schemaname = current_schema()"
            )
        ).scalars().all()
    )
    assert {
        "documents_search_idx",
        "documents_trgm_idx",
        "document_chunks_embedding_idx",
        "gallery_search_idx",
        "lab_tests_search_idx",
        "evidence_search_idx",
        "studies_search_idx",
    }.issubset(indexes)
