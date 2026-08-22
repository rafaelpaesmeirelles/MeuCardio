from pathlib import Path

from app.api import agenda_mobility_targeted as targeted


ROOT = Path(__file__).resolve().parents[2]


class _Query:
    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return object()


class _DB:
    def __init__(self):
        self.commits = 0

    def query(self, _model):
        return _Query()

    def commit(self):
        self.commits += 1


class _User:
    id = 77


def _destination(appointment_id: int, latitude: float, name: str) -> dict:
    return {
        "appointment_id": appointment_id,
        "routine_id": None,
        "starts_at": "2026-08-14T12:00:00+00:00",
        "ends_at": None,
        "service_name": "Consulta",
        "source": "appointment",
        "arrival_buffer_minutes": 15,
        "location": {
            "id": appointment_id + 100,
            "name": name,
            "address": {"city": "Ribeirão Preto"},
            "latitude": latitude,
            "longitude": -47.80,
        },
    }


def test_compromisso_a_nunca_recebe_rota_do_compromisso_b(monkeypatch):
    destinos = [_destination(1, -21.10, "Clínica A"), _destination(2, -21.20, "Clínica B")]
    chamadas = []
    auditoria = []

    monkeypatch.setattr(targeted, "next_locations", lambda **kwargs: destinos)

    def fake_traffic_eta(**kwargs):
        chamadas.append(kwargs)
        return {
            "status": "ok",
            "provider": "teste",
            "updated_at": "2026-08-13T12:00:00+00:00",
            "routes": [{
                "rank": 1,
                "duration_seconds": 1200,
                "traffic_delay_seconds": 180,
                "distance_meters": 11400 if kwargs["destination_latitude"] == -21.20 else 9900,
                "congestion": "moderado",
                "summary": "Rota real do provider",
            }],
            "tips": [],
        }

    monkeypatch.setattr(targeted, "traffic_eta", fake_traffic_eta)
    monkeypatch.setattr(targeted, "_audit", lambda db, user, action, resource, resource_id, metadata: auditoria.append(metadata))

    db = _DB()
    resposta = targeted.commute_appointment(
        targeted.CommuteAppointmentIn(latitude=-21.17, longitude=-47.81, appointment_id=2),
        db=db,
        user=_User(),
    )

    assert resposta["destination"]["appointment_id"] == 2
    assert resposta["destination"]["location"]["name"] == "Clínica B"
    assert chamadas[0]["destination_latitude"] == -21.20
    assert resposta["routes"][0]["distance_meters"] == 11400
    assert resposta["routes"][0]["traffic_delay_seconds"] == 180
    assert db.commits == 1
    assert auditoria == [{"provider": "teste", "status": "ok"}]
    assert "latitude" not in auditoria[0] and "longitude" not in auditoria[0]


def test_destination_mismatch_falha_fechado_sem_consultar_provider(monkeypatch):
    monkeypatch.setattr(targeted, "next_locations", lambda **kwargs: [_destination(1, -21.10, "Clínica A")])
    chamado = False

    def nao_deve_chamar(**kwargs):
        nonlocal chamado
        chamado = True
        raise AssertionError("provider não deve ser chamado em mismatch")

    monkeypatch.setattr(targeted, "traffic_eta", nao_deve_chamar)
    resposta = targeted.commute_appointment(
        targeted.CommuteAppointmentIn(latitude=-21.17, longitude=-47.81, appointment_id=2),
        db=_DB(),
        user=_User(),
    )

    assert resposta == {"status": "destination_mismatch", "destination": None, "routes": [], "tips": []}
    assert chamado is False


