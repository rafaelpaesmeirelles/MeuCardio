from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def _read(relative: str) -> str:
    return (FRONTEND / relative).read_text(encoding="utf-8")


def test_anonymous_root_enters_canonical_login_not_legacy_marketing_landing():
    app = _read("App.tsx")
    assert '<Route path="/" element={<Navigate to="/entrar" replace />} />' in app
    assert '<Route path="/produto" element={<Produto />} />' in app
    assert '<Route path="/" element={<Produto />} />' not in app


def test_authenticated_home_matches_reference_board_structure():
    panel = _read("pages/PainelClinicalOS.tsx")
    final_css = _read("styles/clinical-reference-board-final.css")
    main = _read("main.tsx")

    for token in (
        'ccc-reference-board',
        'className="ccc-command"',
        'ccc-actions-section',
        'ccc-reference-summary',
        'aria-label="Próximo Deslocamento"',
        'ccc-reference-commute__map',
        '<MapaDeslocamento',
        'ccc-reference-updates',
        'ccc-module-directory',
        'aria-label="CorVIA Intelligence"',
        'aria-label="Assistente Pessoal"',
        'ccc-reference-trust',
    ):
        assert token in panel

    for title in (
        "Clínica & Decisão",
        "Estudo & Aprendizagem",
        "Trabalho & Assistência",
        "Ferramentas & Produtividade",
        "Rede & Conectividade",
        "Administração & Conta",
    ):
        assert title in panel

    assert '.ccc-reference-commute' in final_css
    assert '.ccc-module-directory__grid' in final_css
    assert '.ccc-reference-summary > .ccc-reference-commute { order: 1; }' in final_css
    assert '.ccc-reference-summary > .ccc-reference-day { order: 2; }' in final_css
    assert '.ccc-reference-summary > .ccc-reference-assistant-summary { order: 3; }' in final_css
    assert '.ccc-reference-summary > .ccc-reference-updates-summary { order: 4; }' in final_css

    # O override final precisa vir depois de todas as camadas históricas da Home
    # e antes do contrato global de contraste dos formulários.
    reference_import = 'import "./styles/clinical-reference-board-final.css";'
    contrast_import = 'import "./styles/clinical-form-control-contrast.css";'
    assert reference_import in main
    assert main.index(reference_import) < main.index(contrast_import)


def test_mobile_quick_actions_default_to_two_rows_without_duplicate_originals():
    personalizer = _read("components/HomeQuickActionsPersonalizer.tsx")
    css = _read("styles/home-desktop-symmetric-personalizable.css")

    default_block = personalizer.split("const PADRAO_MOBILE = [", 1)[1].split("];", 1)[0]
    assert default_block.count('"') == 16
    assert "repeat(4,minmax(0,1fr))" in css
    assert ".ccc-actions.qa-active>.ccc-action:not(.qa-action)" in css
    assert css.count(".qa-active>.ccc-action:not(.qa-action)") == 1


def test_home_exposes_all_real_functional_areas_without_dead_mock_buttons():
    panel = _read("pages/PainelClinicalOS.tsx")
    app = _read("App.tsx")

    routes = (
        "/doencas", "/medicamentos", "/exames", "/calculadoras", "/emergencia",
        "/checklists", "/triagem-sintomas", "/interacoes", "/condicoes", "/fluxogramas",
        "/avaliacao-preoperatoria", "/evidencias", "/estudos", "/diretrizes",
        "/trilhas/timeline", "/trilhas", "/casos-clinicos", "/biblioteca", "/galeria",
        "/cursos", "/apresentacao", "/round", "/receituario", "/documentos",
        "/material-paciente", "/agenda", "/corvia-mail",
        "/telediagnostico", "/indicadores", "/exportar", "/favoritos", "/busca",
        "/assistente", "/usuarios-online", "/sincronizacao", "/minha-conta",
        "/tour", "/admin", "/admin/usuarios", "/fila-telediagnostico",
    )
    for route in routes:
        assert f'to: "{route}"' in panel
        assert f'path="{route.lstrip("/")}' in app or f'path="{route}"' in app

    assert 'to: "/tour?origem=assinatura&modo=quick"' in panel
    assert 'path="assinatura"' in app
    assert 'path="/em-breve"' in app or 'path="em-breve"' in app


def test_home_full_mobility_functions_are_not_removed_during_visual_rebuild():
    panel = _read("pages/PainelClinicalOS.tsx")
    for token in (
        'mobilidade.automatic_foreground_refresh',
        'mobilidade.refresh_interval_minutes',
        'document.visibilityState !== "visible"',
        'resultado.destination?.target_key !== targetKey',
        'rota.distance_meters',
        'rota.traffic_delay_seconds',
        'rota.duration_seconds + destino.arrival_buffer_minutes * 60',
        '"/agenda/mobility/prepare-next-target"',
        '"/agenda/mobility/next-target"',
        '"/agenda/mobility/commute-target"',
        'const targetKey = destinoPlanejado?.target_key || null',
        'target_type: "day_return"',
    ):
        assert token in panel


def test_navigation_matches_reference_six_area_information_architecture():
    desktop = _read("components/ClinicalDesktopNav.tsx")
    mobile = _read("components/ClinicalMobileNav.tsx")
    nav_css = _read("styles/clinical-navigation-reference-final.css")

    for source in (desktop, mobile):
        for title in (
            "Clínica & Decisão",
            "Estudos & Educação",
            "Trabalho & Assistência",
            "Ferramentas & Produtividade",
            "Rede & Conectividade",
        ):
            assert title in source
        for route in (
            "/triagem-sintomas", "/interacoes", "/condicoes", "/fluxogramas",
            "/material-paciente", "/avaliacao-preoperatoria", "/telediagnostico",
            "/indicadores", "/galeria", "/cursos", "/apresentacao",
            "/usuarios-online", "/sincronizacao", "/exportar", "/assistente",
            "/favoritos", "/minha-conta", "/tour?origem=assinatura&modo=quick", "/tour",
        ):
            assert route in source

    assert "Administração" in desktop
    assert "Administração & Conta" in mobile
    assert ".ccc-nav--reference" in nav_css
    assert ".cc-mobile-more__grid" in nav_css

    labels = ["Início", "Buscar", "Prontuário", "Agenda", "Mais"]
    positions = [mobile.index(f"<span>{label}</span>") for label in labels]
    assert positions == sorted(positions)
    assert len(positions) == 5
