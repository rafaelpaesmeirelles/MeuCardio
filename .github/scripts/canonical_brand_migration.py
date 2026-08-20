from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_exact(path: str, old: str, new: str, expected: int) -> None:
    content = read(path)
    count = content.count(old)
    if count != expected:
        raise RuntimeError(f"{path}: expected {expected} occurrences of {old!r}, found {count}")
    write(path, content.replace(old, new))


# 1) Legacy shell: point directly to the canonical mark instead of depending on CSS content:url.
replace_exact(
    "frontend/src/components/ShellClinicalOSLaunch.tsx",
    "/logo-marca.png",
    "/corvia-mark-canonical.svg",
    3,
)

# 2) Public/legal surfaces on light backgrounds: canonical wordmark.
replace_exact(
    "frontend/src/pages/TermosUso.tsx",
    "/corvia-logo-compacta.png",
    "/corvia-logo-canonical.svg",
    1,
)
replace_exact(
    "frontend/src/pages/PoliticaPrivacidade.tsx",
    "/corvia-logo-compacta.png",
    "/corvia-logo-canonical.svg",
    1,
)
replace_exact(
    "frontend/src/pages/Produto.tsx",
    "/corvia-logo-compacta.png",
    "/corvia-logo-canonical.svg",
    3,
)

# 3) Tour: full wordmark only in the main header; mark in compact UI mockups.
tour_path = "frontend/src/pages/TourClinicalOS.tsx"
tour = read(tour_path)
for old, new in (
    (
        '<span className="cos-tour-mock__brand"><img src="/corvia-logo-compacta.png" alt="" /></span>',
        '<span className="cos-tour-mock__brand"><img src="/corvia-mark-canonical.svg" alt="" /></span>',
    ),
    (
        '<header><img src="/corvia-logo-compacta.png" alt=""/><Icone nome="menu"/></header>',
        '<header><img src="/corvia-mark-canonical.svg" alt=""/><Icone nome="menu"/></header>',
    ),
    (
        '<div className="cos-tour__brand"><img src="/corvia-logo-compacta.png" alt="CorVIA"/><span><strong>CorVIA</strong><small>Clinical OS do médico</small></span></div>',
        '<div className="cos-tour__brand"><img src="/corvia-logo-canonical-dark.svg" alt="CorVIA Clinical OS"/></div>',
    ),
    (
        '<span className="cos-tour-final__mark"><img src="/corvia-logo-compacta.png" alt="" /></span>',
        '<span className="cos-tour-final__mark"><img src="/corvia-mark-canonical.svg" alt="" /></span>',
    ),
):
    count = tour.count(old)
    if count != 1:
        raise RuntimeError(f"{tour_path}: expected 1 exact fragment, found {count}: {old[:90]}")
    tour = tour.replace(old, new)
write(tour_path, tour)

# 4) Remove runtime asset swapping from the shell branding CSS.
write(
    "frontend/src/styles/canonical-brand-standard.css",
    textwrap.dedent(
        """\
        /* Identidade canônica no shell: os componentes apontam diretamente para o símbolo aprovado. */
        .cos-brand__mark img,.cos-topbar__mobile-brand img,.cos-drawer__head img{object-fit:contain}
        """
    ),
)

# 5) Preserve current approved tour geometry without hiding/replacing assets with CSS.
write(
    "frontend/src/styles/tour-branding-hotfix.css",
    textwrap.dedent(
        """\
        /* Tour CorVIA — branding canônico direto, sem troca de asset em runtime. */
        .cos-tour__brand > img {
          display: block;
          width: clamp(150px, 18vw, 210px);
          height: 48px;
          object-fit: contain;
          object-position: left center;
        }

        @media (min-width: 701px) and (max-width: 1180px) {
          .cos-tour__top {
            grid-template-columns: minmax(170px, 1fr) auto minmax(100px, 1fr);
            gap: .75rem;
            padding-inline: 1.25rem;
          }
          .cos-tour__brand > img {
            width: 180px;
            height: 44px;
          }
        }

        @media (max-width: 700px) {
          .cos-tour__brand > img {
            width: 142px;
            height: 38px;
          }
        }
        """
    ),
)

