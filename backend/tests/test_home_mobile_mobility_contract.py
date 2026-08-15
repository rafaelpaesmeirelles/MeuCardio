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


def test_mobilidade_avancada_permanece_no_assistente_sem_redesenhar_home():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assistant = (ROOT / "frontend/src/components/PersonalAssistantPanel.tsx").read_text(encoding="utf-8")
    mobile_nav = (ROOT / "frontend/src/components/ClinicalMobileNav.tsx").read_text(encoding="utf-8")
    css = (ROOT / "frontend/src/styles/clinical-home-mobile-final.css").read_text(encoding="utf-8")
    endpoint = (ROOT / "backend/app/api/agenda_mobility_targeted.py").read_text(encoding="utf-8")

    # A mobilidade avançada continua funcional no Assistente/Agenda e no backend.
    assert 'item.appointment_id === proximo.id' in assistant
    assert 'resultado.destination?.appointment_id !== proximo.id' in assistant
    assert '"/agenda/mobility/commute-appointment"' in assistant

    # Coordenadas só entram na chamada ao provider; auditoria guarda provider/status.
    audit_start = endpoint.index("_audit(")
    audit_block = endpoint[audit_start:endpoint.index("db.commit()", audit_start)]
    assert '"latitude"' not in audit_block
    assert '"longitude"' not in audit_block

    # O painel autenticado volta à composição aprovada anterior ao enriquecimento.
    assert "<MapaDeslocamento" not in home
    assert "ccc-mobile-commute" not in home
    assert "ccc-home-fronts" not in home
    assert "Clínica & Decisão" not in home
    assert "Estudo & Aprendizagem" not in home
    assert "Trabalho & Assistência" not in home

    # Ordem mobile aprovada: Seu dia -> Assistente -> Atualizações.
    seu_dia = home.index("<small>Seu dia</small>")
    assistente = home.index("<small>Assistente</small>", seu_dia)
    atualizacoes = home.index("<small>Atualizações</small>", assistente)
    assert seu_dia < assistente < atualizacoes
    assert "<small>Deslocamento</small>" not in home[seu_dia:atualizacoes]

    # CSS final volta a ser somente a guarda de fidelidade da prancha mobile.
    assert "Final mobile fidelity against the approved HOME MOBILE board" in css
    assert ".ccc-home--board .ccc-updates-section { display: none !important; }" in css
    assert "ccc-mobile-commute" not in css

    # Bottom nav continua imutável.
    labels = ["Início", "Buscar", "Pacientes", "Agenda", "Mais"]
    posicoes = [mobile_nav.index(f"<span>{label}</span>") for label in labels]
    assert posicoes == sorted(posicoes)
    assert len(posicoes) == 5


def test_navegacao_reorganizada_sem_eliminar_funcoes_protegidas():
    desktop = (ROOT / "frontend/src/components/ClinicalDesktopNav.tsx").read_text(encoding="utf-8")
    mobile = (ROOT / "frontend/src/components/ClinicalMobileNav.tsx").read_text(encoding="utf-8")

    for fonte in (desktop, mobile):
        assert "Clínica & Decisão" in fonte
        assert "Estudo & Aprendizagem" in fonte
        assert "Trabalho & Assistência" in fonte
        for rota in (
            "/triagem-sintomas", "/interacoes", "/condicoes", "/fluxogramas",
            "/material-paciente", "/avaliacao-preoperatoria", "/telediagnostico",
            "/indicadores", "/galeria", "/cursos", "/apresentacao",
            "/usuarios-online", "/sincronizacao", "/exportar",
        ):
            assert rota in fonte

    for global_route in ("/assistente", "/favoritos", "/minha-conta", "/assinatura", "/tour"):
        assert global_route in desktop and global_route in mobile
