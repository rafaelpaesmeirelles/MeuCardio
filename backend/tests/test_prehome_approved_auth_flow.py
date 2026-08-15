from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def read(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def test_prehome_approved_visual_contract_is_loaded_last():
    main = read("main.tsx")
    import_line = 'import "./styles/prehome-approved-auth-flow.css";'
    assert import_line in main
    assert main.index(import_line) > main.index('import "./styles/clinical-form-control-contrast.css";')


def test_prehome_brand_matches_approved_corvia_identity():
    brand = read("components/PreHomeBrand.tsx")
    for token in (
        "A PLATAFORMA Nº 1",
        "Inteligência clínica",
        "transforma decisões.",
        "Inteligência Artificial",
        "Evidências atualizadas",
        "Tudo com Tudo",
        "Segurança e Privacidade",
        "prehome-brand__heart",
        "prehome-brand__ring--3",
    ):
        assert token in brand


def test_login_copy_and_all_real_auth_controls_remain_available():
    login = read("pages/Entrar.tsx")
    for token in (
        "Bem-vindo de volta",
        "Entrar na minha conta",
        "Esqueci minha senha",
        "Solicitar acesso",
        "permanecerConectado",
        "await entrar(email.trim().toLowerCase(), senha, permanecerConectado)",
    ):
        assert token in login


def test_approved_prehome_css_keeps_desktop_mobile_and_dark_contracts():
    css = read("styles/prehome-approved-auth-flow.css")
    assert "grid-template-columns: minmax(430px, 42%) minmax(520px, 58%)" in css
    assert ".prehome-brand__pillars" in css
    assert ".prehome-brand__hologram" in css
    assert ".prehome-card" in css
    assert "@media (max-width: 820px)" in css
    assert ".login.prehome { display: block;" in css
    assert ".cos-tour" in css
    assert "--auth-bg: #020710" in css
