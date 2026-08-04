"""Impede reintrodução da configuração class-based removida no Pydantic 3."""

import ast
from pathlib import Path


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
