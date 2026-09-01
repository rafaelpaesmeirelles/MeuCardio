import re
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
    start = caddy.index("@windows_pending path")
    end = caddy.index("# Hash de conteúdo")
    pending = caddy[start:end]
    assert "handle @windows_pending {" in pending
    for path in (
        "/downloads/corvia-os-windows.zip",
        "/downloads/corvia-os-windows.exe",
        "/downloads/corvia-os-windows.exe.sha256",
        "/downloads/corvia-cardiology-spaces-windows-1.2.0.exe",
        "/downloads/corvia-cardiology-spaces-windows-1.2.0.exe.sha256",
    ):
        assert path in pending
    assert pending.count('respond "Aplicativo Windows em preparação" 410') == 1


def test_automatic_release_requires_web_android_but_not_windows_installer():
    deploy = _read(".github/workflows/deploy-production.yml")
    dispatcher = _read(".github/workflows/release-final-dispatch.yml")
    certification = _read("backend/app/services/release_certification.py")
    assert "deploy-web-android $TARGET_SHA $cert" in deploy
    assert "--artifacts android" in deploy
    assert "Native installers" not in deploy
    assert "native-installers.yml" not in dispatcher
    assert '"Native installers"' not in certification


def test_scientific_inventory_is_a_mandatory_exact_sha_release_gate():
    inventory = _read(".github/workflows/corpus-inventory.yml")
    dispatcher = _read(".github/workflows/release-final-dispatch.yml")
    deploy = _read(".github/workflows/deploy-production.yml")
    certification = _read("backend/app/services/release_certification.py")

    assert "workflow_dispatch:" in inventory
    assert "gh workflow run corpus-inventory.yml" in dispatcher
    assert "- Corpus inventory" in deploy
    assert '"Corpus inventory": "workflow_dispatch"' in deploy
    assert '"Corpus inventory",' in certification


def test_automatic_deploy_deduplicates_only_after_a_prior_certified_run():
    deploy = _read(".github/workflows/deploy-production.yml")
    assert "prior-certified-deploy" in deploy
    assert 'run.get("name") == "Deploy production"' in deploy
    assert 'run.get("status") == "completed"' in deploy
    assert 'run.get("conclusion") == "success"' in deploy
    assert 'str(run.get("id")) != current_run_id' in deploy
    assert 'actions/runs/${prior_run}/jobs?per_page=100' in deploy
    assert '.name == "Deploy certified web and Android release"' in deploy
    assert '.status == "completed"' in deploy
    assert '.conclusion == "success"' in deploy
    assert 'if [[ "$certified_jobs" =~ ^[1-9][0-9]*$ ]]' in deploy
    assert 'if [[ -s "$prior_deploy_marker" ]]' in deploy
    assert "already completed for $candidate; skipping duplicate deployment." in deploy
    assert "production-version.json" not in deploy
    assert deploy.index('if [[ -s "$prior_deploy_marker" ]]') < deploy.index('echo "ready=true"')


def test_android_release_certificate_has_a_public_pinned_fallback():
    deploy = _read(".github/workflows/deploy-production.yml")
    match = re.search(
        r"vars\.CORVIA_ANDROID_CERT_SHA256 \|\| '([0-9a-f]{64})'",
        deploy,
    )
    assert match is not None
    assert "no private signing material is stored in Git" in deploy


def test_android_release_recreates_capacitor_assets_before_sync():
    build = _read("ops/build-android-apk.sh")
    assets = 'install -d -m 0755 "$ANDROID_DIR/app/src/main/assets"'
    assert assets in build
    assert build.index(assets) < build.index("npx cap sync android")


def test_android_release_exports_sdk_for_clean_worktree_gradle():
    build = _read("ops/build-android-apk.sh")
    sdk_declaration = (
        'readonly ANDROID_SDK_DIR="${ANDROID_SDK_ROOT:-'
        '${ANDROID_HOME:-/opt/android-sdk}}"'
    )
    export_home = 'export ANDROID_HOME="$ANDROID_SDK_DIR"'
    export_root = 'export ANDROID_SDK_ROOT="$ANDROID_SDK_DIR"'
    gradle = "./gradlew assembleRelease"
    assert sdk_declaration in build
    assert export_home in build
    assert export_root in build
    assert build.index(export_home) < build.index(gradle)
    assert build.index(export_root) < build.index(gradle)


def test_android_badging_avoids_sigpipe_under_pipefail():
    build = _read("ops/build-android-apk.sh")
    unsafe = 'badging="$("$aapt" dump badging "$apk_file" | head -n 1)"'
    capture = 'badging="$("$aapt" dump badging "$apk_file")"'
    assert unsafe not in build
    assert capture in build


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
