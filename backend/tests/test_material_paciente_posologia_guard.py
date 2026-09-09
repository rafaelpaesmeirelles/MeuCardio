"""Regressões do guard de posologia dos materiais educativos."""

import pytest

from app.services.carregar_material_paciente import _encontrar_posologia


@pytest.mark.parametrize(
    "texto",
    [
        "A meta de LDL pode ser 55 mg/dL.",
        "O LDL caiu 8 mg/dL durante o acompanhamento.",
        "A função renal ficou em 30 mL/min/1,73 m².",
    ],
)
def test_nao_confunde_medida_clinica_com_posologia(texto):
    assert _encontrar_posologia(texto) is None


@pytest.mark.parametrize(
    "texto",
    [
        "Administrar 50 mg conforme a prescrição.",
        "Infusão de 0,1 mcg/kg/min.",
        "Solução com 0,1 mg/mL.",
        "Aplicar 80 UI.",
        "Tomar 2 comprimidos ao dia.",
        "Usar 3 x/dia.",
    ],
)
def test_mantem_bloqueio_de_doses_reais(texto):
    assert _encontrar_posologia(texto) is not None
