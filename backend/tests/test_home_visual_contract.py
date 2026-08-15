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


def test_authenticated_home_keeps_approved_board_composition():
    panel = _read("pages/PainelClinicalOS.tsx")

    # Estrutura aprovada da prancha: comando, ações rápidas, resumo móvel,
    # continuidade, atualizações e os dois rails. Não reintroduzir a Home
    # "enriquecida" que alterou a composição sem aprovação.
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

    assert 'ccc-mobile-commute' not in panel
    assert 'MapaDeslocamento' not in panel
    assert 'ccc-home-fronts' not in panel


def test_mobile_home_summary_order_matches_approved_board():
    panel = _read("pages/PainelClinicalOS.tsx")
    start = panel.index('className="ccc-mobile-summary"')
    end = panel.index('className="ccc-section ccc-recent-section"')
    mobile = panel[start:end]

    seu_dia = mobile.index("Seu dia")
    assistente = mobile.index("Assistente")
    atualizacoes = mobile.index("Atualizações")
    assert seu_dia < assistente < atualizacoes
    assert "Deslocamento" not in mobile


def test_mobile_home_css_is_the_approved_fidelity_guard_not_enrichment_layer():
    css = _read("styles/clinical-home-mobile-final.css")
    assert "Final mobile fidelity against the approved HOME MOBILE board" in css
    assert ".ccc-home--board .ccc-updates-section { display: none !important; }" in css
    assert "ccc-mobile-commute" not in css
    assert "MapaDeslocamento" not in css
