from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"


def _hub():
    return next(item for item in load_disease_records(BASE) if item["slug"] == "insuficiencia-cardiaca-avancada")


def _question(hub, question_id):
    return next(item for item in hub["assistant_questions"] if item["id"] == question_id)


def _rule(hub, rule_id):
    return next(item for item in hub["assistant_rules"] if item["id"] == rule_id)


def test_ic_avancada_revisada_e_autorizada():
    hub = _hub()
    assert hub["review_status"] == "revisado"
    assert "publicação autorizada" in hub["review_note"]
    assert "responsável médico" in hub["review_note"]


def test_gates_de_lvad_e_transplante_exigem_contexto_correto():
    hub = _hub()
    assert _question(hub, "lvad_alarm_or_hemolysis")["required"] is True
    assert _question(hub, "suspected_rejection_signs")["required"] is True

    lvad = _rule(hub, "ica-avancada-lvad-trombose")
    assert {item["field"] for item in lvad["when"]["all"]} == {"lvad_carrier", "lvad_alarm_or_hemolysis"}

    rejection = _rule(hub, "ica-avancada-suspeita-rejeicao")
    assert {item["field"] for item in rejection["when"]["all"]} == {"heart_transplant_recipient", "suspected_rejection_signs"}
    flow = " ".join(rejection["add"]["emergency_flow"]).casefold()
    assert "sem atrasar estabilização" in flow
    assert "biópsia" in flow


def test_tcpe_submaximo_nao_inverte_interpretacao():
    hub = _hub()
    text = str(hub).casefold()
    assert "pode fazer a limitação funcional parecer mais grave" in text
    assert "teste submáximo subestima a gravidade real" not in text


def test_hospitalizacao_recorrente_e_alerta_nao_diagnostico_isolado():
    hub = _hub()
    rule = _rule(hub, "ica-avancada-hospitalizacoes-recorrentes")
    text = " ".join(rule["add"]["red_flags"]).casefold()
    assert "sinal de alerta" in text
    assert "não diagnóstico isolado" in text


def test_fontes_momentum3_e_decide_lvad_estao_na_proveniencia():
    hub = _hub()
    refs = " ".join(hub["source_refs"])
    assert "30883052" in refs
    assert "29482225" in refs
