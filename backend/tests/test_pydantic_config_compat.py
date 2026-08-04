"""Protege compatibilidade do Pydantic e do TestClient do Starlette."""

import ast
from pathlib import Path
import warnings

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app


APP_ROOT = Path(__file__).resolve().parents[1] / "app"


def _configs_legados() -> list[str]:
    encontrados: list[str] = []

    for caminho in sorted(APP_ROOT.rglob("*.py")):
        arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))

        for classe in (no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)):
            for membro in classe.body:
                if isinstance(membro, ast.ClassDef) and membro.name == "Config":
                    relativo = caminho.relative_to(APP_ROOT.parent)
                    encontrados.append(
                        f"{relativo}:{membro.lineno} ({classe.name}.Config)"
                    )

    return encontrados


def test_backend_nao_usa_config_class_based_do_pydantic():
    encontrados = _configs_legados()

    assert not encontrados, (
        "Configuração Pydantic class-based encontrada; substitua por "
        "model_config = ConfigDict(...):\n- " + "\n- ".join(encontrados)
    )


def test_settings_config_dict_preserva_leitura_do_env():
    assert Settings.model_config["env_file"] == ".env"
    assert Settings.model_config["case_sensitive"] is False


def test_testclient_nao_usa_httpx_legado():
    with warnings.catch_warnings(record=True) as capturados:
        warnings.simplefilter("always")
        client = TestClient(app)
        client.close()

    avisos_legados = [
        str(aviso.message)
        for aviso in capturados
        if "starlette.testclient" in str(aviso.message).lower()
        or "install httpx2" in str(aviso.message).lower()
    ]
    assert not avisos_legados, "\n".join(avisos_legados)
