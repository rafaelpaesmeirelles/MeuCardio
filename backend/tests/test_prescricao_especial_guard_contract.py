from app.main import app
from app.core.prescricao_especial_isolation import PrescricaoEspecialIsolationMiddleware


def test_middleware_de_isolamento_da_prescricao_especial_esta_registrado():
    assert any(m.cls is PrescricaoEspecialIsolationMiddleware for m in app.user_middleware)
