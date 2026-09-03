from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def _read(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def test_all_public_auth_pages_use_canonical_prehome_shell():
    login = _read("pages/Entrar.tsx")
    frame = _read("components/PublicCardiologyFrame.tsx")
    main = _read("main.tsx")

    # /entrar tem a prancha sideral própria aprovada; os demais fluxos de
    # autenticação compartilham o frame público do Cardiology Spaces.
    assert 'className={`login login-gateway login-gateway--public login-gateway--${temaPublico}`}' in login
    assert 'data-login-theme={temaPublico}' in login
    assert 'import "../styles/cardiology-spaces-login.css";' in login
    assert "PublicCardiologyFrame" not in login
    assert "login prehome" not in login

    for filename in ("EsqueciSenha.tsx", "RedefinirSenha.tsx", "SolicitarAcesso.tsx"):
        source = _read(f"pages/{filename}")
        assert 'import PublicCardiologyFrame from "../components/PublicCardiologyFrame";' in source
        assert "<PublicCardiologyFrame" in source
        assert 'import "../styles/login.css"' in source
        assert "PreHomeBrand" not in source
        assert "login prehome" not in source

    for token in (
        'className={`public-space public-space--${variant} public-space--${tone}`}',
        "PublicCorviaBrand",
        'src="/corvia-mark-canonical.svg"',
        "CARDIOLOGY SPACES",
        "Ambiente protegido",
        "Acesso profissional · LGPD",
    ):
        assert token in frame

    assert 'import "./styles/cardiology-spaces-public.css";' in main


def test_signup_keeps_existing_functional_contract():
    signup = _read("pages/SolicitarAcesso.tsx")
    for field in (
        "recovery_email", "cpf", "birth_date", "profession", "council_name",
        "council_number", "council_state", "specialty", "workplace_name",
        "workplace_department", "workplace_role", "workplace_notes",
        "include_workplace_on_documents", "instagram_handle", "password",
    ):
        assert field in signup
    assert "/auth/solicitar-acesso-com-recuperacao" in signup
    assert "prehome-card--register" in signup
    assert "prehome-steps" in signup


def test_canonical_palette_and_board_components_live_in_login_css():
    css = _read("styles/login.css")
    for token in (
        "--ph-bg:#02070e",
        "--ph-cyan:#20dce5",
        "--ph-violet:#9b6cff",
        ".prehome-brand__hologram",
        ".prehome-card",
        ".prehome-steps",
        ".prehome-confirmation",
        "@media(max-width:1366px)",
        "@media(max-width:900px)",
        "@media(max-width:430px)",
    ):
        assert token in css

    # A regressão que originou a revisão era uma superfície de autenticação
    # clara/genérica desconectada da prancha dark navy do Clinical OS.
    assert "background:#fff" not in css
    assert "background: #fff" not in css


def test_auth_input_autofill_remains_dark_and_legible():
    css = _read("styles/login.css")
    assert ".login .login-formulario input:-webkit-autofill" in css
    assert "-webkit-text-fill-color:#eef6fb" in css
    assert "-webkit-box-shadow:0 0 0 1000px #0d2032 inset" in css
    assert "caret-color:#20dce5" in css


def test_notebook_and_mobile_fidelity_guards_exist():
    css = _read("styles/login.css")
    assert "max-height:800px" in css
    assert ".prehome-brand__benefits" in css
    assert ".prehome--login .prehome-brand" in css
    assert ".prehome--register" in css


def test_no_browser_scale_or_zoom_workaround():
    css = _read("styles/login.css").lower()
    assert "zoom:" not in css
    assert "scale(" not in css


def test_scoped_light_theme_remains_after_global_contrast_guard():
    main = _read("main.tsx")
    imports = [line.strip() for line in main.splitlines() if line.strip().startswith('import "./styles/')]
    assert imports[-2:] == [
        'import "./styles/clinical-form-control-contrast.css";',
        'import "./styles/cardiology-spaces-light-mode.css";',
    ]
    assert 'html[data-corvia-theme="light"]' in _read("styles/cardiology-spaces-light-mode.css")
    assert not any("prehome-register-bridge" in line or "prehome-fidelity-polish" in line for line in imports)
