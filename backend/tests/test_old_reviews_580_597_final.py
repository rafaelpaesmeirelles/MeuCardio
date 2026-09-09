from pathlib import Path

from app.services.disease_manifest import load_disease_records


BASE = Path(__file__).resolve().parents[2] / "doencas" / "metadados.json"


def _records():
    return {item["slug"]: item for item in load_disease_records(BASE)}


def _by_id(items):
    return {item["id"]: item for item in items}


def test_pr580_aorta_preserva_bav_pau_links_e_fontes_primarias():
    hub = _records()["doenca-da-aorta"]
    treatment = hub["treatment_summary"]
    diameter_items = " ".join(
        hub["diagnostic_approach"][
            "cortes_de_diametro_do_aneurisma_toracico_por_etiologia_esc_2024"
        ]
    )

    assert "doenca-arterial-periferica-e-aortica-paad-diretriz-combinada-esc-2024" in hub[
        "related_document_slugs"
    ]
    assert "tipo B assintomática e não complicada" in treatment
    assert "características de imagem de alto risco" in treatment
    assert "Valva bicúspide, fenótipo ascendente" in diameter_items
    assert "a partir de 50 mm" in diameter_items
    assert "crescimento ≥3 mm/ano" in diameter_items
    refs = " ".join(hub["source_refs"])
    for pmid in ("38904579", "40480617", "42389778"):
        assert pmid in refs


def test_pr590_tmcs_e_seletivo_e_nao_disparado_por_scai_ou_48_horas():
    hub = _records()["choque-cardiogenico"]

    assert "o estágio SCAI isolado não seleciona dispositivo" in hub["summary"]
    assert "sem escolha automática de dispositivo pelo estágio SCAI" in hub["emergency_flow"][3]
    assert "não constitui indicação automática" in hub["monitoring"][1]
    assert "quando prolongado além de 48 horas" not in hub["monitoring"][1]


def test_pr594_lvad_nao_atrasa_estabilizacao_local():
    hub = _records()["insuficiencia-cardiaca-avancada"]
    rule = _by_id(hub["assistant_rules"])["ica-avancada-lvad-trombose"]

    assert "o contato não deve atrasar a estabilização" in hub["emergency_flow"][0]
    assert "contatar em paralelo" in rule["add"]["emergency_flow"][0]
    assert "não deve retardar tratamento" in rule["add"]["emergency_flow"][0]


def test_pr596_alerta_contraceptivo_exige_exposicao_real_a_estrogenio():
    hub = _records()["cardiopatia-congenita-do-adulto"]
    question = _by_id(hub["assistant_questions"])["contraception_contains_estrogen"]
    rule = _by_id(hub["assistant_rules"])["achd-contracepcao-estrogenio"]

    assert question["type"] == "boolean"
    assert question["required"] is False
    assert {
        "field": "contraception_contains_estrogen",
        "op": "truthy",
    } in rule["when"]["all"]
    assert all(condition["field"] != "pregnancy_status" for condition in rule["when"]["all"])


def test_pr597_nao_aceita_omissao_de_causas_e_nao_mantem_esquema_automaticamente():
    hub = _records()["hipertensao-resistente-e-refrataria"]
    question = _by_id(hub["assistant_questions"])["secondary_cause_investigated"]
    white_coat = _by_id(hub["assistant_rules"])["har-avental-branco"]
    refs_and_urls = " ".join(hub["source_refs"] + hub["source_urls"])

    assert question["required"] is True
    message = white_coat["add"]["messages"][0]
    assert "Não intensificar" in message
    assert "manter esquema atual" not in message
    for marker in (
        "40267417",
        "40587141",
        "29803589",
        "29803590",
        "P220023",
        "21816315",
        "H130007",
    ):
        assert marker.lower() in refs_and_urls.lower()
