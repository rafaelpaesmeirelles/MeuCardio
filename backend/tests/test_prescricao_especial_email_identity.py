from app.api import prescricao_especial


def test_aliases_de_login_do_rafael_sao_fechados_e_estaveis():
    assert prescricao_especial._Rafael_LOGIN_EMAILS == {
        "rafael@cardiobeneribeirao.com.br",
        "rafael@corvia.med.br",
    }
