"""Protege compatibilidade do Pydantic e do TestClient do Starlette."""

import ast
from pathlib import Path
import warnings

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app


APP_ROOT = Path(__file__).resolve().parents[1] / "app"
PYDANTIC_BASES = {
    ("pydantic", "BaseModel"),
    ("pydantic", "RootModel"),
    ("pydantic_settings", "BaseSettings"),
}


def _caminho_ast(no: ast.expr) -> tuple[str, ...]:
    if isinstance(no, ast.Subscript):
        return _caminho_ast(no.value)
    if isinstance(no, ast.Name):
        return (no.id,)
    if isinstance(no, ast.Attribute):
        return (*_caminho_ast(no.value), no.attr)
    return ()


def _aliases_pydantic(arvore: ast.Module) -> tuple[dict[str, tuple[str, str]], dict[str, str]]:
    simbolos: dict[str, tuple[str, str]] = {}
    modulos: dict[str, str] = {}

    for no in arvore.body:
        if isinstance(no, ast.ImportFrom) and no.module in {"pydantic", "pydantic_settings"}:
            for item in no.names:
                simbolos[item.asname or item.name] = (no.module, item.name)
        elif isinstance(no, ast.Import):
            for item in no.names:
                if item.name in {"pydantic", "pydantic_settings"}:
                    modulos[item.asname or item.name] = item.name

    return simbolos, modulos


def _eh_modelo_pydantic(
    classe: ast.ClassDef,
    simbolos: dict[str, tuple[str, str]],
    modulos: dict[str, str],
) -> bool:
    for base in classe.bases:
        caminho = _caminho_ast(base)
        if not caminho:
            continue

        if len(caminho) == 1 and simbolos.get(caminho[0]) in PYDANTIC_BASES:
            return True

        modulo = modulos.get(caminho[0])
        if modulo and (modulo, caminho[-1]) in PYDANTIC_BASES:
            return True

    return False


def _configs_legados_em_fonte(fonte: str, arquivo: str) -> list[str]:
    arvore = ast.parse(fonte, filename=arquivo)
    simbolos, modulos = _aliases_pydantic(arvore)
    encontrados: list[str] = []

    for classe in (no for no in ast.walk(arvore) if isinstance(no, ast.ClassDef)):
        if not _eh_modelo_pydantic(classe, simbolos, modulos):
            continue

        for membro in classe.body:
            if isinstance(membro, ast.ClassDef) and membro.name == "Config":
                encontrados.append(f"{arquivo}:{membro.lineno} ({classe.name}.Config)")

    return encontrados


def _configs_legados() -> list[str]:
    encontrados: list[str] = []

    for caminho in sorted(APP_ROOT.rglob("*.py")):
        relativo = caminho.relative_to(APP_ROOT.parent)
        encontrados.extend(
            _configs_legados_em_fonte(
                caminho.read_text(encoding="utf-8"),
                str(relativo),
            )
        )

    return encontrados


def test_backend_nao_usa_config_class_based_do_pydantic():
    encontrados = _configs_legados()

    assert not encontrados, (
        "Configuração Pydantic class-based encontrada; substitua por "
        "model_config = ConfigDict(...):\n- " + "\n- ".join(encontrados)
    )


def test_gate_ignora_config_de_classe_que_nao_e_pydantic():
    fonte = """
class ClienteHttp:
    class Config:
        timeout = 5
"""

    assert _configs_legados_em_fonte(fonte, "modulo.py") == []


def test_gate_ignora_classe_local_apenas_chamada_basemodel():
    fonte = """
class BaseModel:
    pass

class Payload(BaseModel):
    class Config:
        formato = "interno"
"""

    assert _configs_legados_em_fonte(fonte, "modulo.py") == []


def test_gate_detecta_config_em_modelo_pydantic_com_alias():
    fonte = """
from pydantic import BaseModel as Modelo

class Payload(Modelo):
    class Config:
        extra = "forbid"
"""

    assert _configs_legados_em_fonte(fonte, "modulo.py") == [
        "modulo.py:5 (Payload.Config)"
    ]


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
