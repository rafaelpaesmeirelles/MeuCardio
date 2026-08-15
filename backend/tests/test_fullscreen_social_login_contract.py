from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"
BACKEND = ROOT / "backend" / "app"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_social_login_router_is_publicly_registered():
    main = read(BACKEND / "main.py")
    assert "social_login" in main
    assert "browser_session.router, social_login.router" in main


def test_social_login_never_auto_provisions_or_bypasses_account_status():
    social = read(BACKEND / "api" / "social_login.py")
    assert "db.query(User).filter(User.email == normalized).first()" in social
    assert 'user.status in {"pendente", "rejeitado"}' in social
    assert "not user.is_active" in social
    assert "db.add(User" not in social
    assert "hash_password" not in social
    assert "secrets.compare_digest(state, expected_state)" in social


def test_provider_catalog_supports_mainstream_account_login():
    social = read(BACKEND / "api" / "social_login.py")
    for provider in ("google", "microsoft", "apple", "github"):
        assert f'("{provider}",' in social
    assert "GOOGLE_SIGNIN_CLIENT_ID" in social
    assert "MICROSOFT_SIGNIN_CLIENT_ID" in social
    assert "APPLE_SIGNIN_CLIENT_ID" in social
    assert "GITHUB_SIGNIN_CLIENT_ID" in social


def test_external_email_is_verified_before_corvia_session():
    social = read(BACKEND / "api" / "social_login.py")
    assert 'body.get("email_verified")' in social
    assert 'claims.get("email_verified"' in social
    assert 'item.get("verified")' in social
    assert "gravar_cookie_sessao(response, create_access_token(user.email, scope=\"app\"))" in social


def test_login_screen_uses_dynamic_viewport_and_social_buttons():
    login = read(FRONTEND / "pages" / "Entrar.tsx")
    css = read(FRONTEND / "styles" / "login-fullscreen-social.css")
    assert 'prehome--login prehome--fullscreen' in login
    assert 'login-fullscreen-social.css' in login
    assert '/auth/social/providers' in login
    assert '/auth/social/${provider}/start' in login
    for provider in ("google", "microsoft", "apple", "github"):
        assert f'provider === "{provider}"' in login or f'"{provider}" |' in login or f'| "{provider}"' in login
    assert "height: 100dvh" in css
    assert "min-height: 100svh" in css
    assert "@media (max-width: 820px)" in css
    assert ".prehome-social__button" in css
