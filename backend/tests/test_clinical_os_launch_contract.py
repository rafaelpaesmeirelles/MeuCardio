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
PAINEL = LAUNCH_FILES[2]
TOUR = LAUNCH_FILES[-1]
MOBILE_NAV = ROOT / "frontend/src/components/ClinicalMobileNav.tsx"


def test_launch_preserva_taxonomia_aprovada_dos_assistentes():
    painel = PAINEL.read_text(encoding="utf-8")
    tour = TOUR.read_text(encoding="utf-8")

    # A nomenclatura aprovada usa CorVIA IA como ação rápida que abre a
    # Assistente Clínica. Isso é distinto do Assistente Pessoal da Home e do
    # CorVIA Chat, que permanece produto de comunicação profissional.
    assert 'titulo: "CorVIA IA"' in painel
    assert 'detalhe: "Assistente Clínica"' in painel
    assert "Assistente Pessoal" in painel
    assert "CorVIA Chat" in tour


def test_mobile_preserva_assistente_pessoal_sem_alterar_bottom_bar_aprovada():
    mobile = MOBILE_NAV.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")

    # A bottom bar aprovada acompanha a área canônica de Prontuário.
    labels = ["Início", "Buscar", "Prontuário", "Agenda", "Mais"]
    positions = [mobile.index(f"<span>{label}</span>") for label in labels]
    assert positions == sorted(positions)

    # O Assistente Pessoal não some: fica acessível no menu Mais e aciona o
    # controlador real do Shell, enquanto /assistente continua Assistente Clínica.
    assert 'className="cc-mobile-more__assistant"' in mobile
    assert "Assistente Pessoal" in mobile
    assert 'document.querySelector<HTMLButtonElement>(".cos-assistant-sidebar")?.click();' in mobile
    assert 'to: "/assistente", label: "Assistente Clínica"' in mobile
    assert 'className="cos-assistant-sidebar"' in shell
    assert "setAssistente(true)" in shell


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
