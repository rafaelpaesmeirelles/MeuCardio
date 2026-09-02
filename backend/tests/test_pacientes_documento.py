"""Cadastro de paciente reutilizável entre documentos (12/08/2026, pedido
do Rafael) — `PatientProfile`, `GET/POST/PUT/DELETE /api/pacientes`, e a
integração com os quatro caminhos de geração de documento
(`app/api/documents.py`): variáveis `{{paciente_...}}` num
`DocumentTemplate`, snapshot congelado na emissão, e sobretudo o
isolamento entre médicos — o item que mais importa nesta suíte.
"""
import shutil
import subprocess

import pytest

from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.patient_profile import PatientProfile
from app.services.patient_profile_service import montar_endereco_completo
from app.models.subscription import Subscription


def _texto_do_pdf(pdf_bytes: bytes) -> str:
    """Extrai o texto visível de um PDF via `pdftotext` (poppler-utils) —
    prova que a identificação do paciente está no PDF DE VERDADE, não só no
    `rendered_body` do JSON: PDFs gerados pelo reportlab comprimem os
    streams de conteúdo (FlateDecode), então o texto não aparece em claro
    nos bytes brutos."""
    resultado = subprocess.run(
        ["pdftotext", "-", "-"], input=pdf_bytes, capture_output=True, check=True,
    )
    return resultado.stdout.decode("utf-8")


_TEM_PDFTOTEXT = shutil.which("pdftotext") is not None


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


