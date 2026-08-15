from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_candidate_hotfix_is_last_visual_override_before_form_contrast():
    main = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    hotfix_import = 'import "./styles/release-candidate-hotfix.css";'
    contrast_import = 'import "./styles/clinical-form-control-contrast.css";'
    assert hotfix_import in main
    assert main.index(hotfix_import) < main.index(contrast_import)


def test_post_86_review_regressions_are_explicitly_hardened():
    css = (ROOT / "frontend/src/styles/release-candidate-hotfix.css").read_text(encoding="utf-8")

    # Duplicate desktop Home search must not remain keyboard-focusable while hidden.
    assert ".ccc-home__main > .ccc-command" in css
    assert ".ccc-home__main > .ccc-examples" in css
    assert "display: none !important" in css

    # Compact desktop route preview must not expose a clipped full route chooser.
    assert ".ccc-reference-commute__map .deslocamento-rotas" in css
    assert "height: 238px !important" in css

    # Do not present journey duration as a countdown until recommended departure.
    assert ".ccc-reference-commute__route > span:first-child > p" in css

    # Authentication layout must remain inside the viewport at 821-939 px.
    assert "@media (min-width: 821px) and (max-width: 939px)" in css
    assert "grid-template-columns: minmax(0, 39%) minmax(0, 61%)" in css
