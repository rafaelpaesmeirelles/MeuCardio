from app.services.carregar_doencas_especializadas import _normalize_prevalence_rank


def test_prevalence_rank_null_e_omitido_para_preservar_existente_ou_default():
    item = {"slug": "exemplo", "prevalence_rank": None}

    error = _normalize_prevalence_rank(item, slug="exemplo")

    assert error is None
    assert "prevalence_rank" not in item


def test_prevalence_rank_positivo_e_preservado():
    item = {"slug": "exemplo", "prevalence_rank": 7}

    error = _normalize_prevalence_rank(item, slug="exemplo")

    assert error is None
    assert item["prevalence_rank"] == 7


def test_prevalence_rank_invalido_e_rejeitado_sem_normalizacao_silenciosa():
    for invalid in (0, -1, True, "7", 1.5):
        item = {"slug": "exemplo", "prevalence_rank": invalid}

        error = _normalize_prevalence_rank(item, slug="exemplo")

        assert error == "exemplo: prevalence_rank deve ser inteiro positivo ou null"
        assert item["prevalence_rank"] == invalid
