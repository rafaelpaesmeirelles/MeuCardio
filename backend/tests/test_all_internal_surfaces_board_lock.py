from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STYLE_MANIFEST = ROOT / "frontend" / "src" / "styles" / "app.css"
APP = ROOT / "frontend" / "src" / "App.tsx"
CONTEXT = ROOT / "frontend" / "src" / "components" / "ClinicalRouteContext.tsx"
BOARD_LOCK = ROOT / "frontend" / "src" / "styles" / "clinical-interior-board-lock.css"


def compact(text: str) -> str:
    return "".join(text.split())


def test_approved_board_lock_is_loaded_after_legacy_fidelity_layers():
    manifest = STYLE_MANIFEST.read_text(encoding="utf-8")
    board_import = '@import "./clinical-interior-board-lock.css";'
    contrast_import = '@import "./clinical-form-control-contrast.css";'
    assert board_import in manifest
    assert contrast_import in manifest
    assert manifest.index(board_import) < manifest.index(contrast_import)
    assert manifest.index(board_import) > manifest.index('@import "./clinical-reference-fidelity-release.css";')


def test_approved_home_is_isolated_from_the_internal_page_lock():
    context = CONTEXT.read_text(encoding="utf-8")
    assert 'if (pathname === "/")' in context
    assert 'document.body.dataset.corviaRoute = "home"' in context
    assert 'document.body.classList.add(classe)' in context


def test_every_internal_route_family_is_subject_to_the_same_board_canvas():
    css = compact(BOARD_LOCK.read_text(encoding="utf-8"))
    context = CONTEXT.read_text(encoding="utf-8")
    assert 'body[class*="corvia-route--"].clinical-os.cos-content' in css
    assert 'width:100%!important' in css
    assert 'max-width:none!important' in css

    route_families = {
        "documentos", "pacientes", "prescricao", "agenda", "mail", "assistente",
        "conhecimento", "ferramentas", "emergencia", "rede", "telediagnostico",
        "integracoes", "conta", "admin", "geral",
    }
    for family in route_families:
        assert f'"{family}"' in context


def test_known_visual_exceptions_are_forced_back_into_the_board_language():
    css = BOARD_LOCK.read_text(encoding="utf-8")
    for selector in (
        "body.corvia-route--pacientes",
        "body.corvia-route--admin",
        "body.corvia-route--emergencia",
    ):
        assert selector in css
    assert "Emergency keeps red only as a clinical accent" in css


def test_canonical_board_lock_does_not_remove_or_replace_feature_routes():
    app = APP.read_text(encoding="utf-8")
    routes = (
        "apresentacao", "biblioteca", "doencas", "triagem-sintomas", "fluxogramas",
        "diretrizes", "busca", "calculadoras", "medicamentos", "interacoes", "condicoes",
        "galeria", "exames", "evidencias", "estudos", "trilhas", "material-paciente",
        "emergencia", "casos-clinicos", "checklists", "indicadores", "cursos", "favoritos",
        "assistente", "round", "agenda", "documentos", "exportar", "avaliacao-preoperatoria",
        "receituario", "assinatura", "minha-conta", "sincronizacao", "verificacao-identidade",
        "telediagnostico", "caixa-de-email", "corvia-mail", "usuarios-online", "privacidade",
        "termos", "admin", "admin/usuarios", "fila-telediagnostico",
    )
    for route in routes:
        assert f'path="{route}"' in app or f'path="{route}/:' in app
