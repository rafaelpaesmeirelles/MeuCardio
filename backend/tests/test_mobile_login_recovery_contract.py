from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_login_updates_authenticated_user_without_full_page_reload():
    auth = _read("frontend/src/lib/auth.tsx")

    assert 'const perfil = await api.get<Usuario>("/auth/me")' in auth
    assert "setUsuario(perfil)" in auth
    assert "window.location.replace(`/?login=" not in auth


def test_root_has_visible_recovery_instead_of_white_screen():
    main = _read("frontend/src/main.tsx")
    boundary = _read("frontend/src/components/AppErrorBoundary.tsx")

    assert "<AppErrorBoundary>" in main
    assert "Não foi possível abrir esta tela." in boundary
    assert "Atualizar e continuar" in boundary
    assert 'role="alert"' in boundary


def test_service_worker_never_substitutes_api_json_with_spa_shell():
    config = _read("frontend/vite.config.ts")

    assert r"navigateFallbackDenylist: [/^\/api\//]" in config
    assert '!url.pathname.startsWith("/api/")' in config


def test_mobile_media_query_supports_legacy_ios_listener():
    personalizer = _read("frontend/src/components/HomeQuickActionsPersonalizer.tsx")

    assert 'typeof media.addEventListener === "function"' in personalizer
    assert 'typeof window.matchMedia === "function"' in personalizer
    assert 'typeof media.addListener === "function"' in personalizer
    assert "media.addListener(atualizar)" in personalizer


def test_optional_home_personalizer_never_blocks_authentication_gates():
    main = _read("frontend/src/main.tsx")
    app = _read("frontend/src/App.tsx")

    # O aprimoramento não pode montar antes de sabermos quem está entrando.
    assert "HomeQuickActionsPersonalizer" not in main

    # Contas normais, convidadas, investidoras e administradoras atravessam
    # os mesmos gates antes que o recurso opcional da home seja instanciado.
    personalizer = app.index("<HomeQuickActionsPersonalizer />")
    assert app.index("if (!usuario)") < personalizer
    assert app.index("usuario.profile_completion_required") < personalizer
    assert app.index("usuario.kyc_required") < personalizer
    assert app.index("usuario.onboarding_pendente") < personalizer
