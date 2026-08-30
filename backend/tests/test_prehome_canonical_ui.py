from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def _read(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def test_all_public_auth_pages_use_canonical_prehome_shell():
    pages = {
        "Entrar.tsx": "prehome--login",
        "EsqueciSenha.tsx": "prehome--recovery",
        "RedefinirSenha.tsx": "prehome--recovery",
        "SolicitarAcesso.tsx": "prehome--register",
    }
    for filename, variant in pages.items():
        source = _read(f"pages/{filename}")
        assert "PreHomeBrand" in source
        assert 'import "../styles/login.css"' in source
        assert "login prehome" in source
        assert variant in source
        assert "prehome-canonical.css" not in source


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


def test_global_safety_stylesheets_remain_at_the_end_of_the_manifest():
    main = _read("main.tsx")
    manifest = _read("styles/app.css")
    imports = [line.strip() for line in main.splitlines() if line.strip().startswith('import "./styles/')]
    manifest_imports = [line.strip() for line in manifest.splitlines() if line.strip().startswith("@import")]
    assert imports == ['import "./styles/app.css";']
    assert manifest_imports[-2:] == [
        '@import "./clinical-form-control-contrast.css";',
        '@import "./clinical-safety-legibility.css";',
    ]
    assert not any("prehome-register-bridge" in line or "prehome-fidelity-polish" in line for line in manifest_imports)