class TestAtestadoESolicitacaoExamesIdentificacaoNoCorpo:
    """02/09/2026, terceira rodada: mesmo defeito confirmado em Atestado e
    Solicitação de Exames — `patient_profile_id` era gravado, mas o corpo
    não identificava o paciente (exames: nenhuma linha; atestado: a frase
    "acima identificado(a)" sem nada acima). Reaproveita
    `_com_identificacao_prefixada`, o mesmo ponto único já usado pelo
    Documento em Branco — nunca confia em nome/CPF/nascimento vindo do
    cliente quando há `patient_profile_id`."""

    # --- Atestado ---

    def test_atestado_com_cadastro_completo_tem_identificacao_no_corpo_e_no_pdf(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        rendered_body = corpo["rendered_body"]
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF: 123.456.789-00" in rendered_body
        assert "Data de nascimento: 20/05/1980" in rendered_body
        assert "acima identificado(a)" in rendered_body

        if _TEM_PDFTOTEXT:
            pdf = client.get(
                f"/api/document-templates/gerados/{corpo['id']}/pdf", headers=_headers(token),
            )
            assert pdf.status_code == 200, pdf.text
            texto = _texto_do_pdf(pdf.content)
            assert "Paciente: Fulano de Tal da Silva" in texto
            assert "CPF: 123.456.789-00" in texto
            assert "Data de nascimento: 20/05/1980" in texto

    def test_atestado_cadastro_sem_cpf_nem_nascimento_nao_gera_linha_vazia(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token, cpf=None, birth_date=None)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3},
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF:" not in rendered_body
        assert "Data de nascimento:" not in rendered_body

    def test_atestado_com_nome_avulso_preserva_comportamento_anterior(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_name": "Ciclano Avulso", "dias_afastamento": 3},
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert "Ciclano Avulso" in rendered_body
        assert "Paciente:" not in rendered_body  # nome avulso continua só embutido na frase, como antes
        assert resposta.json()["patient_profile_id"] is None

    def test_atestado_cid_ausente_nao_aparece(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3},
        )
        assert "CID" not in resposta.json()["rendered_body"]

    def test_atestado_cid_informado_aparece_exatamente_como_antes(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3, "cid": "M54.5"},
        )
        assert "CID: M54.5" in resposta.json()["rendered_body"]

    def test_atestado_com_paciente_de_outro_medico_e_rejeitado(self, client, db, criar_usuario):
        dono, token_dono = criar_usuario(email="dono-atestado@teste.local")
        _dar_assinatura_principal(db, dono)
        paciente = _criar_paciente(client, token_dono)

        outro, token_outro = criar_usuario(email="outro-atestado@teste.local")
        _dar_assinatura_principal(db, outro)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token_outro),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3},
        )
        assert resposta.status_code == 404

    # --- Solicitação de Exames ---

    def test_exames_com_cadastro_completo_tem_identificacao_e_preserva_exames(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "exames": ["Hemograma completo", "TSH"]},
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF: 123.456.789-00" in rendered_body
        assert "Data de nascimento: 20/05/1980" in rendered_body
        assert "- Hemograma completo" in rendered_body
        assert "- TSH" in rendered_body

    def test_exames_cadastro_incompleto_sem_linha_vazia(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token, cpf=None, birth_date=None)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "exames": ["Hemograma completo"]},
        )
        rendered_body = resposta.json()["rendered_body"]
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF:" not in rendered_body
        assert "Data de nascimento:" not in rendered_body

    def test_exames_com_nome_avulso_preserva_comportamento_anterior(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_name": "Ciclano Avulso", "exames": ["Hemograma completo"]},
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert "Paciente: Ciclano Avulso" in rendered_body
        assert resposta.json()["patient_profile_id"] is None

    def test_exames_com_paciente_de_outro_medico_e_rejeitado(self, client, db, criar_usuario):
        dono, token_dono = criar_usuario(email="dono-exames@teste.local")
        _dar_assinatura_principal(db, dono)
        paciente = _criar_paciente(client, token_dono)

        outro, token_outro = criar_usuario(email="outro-exames@teste.local")
        _dar_assinatura_principal(db, outro)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token_outro),
            json={"patient_profile_id": paciente["id"], "exames": ["Hemograma completo"]},
        )
        assert resposta.status_code == 404

    # --- Gerais: snapshot, recriar, assinatura ---

    def test_atestado_e_exames_snapshot_congelado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        for rota, payload in (
            ("/api/document-templates/gerar-atestado", {"patient_profile_id": paciente["id"], "dias_afastamento": 1}),
            ("/api/document-templates/gerar-exames", {"patient_profile_id": paciente["id"], "exames": ["ECG"]}),
        ):
            resposta = client.post(rota, headers=_headers(token), json=payload)
            gerado_id = resposta.json()["id"]
            gerado = db.get(GeneratedDocument, gerado_id)
            assert gerado.patient_profile_id == paciente["id"]
            assert gerado.patient_snapshot_cifrado is not None

    def test_atestado_recriar_baseado_neste_nao_duplica_identificacao(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3},
        )
        gerado_id = resposta.json()["id"]
        detalhe = client.get(
            f"/api/document-templates/gerados/{gerado_id}", headers=_headers(token),
        ).json()
        # As variáveis estruturadas do atestado não guardam texto de
        # identificação nenhum — "recriar baseado neste" reconstrói o corpo
        # do zero a partir delas mais o paciente escolhido de novo, nunca
        # duplicando uma identificação já congelada.
        assert "Paciente:" not in str(detalhe["variables"])

    @pytest.mark.skipif(not _TEM_PDFTOTEXT, reason="pdftotext (poppler-utils) não disponível neste ambiente")
    def test_assinatura_nao_remove_identificacao_do_pdf(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "exames": ["Hemograma completo"]},
        )
        gerado_id = resposta.json()["id"]

        pdf = client.get(
            f"/api/document-templates/gerados/{gerado_id}/pdf?metodo=MANUAL", headers=_headers(token),
        )
        assert pdf.status_code == 200, pdf.text
        texto = _texto_do_pdf(pdf.content)
        assert "Paciente: Fulano de Tal da Silva" in texto


def _corpo_final_exames_como_o_navegador_envia(nome: str | None, exames: list[str]) -> str:
    """Reproduz exatamente `montarCorpoExames()` de Templates.tsx — o
    preview que o navegador REAL monta e manda como `corpo_final`. Só
    inclui o nome (nunca CPF/nascimento, que o cliente não conhece)."""
    linhas = []
    if nome:
        linhas += [f"Paciente: {nome}", ""]
    linhas += ["Solicito a realização dos seguintes exames:", ""]
    linhas += [f"- {e}" for e in exames]
    return "\n".join(linhas)


def _corpo_final_atestado_como_o_navegador_envia(nome: str, dias: int) -> str:
    """Reproduz exatamente a montagem de `origem === "atestado"` em
    Templates.tsx — nome sempre embutido na frase, nunca numa linha
    "Paciente:" própria."""
    return (
        f"Atesto, para os devidos fins, que o(a) paciente {nome} necessita de "
        f"afastamento de suas atividades habituais por {dias} dia(s)."
    )


