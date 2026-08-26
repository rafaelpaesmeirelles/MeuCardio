"""Contratos de regressão do Modo Emergência no frontend."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FLUXOGRAMA = REPO_ROOT / "frontend/src/components/Fluxograma.tsx"
EMERGENCIA = REPO_ROOT / "frontend/src/pages/Emergencia.tsx"
ESTILO = REPO_ROOT / "frontend/src/styles/emergencia.css"
ESTILO_MOBILE = REPO_ROOT / "frontend/src/styles/clinical-interior-board-lock.css"


def _fonte(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def test_fluxograma_usa_mermaid_run_sem_blob_imagem_ou_parser_manual():
    fonte = _fonte(FLUXOGRAMA)

    assert 'securityLevel: "strict"' in fonte
    assert "htmlLabels: true" in fonte
    assert "await mermaid.parse(fonte)" in fonte
    assert "await mermaid.run({ nodes: [alvo], suppressErrors: true })" in fonte
    assert "alvo.textContent = fonte" in fonte
    assert 'alvo.querySelector("svg")' in fonte
    assert "validarSvgMontado(svg)" in fonte
    assert "URL.createObjectURL" not in fonte
    assert "new Blob" not in fonte
    assert "DOMParser" not in fonte
    assert "document.importNode" not in fonte
    assert "<img" not in fonte
    assert "dangerouslySetInnerHTML" not in fonte
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
    assert "validarFonteMermaid" in fonte
    assert "foreignObject" not in fonte.split("ELEMENTOS_PROIBIDOS", 1)[1].split("]);", 1)[0]


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


def test_emergencia_mobile_reserva_navegacao_e_impede_conteudo_sob_cabecalho():
    pagina = _fonte(EMERGENCIA)
    estilo = _fonte(ESTILO)
    estilo_final = _fonte(ESTILO_MOBILE)

    assert '<p className="emerg__origem">' in pagina
    assert "padding: 0 1rem 5.4rem" in estilo
    assert ".emerg__origem { margin: 0.55rem 0.65rem" in estilo
    assert "font-size: 0.58rem" in estilo
    assert "linear-gradient(145deg,#081b28,#04121d)" in estilo_final
