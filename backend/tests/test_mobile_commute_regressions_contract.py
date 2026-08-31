"""Trava as três correções de mobile/deslocamento (PR fix/mobile-commute-regressions).

1. O mapa do Próximo Deslocamento preserva a instância do Google Maps entre
   atualizações de dados — o flicker vinha de recriar ``new google.maps.Map``
   a cada refresh de rota/origem, apagando os tiles por segundos e rebaixando
   tiles/API em todo ciclo.
2. O campo CHEGADA usa o referencial do compromisso (``scheduled_at`` menos o
   buffer de chegada do local), nunca "agora + duração" — que era um segundo
   referencial temporal misturado no mesmo card.
3. O card do Assistente permanece visível na Home MOBILE, na ordem canônica
   (… Seu dia → Assistente → Atualizações). Ocultá-lo é correto apenas no
   desktop (min-width: 901px), onde o rail lateral dedicado existe.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_mapa_preserva_instancia_entre_atualizacoes():
    mapa = (ROOT / "frontend/src/components/MapaDeslocamento.tsx").read_text(encoding="utf-8")
    # Uma única criação de mapa em todo o componente; atualizações redesenham
    # sobre a MESMA instância (refs), nunca reinstanciam.
    assert mapa.count("new google.maps.Map(") == 1
    assert "mapaInstanciaRef" in mapa
    assert "preserva a instância entre atualizações de dados" in mapa
    assert "sobreposicoesRef" in mapa
    # fitBounds só quando a geometria realmente muda — sem "pulos" de viewport.
    assert "assinaturaEnquadramento" in mapa


def test_chegada_usa_referencial_do_compromisso():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assert "new Date(proximo.scheduled_at).getTime() - destino.arrival_buffer_minutes * 60000" in home
    # A fórmula antiga ("updated_at/agora + duração") não pode voltar.
    assert "Date.now()) + rota.duration_seconds" not in home
    # A SAÍDA recomendada preexistente permanece intacta.
    assert "rota.duration_seconds + destino.arrival_buffer_minutes * 60" in home


def test_assistente_visivel_na_home_mobile_na_ordem_canonica():
    board = (ROOT / "frontend/src/styles/clinical-reference-board-final.css").read_text(encoding="utf-8")
    fidelity = (ROOT / "frontend/src/styles/clinical-reference-fidelity-release.css").read_text(encoding="utf-8")
    # Nenhuma LINHA pode ocultar o card do Assistente (a regra desktop legítima
    # oculta via seletor em linha própria, sem display na mesma linha).
    for nome, css in (("board-final", board), ("fidelity-release", fidelity)):
        for linha in css.splitlines():
            if "display: none" in linha and ("assistant-summary" in linha or "card--assistant" in linha):
                raise AssertionError(f"card do Assistente oculto indevidamente em {nome}: {linha.strip()}")
    # Ordem canônica do mobile: Deslocamento(1) → Seu dia(2) → Assistente(3) → Atualizações(4).
    assert ".ccc-reference-summary > .ccc-reference-assistant-summary { order: 3; }" in board
    assert ".ccc-reference-summary > .ccc-reference-updates-summary { order: 4; }" in board


def test_menu_sem_duplicidade_de_interacoes():
    """Uma única entrada canônica de Interações no menu: "Interações medicamentosas".

    A duplicação ("Interações" + "Interações medicamentosas", ambas → /interacoes)
    confundia o menu lateral. A rota /interacoes é única e canônica — nenhum alias
    é necessário; o guard impede a volta da duplicata e o rótulo antigo.
    """
    import re

    for arquivo in ("frontend/src/components/ClinicalDesktopNav.tsx",
                    "frontend/src/components/ClinicalMobileNav.tsx"):
        fonte = (ROOT / arquivo).read_text(encoding="utf-8")
        entradas = re.findall(r'to:\s*"/interacoes",\s*label:\s*"([^"]+)"', fonte)
        assert entradas == ["Interações medicamentosas"], (
            f"{arquivo}: esperado exatamente 1 entrada '/interacoes' rotulada "
            f"'Interações medicamentosas'; encontrado {entradas}"
        )
        # o rótulo curto legado não pode voltar como item de navegação
        assert 'label: "Interações"' not in fonte, (
            f"{arquivo}: rótulo legado 'Interações' reapareceu no menu"
        )


def test_header_mobile_composto():
    """Header mobile: logo à esquerda, busca no centro, 1º nome + avatar à direita.

    O canonical ocultava a busca e as ações no mobile (centro vazio, conta sem
    nome). A camada mobile-header-composed reexibe busca e identidade com
    ellipsis. Pelo item 9: SEM hambúrguer no topo mobile (navegação principal é
    a barra inferior / "Mais") e só o PRIMEIRO nome ao lado do avatar; o
    desktop segue com o nome completo.
    """
    main = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    css = (ROOT / "frontend/src/styles/mobile-header-composed.css").read_text(encoding="utf-8")
    shell = (ROOT / "frontend/src/components/ShellClinicalOSLaunch.tsx").read_text(encoding="utf-8")
    assert 'import "./styles/mobile-header-composed.css";' in main
    # antes do form-control-contrast (que precisa seguir por último)
    assert main.index("mobile-header-composed.css") < main.index("clinical-form-control-contrast.css")
    assert ".clinical-os .cos-command-mini" in css and "display: flex !important" in css
    assert ".clinical-os .cos-account__identity" in css
    assert "text-overflow: ellipsis" in css
    # item 9: hambúrguer fora do topo mobile — e nada no lugar dele
    assert ".clinical-os .cos-topbar__menu { display: none !important; }" in css
    assert "display: grid !important; order: 3" not in css  # a regra que o reexibia não pode voltar
    # item 9/29: tratamento cadastrado + nome curto no mobile e tratamento +
    # nome completo no desktop.
    assert "cos-account__nome-curto" in shell and "cos-account__nome-completo" in shell
    assert 'import { nomeComTratamento } from "../lib/clinicalIdentity";' in shell
    assert "nomeComTratamento(usuario, true)" in shell
    assert "nomeComTratamento(usuario)" in shell
    assert ".cos-account__nome-curto { display: none; }" in css  # default desktop
    assert ".clinical-os .cos-account__nome-completo { display: none; }" in css  # mobile
    # A extração e o tratamento ficam centralizados na identidade clínica,
    # evitando regras divergentes entre desktop, mobile e documentos.
    identidade = (ROOT / "frontend/src/lib/clinicalIdentity.ts").read_text(encoding="utf-8")
    assert "professional_title" in identidade
    assert "curto ? nomeSemTitulo.split" in identidade


def test_css_de_pagina_entra_no_bundle():
    """As folhas *-v2 usadas por páginas reais PRECISAM estar no main.tsx.

    Causa raiz da paleta quebrada em /interacoes: clinical-interactions-v2.css
    existia no repositório mas nunca era importado — a página renderizava a
    metade inferior sem estilo (chips/cards brancos do user-agent sobre o
    dark). O mesmo valia para tools/exams/guidelines.
    """
    main = (ROOT / "frontend/src/main.tsx").read_text(encoding="utf-8")
    for folha in ("clinical-interactions-v2.css", "clinical-tools-v2.css",
                  "clinical-exams-v2.css", "clinical-guidelines-v2.css"):
        assert f'import "./styles/{folha}";' in main, f"{folha} fora do bundle"
    # form-control-contrast continua sendo o último import de estilos
    posicoes = [main.index(f'import "./styles/{f}";') for f in (
        "clinical-interactions-v2.css", "clinical-form-control-contrast.css")]
    assert posicoes[0] < posicoes[1], "cascata violada: interactions após form-control-contrast"


def test_mapa_preenche_area_no_desktop():
    """O mapa ocupa toda a área reservada no card (desktop).

    shell.css monta .deslocamento-painel como grid de 2 colunas (mapa +
    seletor de rotas); no desktop o seletor é oculto pelo hotfix, mas a
    trilha vazia ficava reservada (~350px mortos à direita). O painel vira
    display:block dentro do frame do card — mesmo padrão do mobile.
    """
    fidelity = (ROOT / "frontend/src/styles/clinical-reference-fidelity-release.css").read_text(encoding="utf-8")
    assert ".ccc-reference-board .ccc-reference-commute__map .deslocamento-painel" in fidelity
    assert "display: block !important" in fidelity
    assert ".ccc-reference-board .ccc-reference-commute__map .deslocamento-mapa__google" in fidelity


def test_identidade_de_navegador_canonica():
    """Aba/PWA usam a identidade canônica CorVIA — Cardiology Spaces.

    O título legado ("Corvia — O caminho do coração") e o favicon antigo não
    podem voltar à identidade de NAVEGADOR (title/favicon/manifest/metas).
    A assinatura "O caminho do coração" permanece permitida em superfícies de
    marca aprovadas fora do navegador (ex.: alt de logo em documentos).
    """
    index = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
    vite = (ROOT / "frontend/vite.config.ts").read_text(encoding="utf-8")

    assert "<title>CorVIA — Cardiology Spaces</title>" in index
    assert "O caminho do coração" not in index
    assert "Corvia —" not in index  # grafia legada na identidade de navegador
    assert '<link rel="icon" type="image/svg+xml" href="/corvia-mark-canonical.svg" />' in index
    assert 'property="og:title" content="CorVIA — Cardiology Spaces"' in index
    assert 'content="#03101A"' in index  # theme-color alinhado ao manifest

    # Manifest PWA canônico e sem referências mortas de assets.
    assert '"CorVIA — Cardiology Spaces"' in vite or "'CorVIA — Cardiology Spaces'" in vite
    assert "logo-horizontal.png" not in vite and "brasao.png" not in vite
    for asset in ("corvia-mark-canonical.svg", "favicon.png", "apple-touch-icon.png",
                  "icon-192.png", "icon-512.png", "icon-maskable.png"):
        assert (ROOT / "frontend/public" / asset).is_file(), f"asset ausente: {asset}"


def test_parent_nao_recria_referencias_identicas():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    # Guardas de identidade: origem e alvo só trocam de referência quando o
    # conteúdo muda — evita invalidar deps e redesenhar o mapa à toa.
    assert "atual.latitude === origemAtual.latitude" in home
    assert "JSON.stringify(atual) === JSON.stringify(resultado.destination)" in home
