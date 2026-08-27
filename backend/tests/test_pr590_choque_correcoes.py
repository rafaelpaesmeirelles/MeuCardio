from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"


def _hub():
    return next(item for item in load_disease_records(BASE) if item["slug"] == "choque-cardiogenico")


def _question(hub, question_id):
    return next(item for item in hub["assistant_questions"] if item["id"] == question_id)


def _rule(hub, rule_id):
    return next(item for item in hub["assistant_rules"] if item["id"] == rule_id)


def test_choque_revisado_e_autorizado_para_publicacao():
    hub = _hub()
    assert hub["review_status"] == "revisado"
    assert "publicação autorizada" in hub["review_note"]
    assert "responsável médico" in hub["review_note"]


def test_hipoperfusao_nao_exige_hipotensao_e_complicacao_mecanica_e_separada():
    hub = _hub()
    label = _question(hub, "hypoperfusion_signs")["label"].casefold()
    assert "independentemente da pressão arterial" in label
    options = {item["value"]: item["label"] for item in _question(hub, "shock_etiology")["options"]}
    assert "complicacao_mecanica_pos_iam" in options
    assert "sem complicação mecânica" in options["isquemica_iam"].casefold()
    mechanical = _rule(hub, "choque-cardiogenico-complicacao-mecanica-pos-iam")
    assert mechanical["add"]["risk"] == "emergencia"
    assert any("ecocardiograma urgente" in text.casefold() for text in mechanical["add"]["suggested_tests"])


def test_deterioracao_respeita_suporte_ja_instalado_e_nao_escolhe_dispositivo_por_scai():
    hub = _hub()
    no_mcs = _rule(hub, "choque-cardiogenico-refratario-deterioracao")
    assert {item["field"] for item in no_mcs["when"]["all"]} == {"deterioration_despite_support", "current_mcs"}
    text = " ".join(no_mcs["add"]["emergency_flow"]).casefold()
    assert "não selecionar dispositivo pelo estágio scai isolado" in text

    on_mcs = _rule(hub, "choque-cardiogenico-deterioracao-em-mcs")
    text = " ".join(on_mcs["add"]["emergency_flow"]).casefold()
    assert "não recomendar automaticamente adicionar iabp, impella ou ecmo" in text
    assert "complicações do dispositivo" in text


def test_falencia_vd_usa_otimizacao_de_preload_sem_reflexo_de_volume():
    hub = _hub()
    text = str(hub).casefold()
    assert "otimizar preload" in text
    assert "evitando tanto expansão reflexa quanto restrição reflexa" in text
    assert "restringir, não expandir, volume" not in text


def test_fontes_terapeuticas_primarias_foram_incorporadas():
    hub = _hub()
    refs = " ".join(hub["source_refs"])
    for pmid in ("34347952", "22920912", "38587239", "37634145", "41324946"):
        assert pmid in refs
