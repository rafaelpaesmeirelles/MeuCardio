from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_home_e_assistente_usam_o_mesmo_alvo_canonico():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assistant = (ROOT / "frontend/src/components/PersonalAssistantPanel.tsx").read_text(encoding="utf-8")
    endpoint = (ROOT / "backend/app/api/agenda_mobility_targeted.py").read_text(encoding="utf-8")

    for fonte in (home, assistant):
        assert '"/agenda/mobility/prepare-next-target"' in fonte
        assert '"/agenda/mobility/commute-target"' in fonte
        assert 'target_key: targetKey' in fonte
        assert 'resultado.destination?.target_key !== targetKey' in fonte

    assert '"/agenda/workday/next-locations?limit=10"' not in home
    assert '"/agenda/mobility/commute-appointment"' not in home
    assert '@router.post("/mobility/prepare-next-target")' in endpoint
    assert '@router.post("/mobility/commute-target")' in endpoint
    assert '_commitment_occurrences' in endpoint
    assert '"source": "commitment"' in endpoint


def test_home_nao_pede_origem_antes_do_consentimento_e_nao_bloqueia_geocode_do_destino():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    endpoint = (ROOT / "backend/app/api/agenda_mobility_targeted.py").read_text(encoding="utf-8")

    inicio = home.index("const calcularDeslocamento")
    fim = home.index("useEffect(() => {", inicio)
    funcao = home[inicio:fim]

    assert funcao.index("!mobilidade?.enabled") < funcao.index("navigator.geolocation")
    assert 'destino.location.latitude == null || destino.location.longitude == null) return' not in funcao
    assert 'permissao !== "concedida"' in funcao
    assert "mobilidade.automatic_foreground_refresh" in home
    assert 'document.visibilityState !== "visible"' in home
    assert 'document.addEventListener("visibilitychange"' in home

    assert 'geocode_address(query)' in endpoint
    assert 'mobility_destination_geocode' in endpoint
    assert 'target = _ensure_geocoded(db, user, target)' in endpoint


def test_mapa_do_destino_existe_no_mobile_e_no_rail_desktop_antes_da_rota():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    mapa = (ROOT / "frontend/src/components/MapaDeslocamento.tsx").read_text(encoding="utf-8")
    board_css = (ROOT / "frontend/src/styles/clinical-home-board-fidelity.css").read_text(encoding="utf-8")

    assert "destinoMapeavel" in home
    assert 'provider={provedorMapa}' in home
    assert 'ccc-reference-commute__map' in home
    assert 'ccc-assistant-commute-map' in home
    assert '.ccc-assistant-commute-map' in board_css
    # Os aliases oficiais usam a mesma cartografia; um destino válido pode
    # abrir o canvas antes de haver rota, geometria ou posição de origem.
    assert '["google maps", "google_maps", "google_routes"].includes((provider || "").toLowerCase())' in mapa
    assert 'const validDestination = coordinateValid(destino.latitude, destino.longitude);' in mapa
    assert 'const googleCanvas = isGoogle && Boolean(googleMapsApiKey) && validDestination;' in mapa
    assert 'aria-label={`Mapa ${activeGeometry ? "do percurso até" : "do destino"} ${destino.name}`}' in mapa
    assert '{googleCanvas ? <>' in mapa
    assert '<div ref={canvasRef} className="deslocamento-mapa__google" />' in mapa

    # A Home Atelier usa o mesmo mapa no diálogo, inclusive com rotas vazias;
    # a prévia compacta não precisa carregar cartografia antes da interação.
    atelier = (ROOT / "frontend/src/pages/CardiologySpacesHome.tsx").read_text(encoding="utf-8")
    assert '{travelDestination ? <div className="spaces-travel__map">' in atelier
    assert 'rotas={resultMatchesTarget ? mobilityResult?.routes || [] : []}' in atelier
    assert 'destino={travelDestination}' in atelier


def test_prancha_e_navegacao_mobile_permanecem_canonicas_com_p1():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    mobile = (ROOT / "frontend/src/components/ClinicalMobileNav.tsx").read_text(encoding="utf-8")

    assert 'ccc-reference-board' in home
    assert 'ccc-actions-section' in home
    assert 'ccc-reference-summary' in home
    assert 'ccc-module-directory' in home
    assert 'CorVIA Cardiology Spaces' in home
    assert 'Tudo com Tudo' in home

    labels = ["Início", "Buscar", "Prontuário", "Agenda", "Mais"]
    posicoes = [mobile.index(f"<span>{label}</span>") for label in labels]
    assert posicoes == sorted(posicoes)
    assert 'className="cc-mobile-more__assistant"' in mobile
    assert "Assistente Pessoal" in mobile
    assert 'to: "/assistente", label: "Assistente Clínica"' in mobile
