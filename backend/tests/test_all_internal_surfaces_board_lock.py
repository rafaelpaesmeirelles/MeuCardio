import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "frontend" / "src" / "main.tsx"
APP = ROOT / "frontend" / "src" / "App.tsx"
CONTEXT = ROOT / "frontend" / "src" / "components" / "ClinicalRouteContext.tsx"
APP_FRAME = ROOT / "frontend" / "src" / "components" / "CardiologySpacesAppFrame.tsx"
ROUTE_REGISTRY = ROOT / "frontend" / "src" / "lib" / "clinicalRouteRegistry.ts"
BOARD_LOCK = ROOT / "frontend" / "src" / "styles" / "clinical-interior-board-lock.css"
INTERIOR_APPROVED = ROOT / "frontend" / "src" / "styles" / "cardiology-spaces-interior-approved.css"
ROUTE_DEEP = ROOT / "frontend" / "src" / "styles" / "cardiology-spaces-route-deep.css"
CONSULTORIO_PAGES = ROOT / "frontend" / "src" / "styles" / "cardiology-spaces-consultorio-pages.css"
CONSULTORIO_PRESCRICAO = ROOT / "frontend" / "src" / "styles" / "cardiology-spaces-consultorio-prescricao.css"


def compact(text: str) -> str:
    return "".join(text.split())


def test_approved_board_lock_is_loaded_after_legacy_fidelity_layers():
    main = MAIN.read_text(encoding="utf-8")
    board_import = 'import "./styles/clinical-interior-board-lock.css";'
    contrast_import = 'import "./styles/clinical-form-control-contrast.css";'
    assert board_import in main
    assert contrast_import in main
    assert main.index(board_import) < main.index(contrast_import)
    assert main.index(board_import) > main.index('import "./styles/clinical-reference-fidelity-release.css";')


def test_approved_home_is_isolated_from_the_internal_page_lock():
    context = CONTEXT.read_text(encoding="utf-8")
    assert 'if (pathname === "/")' in context
    assert 'document.body.dataset.corviaRoute = "home"' in context
    assert 'document.body.classList.add(routeClass, spaceClass)' in context


def test_every_internal_route_family_is_subject_to_the_same_board_canvas():
    css = compact(BOARD_LOCK.read_text(encoding="utf-8"))
    frame = APP_FRAME.read_text(encoding="utf-8")
    registry = ROUTE_REGISTRY.read_text(encoding="utf-8")
    assert 'body[class*="corvia-route--"].clinical-os.cos-content' in css
    assert 'width:100%!important' in css
    assert 'max-width:none!important' in css
    assert 'className={`cv-content${nativePage ? "" : " clinical-os"}`}' in frame
    assert '<div className="conteudo cos-content">' in frame
    assert frame.count('id="conteudo-principal"') == 1

    route_families = {
        "documentos", "pacientes", "prescricao", "agenda", "mail", "assistente",
        "conhecimento", "ferramentas", "emergencia", "rede", "telediagnostico",
        "integracoes", "conta", "admin", "geral",
    }
    for family in route_families:
        assert f'| "{family}"' in registry


def test_native_matrices_are_explicitly_isolated_from_the_legacy_board_canvas():
    frame = APP_FRAME.read_text(encoding="utf-8")
    native_block = re.search(r"const NATIVE_PAGE_PATHS = new Set\(\[(.*?)\]\);", frame, re.DOTALL)
    assert native_block is not None
    native_paths = set(re.findall(r'"(/[^"]+)"', native_block.group(1)))
    assert native_paths == {
        "/calculadoras",
        "/emergencia",
        "/trilhas",
        "/evidencias",
        "/indicadores",
    }
    assert "const nativePage = NATIVE_PAGE_PATHS.has(location.pathname);" in frame
    assert "{nativePage ? (" in frame


def test_current_and_legacy_shared_headers_do_not_receive_a_duplicate_context_strip():
    route_deep = ROUTE_DEEP.read_text(encoding="utf-8")
    selector = ".cos-content:not(:has(.cs-page-header, .cv-page-hero))"
    assert route_deep.count(selector) == 3


def test_internal_board_geometry_is_symmetric_and_does_not_restore_home_trapezoids():
    board_lock = BOARD_LOCK.read_text(encoding="utf-8")
    interior = INTERIOR_APPROVED.read_text(encoding="utf-8")
    consultorio = CONSULTORIO_PAGES.read_text(encoding="utf-8")
    prescricao = CONSULTORIO_PRESCRICAO.read_text(encoding="utf-8")
    assert "border-radius:8px" not in board_lock
    assert board_lock.count("border-radius:12px!important") >= 3
    assert "clip-path" not in interior
    assert "border-radius:12px!important" in interior
    assert "clip-path" not in consultorio
    assert "clip-path" not in prescricao
    assert ".agenda-cabecalho" in consultorio and "border-radius:12px!important" in consultorio
    assert ".prescricao__cabecalho" in prescricao and "border-radius:12px!important" in prescricao


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
