from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_native_installers_are_not_exposed_on_public_login():
    login = _read("frontend/src/pages/Entrar.tsx")
    assert "Aplicativo para Windows" not in login
    assert "MarcaWindows" not in login
    assert "MarcaAndroid" not in login
    assert "/downloads/corvia-cardiology-spaces-windows-1.2.0.exe" not in login
    assert 'href="/downloads/corvia-cardiology-spaces-android-1.2.0.apk"' not in login
    assert 'className="login-gateway__join" to="/solicitar-acesso"' in login
    assert "Novo no CorVIA?" in login
    assert "Solicite seu Acesso" in login


def test_automatic_release_is_web_only():
    deploy = _read(".github/workflows/deploy-production.yml")
    emergency = _read(".github/workflows/deploy-login-emergency.yml")
    entrypoint = _read("ops/remote-deploy-entrypoint.sh")

    assert '"deploy-web $TARGET_SHA"' in deploy
    assert '"deploy-web $TARGET_SHA"' in emergency
    assert "deploy-web-android" not in deploy
    assert "deploy-web-android" not in emergency
    assert "ANDROID_CERT_SHA256" not in deploy
    assert "ANDROID_CERT_SHA256" not in emergency
    assert "windows-stage" not in entrypoint
    assert "deploy-release" not in entrypoint
    assert "deploy-web-android" not in entrypoint
    assert "deploy-web" in entrypoint


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


def test_automatic_deploy_deduplicates_only_after_a_prior_certified_web_run():
    deploy = _read(".github/workflows/deploy-production.yml")
    assert "prior-certified-deploy" in deploy
    assert 'run.get("name") == "Deploy production"' in deploy
    assert 'run.get("status") == "completed"' in deploy
    assert 'run.get("conclusion") == "success"' in deploy
    assert 'str(run.get("id")) != current_run_id' in deploy
    assert 'actions/runs/${prior_run}/jobs?per_page=100' in deploy
    assert '.name == "Deploy certified web release"' in deploy
    assert '.status == "completed"' in deploy
    assert '.conclusion == "success"' in deploy
    assert 'if [[ "$certified_jobs" =~ ^[1-9][0-9]*$ ]]' in deploy
    assert 'if [[ -s "$prior_deploy_marker" ]]' in deploy
    assert "already completed for $candidate; skipping duplicate deployment." in deploy
    assert deploy.index('if [[ -s "$prior_deploy_marker" ]]') < deploy.index('echo "ready=true"')


def test_bootstrap_rejects_native_release_protocols():
    bootstrap = _read("ops/bootstrap-release-entrypoint.sh")
    assert "grep -Fq 'deploy-web'" in bootstrap
    assert "deploy-web-android|windows-stage|deploy-release" in bootstrap
    assert "Native release commands are still present; refusing web-only bootstrap." in bootstrap


def test_web_only_policy_is_recorded():
    policy = _read("ops/WEB_ONLY_RELEASE_POLICY_20260904.md")
    assert "Não construir, assinar, promover ou validar APK Android." in policy
    assert "Não construir, promover ou validar instalador Windows." in policy
    assert "deploy-web <SHA-da-main>" in policy
