"""Garante compatibilidade integral dos hashes bcrypt após remover o Passlib."""

from pathlib import Path

from app.core.security import BCRYPT_ROUNDS, hash_password, verify_password


# Vetor bcrypt fixo para a senha ``SenhaLegada!123``. O mesmo payload é
# reconhecido pelos identificadores históricos 2a, 2b e 2y. O Passlib 1.7.4
# produzia/validava esses formatos com o backend bcrypt; manter estes vetores
# evita invalidar credenciais já persistidas.
LEGACY_HASH_2B = "$2b$04$pfc4MxmEPYYchuDziKQWSubXuElJcVGdYcx4LNqb.is4Z.GiciIUm"


def test_hash_legado_bcrypt_continua_valido():
    assert verify_password("SenhaLegada!123", LEGACY_HASH_2B)
    assert not verify_password("senha-incorreta", LEGACY_HASH_2B)


def test_identificadores_bcrypt_historicos_continuam_validos():
    for identificador in ("2a", "2b", "2y"):
        hash_historico = f"${identificador}${LEGACY_HASH_2B[4:]}"
        assert verify_password("SenhaLegada!123", hash_historico)


def test_novo_hash_preserva_contrato_e_custo():
    gerado = hash_password("NovaSenha!456")

    assert gerado.startswith(f"$2b${BCRYPT_ROUNDS:02d}$")
    assert verify_password("NovaSenha!456", gerado)
    assert not verify_password("outra-senha", gerado)


def test_hash_invalido_retorna_falso_sem_excecao():
    for invalido in ("", "nao-e-bcrypt", "$2b$12$curto", "á" * 80):
        assert verify_password("qualquer", invalido) is False


def test_passlib_nao_permanece_no_codigo_ou_dependencias():
    backend = Path(__file__).resolve().parents[1]
    requisitos = (backend / "requirements.txt").read_text(encoding="utf-8").lower()
    seguranca = (backend / "app/core/security.py").read_text(encoding="utf-8").lower()

    assert "passlib" not in requisitos
    assert "from passlib" not in seguranca
    assert "import passlib" not in seguranca
