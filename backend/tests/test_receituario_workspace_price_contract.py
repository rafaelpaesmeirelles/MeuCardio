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
    # A decisão aprovada é exibir o menor PMC publicado por apresentação,
    # não uma faixa entre alíquotas nem um suposto preço de varejo.
    assert "somaPrecosMaximos" not in page
    assert 'total + (it.price_min ?? it.pmc_snapshot ?? 0)' in page
    assert 'formatarPreco(somaPrecosMinimos) : "Sem preço vinculado"' in page
    assert 'if (item.price_source === "kairos") return formatarPreco(item.price_min);' in page
    assert 'Menor PMC publicado para cada apresentação, entre as alíquotas da edição.' in page
    assert 'não é uma oferta de farmácia' in page
    kairos_selection = page.split('function escolherApresentacaoKairos(', 1)[1].split('function voltarParaGenerico(', 1)[0]
    for contract in (
        'manufacturer: ap.laboratorio', 'apresentacao: ap.apresentacao',
        'price_source: "kairos"', 'price_min: ap.preco_minimo',
        'price_reference: `edição ${fonte.edicao} · competência ${fonte.competencia}`',
        'price_source_page: ap.pagina_fonte ?? undefined',
        'pmc_snapshot: undefined', 'cmed_version: undefined',
    ):
        assert contract in kairos_selection
    assert "precoCmedExibivel" in page
    assert 'preco.fonte_icms === "media_nacional_nao_verificada"' in page
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
