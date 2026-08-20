from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CSS_FILE_CEILING = 74
GLOBAL_STYLE_IMPORT_CEILING = 59
IMPORTANT_CEILING = 1504
DEBT_LAYER_NAME_CEILING = 22


def test_frontend_style_debt_does_not_grow():
    css_files = sorted((ROOT / "frontend" / "src").rglob("*.css"))
    assert len(css_files) <= CSS_FILE_CEILING

    main = (ROOT / "frontend" / "src" / "main.tsx").read_text(encoding="utf-8")
    imports = len(re.findall(r'import\s+["\']\./styles/[^"\']+\.css["\'];', main))
    assert imports <= GLOBAL_STYLE_IMPORT_CEILING

    important = sum(path.read_text(encoding="utf-8").count("!important") for path in css_files)
    assert important <= IMPORTANT_CEILING

    debt_names = ("hotfix", "fidelity", "final", "canonical", "release")
    debt_layers = sum(1 for path in css_files if any(term in path.name.lower() for term in debt_names))
    assert debt_layers <= DEBT_LAYER_NAME_CEILING
