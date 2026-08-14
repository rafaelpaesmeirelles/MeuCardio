from pathlib import Path


CADDYFILE = Path(__file__).resolve().parents[2] / "infra" / "Caddyfile"


def _caddy() -> str:
    return CADDYFILE.read_text(encoding="utf-8")


def test_gallery_static_handler_only_claims_existing_files() -> None:
    caddy = _caddy()

    # Regression guard: an unconditional /galeria/* handle shadows the React
    # route /galeria/:slug and turns direct navigation/reload into a Caddy 404.
    assert "handle_path /galeria/*" not in caddy

    expected_matcher = """\t@galeria_estatica {
\t\tpath /galeria/*
\t\tnot path /galeria/
\t\tfile {
\t\t\troot /
\t\t\ttry_files {path}
\t\t}
\t}"""
    assert expected_matcher in caddy

    expected_handler = """\thandle @galeria_estatica {
\t\troot * /
\t\tfile_server
\t\theader Cache-Control \"public, max-age=2592000\"
\t}"""
    assert expected_handler in caddy


def test_gallery_deeplink_can_reach_no_store_spa_fallback() -> None:
    caddy = _caddy()
    gallery_handler = caddy.index("handle @galeria_estatica")
    spa_fallback = caddy.index("\thandle {", gallery_handler)

    assert gallery_handler < spa_fallback
    assert 'header Cache-Control "no-store, no-cache, must-revalidate, max-age=0"' in caddy[spa_fallback:]
    assert "try_files {path} /index.html" in caddy[spa_fallback:]
