from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def _read(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def test_auth_pages_use_canonical_prehome_shell():
    entrar = _read("pages/Entrar.tsx")
    esqueci = _read("pages/EsqueciSenha.tsx")
    redefinir = _read("pages/RedefinirSenha.tsx")

    assert 'className="login prehome prehome--login"' in entrar
    assert 'className="login prehome prehome--recovery"' in esqueci
    assert 'className="login prehome prehome--recovery"' in redefinir
    for source in (entrar, esqueci, redefinir):
        assert "PreHomeBrand" in source
        assert 'prehome-canonical.css' in source


def test_signup_keeps_recovery_and_existing_functional_fields():
    signup = _read("pages/SolicitarAcesso.tsx")
    # O redesign é apenas visual: não pode simplificar o formulário removendo
    # identidade profissional, CPF/conselho ou o segundo canal de recuperação.
    assert 'recovery_email' in signup
    assert 'cpf' in signup
    assert 'council_number' in signup
    assert 'workplace_name' in signup
    assert '/auth/solicitar-acesso-com-recuperacao' in signup


def test_canonical_prehome_palette_is_dark_and_board_aligned():
    css = _read("styles/prehome-canonical.css")
    required = (
        "--ph-bg: #02070e",
        "--ph-cyan: #20dce5",
        "--ph-violet: #9b6cff",
        ".prehome-brand__hologram",
        ".prehome-card",
        "@media (max-width: 900px)",
        "@media (max-width: 1366px)",
    )
    for token in required:
        assert token in css

    # Regressão que motivou este trabalho: a área transacional não pode voltar
    # ao painel branco genérico do login anterior.
    assert "background: linear-gradient(150deg, #fff" not in css


def test_registration_bridge_overrides_legacy_light_panel_without_losing_form():
    css = _read("styles/prehome-register-bridge.css")
    assert ".login--solicitar-acesso .login-acesso" in css
    assert "#f2f7fb" in css
    assert "prehome" not in _read("pages/SolicitarAcesso.tsx") or "recovery_email" in _read("pages/SolicitarAcesso.tsx")


def test_no_browser_scale_or_zoom_workaround_in_prehome_styles():
    css = (_read("styles/prehome-canonical.css") + _read("styles/prehome-register-bridge.css")).lower()
    assert "zoom:" not in css
    assert "scale(" not in css
