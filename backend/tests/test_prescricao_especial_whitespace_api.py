import pytest
from pydantic import ValidationError

from app.api.prescricao_especial import AtualizarIn, CriarIn


def test_criar_rejeita_campos_so_com_espacos():
    with pytest.raises(ValidationError):
        CriarIn(patient_name="  ", body="   ", mode="rafael")


def test_atualizar_rejeita_campos_so_com_espacos():
    with pytest.raises(ValidationError):
        AtualizarIn(patient_name="  ", body="   ")
