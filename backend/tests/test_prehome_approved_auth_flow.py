import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def read(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def test_prehome_approved_visual_contract_precedes_global_contrast_guard():
    main = read("main.tsx")
    prehome = 'import "./styles/prehome-approved-auth-flow.css";'
    contrast = 'import "./styles/clinical-form-control-contrast.css";'
    assert prehome in main
    assert contrast in main
    assert main.index(prehome) < main.index(contrast)


def test_prehome_brand_matches_approved_corvia_identity():
    login = read("pages/Entrar.tsx")
    for token in (
        'className={`login login-gateway login-gateway--public login-gateway--${temaPublico} corvia-atelier-login`}',
        'data-login-theme={temaPublico}',
        'src="/atelier/corvia-logo-atelier.svg"',
        "CorVIA · Cardiology Spaces",
        "Cinco espaços de trabalho.",
        "Uma só cardiologia.",
        "Os espaços de trabalho mudam.",
        "O CorVIA permanece ao seu lado.",
        'src="/atelier/atelier-entrance.webp"',
        "Ambiente Protegido",
        "Sistema seguro",
        'to="/esqueci-senha"',
        "corvia-atelier-login.css",
    ):
        assert token in login

    for space_id, name in (
        ("consultorio", "Consultório"),
        ("hospital", "Hospital"),
        ("ensino", "Ensino"),
        ("pesquisa", "Pesquisa"),
        ("gestao", "Gestão"),
    ):
        assert f'{{ id: "{space_id}", nome: "{name}"' in login

    assert "login-gateway__routes" not in login
    assert "login-gateway__ring" not in login
    assert "A PLATAFORMA Nº 1" not in login

    # The architectural entrance replaces the cosmic animation in both
    # appearances. Real images remain available and motion can be disabled.
    assert "LoginGalaxy" not in login
    assert 'width="1536" height="1024"' in login
    assert "prefers-reduced-motion: reduce" in read("styles/corvia-atelier-login.css")
    for asset in ("atelier-entrance.webp", "corvia-logo-atelier.svg"):
        assert (FRONTEND.parent / "public/atelier" / asset).is_file()


def test_login_copy_and_all_real_auth_controls_remain_available():
    login = read("pages/Entrar.tsx")
    for token in (
        'id="login-acesso-titulo" tabIndex={-1}>Bem-vindo',
        'name="tema-publico"',
        "Modo claro",
        "Modo escuro",
        '<form className="login-gateway__form" onSubmit={enviar} aria-busy={enviando}>',
        'id="email" type="email"',
        'id="senha" type={mostrarSenha ? "text" : "password"}',
        'type="submit" disabled={enviando}',
        'aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"}',
        "permanecerConectado",
        "await entrar(email.trim().toLowerCase(), senha, permanecerConectado)",
        'to="/solicitar-acesso"',
        "Novo no CorVIA?",
        "Solicitar acesso profissional",
    ):
        assert token in login

    assert "Bem-vindo de volta" not in login
    assert "Entrar na minha conta" not in login


def test_public_login_no_longer_exposes_native_app_downloads_while_apps_are_paused():
    login = read("pages/Entrar.tsx")
    hrefs = re.findall(r'href="([^"]+)"', login)

    assert "/downloads/corvia-cardiology-spaces-android-1.2.0.apk" not in hrefs
    assert "CorVIA-Cardiology-Spaces-Android" not in login
    assert "MarcaAndroid" not in login
    assert "MarcaWindows" not in login
    assert "Baixar app" not in login
    assert "Aplicativo para Windows" not in login
    assert all("windows" not in href.lower() and not href.lower().endswith(".exe") for href in hrefs)
    assert 'className="atelier-login__join" to="/solicitar-acesso"' in login


def test_approved_prehome_css_keeps_desktop_mobile_and_dark_contracts():
    css = read("styles/prehome-approved-auth-flow.css")
    compact = "".join(css.split())
    assert "grid-template-columns:minmax(430px,42%)minmax(520px,58%)!important" in compact
    assert ".prehome-brand__pillars" in css
    assert ".prehome-brand__hologram" in css
    assert ".prehome-card" in css
    assert "@media(max-width:820px)" in compact
    assert ".login.prehome{display:block!important;min-height:100svh}" in compact
    assert ".prehome-brand__benefits,.prehome-brand__trust{display:none!important}" in compact
    assert ".cos-tour" in css
    assert "--auth-bg:#020710" in compact
