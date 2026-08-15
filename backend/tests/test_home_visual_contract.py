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


def test_authenticated_home_is_full_panel_with_displacement_and_fronts():
    panel = _read("pages/PainelClinicalOS.tsx")
    css = _read("styles/clinical-home-mobile-final.css")

    for token in (
        'className="ccc-command"',
        'className="ccc-actions"',
        'className="ccc-mobile-summary"',
        'className="ccc-recent"',
        'className="ccc-updates"',
        'aria-label="CorVIA Intelligence"',
        'aria-label="Assistente Pessoal"',
        'ccc-home-fronts',
        'Clínica & Decisão',
        'Estudo & Aprendizagem',
        'Trabalho & Assistência',
        'Tudo com Tudo',
        'ccc-mobile-commute',
        '<MapaDeslocamento',
        '"/agenda/mobility/commute-appointment"',
    ):
        assert token in panel

    assert '.ccc-mobile-commute {' in css
    assert 'display: grid;' in css
    assert '.ccc-home--board .ccc-updates-section { display: block !important; }' in css


def test_mobile_home_contains_displacement_between_day_and_assistant():
    panel = _read("pages/PainelClinicalOS.tsx")
    start = panel.index('className="ccc-mobile-summary"')
    end = panel.index('className="ccc-section ccc-recent-section"')
    mobile = panel[start:end]

    seu_dia = mobile.index("Seu dia")
    deslocamento = mobile.index("Deslocamento")
    assistente = mobile.index("Assistente")
    atualizacoes = mobile.index("Atualizações")
    assert seu_dia < deslocamento < assistente < atualizacoes


def test_home_full_functions_are_not_removed_again():
    panel = _read("pages/PainelClinicalOS.tsx")
    for token in (
        'mobilidade.automatic_foreground_refresh',
        'mobilidade.refresh_interval_minutes',
        'document.visibilityState !== "visible"',
        'resultado.destination?.appointment_id !== proximo.id',
        'rota.distance_meters',
        'rota.traffic_delay_seconds',
        'rota.duration_seconds + destino.arrival_buffer_minutes * 60',
    ):
        assert token in panel
