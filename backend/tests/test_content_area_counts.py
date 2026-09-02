from app.services.content_areas import matching_area_ids


def test_classifica_conteudo_pediatrico_e_neonatal_sem_perder_a_area_maior():
    areas = matching_area_ids(
        "Triagem neonatal de cardiopatia congênita crítica",
        "Cardiologia pediátrica",
        ["recém-nascido", "oximetria"],
    )

    assert {"pediatrica", "neonatal", "congenita"} <= areas


def test_classifica_acervos_especializados_pelos_vocabularios_do_banco():
    assert "cardiooncologia" in matching_area_ids("cardiooncologia", "terapia_alvo")
    assert "gestacao" in matching_area_ids("gravidez", "planejamento_reprodutivo")
    assert "geriatria" in matching_area_ids("cardiogeriatria", "fragilidade")
    assert "fetal" in matching_area_ids("cardiopediatria", "cardiologia_fetal")


def test_conteudo_adulto_sem_populacao_especializada_entra_em_cardiologia_geral():
    assert matching_area_ids("Insuficiência cardíaca", "monitorização ambulatorial") == {"geral"}


def test_cardiologia_geral_explicita_pode_coexistir_com_faceta_especializada():
    assert matching_area_ids("Cardiologia Geral", "Cardio-Oncologia") == {"geral", "cardiooncologia"}
