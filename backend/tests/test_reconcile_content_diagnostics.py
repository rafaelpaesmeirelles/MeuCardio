"""Garante que nenhum arquivo ignorado seja certificado pelo reconciliador."""

import json

import pytest

from app.commands.reconcile_content import (
    BLOCKING_DIAGNOSTIC_KEYS,
    _assert_no_rejections,
    _collect_blocking_diagnostics,
    _manifest_slugs,
    _markdown_slugs,
)


@pytest.mark.parametrize(
    "chave",
    [
        "avisos", "duplicados_ignorados", "erros", "falhas", "ignoradas",
        "ignorados", "puladas", "pulados", "recusadas", "recusados",
        "sem_arquivo", "vazios",
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
        "vazios": [],
    }

    assert _collect_blocking_diagnostics(resultado) == {}
    _assert_no_rejections("documentos", resultado)


def test_manifesto_com_slugs_unicos_retorna_conjunto_canonico(tmp_path):
    manifesto = tmp_path / "metadados.json"
    manifesto.write_text(
        json.dumps([{"slug": "um"}, {"slug": "dois"}], ensure_ascii=False),
        encoding="utf-8",
    )

    assert _manifest_slugs("exames", manifesto) == {"um", "dois"}


def test_manifesto_com_slug_duplicado_bloqueia_antes_do_upsert(tmp_path):
    manifesto = tmp_path / "metadados.json"
    manifesto.write_text(
        json.dumps([{"slug": "duplicado"}, {"slug": "duplicado"}], ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="slugs duplicados") as erro:
        _manifest_slugs("evidencias", manifesto)

    assert "duplicado" in str(erro.value)


@pytest.mark.parametrize("slug", [" exame-x", "exame-x ", " exame-x "])
def test_manifesto_com_slug_com_espacos_bloqueia_sem_normalizar(tmp_path, slug):
    manifesto = tmp_path / "metadados.json"
    manifesto.write_text(
        json.dumps([{"slug": slug}], ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="slugs com espaços nas extremidades") as erro:
        _manifest_slugs("exames", manifesto)

    assert "índices: [0]" in str(erro.value)


def test_markdown_com_slug_explicito_com_espacos_tambem_bloqueia(tmp_path):
    documento = tmp_path / "documento.md"
    documento.write_text(
        '---\ntitle: Documento\nslug: " documento "\n---\nConteúdo científico.\n',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="slug com espaços nas extremidades"):
        _markdown_slugs("documentos", tmp_path)


@pytest.mark.parametrize(
    "itens",
    [
        [{"name": "sem slug"}],
        [{"slug": ""}],
        ["não é objeto"],
    ],
)
def test_manifesto_com_item_sem_slug_valido_bloqueia(tmp_path, itens):
    manifesto = tmp_path / "metadados.json"
    manifesto.write_text(json.dumps(itens, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(RuntimeError, match="sem slug válido"):
        _manifest_slugs("galeria", manifesto)
