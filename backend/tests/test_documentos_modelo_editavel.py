""""Modelo é ponto de partida editável, nunca documento final imutável"
(12/08/2026, pedido do Rafael) — `corpo_final` em `GerarDocumentoIn`/
`SolicitacaoExamesIn`/`AtestadoRapidoIn`: quando o médico revisa/edita o
texto na tela antes de gerar, é ESSE texto que vira `rendered_body`, sem
voltar a passar pela substituição de `{{variavel}}` — e o `DocumentTemplate`
salvo nunca é alterado por isso (a edição vale só para aquele documento).
"""
from app.models.clinical_docs import DocumentTemplate, GeneratedDocument
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _dar_assinatura_principal(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


class TestCorpoFinalNoFluxoDeModelo:
    def test_texto_editado_na_emissao_e_o_que_vale_no_pdf(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        template = DocumentTemplate(
            owner_id=user.id, title="Solicitação de Exames Complementares", doc_type="laudo",
            body="Solicito {{exame}} para o(a) paciente {{nome}}.",
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        texto_editado = (
            "Solicito os seguintes exames para o(a) paciente Fulano de Tal:\n\n"
            "- Hemograma completo\n"
            "- Dosagem de vitamina D (exame acrescentado na hora de emitir)\n\n"
            "Indicação clínica: investigação de fadiga."
        )
        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={
                "template_id": template.id,
                "variables": {"exame": "hemograma", "nome": "Fulano de Tal"},
                "corpo_final": texto_editado,
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["rendered_body"] == texto_editado
        assert "{{exame}}" not in corpo["rendered_body"]
        assert "Dosagem de vitamina D (exame acrescentado na hora de emitir)" in corpo["rendered_body"]

        pdf = client.get(f"/api/document-templates/gerados/{corpo['id']}/pdf", headers=_headers(token))
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF-")

    def test_editar_na_emissao_nunca_altera_o_modelo_original_salvo(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        template = DocumentTemplate(
            owner_id=user.id, title="Atestado padrão", doc_type="atestado",
            body="Atesto que {{nome}} necessita de repouso.",
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        corpo_original_do_modelo = template.body

        client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={
                "template_id": template.id,
                "variables": {"nome": "Beltrano"},
                "corpo_final": "Texto inteiramente reescrito na hora de emitir, sem relação com o modelo.",
            },
        )

        # Reabre o modelo pela mesma rota que a tela usa para listar
        # modelos salvos — precisa estar BYTE A BYTE igual ao que era
        # antes da emissão.
        modelos = client.get("/api/document-templates", headers=_headers(token)).json()
        modelo_reaberto = next(m for m in modelos if m["id"] == template.id)
        assert modelo_reaberto["body"] == corpo_original_do_modelo
        assert "{{nome}}" in modelo_reaberto["body"]

        db.refresh(template)
        assert template.body == corpo_original_do_modelo

    def test_corpo_final_em_branco_e_ignorado_cai_no_comportamento_padrao(self, client, db, criar_usuario):
        """`corpo_final` só espaços/vazio não é "edição de propósito" — não
        deve sobrepor a substituição normal de `{{variavel}}`."""
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        template = DocumentTemplate(
            owner_id=user.id, title="X", doc_type="outro", body="Olá, {{nome}}.",
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        resposta = client.post(
            "/api/document-templates/gerar", headers=_headers(token),
            json={"template_id": template.id, "variables": {"nome": "Ciclana"}, "corpo_final": "   "},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["rendered_body"] == "Olá, Ciclana."


class TestCorpoFinalNosAtalhosSemModelo:
    def test_solicitacao_de_exames_com_corpo_editado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        texto_editado = "Texto totalmente reescrito pelo médico antes de gerar a solicitação."
        resposta = client.post(
            "/api/document-templates/gerar-exames", headers=_headers(token),
            json={"exames": ["Hemograma completo"], "corpo_final": texto_editado},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["rendered_body"] == texto_editado
        # os campos estruturados continuam gravados em `variables`, para
        # "recriar baseado neste" reabrir o formulário certo mesmo quando
        # o corpo final foi editado à mão.
        gerado = db.get(GeneratedDocument, resposta.json()["id"])
        assert gerado.variables["exames"] == ["Hemograma completo"]

    def test_atestado_rapido_com_corpo_editado(self, client, db, criar_usuario):
        user, token = criar_usuario()
        _dar_assinatura_principal(db, user)
        texto_editado = "Atesto, com texto próprio, que o paciente precisa de afastamento."
        resposta = client.post(
            "/api/document-templates/gerar-atestado", headers=_headers(token),
            json={"dias_afastamento": 3, "corpo_final": texto_editado},
        )
        assert resposta.status_code == 201, resposta.text
        assert resposta.json()["rendered_body"] == texto_editado
