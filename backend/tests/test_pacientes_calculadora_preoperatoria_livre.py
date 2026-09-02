"""Parte 1/6 da correção coordenada de 02/09/2026: `patient_profile_id`
chegou nesta rodada em três pontos que antes só aceitavam nome digitado
livre — Calculadora ("gerar laudo"), Avaliação Pré-Operatória, e Prescrição
Especial — além do "Documento em Branco" (`documents.py`), que já aceitava
o campo mas não tinha teste dedicado com paciente vinculado. Mesma
infraestrutura de `test_pacientes_documento.py` (cadastro reutilizável,
`patient_profile_service.resolver_paciente_documento`), reaproveitada aqui
sem duplicar o que já está coberto lá (isolamento entre médicos, snapshot
congelado, variáveis de template)."""

from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _dar_assinatura_principal(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _criar_paciente(client, token, **overrides) -> dict:
    payload = {
        "full_name": "Beatriz Andrade Cardoso",
        "cpf": "987.654.321-00",
        "birth_date": "1975-03-12",
        "sex": "F",
        "phone": "(11) 98888-1111",
        "email": "beatriz@teste.local",
        "endereco": {},
    }
    payload.update(overrides)
    resposta = client.post("/api/pacientes", headers=_headers(token), json=payload)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


class TestCalculadoraComPacienteCadastrado:
    def test_gerar_documento_com_patient_profile_id_congela_snapshot(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/calculators/cha2ds2-vasc/gerar-documento", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"],
                "payload": {
                    "idade": 68, "sexo": "F", "icc": True, "hipertensao": True,
                    "avc_aits_tromboembolismo": False, "doenca_vascular": False, "diabetes": False,
                },
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_profile_id"] == paciente["id"]
        assert corpo["patient_name"] == "Beatriz Andrade Cardoso"

    def test_gerar_documento_sem_paciente_continua_com_nome_avulso(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/calculators/cha2ds2-vasc/gerar-documento", headers=_headers(token),
            json={
                "patient_name": "Nome avulso sem cadastro",
                "payload": {
                    "idade": 68, "sexo": "F", "icc": True, "hipertensao": True,
                    "avc_aits_tromboembolismo": False, "doenca_vascular": False, "diabetes": False,
                },
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_profile_id"] is None
        assert corpo["patient_name"] == "Nome avulso sem cadastro"

    def test_gerar_documento_com_paciente_de_outro_medico_e_rejeitado(self, client, db, criar_usuario):
        dono, token_dono = criar_usuario(email="dono-calc@teste.local")
        _dar_assinatura_principal(db, dono)
        paciente = _criar_paciente(client, token_dono)

        outro, token_outro = criar_usuario(email="outro-calc@teste.local")
        _dar_assinatura_principal(db, outro)

        resposta = client.post(
            "/api/calculators/cha2ds2-vasc/gerar-documento", headers=_headers(token_outro),
            json={
                "patient_profile_id": paciente["id"],
                "payload": {
                    "idade": 68, "sexo": "F", "icc": True, "hipertensao": True,
                    "avc_aits_tromboembolismo": False, "doenca_vascular": False, "diabetes": False,
                },
            },
        )
        assert resposta.status_code == 404, resposta.text


class TestAvaliacaoPreOperatoriaComPacienteCadastrado:
    def test_gerar_com_patient_profile_id_congela_snapshot(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/avaliacao-preoperatoria/gerar", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"],
                "procedimento_planejado": "Colecistectomia videolaparoscópica eletiva",
                "rcri": {
                    "cirurgia_alto_risco": True, "doenca_cardiaca_isquemica": False,
                    "icc": False, "doenca_cerebrovascular": False,
                    "diabetes_insulina": False, "creatinina_maior_2": False,
                },
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_profile_id"] == paciente["id"]
        assert corpo["patient_name"] == "Beatriz Andrade Cardoso"

    def test_gerar_com_paciente_de_outro_medico_e_rejeitado(self, client, db, criar_usuario):
        dono, token_dono = criar_usuario(email="dono-preop@teste.local")
        _dar_assinatura_principal(db, dono)
        paciente = _criar_paciente(client, token_dono)

        outro, token_outro = criar_usuario(email="outro-preop@teste.local")
        _dar_assinatura_principal(db, outro)

        resposta = client.post(
            "/api/avaliacao-preoperatoria/gerar", headers=_headers(token_outro),
            json={
                "patient_profile_id": paciente["id"],
                "procedimento_planejado": "Colecistectomia videolaparoscópica eletiva",
                "rcri": {
                    "cirurgia_alto_risco": True, "doenca_cardiaca_isquemica": False,
                    "icc": False, "doenca_cerebrovascular": False,
                    "diabetes_insulina": False, "creatinina_maior_2": False,
                },
            },
        )
        assert resposta.status_code == 404, resposta.text


class TestDocumentoLivreComEsemPaciente:
    def test_documento_livre_com_paciente_cadastrado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Anotação livre de teste",
                "corpo": "Corpo do documento livre de teste.",
                "patient_profile_id": paciente["id"],
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_profile_id"] == paciente["id"]
        assert corpo["patient_name"] == "Beatriz Andrade Cardoso"

    def test_documento_livre_sem_paciente_continua_funcionando(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={"titulo": "Anotação sem paciente", "corpo": "Corpo de teste."},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_profile_id"] is None
        assert corpo["patient_name"] is None


class TestPrescricaoEspecialComPacienteCadastrado:
    def test_criar_com_patient_profile_id_congela_snapshot(self, client, db, criar_usuario):
        from app.models.email_account import EmailAccount

        # Prescrição especial é uma lista nominal fechada por CorVIA Mail
        # (`_USUARIOS_ESPECIAIS` em prescricao_especial.py) — mesmo padrão de
        # setup de test_prescricao_especial.py.
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        db.add(EmailAccount(
            user_id=user.id, email_address="natalia@corvia.med.br",
            mail360_account_key=f"key-{user.id}", status="ativa",
        ))
        db.commit()
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/prescricao-especial", headers=_headers(token),
            json={
                "mode": "propria",
                "patient_name": "Nome digitado (ignorado quando ha cadastro)",
                "patient_profile_id": paciente["id"],
                "body": "Corpo de teste da prescrição especial.",
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_name"] == "Beatriz Andrade Cardoso"