class TestCorpoFinalDoNavegadorPreservaIdentificacao:
    """02/09/2026, terceira rodada: `corpo_final` (o preview que o
    navegador REAL sempre manda para Exames/Atestado) estava apagando a
    identificação server-side que tinha acabado de ser prefixada, porque
    a ordem de chamada estava invertida. Estes testes reproduzem
    literalmente o que Templates.tsx envia hoje — não a API "nua" sem
    `corpo_final` dos testes acima."""

    def test_exames_com_corpo_final_do_navegador_ganha_cpf_e_nascimento_sem_duplicar_nome(
        self, client, db, criar_usuario,
    ):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)
        corpo_final = _corpo_final_exames_como_o_navegador_envia(
            "Fulano de Tal da Silva", ["Hemograma completo"],
        )

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": corpo_final,
            },
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert rendered_body.count("Paciente:") == 1  # nunca duplicado
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF: 123.456.789-00" in rendered_body
        assert "Data de nascimento: 20/05/1980" in rendered_body
        assert "- Hemograma completo" in rendered_body

        if _TEM_PDFTOTEXT:
            pdf = client.get(
                f"/api/document-templates/gerados/{resposta.json()['id']}/pdf", headers=_headers(token),
            )
            texto = _texto_do_pdf(pdf.content)
            assert texto.count("Paciente:") == 1
            assert "CPF: 123.456.789-00" in texto

    def test_exames_edicao_manual_do_medico_e_preservada_por_inteiro(self, client, db, criar_usuario):
        """O médico altera o texto padrão à mão — a edição não pode se
        perder, só a identificação canônica entra por cima dela."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)
        corpo_final = _corpo_final_exames_como_o_navegador_envia(
            "Fulano de Tal da Silva", ["Hemograma completo"],
        ).replace(
            "Solicito a realização dos seguintes exames:",
            "Solicito, devido ao quadro clínico descrito, a realização dos seguintes exames:",
        )

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": corpo_final,
            },
        )
        rendered_body = resposta.json()["rendered_body"]
        assert "Solicito, devido ao quadro clínico descrito," in rendered_body
        assert "CPF: 123.456.789-00" in rendered_body

    def test_exames_cadastro_sem_cpf_nem_nascimento_com_corpo_final_do_navegador(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token, cpf=None, birth_date=None)
        corpo_final = _corpo_final_exames_como_o_navegador_envia(
            "Fulano de Tal da Silva", ["Hemograma completo"],
        )

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": corpo_final,
            },
        )
        rendered_body = resposta.json()["rendered_body"]
        assert rendered_body.count("Paciente:") == 1
        assert "CPF:" not in rendered_body
        assert "Data de nascimento:" not in rendered_body

    def test_exames_nome_avulso_com_corpo_final_nao_sofre_alteracao_server_side(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        corpo_final = _corpo_final_exames_como_o_navegador_envia("Ciclano Avulso", ["Hemograma completo"])

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_name": "Ciclano Avulso", "exames": ["Hemograma completo"], "corpo_final": corpo_final},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["rendered_body"] == corpo_final  # sem patient_profile_id, nenhuma alteração

    def test_exames_tenant_isolation_com_corpo_final(self, client, db, criar_usuario):
        dono, token_dono = criar_usuario(email="dono-exames-cf@teste.local")
        _dar_assinatura_principal(db, dono)
        paciente = _criar_paciente(client, token_dono)
        outro, token_outro = criar_usuario(email="outro-exames-cf@teste.local")
        _dar_assinatura_principal(db, outro)

        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token_outro),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": _corpo_final_exames_como_o_navegador_envia("Fulano", ["Hemograma completo"]),
            },
        )
        assert resposta.status_code == 404

    def test_atestado_com_corpo_final_do_navegador_ganha_bloco_no_topo_sem_remover_nome_da_frase(
        self, client, db, criar_usuario,
    ):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)
        corpo_final = _corpo_final_atestado_como_o_navegador_envia("Fulano de Tal da Silva", 3)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3, "corpo_final": corpo_final},
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        # O bloco no topo mais o nome dentro da frase do atestado — dois
        # lugares é aceitável aqui (pedido explícito do Rafael): a frase é
        # conteúdo clínico/redacional legítimo, nunca reescrita.
        assert rendered_body.startswith("Paciente: Fulano de Tal da Silva\nCPF: 123.456.789-00\nData de nascimento: 20/05/1980\n\n")
        assert "Atesto, para os devidos fins, que o(a) paciente Fulano de Tal da Silva necessita" in rendered_body

        if _TEM_PDFTOTEXT:
            pdf = client.get(
                f"/api/document-templates/gerados/{resposta.json()['id']}/pdf", headers=_headers(token),
            )
            texto = _texto_do_pdf(pdf.content)
            assert "CPF: 123.456.789-00" in texto
            assert "Data de nascimento: 20/05/1980" in texto

    def test_atestado_cadastro_sem_cpf_nem_nascimento_com_corpo_final_do_navegador(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token, cpf=None, birth_date=None)
        corpo_final = _corpo_final_atestado_como_o_navegador_envia("Fulano de Tal da Silva", 3)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "dias_afastamento": 3, "corpo_final": corpo_final},
        )
        rendered_body = resposta.json()["rendered_body"]
        assert rendered_body.startswith("Paciente: Fulano de Tal da Silva\n\n")
        assert "CPF:" not in rendered_body.split("\n\n")[0]
        assert "Data de nascimento:" not in rendered_body.split("\n\n")[0]

    def test_atestado_nome_avulso_com_corpo_final_nao_sofre_alteracao_server_side(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        corpo_final = _corpo_final_atestado_como_o_navegador_envia("Ciclano Avulso", 3)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"patient_name": "Ciclano Avulso", "dias_afastamento": 3, "corpo_final": corpo_final},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["rendered_body"] == corpo_final

    def test_atestado_tenant_isolation_com_corpo_final(self, client, db, criar_usuario):
        dono, token_dono = criar_usuario(email="dono-atestado-cf@teste.local")
        _dar_assinatura_principal(db, dono)
        paciente = _criar_paciente(client, token_dono)
        outro, token_outro = criar_usuario(email="outro-atestado-cf@teste.local")
        _dar_assinatura_principal(db, outro)

        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token_outro),
            json={
                "patient_profile_id": paciente["id"], "dias_afastamento": 3,
                "corpo_final": _corpo_final_atestado_como_o_navegador_envia("Fulano", 3),
            },
        )
        assert resposta.status_code == 404

    def test_gerar_recriar_gerar_nao_acumula_blocos_de_identificacao(self, client, db, criar_usuario):
        """Simula gerar → reabrir a tela com o mesmo paciente já
        selecionado (o preview volta a montar `corpo_final` do zero a
        partir do estado, igual ao navegador faria) → gerar de novo. Nunca
        mais de um bloco de identificação, em nenhuma das duas gerações."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        primeira = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": _corpo_final_exames_como_o_navegador_envia(
                    "Fulano de Tal da Silva", ["Hemograma completo"],
                ),
            },
        )
        assert primeira.json()["rendered_body"].count("Paciente:") == 1

        # "Recriar": o navegador reconstrói o preview do zero a partir dos
        # campos estruturados + paciente selecionado de novo — nunca reusa
        # o rendered_body anterior (que já tem o bloco). Reproduzido aqui
        # chamando de novo com o MESMO corpo_final "cru" (sem bloco).
        segunda = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": _corpo_final_exames_como_o_navegador_envia(
                    "Fulano de Tal da Silva", ["Hemograma completo"],
                ),
            },
        )
        assert segunda.json()["rendered_body"].count("Paciente:") == 1
        assert segunda.json()["rendered_body"] == primeira.json()["rendered_body"]  # idempotente

    def test_idempotente_reaplicar_prefixacao_sobre_corpo_ja_prefixado_nao_duplica(self, client, db, criar_usuario):
        """Se por algum motivo o `corpo_final` enviado já é um
        `rendered_body` anterior (bloco completo, nome+CPF+nascimento),
        reaplicar a prefixação não duplica nada."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        primeira = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"patient_profile_id": paciente["id"], "exames": ["Hemograma completo"]},
        )
        rendered_body_ja_prefixado = primeira.json()["rendered_body"]

        segunda = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={
                "patient_profile_id": paciente["id"], "exames": ["Hemograma completo"],
                "corpo_final": rendered_body_ja_prefixado,
            },
        )
        assert segunda.json()["rendered_body"].count("Paciente:") == 1
        assert segunda.json()["rendered_body"] == rendered_body_ja_prefixado


class TestDocumentoLivreIdentificacaoNoCorpo:
    """02/09/2026, segunda rodada: selecionar paciente no Documento em Branco
    já gravava `patient_profile_id`/snapshot, mas o texto emitido (e por
    tabela o PDF, que renderiza `rendered_body` sem builder próprio) não
    identificava o paciente de jeito nenhum. Sem paciente selecionado, o
    comportamento tem que continuar idêntico ao de antes — byte a byte."""

    def test_sem_paciente_rendered_body_e_identico_ao_texto_digitado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        texto_digitado = "Encaminhamento para avaliação especializada.\n\nSem outras observações."

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={"titulo": "Encaminhamento", "corpo": texto_digitado},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["rendered_body"] == texto_digitado
        assert corpo["patient_profile_id"] is None

    def test_com_paciente_cadastrado_rendered_body_contem_o_nome(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)
        texto_digitado = "Corpo do documento livre digitado pelo médico."

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Anotação", "corpo": texto_digitado,
                "patient_profile_id": paciente["id"],
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert "Paciente: Fulano de Tal da Silva" in corpo["rendered_body"]
        # O texto digitado pelo médico continua intacto, só com a
        # identificação na frente — nunca reescrito ou reformatado.
        assert texto_digitado in corpo["rendered_body"]

    def test_com_cpf_e_nascimento_identificacao_contem_os_dados(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Anotação", "corpo": "Corpo de teste.",
                "patient_profile_id": paciente["id"],
            },
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF: 123.456.789-00" in rendered_body
        assert "Data de nascimento: 20/05/1980" in rendered_body

    def test_campos_ausentes_no_cadastro_nao_viram_linha_vazia(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token, cpf=None, birth_date=None)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Anotação", "corpo": "Corpo de teste.",
                "patient_profile_id": paciente["id"],
            },
        )
        assert resposta.status_code == 201, resposta.text
        rendered_body = resposta.json()["rendered_body"]
        assert "Paciente: Fulano de Tal da Silva" in rendered_body
        assert "CPF:" not in rendered_body
        assert "Data de nascimento:" not in rendered_body
        # Nenhuma linha em branco sobrando entre a identificação e o corpo
        # além do separador de parágrafo esperado (identificação + linha
        # em branco + corpo, nunca duas ou mais linhas em branco seguidas).
        assert "\n\n\n" not in rendered_body

    def test_patient_profile_id_e_snapshot_permanecem_gravados(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Anotação", "corpo": "Corpo de teste.",
                "patient_profile_id": paciente["id"],
            },
        )
        assert resposta.status_code == 201, resposta.text
        gerado_id = resposta.json()["id"]

        gerado = db.get(GeneratedDocument, gerado_id)
        assert gerado.patient_profile_id == paciente["id"]
        assert gerado.patient_snapshot_cifrado is not None
        assert gerado.patient_name_cifrado is not None

    def test_recriar_baseado_neste_documento_nao_duplica_identificacao(self, client, db, criar_usuario):
        """`variables["corpo"]` guarda o texto ORIGINAL sem a identificação —
        é o que "recriar baseado neste" usa pra repopular o editor."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)
        texto_digitado = "Corpo original digitado pelo médico."

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Anotação", "corpo": texto_digitado,
                "patient_profile_id": paciente["id"],
            },
        )
        gerado_id = resposta.json()["id"]

        detalhe = client.get(
            f"/api/document-templates/gerados/{gerado_id}", headers=_headers(token),
        )
        assert detalhe.status_code == 200, detalhe.text
        assert detalhe.json()["variables"]["corpo"] == texto_digitado

    @pytest.mark.skipif(not _TEM_PDFTOTEXT, reason="pdftotext (poppler-utils) não disponível neste ambiente")
    def test_pdf_real_contem_a_identificacao_do_paciente(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        paciente = _criar_paciente(client, token)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={
                "titulo": "Nota livre", "corpo": "Corpo do documento livre digitado pelo médico.",
                "patient_profile_id": paciente["id"],
            },
        )
        gerado_id = resposta.json()["id"]

        pdf = client.get(
            f"/api/document-templates/gerados/{gerado_id}/pdf", headers=_headers(token),
        )
        assert pdf.status_code == 200, pdf.text
        assert pdf.content.startswith(b"%PDF-")

        texto = _texto_do_pdf(pdf.content)
        assert "Paciente: Fulano de Tal da Silva" in texto
        assert "CPF: 123.456.789-00" in texto
        assert "Data de nascimento: 20/05/1980" in texto
        assert "Corpo do documento livre digitado pelo médico." in texto

    @pytest.mark.skipif(not _TEM_PDFTOTEXT, reason="pdftotext (poppler-utils) não disponível neste ambiente")
    def test_pdf_real_sem_paciente_nao_contem_identificacao(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={"titulo": "Nota livre", "corpo": "Corpo do documento sem paciente."},
        )
        gerado_id = resposta.json()["id"]

        pdf = client.get(
            f"/api/document-templates/gerados/{gerado_id}/pdf", headers=_headers(token),
        )
        assert pdf.status_code == 200, pdf.text
        texto = _texto_do_pdf(pdf.content)
        assert "Paciente:" not in texto
        assert "Corpo do documento sem paciente." in texto


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
