"""Contratos do painel Tudo com Tudo ancorado no medicamento."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MEDICAMENTOS = REPO_ROOT / "frontend/src/pages/MedicamentosClinicalCommand.tsx"
PAINEL = REPO_ROOT / "frontend/src/components/TudoSobreEsteTema.tsx"
BUSCA = REPO_ROOT / "frontend/src/pages/Busca.tsx"


def test_medicamento_nao_usa_farmacologia_generica_como_assunto():
    fonte = MEDICAMENTOS.read_text(encoding="utf-8")

    assert "medicamentoSlug={drug.slug}" in fonte
    assert 'tema="Farmacologia"' not in fonte


def test_painel_chama_rota_contextual_do_medicamento_e_separa_grupos():
    fonte = PAINEL.read_text(encoding="utf-8")

    assert "/relacionados/medicamento/" in fonte
    assert 'resposta.grupos.filter((g) => g.itens.length > 0)' in fonte
    assert "grupos.map((g)" in fonte
    assert "resposta.temas.map" in fonte
    assert "let ativo = true" in fonte and "if (ativo) setResposta(dados)" in fonte


def test_busca_ancora_medicamento_e_abre_cada_frente_na_rota_correta():
    fonte = BUSCA.read_text(encoding="utf-8")

    assert "/drugs?q=" in fonte
    assert "/drug-insights/" in fonte
    assert "brand_names?.some" in fonte
    assert '["Visão geral e características", "Fundamentos e conteúdo de referência", "/biblioteca"' in fonte
    assert '["Estudos", "Literatura original e trabalhos científicos", "/estudos"' in fonte
    assert '["Evidências", "Recomendações e níveis de evidência", "/evidencias"' in fonte
    assert '["Exames", "Diagnóstico, indicação e interpretação", "/exames"' in fonte
    assert '["Galeria clínica", "Imagens e achados relacionados", "/galeria"' in fonte
    for topico in ("Características", "Posologia e potência", "Indicações", "Segurança", "Timeline"):
        assert topico in fonte


def test_qualquer_assunto_e_organizado_sem_expandir_tema_amplo_por_inferencia():
    fonte = BUSCA.read_text(encoding="utf-8")

    for area in (
        "Visão geral e características",
        "Condutas e protocolos",
        "Diretrizes e consensos",
        "Fluxogramas",
        "Estudos",
        "Evidências",
        "Exames",
        "Galeria clínica",
    ):
        assert area in fonte
    assert "Tudo sobre ${assunto}" in fonte
    assert "/relacionados?tema=" in fonte
    assert ".find((x) => norm(x) === n)" in fonte
    assert "if (!medicamentoForte)" in fonte
    assert "new Set(itens.map" in fonte
    assert "temasUnicos.length === 1" not in fonte
