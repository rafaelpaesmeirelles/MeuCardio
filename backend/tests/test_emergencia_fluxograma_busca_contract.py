"""Contratos de regressão do Modo Emergência no frontend."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FLUXOGRAMA = REPO_ROOT / "frontend/src/components/Fluxograma.tsx"
EMERGENCIA = REPO_ROOT / "frontend/src/pages/Emergencia.tsx"
ESTILO = REPO_ROOT / "frontend/src/styles/emergencia.css"


def _fonte(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def test_fluxograma_monta_svg_validado_sem_blob_ou_mermaid_bruto():
    fonte = _fonte(FLUXOGRAMA)

    assert 'securityLevel: "strict"' in fonte
    assert "htmlLabels: true" in fonte
    assert "await mermaid.parse(fonte)" in fonte
    assert 'new DOMParser().parseFromString(svg, "image/svg+xml")' in fonte
    assert 'document.importNode(svgValidado, true)' in fonte
    assert "replaceChildren(svgImportado)" in fonte
    assert "URL.createObjectURL" not in fonte
    assert "new Blob" not in fonte
    assert "<img" not in fonte
    assert "dangerouslySetInnerHTML" not in fonte
    assert "foreignObject" not in fonte.split("ELEMENTOS_PROIBIDOS", 1)[1].split("]);", 1)[0]
    assert "<code>{fonte}</code>" not in fonte
    assert "Não foi possível desenhar esta árvore de decisão" in fonte


def test_fluxograma_bloqueia_execucao_formularios_e_recursos_externos():
    fonte = _fonte(FLUXOGRAMA)

    for elemento in (
        '"script"',
        '"iframe"',
        '"object"',
        '"embed"',
        '"form"',
        '"input"',
        '"button"',
        '"img"',
        '"image"',
    ):
        assert elemento in fonte
    assert 'nomeAtributo.startsWith("on")' in fonte
    assert '["href", "xlink:href", "src"]' in fonte
    assert "cssContemReferenciaPerigosa" in fonte
    assert "parsererror" in fonte


def test_busca_emergencia_filtra_por_nome_gatilho_titulo_e_tema_sem_acentos():
    fonte = _fonte(EMERGENCIA)

    assert "function normalizarBusca" in fonte
    assert '.normalize("NFD")' in fonte
    assert 'type="search"' in fonte
    assert 'placeholder="Ex.: infarto, choque, arritmia"' in fonte
    assert "const protocolosFiltrados = useMemo" in fonte
    assert "p.titulo" in fonte
    assert 'p.gatilho || ""' in fonte
    assert 'documento?.title || ""' in fonte
    assert 'documento?.theme || ""' in fonte
    assert "termos.every((termo) => texto.includes(termo))" in fonte
    assert "protocolosFiltrados.map" in fonte
    assert "Nenhum protocolo encontrado" in fonte


def test_busca_e_falha_do_fluxograma_possuem_estilos_visiveis():
    fonte = _fonte(ESTILO)

    assert ".emerg__busca" in fonte
    assert ".emerg__busca input" in fonte
    assert ".emerg__semResultado" in fonte
    assert ".fluxograma__erro" in fonte
