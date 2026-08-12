"""Solicitação de exames, atestado rápido e documento em branco — três
caminhos de entrada para `GeneratedDocument` que NÃO exigem um
`DocumentTemplate` prévio (pedido do Rafael, 12/08/2026).

Reaproveitam por inteiro a infraestrutura já testada em outros arquivos
(PDF, assinatura, envio por e-mail) — aqui cobre-se só o que é NOVO: os
três endpoints de criação, a lista de sugestão de exames, o filtro por
tipo em `/gerados`, e que `GET /gerados/{id}` devolve o suficiente
(`doc_type`, `template_id=None`, `variables`) para o frontend reconstruir
o formulário em "recriar baseado neste"."""
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _dar_assinatura_principal(db, user) -> None:
    """`documents.router` está atrás de `assinante_ativo` (app/main.py) —
    exige `Subscription(kind='meucardio')` ativa, mesmo padrão já usado em
    `test_envio_paciente_documento_gerado.py`."""
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


class TestExamesSugeridos:
    def test_lista_agrupada_por_categoria_e_inclui_exemplos_do_pedido(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.get("/api/document-templates/exames-sugeridos", headers=_headers(token))
        assert resposta.status_code == 200, resposta.text
        corpo = resposta.json()
        assert isinstance(corpo, dict)
        assert "Laboratoriais" in corpo
        assert "Cardiologia" in corpo
        todos = {e for lista in corpo.values() for e in lista}
        for esperado in (
            "Hemograma completo", "Creatinina", "Sódio", "Potássio", "TSH", "T4 livre",
            "NT-proBNP", "Ecocardiograma transtorácico", "Holter 24h", "MAPA",
            "Teste ergométrico", "Ressonância cardíaca",
        ):
            assert esperado in todos, esperado


class TestGerarSolicitacaoExames:
    def test_com_exame_digitado_livremente_alem_da_lista_sugerida(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={
                "patient_name": "Fulano de Tal",
                "exames": ["Hemograma completo", "Dosagem de vitamina B12 e ferritina (exame incomum)"],
                "indicacao": "Investigação de anemia",
                "prioridade": "rotina",
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["doc_type"] == "solicitacao_exames"
        assert corpo["patient_name"] == "Fulano de Tal"
        assert "Hemograma completo" in corpo["rendered_body"]
        assert "Dosagem de vitamina B12 e ferritina (exame incomum)" in corpo["rendered_body"]
        assert "Investigação de anemia" in corpo["rendered_body"]

        gerado = db.get(GeneratedDocument, corpo["id"])
        assert gerado.template_id is None
        assert gerado.variables["exames"] == [
            "Hemograma completo", "Dosagem de vitamina B12 e ferritina (exame incomum)",
        ]

        log = db.query(AuditLog).filter(
            AuditLog.action == "gerar_solicitacao_exames", AuditLog.entity_id == str(corpo["id"]),
        ).first()
        assert log is not None
        assert log.detail["quantidade_exames"] == 2

    def test_sem_paciente_informado_ainda_funciona(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={"exames": ["Eletrocardiograma (ECG)"]},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["patient_name"] is None
        assert "Paciente:" not in corpo["rendered_body"]

    def test_lista_vazia_de_exames_e_rejeitada(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={"exames": []},
        )
        assert resposta.status_code == 422

    def test_lista_so_com_espacos_em_branco_tambem_e_rejeitada(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={"exames": ["   ", ""]},
        )
        assert resposta.status_code == 422

    def test_prioridade_urgente_aparece_no_corpo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={"exames": ["Troponina"], "prioridade": "urgente"},
        )
        assert resposta.status_code == 201, resposta.text
        assert "URGENTE" in resposta.json()["rendered_body"]


class TestGerarDocumentoLivre:
    def test_so_titulo_e_corpo_gera_com_sucesso(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-livre",
            headers=_headers(token),
            json={"titulo": "Declaração de comparecimento", "corpo": "Declaro que o paciente compareceu à consulta."},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["doc_type"] == "documento_livre"
        assert corpo["title"] == "Declaração de comparecimento"
        assert corpo["rendered_body"] == "Declaro que o paciente compareceu à consulta."
        assert corpo["patient_name"] is None

        gerado = db.get(GeneratedDocument, corpo["id"])
        assert gerado.template_id is None

    def test_titulo_vazio_e_rejeitado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-livre",
            headers=_headers(token),
            json={"titulo": "", "corpo": "Texto qualquer."},
        )
        assert resposta.status_code == 422

    def test_corpo_vazio_e_rejeitado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-livre",
            headers=_headers(token),
            json={"titulo": "Título válido", "corpo": ""},
        )
        assert resposta.status_code == 422


class TestGerarAtestadoRapido:
    def test_por_quantidade_de_dias(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-atestado",
            headers=_headers(token),
            json={"patient_name": "Ciclana da Silva", "dias_afastamento": 3, "cid": "J06.9"},
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["doc_type"] == "atestado"
        assert "3 dia(s)" in corpo["rendered_body"]
        assert "J06.9" in corpo["rendered_body"]
        assert "Ciclana da Silva" in corpo["rendered_body"]

    def test_por_periodo_completo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-atestado",
            headers=_headers(token),
            json={"data_inicio": "2026-08-01", "data_fim": "2026-08-05"},
        )
        assert resposta.status_code == 201, resposta.text
        assert "01/08/2026" in resposta.json()["rendered_body"]
        assert "05/08/2026" in resposta.json()["rendered_body"]

    def test_sem_dias_nem_periodo_e_rejeitado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-atestado",
            headers=_headers(token),
            json={"patient_name": "Alguém"},
        )
        assert resposta.status_code == 422

    def test_data_fim_antes_da_data_inicio_e_rejeitado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)

        resposta = client.post(
            "/api/document-templates/gerar-atestado",
            headers=_headers(token),
            json={"data_inicio": "2026-08-05", "data_fim": "2026-08-01"},
        )
        assert resposta.status_code == 422


