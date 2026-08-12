"""Contratos de privacidade do Clinical OS que não dependem do navegador."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "frontend/src/components/ShellClinicalOSLaunch.tsx"
PAINEL = ROOT / "frontend/src/pages/PainelClinicalOS.tsx"
ASSISTENTE = ROOT / "frontend/src/components/PersonalAssistantPanel.tsx"


def test_contexto_recente_e_temporario_e_separado_por_usuario():
    shell = SHELL.read_text(encoding="utf-8")
    painel = PAINEL.read_text(encoding="utf-8")

    for fonte in (shell, painel):
        assert "sessionStorage" in fonte
        assert "corvia:contextos-recentes:${userId}" in fonte
        assert 'localStorage.getItem("corvia:contextos-recentes")' not in fonte
        assert 'localStorage.setItem("corvia:contextos-recentes"' not in fonte


def test_logout_remove_contexto_recente_somente_do_usuario_atual():
    fonte = SHELL.read_text(encoding="utf-8")

    inicio = fonte.index("async function encerrar()")
    chave = fonte.index("chaveContextosRecentes(usuario?.id)", inicio)
    remocao = fonte.index("sessionStorage.removeItem(chave)", inicio)
    logout = fonte.index("await sair()", inicio)
    assert inicio < chave < remocao < logout


def test_home_abre_assistente_pessoal_sem_transformar_em_rota_clinica():
    shell = SHELL.read_text(encoding="utf-8")
    painel = PAINEL.read_text(encoding="utf-8")

    evento = "corvia:abrir-assistente-pessoal"
    assert evento in painel
    assert evento in shell
    assert "setAssistente(true)" in shell


def test_dados_pessoais_so_sao_carregados_quando_assistente_esta_aberto():
    fonte = ASSISTENTE.read_text(encoding="utf-8")

    guarda = fonte.index("if (!aberto) return;")
    agenda = fonte.index('api.get<Agendamento[]>("/appointments")')
    mail = fonte.index('api.get<ResumoEmail>("/email/resumo")')
    assert guarda < agenda < mail
    assert "if (!aberto) return null;" in fonte


def test_geolocalizacao_exige_acao_explicita_e_mobilidade_autorizada():
    fonte = ASSISTENTE.read_text(encoding="utf-8")

    inicio_funcao = fonte.index("function atualizarDeslocamento()")
    preferencia_disponivel = fonte.index("if (!mobilidade)", inicio_funcao)
    preferencia_ativa = fonte.index("if (!mobilidade.enabled)", inicio_funcao)
    geolocalizacao = fonte.index("navigator.geolocation.getCurrentPosition", inicio_funcao)
    botao = fonte.index("onClick={atualizarDeslocamento}")
    assert inicio_funcao < preferencia_disponivel < preferencia_ativa < geolocalizacao < botao
    assert "automatic_foreground_refresh" in fonte  # preferência lida, não usada para disparar GPS
    assert fonte.count("navigator.geolocation.getCurrentPosition") == 1
