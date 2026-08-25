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


def test_busca_ancora_medicamento_e_abre_cada_frente_na_rota_correta():
    fonte = BUSCA.read_text(encoding="utf-8")

    assert "/drugs?q=" in fonte
    assert "/drug-insights/" in fonte
    assert 'titulo: "Visão geral e características"' in fonte and 'rota: "/biblioteca"' in fonte
    assert 'titulo: "Estudos"' in fonte and 'rota: "/estudos"' in fonte
    assert 'titulo: "Evidências"' in fonte and 'rota: "/evidencias"' in fonte
    assert 'titulo: "Exames"' in fonte and 'rota: "/exames"' in fonte
    assert 'titulo: "Galeria clínica"' in fonte and 'rota: "/galeria"' in fonte
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
    assert "Tudo sobre ${termoBuscado}" in fonte
    assert "/relacionados?tema=" in fonte
    assert "const temaCanonico = temaExato ?? null" in fonte
    assert "temasUnicos.length === 1" not in fonte
