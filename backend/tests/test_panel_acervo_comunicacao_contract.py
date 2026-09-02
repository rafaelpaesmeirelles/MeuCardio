"""Gates de fonte para acervo e acessos de comunicação no Clinical OS."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PAINEL = REPO_ROOT / "frontend/src/pages/PainelClinicalOS.tsx"
BIBLIOTECA = REPO_ROOT / "frontend/src/pages/Biblioteca.tsx"
GUIA_DOENCAS = REPO_ROOT / "frontend/src/pages/GuiaDoencas.tsx"
SHELL = REPO_ROOT / "frontend/src/components/ShellClinicalOSLaunch.tsx"
APP = REPO_ROOT / "frontend/src/App.tsx"
CHAT = REPO_ROOT / "frontend/src/components/ChatFlutuante.tsx"
ASSISTENTE_PESSOAL = REPO_ROOT / "frontend/src/components/PersonalAssistantPanel.tsx"


def _fonte(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def test_painel_usa_catalogo_canonico_em_vez_de_somar_temas():
    fonte = _fonte(PAINEL)

    assert 'api.get<Catalogo>("/library/catalog")' in fonte
    assert 'catalogo?.published_total ?? catalogo?.total ?? "—"' in fonte
    assert "temas?.reduce" not in fonte
    # O copy da prancha canônica mudou, mas a métrica continua vindo do
    # catálogo transversal único — este é o contrato que importa.
    assert "conteúdos únicos publicados" in fonte
    assert "(catalogo?.published_total ?? catalogo?.total ?? 9452) - 9452" in fonte
    assert "aprofundamentos, revisões e vínculos Tudo com Tudo não duplicam" in fonte


def test_home_nao_duplica_contagem_especializada_que_ja_e_canonica_na_biblioteca():
    painel = _fonte(PAINEL)
    biblioteca = _fonte(BIBLIOTECA)
    guia = _fonte(GUIA_DOENCAS)

    # No Clinical Command Center, áreas são pontos de entrada. A contagem
    # transversal continua tendo fonte canônica única nas páginas que a exibem.
    assert 'api.get<AreaCountsResponse>("/library/area-counts")' not in painel
    assert 'api.get<AreaCountsResponse>("/library/area-counts")' in biblioteca
    assert "Conteúdos por área clínica" in biblioteca
    assert 'geral: "/doencas?tab=catalogo&area=geral"' in biblioteca
    assert 'neonatal: "/doencas?tab=catalogo&area=cardiopediatria&q=neonatal"' in biblioteca
    assert "Buscar área da Cardiologia" in biblioteca
    assert 'geral: "Cardiologia Geral"' in guia
    assert "Buscar área ou grupo clínico" in guia
    assert 'api.get<DiseaseFacetsResponse>(`/specialty-guides/disease-facets' in guia
    assert "areasFiltradas.map" in guia
    assert "dominiosFiltrados.map" in guia


def test_comunicacao_permanece_acionavel_no_shell_e_no_assistente_pessoal():
    shell = _fonte(SHELL)
    assistente = _fonte(ASSISTENTE_PESSOAL)

    assert '{ to: "/corvia-mail", rotulo: "CorVIA Mail"' in shell
    assert 'aria-label="CorVIA Mail"' in shell
    assert "<ChatFlutuante />" in shell
    assert "CorVIA Mail" in assistente
    assert "/corvia-mail" in assistente


def test_rotas_menu_e_widget_de_comunicacao_continuam_publicados():
    app = _fonte(APP)
    shell = _fonte(SHELL)
    chat = _fonte(CHAT)

    assert 'path="corvia-mail"' in app
    assert 'to: "/corvia-mail"' in shell
    assert "<ChatFlutuante />" in shell
    assert 'aria-label={naoLidas > 0 ? `Abrir o CorvIA Chat' in chat


def test_painel_nao_expoe_alerta_operacional_e_biblioteca_mantem_integridade():
    painel = _fonte(PAINEL)
    biblioteca = _fonte(BIBLIOTECA)

    assert 'catalogo?.integrity_ok === false' not in painel
    assert "Acervo de produção abaixo do inventário certificado" not in painel
    assert 'catalogo?.integrity_ok === false' in biblioteca
    assert "Acervo abaixo do inventário certificado" in biblioteca
