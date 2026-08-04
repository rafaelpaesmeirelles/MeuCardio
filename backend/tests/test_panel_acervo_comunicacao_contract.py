"""Gates de fonte para o total do acervo e acessos de comunicação no Painel."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PAINEL = REPO_ROOT / "frontend/src/pages/Painel.tsx"
BIBLIOTECA = REPO_ROOT / "frontend/src/pages/Biblioteca.tsx"
SHELL = REPO_ROOT / "frontend/src/components/Shell.tsx"
APP = REPO_ROOT / "frontend/src/App.tsx"
CHAT = REPO_ROOT / "frontend/src/components/ChatFlutuante.tsx"


def _fonte(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def test_painel_usa_catalogo_canônico_em_vez_de_somar_temas():
    fonte = _fonte(PAINEL)

    assert 'api.get<Catalogo>("/library/catalog")' in fonte
    assert 'valor={catalogo?.total ?? null}' in fonte
    assert "temas?.reduce" not in fonte
    assert 'rotulo="itens científicos"' in fonte


def test_painel_expoe_mail_e_chat_com_acesso_acionavel():
    fonte = _fonte(PAINEL)

    assert 'nome: "CorvIA Chat"' in fonte
    assert 'acao: "abrir-chat"' in fonte
    assert 'button[aria-label^="Abrir o CorvIA Chat"]' in fonte
    assert 'nome: "CorvIA Mail"' in fonte
    assert 'to: "/corvia-mail"' in fonte


def test_rotas_menu_e_widget_de_comunicacao_continuam_publicados():
    app = _fonte(APP)
    shell = _fonte(SHELL)
    chat = _fonte(CHAT)

    assert 'path="corvia-mail"' in app
    assert 'to: "/corvia-mail"' in shell
    assert "<ChatFlutuante />" in shell
    assert 'aria-label={naoLidas > 0 ? `Abrir o CorvIA Chat' in chat


def test_painel_e_biblioteca_alertam_quando_corpus_estiver_incompleto():
    painel = _fonte(PAINEL)
    biblioteca = _fonte(BIBLIOTECA)

    assert 'catalogo?.integrity_ok === false' in painel
    assert "Acervo de produção abaixo do inventário certificado" in painel
    assert "4_936" in painel
    assert "1_327" in painel
    assert 'catalogo?.integrity_ok === false' in biblioteca
    assert "Acervo abaixo do inventário certificado" in biblioteca
