"""Protege o comportamento legado do bcrypt para entradas acima de 72 bytes."""

from app.core.security import hash_password, verify_password


def test_senha_longa_preserva_compatibilidade_bcrypt_4():
    prefixo = "a" * 72
    original = prefixo + "-sufixo-original"
    equivalente_no_bcrypt_legado = prefixo + "-outro-sufixo"
    gerado = hash_password(original)

    assert verify_password(original, gerado)
    # bcrypt 4.x, assim como o Passlib usado anteriormente, considera apenas
    # os primeiros 72 bytes. Este teste documenta o contrato existente para
    # não invalidar senhas já persistidas durante a remoção do Passlib.
    assert verify_password(equivalente_no_bcrypt_legado, gerado)
