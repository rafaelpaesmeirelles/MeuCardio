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
        'className={`login login-gateway login-gateway--public login-gateway--${temaPublico}`}',
        'data-login-theme={temaPublico}',
        'src="/corvia-mark-canonical.svg"',
        "CARDIOLOGY SPACES",
        "CORVIA · CARDIOLOGY SPACES",
        "Um universo de espaços.",
        "Uma só cardiologia.",
        "Consultório, Hospital, Ensino, Pesquisa e Gestão orbitando juntos no seu Universo Profissional.",
        "CoracaoHolografico",
        "login-gateway__stars",
        "login-gateway__milky-way",
        "login-gateway__pulse",
        "cardiology-spaces-login-approved-final.css",
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


def test_login_copy_and_all_real_auth_controls_remain_available():
    login = read("pages/Entrar.tsx")
    for token in (
        "Entre no CorVIA",
        'name="tema-publico"',
        "Modo claro",
        "Modo escuro",
        "Seu acesso e suas permissões não mudam.",
        '<form className="login-gateway__form" onSubmit={enviar}>',
        'id="email" type="email"',
        'id="senha" type={mostrarSenha ? "text" : "password"}',
        'type="submit" disabled={enviando}',
        'aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"}',
        "permanecerConectado",
        "await entrar(email.trim().toLowerCase(), senha, permanecerConectado)",
        '<Link to="/esqueci-senha">Esqueci minha senha</Link>',
        'to="/solicitar-acesso"',
        "Novo no CorVIA?",
        "Solicite seu Acesso",
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
    assert 'className="login-gateway__join" to="/solicitar-acesso"' in login


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
