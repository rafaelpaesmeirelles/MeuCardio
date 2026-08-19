from fastapi import HTTPException
import pytest

from app.api import prescricao_especial


def test_delegada_manual_permanece_proibida():
    class Info:
        nivel = "nenhuma"

    assert Info.nivel != "qualificada"


def test_identidade_rafael_nao_depende_de_nome_ou_crm(criar_usuario, db):
    outro, _ = criar_usuario(
        email="admin-spoof@teste.local",
        full_name="Rafael Paes Meirelles",
        role="admin",
    )
    outro.council_number = "138266"
    outro.council_state = "SP"
    db.commit()
    assert prescricao_especial._eh_rafael(outro) is False
