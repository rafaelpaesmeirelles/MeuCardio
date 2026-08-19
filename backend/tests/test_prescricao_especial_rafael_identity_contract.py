from app.api import prescricao_especial


def test_autorizacao_privilegiada_nao_usa_nome_ou_crm():
    names = prescricao_especial._eh_rafael.__code__.co_names
    assert "normalize_search_text" not in names