# 6) Add a regression contract so direct legacy references and branding CSS swaps cannot return.
brand_test_path = "backend/tests/test_canonical_branding_contract.py"
brand_test = read(brand_test_path)
marker = "def test_frontend_sources_do_not_reference_legacy_brand_assets_or_runtime_swaps():"
if marker not in brand_test:
    brand_test += textwrap.dedent(
        """


        def test_frontend_sources_do_not_reference_legacy_brand_assets_or_runtime_swaps():
            frontend = ROOT / "frontend" / "src"
            source = "\n".join(
                path.read_text(encoding="utf-8")
                for path in frontend.rglob("*")
                if path.is_file() and path.suffix in {".ts", ".tsx", ".css", ".html"}
            )
            assert "/logo-marca.png" not in source
            assert "/corvia-logo-compacta.png" not in source

            shell_brand_css = _read("frontend/src/styles/canonical-brand-standard.css")
            tour_brand_css = _read("frontend/src/styles/tour-branding-hotfix.css")
            assert "content:url" not in shell_brand_css.replace(" ", "")
            assert "content:url" not in tour_brand_css.replace(" ", "")
            assert "display: none !important" not in tour_brand_css
        """
    )
    write(brand_test_path, brand_test)

# 7) Freeze the current stylesheet debt as a ceiling. Future approved cleanup can lower these constants.
css_files = sorted((ROOT / "frontend" / "src").rglob("*.css"))
important_count = sum(path.read_text(encoding="utf-8").count("!important") for path in css_files)
main_source = read("frontend/src/main.tsx")
global_imports = len(re.findall(r'import\s+["\']\./styles/[^"\']+\.css["\'];', main_source))
debt_names = ("hotfix", "fidelity", "final", "canonical", "release")
debt_layers = sum(1 for path in css_files if any(term in path.name.lower() for term in debt_names))

budget_test = textwrap.dedent(
    f"""\
    from pathlib import Path
    import re

    ROOT = Path(__file__).resolve().parents[2]
    CSS_FILE_CEILING = {len(css_files)}
    GLOBAL_STYLE_IMPORT_CEILING = {global_imports}
    IMPORTANT_CEILING = {important_count}
    DEBT_LAYER_NAME_CEILING = {debt_layers}


    def test_frontend_style_debt_does_not_grow():
        css_files = sorted((ROOT / "frontend" / "src").rglob("*.css"))
        assert len(css_files) <= CSS_FILE_CEILING

        main = (ROOT / "frontend" / "src" / "main.tsx").read_text(encoding="utf-8")
        imports = len(re.findall(r'import\\s+["\\\']\\./styles/[^"\\\']+\\.css["\\\'];', main))
        assert imports <= GLOBAL_STYLE_IMPORT_CEILING

        important = sum(path.read_text(encoding="utf-8").count("!important") for path in css_files)
        assert important <= IMPORTANT_CEILING

        debt_names = ("hotfix", "fidelity", "final", "canonical", "release")
        debt_layers = sum(1 for path in css_files if any(term in path.name.lower() for term in debt_names))
        assert debt_layers <= DEBT_LAYER_NAME_CEILING
    """
)
write("backend/tests/test_frontend_style_debt_budget.py", budget_test)

# Final safety checks for this migration.
frontend_source = "\n".join(
    path.read_text(encoding="utf-8")
    for path in (ROOT / "frontend" / "src").rglob("*")
    if path.is_file() and path.suffix in {".ts", ".tsx", ".css", ".html"}
)
for legacy in ("/logo-marca.png", "/corvia-logo-compacta.png"):
    if legacy in frontend_source:
        raise RuntimeError(f"legacy branding reference remains: {legacy}")

print(
    "Canonical branding migration complete: "
    f"css_files={len(css_files)}, global_imports={global_imports}, "
    f"important={important_count}, debt_layers={debt_layers}"
)
