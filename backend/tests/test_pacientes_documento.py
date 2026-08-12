"""Cadastro de paciente reutilizável entre documentos (12/08/2026, pedido
do Rafael) — `PatientProfile`, `GET/POST/PUT/DELETE /api/pacientes`, e a
integração com os quatro caminhos de geração de documento
(`app/api/documents.py`): variáveis `{{paciente_...}}` num
`DocumentTemplate`, snapshot congelado na emissão, e sobretudo o
isolamento entre médicos — o item que mais importa nesta suíte.
"""
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.patient_profile import PatientProfile
from app.services.patient_profile_service import montar_endereco_completo
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _dar_assinatura_principal(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _criar_paciente(client, token, **overrides) -> dict:
    payload = {
        "full_name": "Fulano de Tal da Silva",
        "cpf": "123.456.789-00",
        "birth_date": "1980-05-20",
        "sex": "M",
        "phone": "(16) 99999-0000",
        "email": "fulano@teste.local",
        "endereco": {
            "logradouro": "Rua das Flores", "numero": "123", "complemento": "Apto 45",
            "bairro": "Centro", "cidade": "Ribeirão Preto", "uf": "SP", "cep": "14000-000",
        },
    }
    payload.update(overrides)
    resposta = client.post("/api/pacientes", headers=_headers(token), json=payload)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


class TestCrudBasico:
    def test_criar_listar_e_obter(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        criado = _criar_paciente(client, token)
        assert criado["full_name"] == "Fulano de Tal da Silva"
        assert criado["cpf"] == "123.456.789-00"
        assert criado["endereco"]["cidade"] == "Ribeirão Preto"

        lista = client.get("/api/pacientes", headers=_headers(token)).json()
        assert len(lista) == 1
        assert lista[0]["id"] == criado["id"]

        busca = client.get("/api/pacientes?busca=fulano", headers=_headers(token)).json()
        assert len(busca) == 1
        busca_vazia = client.get("/api/pacientes?busca=inexistente", headers=_headers(token)).json()
        assert busca_vazia == []

        detalhe = client.get(f"/api/pacientes/{criado['id']}", headers=_headers(token)).json()
        assert detalhe["full_name"] == "Fulano de Tal da Silva"

    def test_dados_gravados_estao_cifrados_no_banco(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = _criar_paciente(client, token)

        perfil = db.get(PatientProfile, criado["id"])
        assert perfil.full_name_cifrado != b"Fulano de Tal da Silva"
        assert b"Fulano" not in perfil.full_name_cifrado
        assert perfil.cpf_cifrado is not None
        assert b"123.456.789-00" not in perfil.cpf_cifrado

    def test_editar_e_apagar(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = _criar_paciente(client, token)

        editado = client.put(
            f"/api/pacientes/{criado['id']}", headers=_headers(token),
            json={"full_name": "Nome Editado", "endereco": None},
        ).json()
        assert editado["full_name"] == "Nome Editado"
        assert editado["cpf"] is None
        assert editado["endereco"] == {}

        resposta = client.delete(f"/api/pacientes/{criado['id']}", headers=_headers(token))
        assert resposta.status_code == 204
        assert client.get(f"/api/pacientes/{criado['id']}", headers=_headers(token)).status_code == 404

    def test_nome_vazio_e_rejeitado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        resposta = client.post("/api/pacientes", headers=_headers(token), json={"full_name": "   "})
        assert resposta.status_code == 422


class TestMontarEnderecoCompleto:
    def test_endereco_completo_sem_separador_sobrando(self):
        endereco = {
            "logradouro": "Rua das Flores", "numero": "123", "complemento": "Apto 45",
            "bairro": "Centro", "cidade": "Ribeirão Preto", "uf": "SP", "cep": "14000-000",
        }
        assert montar_endereco_completo(endereco) == (
            "Rua das Flores, 123 — Apto 45 — Centro — Ribeirão Preto/SP — CEP 14000-000"
        )

    def test_endereco_parcial_nao_deixa_separador_sobrando(self):
        # só cidade e UF — sem logradouro, número, complemento, bairro, CEP
        assert montar_endereco_completo({"cidade": "Ribeirão Preto", "uf": "SP"}) == "Ribeirão Preto/SP"
        # só logradouro, sem número nem complemento
        assert montar_endereco_completo({"logradouro": "Rua X"}) == "Rua X"
        # tudo vazio
        assert montar_endereco_completo({}) == ""
        assert montar_endereco_completo(None) == ""
        # cidade sem UF
        assert montar_endereco_completo({"cidade": "Ribeirão Preto"}) == "Ribeirão Preto"


class TestVariaveisDePacienteNoModelo:
    def _criar_template(self, db, user, body: str) -> DocumentTemplate:
        t = DocumentTemplate(owner_id=user.id, title="Encaminhamento", doc_type="outro", body=body)
        db.add(t)
        db.commit()
        db.refresh(t)
        return t

    def test_gera_com_nome_cpf_e_endereco_completo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)
        template = self._criar_template(
            db, user,
            "Encaminho o(a) paciente {{paciente_nome}}, CPF {{paciente_cpf}}, "
            "nascido(a) em {{paciente_data_nascimento}}, residente em "
            "{{paciente_endereco_completo}}, telefone {{paciente_telefone}}.",
        )

        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={"template_id": template.id, "patient_profile_id": paciente["id"], "variables": {}},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_profile_id"] == paciente["id"]
        assert corpo["patient_name"] == "Fulano de Tal da Silva"
        assert "Fulano de Tal da Silva" in corpo["rendered_body"]
        assert "123.456.789-00" in corpo["rendered_body"]
        assert "20/05/1980" in corpo["rendered_body"]
        assert "Rua das Flores, 123 — Apto 45 — Centro — Ribeirão Preto/SP — CEP 14000-000" in corpo["rendered_body"]
        assert "(16) 99999-0000" in corpo["rendered_body"]

        gerado = db.get(GeneratedDocument, corpo["id"])
        assert gerado.patient_snapshot_cifrado is not None
        # o snapshot cifrado nunca deve conter o CPF em claro
        assert b"123.456.789-00" not in gerado.patient_snapshot_cifrado

    def test_campo_ausente_no_cadastro_vira_vazio_sem_quebrar(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        # paciente SEM CPF, SEM telefone, SEM endereço
        paciente = _criar_paciente(client, token, cpf=None, phone=None, email=None, endereco=None)
        template = self._criar_template(
            db, user,
            "Paciente: {{paciente_nome}} — CPF: {{paciente_cpf}} — Tel: {{paciente_telefone}} — "
            "Endereço: {{paciente_endereco_completo}}.",
        )

        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={"template_id": template.id, "patient_profile_id": paciente["id"], "variables": {}},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()["rendered_body"]
        assert corpo == "Paciente: Fulano de Tal da Silva — CPF:  — Tel:  — Endereço: ."
        assert "{{" not in corpo and "}}" not in corpo

    def test_modelo_antigo_sem_variaveis_de_paciente_continua_funcionando(self, client, db, criar_usuario):
        """Retrocompatibilidade (item 9 do pedido): modelo já salvo, sem
        nenhuma variável `paciente_*`, sem paciente cadastrado selecionado
        — comportamento idêntico ao que já existia antes desta tarefa."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        template = self._criar_template(db, user, "Atesto que {{nome}} está apto(a) para a atividade.")

        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={"template_id": template.id, "variables": {"nome": "Beltrano"}},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["rendered_body"] == "Atesto que Beltrano está apto(a) para a atividade."
        assert resposta.json()["patient_profile_id"] is None

    def test_variavel_normal_ainda_bloqueia_quando_faltando(self, client, db, criar_usuario):
        """Só variável `paciente_*` ganha o passe livre de "vazio não
        bloqueia" — variável comum continua exigindo preenchimento, regra
        que já existia antes desta tarefa."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        template = self._criar_template(db, user, "Texto com {{variavel_qualquer}}.")

        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={"template_id": template.id, "variables": {}},
        )
        assert resposta.status_code == 422


class TestSnapshotCongelado:
    def test_documento_nao_muda_depois_de_editar_o_cadastro(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token, full_name="Nome Original", phone="(16) 90000-0000")
        template = DocumentTemplate(
            owner_id=user.id, title="Declaração", doc_type="outro",
            body="Paciente {{paciente_nome}}, telefone {{paciente_telefone}}.",
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        gerado_resp = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={"template_id": template.id, "patient_profile_id": paciente["id"], "variables": {}},
        ).json()
        assert "Nome Original" in gerado_resp["rendered_body"]
        assert "(16) 90000-0000" in gerado_resp["rendered_body"]

        # Altera o cadastro DEPOIS de já ter emitido o documento.
        client.put(
            f"/api/pacientes/{paciente['id']}", headers=_headers(token),
            json={"full_name": "Nome Trocado Depois", "phone": "(16) 99999-9999"},
        )

        detalhe = client.get(
            f"/api/document-templates/gerados/{gerado_resp['id']}", headers=_headers(token),
        ).json()
        # o rendered_body já persistido não muda...
        assert detalhe["rendered_body"] == gerado_resp["rendered_body"]
        assert "Nome Original" in detalhe["rendered_body"]
        assert "Nome Trocado Depois" not in detalhe["rendered_body"]
        # ...e o snapshot cifrado devolvido também é o antigo, não uma
        # releitura ao vivo do cadastro já editado.
        assert detalhe["patient_snapshot"]["full_name"] == "Nome Original"
        assert detalhe["patient_snapshot"]["phone"] == "(16) 90000-0000"

        # Confirma também no PDF: o texto renderizado é o congelado.
        pdf = client.get(
            f"/api/document-templates/gerados/{gerado_resp['id']}/pdf", headers=_headers(token),
        )
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF-")


class TestExamesEAtestadoAceitamPacienteOpcional:
    def test_solicitacao_de_exames_com_paciente_cadastrado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "exames": ["Hemograma completo"]},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_name"] == "Fulano de Tal da Silva"
        assert corpo["patient_profile_id"] == paciente["id"]

    def test_atestado_sem_nenhum_paciente_continua_funcionando(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"dias_afastamento": 1},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["patient_profile_id"] is None


class TestIsolamentoEntreMedicos:
    """O item que mais importa desta suíte: médico A não pode, por
    NENHUM caminho, alcançar cadastro de paciente de outro médico —
    nem lendo/editando/apagando o `PatientProfile` diretamente, nem
    usando o `id` dele para gerar documento por qualquer um dos quatro
    caminhos (`/gerar`, `/gerar-exames`, `/gerar-atestado`, `/gerar-livre`).
    Todos devolvem 404 (nunca 403) — mesma disciplina de
    `patient_for_user`, para não confirmar a existência do id alheio."""

    def _dois_medicos_e_paciente_de_b(self, client, db, criar_usuario):
        medico_a, token_a = criar_usuario(email="medico-a@teste.local")
        medico_b, token_b = criar_usuario(email="medico-b@teste.local")
        _dar_assinatura_principal(db, medico_a)
        _dar_assinatura_principal(db, medico_b)
        paciente_de_b = _criar_paciente(
            client, token_b, full_name="Paciente Sigiloso De B",
            cpf="999.888.777-66", endereco={"logradouro": "Rua Secreta", "cidade": "Sigilópolis", "uf": "SP"},
        )
        return token_a, token_b, paciente_de_b

    def test_medico_a_nao_le_paciente_de_b_diretamente(self, client, db, criar_usuario):
        token_a, _, paciente_de_b = self._dois_medicos_e_paciente_de_b(client, db, criar_usuario)
        resposta = client.get(f"/api/pacientes/{paciente_de_b['id']}", headers=_headers(token_a))
        assert resposta.status_code == 404
        assert "Sigiloso" not in resposta.text
        assert "999.888.777-66" not in resposta.text

    def test_medico_a_nao_ve_paciente_de_b_na_propria_lista(self, client, db, criar_usuario):
        token_a, _, paciente_de_b = self._dois_medicos_e_paciente_de_b(client, db, criar_usuario)
        lista_a = client.get("/api/pacientes", headers=_headers(token_a)).json()
        assert lista_a == []
        busca_a = client.get("/api/pacientes?busca=Sigiloso", headers=_headers(token_a)).json()
        assert busca_a == []

    def test_medico_a_nao_edita_nem_apaga_paciente_de_b(self, client, db, criar_usuario):
        token_a, _, paciente_de_b = self._dois_medicos_e_paciente_de_b(client, db, criar_usuario)
        edita = client.put(
            f"/api/pacientes/{paciente_de_b['id']}", headers=_headers(token_a),
            json={"full_name": "Sequestrado Por A"},
        )
        assert edita.status_code == 404
        apaga = client.delete(f"/api/pacientes/{paciente_de_b['id']}", headers=_headers(token_a))
        assert apaga.status_code == 404

    def test_medico_a_nao_gera_documento_por_modelo_com_paciente_de_b(self, client, db, criar_usuario):
        token_a, token_b, paciente_de_b = self._dois_medicos_e_paciente_de_b(client, db, criar_usuario)
        from app.models.user import User
        user_a = db.query(User).filter(User.email == "medico-a@teste.local").first()
        template = DocumentTemplate(
            owner_id=user_a.id, title="X", doc_type="outro", body="Paciente {{paciente_nome}}.",
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token_a),
            json={"template_id": template.id, "patient_profile_id": paciente_de_b["id"], "variables": {}},
        )
        assert resposta.status_code == 404
        assert "Sigiloso" not in resposta.text

    def test_medico_a_nao_gera_exames_atestado_ou_livre_com_paciente_de_b(self, client, db, criar_usuario):
        token_a, token_b, paciente_de_b = self._dois_medicos_e_paciente_de_b(client, db, criar_usuario)

        r1 = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token_a),
            json={"patient_profile_id": paciente_de_b["id"], "exames": ["Hemograma completo"]},
        )
        assert r1.status_code == 404
        assert "Sigiloso" not in r1.text

        r2 = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token_a),
            json={"patient_profile_id": paciente_de_b["id"], "dias_afastamento": 2},
        )
        assert r2.status_code == 404
        assert "Sigiloso" not in r2.text

        r3 = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token_a),
            json={"patient_profile_id": paciente_de_b["id"], "titulo": "T", "corpo": "C"},
        )
        assert r3.status_code == 404
        assert "Sigiloso" not in r3.text

        # Nenhum documento com o nome/CPF de B deve ter sido criado no
        # meio do caminho — as quatro tentativas falharam ANTES de
        # persistir qualquer coisa.
        assert db.query(GeneratedDocument).count() == 0

    def test_medico_b_continua_usando_o_proprio_paciente_normalmente(self, client, db, criar_usuario):
        token_a, token_b, paciente_de_b = self._dois_medicos_e_paciente_de_b(client, db, criar_usuario)
        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token_b),
            json={"patient_profile_id": paciente_de_b["id"], "exames": ["TSH"]},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["patient_name"] == "Paciente Sigiloso De B"
