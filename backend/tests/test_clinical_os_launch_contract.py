"""Contratos estáticos da superfície de lançamento do Clinical OS."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAUNCH_FILES = [
    ROOT / "frontend/src/components/ShellClinicalOSLaunch.tsx",
    ROOT / "frontend/src/components/PersonalAssistantPanel.tsx",
    ROOT / "frontend/src/pages/PainelClinicalOS.tsx",
    ROOT / "frontend/src/pages/TourClinicalOS.tsx",
]
A11Y = ROOT / "frontend/src/styles/clinical-os-a11y.css"
SHELL = LAUNCH_FILES[0]
TOUR = LAUNCH_FILES[-1]


def test_launch_expoe_um_unico_nome_para_o_assistente():
    for caminho in LAUNCH_FILES:
        fonte = caminho.read_text(encoding="utf-8")
        assert "CorVIA AI" not in fonte, caminho

    tour = TOUR.read_text(encoding="utf-8")
    assert "CorVIA Chat" in tour  # comunicação profissional continua sendo produto separado


def test_tour_nao_posiciona_corvia_como_prontuario_e_identifica_dados_de_mock():
    tour = TOUR.read_text(encoding="utf-8")

    assert "Não é só prontuário" not in tour
    assert "Não é prontuário." in tour
    assert "exemplo ilustrativo" in tour


def test_drawer_e_assistente_tem_empilhamento_deterministico_e_abertura_exclusiva():
    css = A11Y.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")

    assert ".cos-drawer-backdrop { z-index: 110; }" in css
    assert ".cos-drawer { z-index: 120; }" in css
    assert ".cos-assistant-backdrop { z-index: 130; }" in css
    assert ".cos-assistant-panel { z-index: 140; }" in css

    assert "setAssistente(false); setConta(false); setDrawer(true);" in shell
    assert "setDrawer(false); setConta(false); setAssistente(true);" in shell
    assert "setDrawer(false); setAssistente(true);" in shell


def test_drawer_movel_prende_foco_e_devolve_ao_disparador():
    shell = SHELL.read_text(encoding="utf-8")

    assert "drawerRef = useRef<HTMLElement>(null)" in shell
    assert "fecharDrawerRef = useRef<HTMLButtonElement>(null)" in shell
    assert "disparadorDrawerRef = useRef<HTMLElement | null>(null)" in shell
    assert 'if (evento.key !== "Tab") return;' in shell
    assert "document.activeElement === primeiro" in shell
    assert "document.activeElement === ultimo" in shell
    assert "requestAnimationFrame(() => fecharDrawerRef.current?.focus())" in shell
    assert "requestAnimationFrame(() => disparadorDrawerRef.current?.focus())" in shell
    assert 'if (evento.key === "Escape")' in shell
