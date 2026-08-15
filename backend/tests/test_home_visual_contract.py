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


def test_authenticated_home_preserves_approved_board_and_full_functions():
    panel = _read("pages/PainelClinicalOS.tsx")
    css = _read("styles/clinical-home-mobile-final.css")

    # Estrutura visual canônica da prancha permanece presente.
    for token in (
        'className="ccc-command"',
        'className="ccc-actions"',
        'className="ccc-mobile-summary"',
        'className="ccc-recent"',
        'className="ccc-updates"',
        'aria-label="CorVIA Intelligence"',
        'aria-label="Assistente Pessoal"',
    ):
        assert token in panel

    # As funções que existiam antes do rollback não podem desaparecer.
    for token in (
        'ccc-home-fronts',
        'Clínica & Decisão',
        'Estudo & Aprendizagem',
        'Trabalho & Assistência',
        'Tudo com Tudo',
        '"/agenda/mobility/commute-appointment"',
        'mobilidade.automatic_foreground_refresh',
        'mobilidade.refresh_interval_minutes',
        'document.visibilityState !== "visible"',
        'resultado.destination?.appointment_id !== proximo.id',
    ):
        assert token in panel

    # O card móvel de mapa pode continuar no DOM para manter a lógica completa,
    # mas não pode alterar a composição visual aprovada da Home.
    assert 'ccc-mobile-commute' in panel
    assert '.ccc-mobile-commute { display: none !important; }' in css


def test_mobile_home_visible_order_matches_approved_board():
    panel = _read("pages/PainelClinicalOS.tsx")
    css = _read("styles/clinical-home-mobile-final.css")
    start = panel.index('className="ccc-mobile-summary"')
    end = panel.index('className="ccc-section ccc-recent-section"')
    mobile = panel[start:end]

    seu_dia = mobile.index("Seu dia")
    assistente = mobile.index("Assistente")
    atualizacoes = mobile.index("Atualizações")
    assert seu_dia < assistente < atualizacoes
    assert '.ccc-mobile-commute { display: none !important; }' in css
    assert '.ccc-home--board .ccc-updates-section { display: none !important; }' in css


def test_home_fronts_are_available_without_replacing_canonical_top_composition():
    panel = _read("pages/PainelClinicalOS.tsx")
    fronts = panel.index('className="ccc-section ccc-home-fronts"')
    updates = panel.index('className="ccc-section ccc-updates-section"')
    intelligence = panel.index('aria-label="CorVIA Intelligence"')
    assert updates < fronts < intelligence
