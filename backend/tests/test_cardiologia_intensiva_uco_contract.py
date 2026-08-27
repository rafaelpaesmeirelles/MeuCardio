"""Contrato auditável do cockpit de Cardiologia Intensiva e UCO."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def _texto(caminho: str) -> str:
    return (FRONTEND / caminho).read_text(encoding="utf-8")


def test_rota_e_lazy_loading_estao_registrados():
    app = _texto("App.tsx")

    assert 'lazy(() => import("./pages/CardiologiaIntensiva"))' in app
    assert 'path="cardiologia-intensiva"' in app


def test_modulo_esta_nas_navegacoes_canonicas():
    arquivos = [
        "components/ClinicalDesktopNav.tsx",
        "components/ClinicalMobileNav.tsx",
        "components/ShellClinicalOSLaunch.tsx",
        "pages/PainelClinicalOS.tsx",
    ]

    for arquivo in arquivos:
        conteudo = _texto(arquivo)
        assert "/cardiologia-intensiva" in conteudo, arquivo
        assert "Cardiologia Intensiva & UCO" in conteudo, arquivo


def test_cockpit_carrega_colecoes_em_paralelo_e_usa_tema_canonico():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert 'const TEMA = "Terapia intensiva"' in pagina
    assert "Promise.all([" in pagina
    assert "/library/documents?theme=" in pagina
    assert 'api.get<Calculadora[]>("/calculators")' in pagina
    assert 'api.get<Checklist[]>("/checklists")' in pagina
    assert "<TudoSobreEsteTema tema={TEMA}" in pagina


def test_cockpit_preserva_gates_humanos_e_nao_promete_prescricao_automatica():
    pagina = _texto("pages/CardiologiaIntensiva.tsx")

    assert "nenhuma estação substitui protocolo local" in pagina
    assert "ainda não há prescrição automática de antibióticos" in pagina
    assert "decisão final preservada pelo médico" in pagina