class TestPdfDosTiposNovos:
    def test_pdf_da_solicitacao_de_exames_e_um_pdf_real(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={"exames": ["Hemograma completo"]},
        ).json()

        resposta = client.get(
            f"/api/document-templates/gerados/{criado['id']}/pdf", headers=_headers(token),
        )
        assert resposta.status_code == 200, resposta.text
        assert resposta.content.startswith(b"%PDF-")
        assert resposta.headers["content-type"] == "application/pdf"

    def test_pdf_do_documento_livre_e_um_pdf_real(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = client.post(
            "/api/document-templates/gerar-livre",
            headers=_headers(token),
            json={"titulo": "Nota livre", "corpo": "Corpo qualquer do documento livre."},
        ).json()

        resposta = client.get(
            f"/api/document-templates/gerados/{criado['id']}/pdf", headers=_headers(token),
        )
        assert resposta.status_code == 200, resposta.text
        assert resposta.content.startswith(b"%PDF-")

    def test_pdf_do_atestado_rapido_e_um_pdf_real(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = client.post(
            "/api/document-templates/gerar-atestado",
            headers=_headers(token),
            json={"dias_afastamento": 2},
        ).json()

        resposta = client.get(
            f"/api/document-templates/gerados/{criado['id']}/pdf", headers=_headers(token),
        )
        assert resposta.status_code == 200, resposta.text
        assert resposta.content.startswith(b"%PDF-")


class TestFiltroPorTipoNaListagem:
    def test_filtro_encontra_os_tipos_novos(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"exames": ["Hemograma completo"]},
        )
        client.post(
            "/api/document-templates/gerar-livre", headers=_headers(token),
            json={"titulo": "Livre 1", "corpo": "corpo"},
        )

        so_exames = client.get(
            "/api/document-templates/gerados?tipo=solicitacao_exames", headers=_headers(token),
        ).json()
        assert so_exames["total"] == 1
        assert all(item["doc_type"] == "solicitacao_exames" for item in so_exames["items"])

        so_livre = client.get(
            "/api/document-templates/gerados?tipo=documento_livre", headers=_headers(token),
        ).json()
        assert so_livre["total"] == 1
        assert so_livre["items"][0]["title"] == "Livre 1"

        todos = client.get("/api/document-templates/gerados", headers=_headers(token)).json()
        assert todos["total"] == 2


class TestRecriarBaseadoNesteFuncionaSemModelo:
    """`recriar baseado neste`, no frontend, depende de `GET /gerados/{id}`
    devolver `doc_type` + `template_id=None` + `variables` — o suficiente
    para reabrir o formulário certo (exames/atestado/livre) já preenchido,
    sem precisar de um `DocumentTemplate` (que nunca existiu para estes
    três tipos)."""

    def test_detalhe_da_solicitacao_de_exames_traz_o_necessario_para_recriar(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = client.post(
            "/api/document-templates/gerar-exames",
            headers=_headers(token),
            json={
                "patient_name": "Beltrano", "exames": ["Hemograma completo", "TSH"],
                "indicacao": "Check-up", "cid": None, "prioridade": "rotina",
            },
        ).json()

        detalhe = client.get(
            f"/api/document-templates/gerados/{criado['id']}", headers=_headers(token),
        ).json()
        assert detalhe["template_id"] is None
        assert detalhe["doc_type"] == "solicitacao_exames"
        assert detalhe["variables"]["exames"] == ["Hemograma completo", "TSH"]
        assert detalhe["variables"]["indicacao"] == "Check-up"
        assert detalhe["patient_name"] == "Beltrano"

    def test_detalhe_do_documento_livre_traz_titulo_e_corpo_originais(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = client.post(
            "/api/document-templates/gerar-livre",
            headers=_headers(token),
            json={"titulo": "Original", "corpo": "Corpo original do documento."},
        ).json()

        detalhe = client.get(
            f"/api/document-templates/gerados/{criado['id']}", headers=_headers(token),
        ).json()
        assert detalhe["template_id"] is None
        assert detalhe["doc_type"] == "documento_livre"
        assert detalhe["variables"]["titulo"] == "Original"
        assert detalhe["variables"]["corpo"] == "Corpo original do documento."

    def test_detalhe_do_atestado_rapido_distingue_de_atestado_por_modelo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        criado = client.post(
            "/api/document-templates/gerar-atestado",
            headers=_headers(token),
            json={"dias_afastamento": 5},
        ).json()

        detalhe = client.get(
            f"/api/document-templates/gerados/{criado['id']}", headers=_headers(token),
        ).json()
        # `doc_type == "atestado"` é o MESMO valor que um atestado gerado por
        # modelo usaria — é `template_id is None` que sinaliza "veio do
        # atalho rápido, sem modelo por trás" para o frontend decidir qual
        # formulário reabrir em "recriar baseado neste".
        assert detalhe["doc_type"] == "atestado"
        assert detalhe["template_id"] is None
        assert detalhe["variables"]["dias_afastamento"] == 5