def test_home_mobile_mobilidade_e_privacidade_contract():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assistant = (ROOT / "frontend/src/components/PersonalAssistantPanel.tsx").read_text(encoding="utf-8")
    mobile_nav = (ROOT / "frontend/src/components/ClinicalMobileNav.tsx").read_text(encoding="utf-8")
    css = (ROOT / "frontend/src/styles/clinical-reference-board-final.css").read_text(encoding="utf-8")
    endpoint = (ROOT / "backend/app/api/agenda_mobility_targeted.py").read_text(encoding="utf-8")

    # Home e Assistente usam o mesmo alvo canônico e falham fechado pelo target_key exato.
    for source in (home, assistant):
        assert '"/agenda/mobility/prepare-next-target"' in source
        assert '"/agenda/mobility/next-target"' in source
        assert '"/agenda/mobility/commute-target"' in source
        assert "target_key" in source
        assert "destination?.target_key" in source
    assert 'resultado.destination?.target_key !== targetKey' in home
    assert 'resultado.destination?.target_key !== targetKey' in assistant

    # Disabled não deve alcançar geolocation; auto-refresh exige preferência e foreground.
    inicio_funcao = home.index("const calcularDeslocamento")
    fim_funcao = home.index("useEffect(() => {", inicio_funcao)
    funcao = home[inicio_funcao:fim_funcao]
    assert funcao.index("!mobilidade?.enabled") < funcao.index("navigator.geolocation")
    assert "mobilidade.automatic_foreground_refresh" in home
    assert "mobilidade.refresh_interval_minutes" in home
    assert 'document.visibilityState !== "visible"' in home
    assert 'document.addEventListener("visibilitychange"' in home
    assert "chamadaRotaEmCurso.current" in home

    # Estados e métricas vêm do retorno real, sem destino inventado.
    assert 'permissao === "negada"' in home
    assert 'Provider de trânsito indisponível' in home
    assert 'resultado.status: "destination_mismatch"' not in home
    assert "rota.distance_meters" in home
    assert "rota.traffic_delay_seconds" in home
    assert "rota.duration_seconds + destino.arrival_buffer_minutes * 60" in home
    assert "const saidaPlanejada" in home
    assert "const rotaAtualizadaEm = deslocamento?.updated_at" in home
    assert "Math.max(agora.getTime(), rotaAtualizadaEm.getTime())" in home
    assert "const rotaAtualizadaAgora" in home
    assert "saidaRecomendada.getTime() + rota.duration_seconds * 1000" in home
    assert "const destino = deslocamento &&" in home
    assert "const targetKey = destinoPlanejado?.target_key || null" in home
    assert 'target_type: "day_return"' in home

    # Coordenadas só entram na chamada ao provider; auditoria guarda provider/status.
    audit_start = endpoint.index("_audit(")
    audit_block = endpoint[audit_start:endpoint.index("db.commit()", audit_start)]
    assert '"latitude"' not in audit_block
    assert '"longitude"' not in audit_block

    # O mapa agora possui área obrigatória no Próximo Deslocamento inclusive mobile.
    assert "<MapaDeslocamento" in home
    assert "ccc-reference-commute__map" in home
    assert ".ccc-reference-commute__map" in css
    assert 'grid-template-areas: "head" "map" "details"' in css
    assert "min-height: 185px" in css

    # Ordem visual mobile canônica da prancha: Deslocamento -> Seu Dia -> Atualizações.
    assert '.ccc-reference-summary > .ccc-reference-commute { order: 1; }' in css
    assert '.ccc-reference-summary > .ccc-reference-day { order: 2; }' in css
    assert '.ccc-reference-summary > .ccc-reference-assistant-summary { order: 3; }' in css
    assert '.ccc-reference-summary > .ccc-reference-updates-summary { order: 4; }' in css

    # Bottom bar imutável, agora com o Prontuário como área clínica canônica.
    labels = ["Início", "Buscar", "Prontuário", "Agenda", "Mais"]
    posicoes = [mobile_nav.index(f"<span>{label}</span>") for label in labels]
    assert posicoes == sorted(posicoes)
    assert len(posicoes) == 5

    # A Home ganhou densidade sem apagar macroáreas nem Tudo com Tudo.
    for token in (
        "Clínica & Decisão", "Estudo & Aprendizagem", "Trabalho & Assistência",
        "Ferramentas & Produtividade", "Rede & Conectividade", "Administração & Conta",
        "Integração Tudo com Tudo",
    ):
        assert token in home


def test_navegacao_reorganizada_sem_eliminar_funcoes_protegidas():
    desktop = (ROOT / "frontend/src/components/ClinicalDesktopNav.tsx").read_text(encoding="utf-8")
    mobile = (ROOT / "frontend/src/components/ClinicalMobileNav.tsx").read_text(encoding="utf-8")

    for fonte in (desktop, mobile):
        assert "Clínica & Decisão" in fonte
        assert "Trabalho & Assistência" in fonte
        assert "Ferramentas & Produtividade" in fonte
        assert "Rede & Conectividade" in fonte
        for rota in (
            "/triagem-sintomas", "/interacoes", "/condicoes", "/fluxogramas",
            "/material-paciente", "/avaliacao-preoperatoria", "/telediagnostico",
            "/indicadores", "/galeria", "/cursos", "/apresentacao",
            "/usuarios-online", "/sincronizacao", "/exportar",
            "/assistente", "/favoritos", "/minha-conta", "/assinatura", "/tour",
        ):
            assert rota in fonte

    assert "Estudos & Educação" in desktop and "Estudos & Educação" in mobile
    assert "Administração" in desktop and "Administração & Conta" in mobile
