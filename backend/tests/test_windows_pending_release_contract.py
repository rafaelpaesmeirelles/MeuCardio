from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_windows_is_pending_without_public_login_link():
    login = _read("frontend/src/pages/Entrar.tsx")
    assert "Aplicativo para Windows" in login
    assert "pendente de assinatura" in login
    assert "/downloads/corvia-cardiology-spaces-windows-1.2.0.exe" not in login
    assert 'href="/downloads/corvia-cardiology-spaces-android-1.2.0.apk"' in login


def test_windows_download_routes_are_explicitly_unavailable():
    caddy = _read("infra/Caddyfile")
    assert 'respond /downloads/corvia-cardiology-spaces-windows-1.2.0.exe ' in caddy
    assert 'respond /downloads/corvia-os-windows.exe ' in caddy
    assert caddy.count('"Aplicativo Windows em preparação" 410') == 5


def test_automatic_release_requires_web_android_but_not_windows_installer():
    deploy = _read(".github/workflows/deploy-production.yml")
    dispatcher = _read(".github/workflows/release-final-dispatch.yml")
    certification = _read("backend/app/services/release_certification.py")
    assert "deploy-web-android $TARGET_SHA $cert" in deploy
    assert "--artifacts android" in deploy
    assert "Native installers" not in deploy
    assert "native-installers.yml" not in dispatcher
    assert '"Native installers"' not in certification


def test_windows_manual_release_stays_fail_closed_and_strictly_signed():
    workflow = _read(".github/workflows/native-installers.yml")
    entrypoint = _read("ops/remote-deploy-entrypoint.sh")
    for token in (
        "CORVIA_WINDOWS_CODE_SIGNING_CERT is required",
        "CORVIA_WINDOWS_CODE_SIGNING_PASSWORD is required",
        "Get-AuthenticodeSignature",
        "CORVIA_WINDOWS_SIGNING_CERT_SHA256",
    ):
        assert token in workflow
    assert "windows-stage" in entrypoint
    assert "deploy-release" in entrypoint
    assert 'validate_staged_artifact "$RELEASE_STAGING_DIR/$WINDOWS_NAME"' in entrypoint


def test_remote_protocol_supports_android_only_without_deleting_windows():
    entrypoint = _read("ops/remote-deploy-entrypoint.sh")
    assert "deploy-web-android" in entrypoint
    assert 'release_artifacts=("$ANDROID_NAME" "$ANDROID_NAME.sha256")' in entrypoint
    assert 'release_artifacts+=("$WINDOWS_NAME" "$WINDOWS_NAME.sha256")' in entrypoint
