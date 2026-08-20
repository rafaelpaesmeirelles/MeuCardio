from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_mail_navigation_has_one_user_facing_entry():
    for path in ("frontend/src/components/ClinicalDesktopNav.tsx", "frontend/src/components/ClinicalMobileNav.tsx"):
        src = text(path)
        assert 'to: "/corvia-mail", label: "CorVIA Mail"' in src
        assert 'to: "/caixa-de-email", label: "CorVIA Mail"' not in src
        assert 'label: "Caixa de e-mail"' not in src

def test_mail_bulk_delete_is_real():
    src = text("frontend/src/pages/CaixaDeEmailProfessional.tsx")
    assert "async function excluirSelecionadas" in src
    assert "Promise.all(ids.map" in src
    assert "if (ids.length === 1)" not in src

def test_connected_accounts_are_automatic_and_removable():
    src = text("frontend/src/pages/Sincronizacao.tsx")
    assert "Sincronizar agora" not in src
    assert "sincronizarConta" not in src
    assert "Remover conta" in src
    assert "manutenção automática" in src

def test_public_validation_page_is_wired_before_auth_gates():
    src = text("frontend/src/App.tsx")
    assert 'location.pathname.startsWith("/validar/")' in src
    assert '<Route path="/validar/:codigo" element={<ValidarDocumento />}' in src

def test_legacy_brand_sources_removed_from_reported_pages():
    for path in ("frontend/src/pages/TermosUso.tsx", "frontend/src/pages/PoliticaPrivacidade.tsx", "frontend/src/pages/TourClinicalOS.tsx"):
        assert "/corvia-logo-compacta.png" not in text(path)

def test_tour_has_no_broken_user_avatar_tile():
    src = text("frontend/src/pages/TourClinicalOS.tsx")
    assert "cos-tour-welcome__avatar" not in src
    assert "fotoFalhou" not in src

def test_prescription_selected_product_has_explicit_contrast():
    src = text("frontend/src/styles/clinical-form-control-contrast.css")
    assert ".clinical-os .prescricao-selecao" in src
    assert "#f4fdff" in src
