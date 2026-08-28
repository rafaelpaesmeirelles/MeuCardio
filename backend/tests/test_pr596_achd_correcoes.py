from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"


def _hub():
    return next(item for item in load_disease_records(BASE) if item["slug"] == "cardiopatia-congenita-do-adulto")


def _question(hub, question_id):
    return next(item for item in hub["assistant_questions"] if item["id"] == question_id)


def _rule(hub, rule_id):
    return next(item for item in hub["assistant_rules"] if item["id"] == rule_id)


def test_achd_revisado_e_autorizado():
    hub = _hub()
    note = hub["review_note"].casefold()
    assert hub["review_status"] == "revisado"
    assert "publicação autorizada" in note
    assert "responsável médico" in note


def test_cianose_e_eisenmenger_sao_estados_separados():
    hub = _hub()
    assert _question(hub, "cyanosis_eisenmenger")["label"] == "Há cianose/hipoxemia crônica documentada?"
    eisenmenger = _question(hub, "eisenmenger_documented")
    assert eisenmenger["required"] is True
    crisis = _rule(hub, "achd-eisenmenger-crise-cianotica")
    assert "eisenmenger_documented" in {item["field"] for item in crisis["when"]["all"]}
    non_eisenmenger = _rule(hub, "achd-cianose-cronica-piora-sem-eisenmenger")
    assert non_eisenmenger["add"]["risk"] == "urgente"


def test_fontan_reconhece_dispneia_ou_congestao():
    hub = _hub()
    rule = _rule(hub, "achd-fontan-descompensacao-aguda")
    values = {item["value"] for item in rule["when"]["any"]}
    assert values == {"dispneia_nova", "edema_ascite"}


def test_hemoptise_tem_fluxo_geral_e_eisenmenger_mais_especifico():
    hub = _hub()
    options = {item["value"] for item in _question(hub, "decompensation_symptoms")["options"]}
    assert "hemoptise" in options

    generic = _rule(hub, "achd-hemoptise-geral-sem-eisenmenger")
    assert generic["add"]["risk"] == "urgente"
    assert any(item["value"] == "hemoptise" for item in generic["when"]["all"])
    assert any(item["field"] == "eisenmenger_documented" for item in generic["when"]["none"])

    hemoptysis = _rule(hub, "achd-eisenmenger-hemoptise")
    assert hemoptysis["add"]["risk"] == "emergencia"
    assert "não iniciar, manter ou intensificar anticoagulação de forma automática" in " ".join(hemoptysis["add"]["emergency_flow"])


def test_gestacao_eisenmenger_nao_pode_ser_omitida():
    hub = _hub()
    pregnancy_status = _question(hub, "pregnancy_status")
    assert pregnancy_status["required"] is True
    assert "nao_aplicavel" in {item["value"] for item in pregnancy_status["options"]}

    current_pregnancy = _rule(hub, "achd-eisenmenger-gestacao-atual")
    assert current_pregnancy["add"]["risk"] == "urgente"
    preconception = _rule(hub, "achd-gravidez-alto-risco")
    assert "formalmente contraindicada" in " ".join(preconception["add"]["messages"])


def test_complexidade_anatomica_nao_e_chamada_de_estagio_fisiologico():
    hub = _hub()
    question = _question(hub, "lesion_complexity")
    labels = " ".join(item["label"] for item in question["options"]).casefold()
    assert "complexidade anatômica" in labels
    assert "estágio i" not in labels
    assert "estágio ii" not in labels
    assert "estágio iii" not in labels


def test_sincope_generica_e_urgente_mas_alto_risco_escala_para_emergencia():
    hub = _hub()
    generic = _rule(hub, "achd-sincope-alto-risco")
    assert generic["add"]["risk"] == "urgente"
    high_risk = _rule(hub, "achd-sincope-fisiologia-alto-risco")
    assert high_risk["add"]["risk"] == "emergencia"


def test_biopsia_hepatica_fontan_nao_e_rotina_de_vigilancia():
    hub = _hub()
    text = str(hub).casefold()
    assert "biópsia hepática não é método de vigilância rotineira" in text
    assert "biópsia é seletiva" in text
    assert "biópsia hepática permanece padrão-ouro para estadiamento em casos de dúvida" not in text


def test_diretriz_gestacao_2025_esta_na_proveniencia():
    hub = _hub()
    assert "40878294" in " ".join(hub["source_refs"])
