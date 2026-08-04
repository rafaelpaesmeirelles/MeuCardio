"""Garante que nenhum arquivo ignorado seja certificado pelo reconciliador."""

import pytest

from app.commands.reconcile_content import (
    BLOCKING_DIAGNOSTIC_KEYS,
    _assert_no_rejections,
    _collect_blocking_diagnostics,
)


@pytest.mark.parametrize(
    "chave",
    [
        "avisos",
        "duplicados_ignorados",
        "erros",
        "falhas",
        "ignoradas",
        "ignorados",
        "puladas",
        "pulados",
        "recusadas",
        "recusados",
        "sem_arquivo",
    ],
)
def test_todo_diagnostico_de_item_ignorado_bloqueia(chave):
    assert chave in BLOCKING_DIAGNOSTIC_KEYS

    with pytest.raises(RuntimeError, match="Frente teste recusou conteúdo") as erro:
        _assert_no_rejections("teste", {"novos": 10, chave: ["item.md"]})

    assert chave in str(erro.value)
    assert "item.md" in str(erro.value)


def test_diagnostico_aninhado_tambem_bloqueia():
    resultado = {
        "grupos": [
            {"tipo": "valido", "novos": 2},
            {"tipo": "incompleto", "resultado": {"avisos": ["caso-17 ignorado"]}},
        ]
    }

    encontrados = _collect_blocking_diagnostics(resultado)

    assert encontrados == {"grupos[1].resultado.avisos": ["caso-17 ignorado"]}
    with pytest.raises(RuntimeError, match="caso-17 ignorado"):
        _assert_no_rejections("casos_clinicos", resultado)


def test_contagens_e_notas_informativas_nao_bloqueiam():
    resultado = {
        "novos": 3,
        "atualizados": 2,
        "inalterados": 8,
        "origem": "/content",
        "nota": "Carga idempotente concluída.",
        "falhas": [],
        "avisos": [],
    }

    assert _collect_blocking_diagnostics(resultado) == {}
    _assert_no_rejections("documentos", resultado)
