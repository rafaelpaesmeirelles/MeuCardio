from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_receituario_workspace_uses_audited_kairos_price_without_changing_shell():
    page = (ROOT / "frontend/src/pages/Receituario.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "frontend/src/styles/shell.css").read_text(encoding="utf-8")

    assert 'className="prescricao-workspace"' in page
    assert 'className="prescricao-resumo"' in page
    assert "princípio ativo ou marca" in page
    assert "K@iros · edição" in page
    assert "CMED/ANVISA permanece a referência regulatória oficial" in page
    assert "formatarFaixaPreco" in page
    assert "somaPrecosMinimos" in page
    assert "somaPrecosMaximos" in page
    assert "precoCmedExibivel" in page
    assert "Preço não disponível para esta UF" in page
    assert "verificação humana" not in page.lower()
    assert "/receituario/enderecos/cep/" in page
    assert "setBairro" in page
    assert "setCidade" in page
    assert "setUf" in page
    assert ".prescricao-workspace" in styles
    assert ".prescricao-sugestao__preco" in styles
    assert ".prescricao-resumo" in styles

    # A página central não cria navegação paralela nem troca a identidade
    # canônica do shell — desktop e mobile continuam sob os componentes
    # globais aprovados.
    assert "ClinicalDesktopNav" not in page
    assert "ClinicalMobileNav" not in page
    assert "corvia-logo" not in page
