"""Contratos de privacidade do Clinical OS que não dependem do navegador."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "frontend/src/components/ShellClinicalOSLaunch.tsx"
PAINEL = ROOT / "frontend/src/pages/PainelClinicalOS.tsx"


def test_contexto_recente_e_temporario_e_separado_por_usuario():
    shell = SHELL.read_text(encoding="utf-8")
    painel = PAINEL.read_text(encoding="utf-8")

    for fonte in (shell, painel):
        assert "sessionStorage" in fonte
        assert "corvia:contextos-recentes:${userId}" in fonte
        assert 'localStorage.getItem("corvia:contextos-recentes")' not in fonte
        assert 'localStorage.setItem("corvia:contextos-recentes"' not in fonte


def test_home_abre_assistente_pessoal_sem_transformar_em_rota_clinica():
    shell = SHELL.read_text(encoding="utf-8")
    painel = PAINEL.read_text(encoding="utf-8")

    evento = "corvia:abrir-assistente-pessoal"
    assert evento in painel
    assert evento in shell
    assert "setAssistente(true)" in shell
