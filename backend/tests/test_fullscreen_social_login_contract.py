from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"
BACKEND = ROOT / "backend" / "app"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact(value: str) -> str:
    return "".join(value.split())


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
    for variable in (
        "GOOGLE_SIGNIN_CLIENT_ID",
        "MICROSOFT_SIGNIN_CLIENT_ID",
        "APPLE_SIGNIN_CLIENT_ID",
        "GITHUB_SIGNIN_CLIENT_ID",
    ):
        assert variable in social


def test_external_email_is_verified_before_corvia_session():
    social = read(BACKEND / "api" / "social_login.py")
    assert 'body.get("email_verified")' in social
    assert 'claims.get("email_verified"' in social
    assert 'body.get("email_verified") is not True' in social
    assert 'item.get("verified")' in social
    assert "start_session(" in social
    assert 'create_access_token(user.email,scope="app",session_id=session_id)' in compact(social)


def test_yahoo_is_not_offered_as_social_login():
    social = read(BACKEND / "api" / "social_login.py")
    login = read(FRONTEND / "pages" / "Entrar.tsx")
    assert '("yahoo", "Yahoo")' not in social
    assert '"yahoo" |' not in login


def test_apple_uses_signed_client_secret_and_verified_identity_token():
    social = read(BACKEND / "api" / "social_login.py")
    assert "https://appleid.apple.com/auth/authorize" in social
    assert "https://appleid.apple.com/auth/token" in social
    assert "https://appleid.apple.com/auth/keys" in social
    assert 'algorithm="ES256"' in social
    assert 'algorithms=["RS256"]' in social
    assert 'issuer="https://appleid.apple.com"' in social


def test_login_screen_uses_dynamic_viewport_without_social_buttons():
    login = read(FRONTEND / "pages" / "Entrar.tsx")
    css = compact(read(FRONTEND / "styles" / "cardiology-spaces-login.css"))
    local_styles = [
        line.strip()
        for line in login.splitlines()
        if line.strip().startswith('import "../styles/')
    ]

    assert '<main className="login login-gateway">' in login
    assert 'prehome--login prehome--fullscreen' not in login
    assert local_styles[-1] == 'import "../styles/cardiology-spaces-login.css";'
    assert '/auth/social/providers' not in login
    assert '/auth/social/${provider}/start' not in login
    assert 'prehome-social' not in login
    assert ".login-gateway{" in css
    assert "height:100svh" in css
    assert "overflow:hidden" in css
    assert "@media(max-width:760px)" in css
    assert "height:auto" in css
    assert "min-height:100svh" in css
    assert "overflow-y:auto" in css


def test_login_route_stays_online_first_instead_of_inflating_pwa_preload():
    vite = read(ROOT / "frontend" / "vite.config.ts")
    assert "loginSomenteOnline" in vite
    assert "Entrar-[^/]*" in vite
    assert "(?:js|css)" in vite
    assert "if (loginSomenteOnline.test(entry.url)) return false" in vite
    assert 'urlPattern: /\\/assets\\/.*\\.(?:js|css)$/' in vite
    assert 'handler: "NetworkFirst"' in vite
