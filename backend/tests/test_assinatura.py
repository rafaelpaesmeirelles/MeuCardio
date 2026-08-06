"""Testes da Tarefa 4 — catálogo de assinatura digital e persistência do PDF.

Cobre os dois caminhos de emissão (receituário e documento gerado a partir
de modelo): o método "MANUAL" tem que funcionar de ponta a ponta e produzir
PDF determinístico (mesmo hash em downloads repetidos); qualquer outro
método do catálogo, sem credencial configurada, tem que recusar com 409 e
`nada_foi_simulado: true` — nunca assinar de mentira.
"""
import hashlib

import pytest
from sqlalchemy import text

from app.models.assinatura import DocumentoEmitido
from app.models.audit import AuditLog
from app.models.receituario import PrescriptionType

_TABELAS_ASSINATURA = (
    "documentos_emitidos", "prescription_documents", "prescription_recipients",
    "prescriptions", "generated_documents", "document_templates", "prescription_types",
)


@pytest.fixture(autouse=True)
def _limpar_e_semear(db):
    db.execute(text(f"TRUNCATE {', '.join(_TABELAS_ASSINATURA)} RESTART IDENTITY CASCADE"))
    db.add(PrescriptionType(codigo="COMUM", nome="Receituário comum", ativo=True))
    db.add(PrescriptionType(codigo="RCE", nome="Receita de Controle Especial", ativo=False))
    db.commit()
    yield


def _autorizado(role="admin"):
    return role


class TestCatalogoDeProvedores:
    def test_lista_14_provedores_manual_e_fluxo_iti_disponiveis(self, client, criar_usuario):
        """Trabalho 14 (06/08/2026): GOVBR e as clouds sem credencial
        comercial (VIDAAS/BIRDID/SAFEID/NEOID/REMOTEID) passaram a ter
        adaptador real — fluxo manual do Assinador ITI, disponível sem
        nenhuma credencial (o médico assina fora e reenvia)."""
        _, token = criar_usuario(role="admin")
        r = client.get("/api/assinatura/provedores", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        provedores = r.json()
        assert len(provedores) == 14
        por_codigo = {p["codigo"]: p for p in provedores}

        disponiveis = {"MANUAL", "GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID"}
        for codigo in disponiveis:
            assert por_codigo[codigo]["disponivel"] is True, codigo
            assert por_codigo[codigo]["motivo"] is None, codigo

        for codigo, p in por_codigo.items():
            if codigo in disponiveis:
                continue
            assert p["disponivel"] is False, codigo
            assert p["motivo"], codigo


def _criar_e_revisar_receita(client, token, itens=None):
    itens = itens or [{"descricao": "Dipirona 500mg", "posologia": "1 cp a cada 6h"}]
    r = client.post(
        "/api/receituario",
        headers={"Authorization": f"Bearer {token}"},
        json={"destinatario": {"nome": "Paciente de Teste"}, "itens": itens},
    )
    assert r.status_code == 201, r.text
    doc_id = r.json()["documentos"][0]["id"]
    r = client.post(
        f"/api/receituario/documentos/{doc_id}/revisar",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmar": True},
    )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "revisado"
    return doc_id


class TestCorrigirTipo:
    """O médico pode corrigir a classificação automática, com motivo auditável."""

    def _criar_documento(self, client, token):
        r = client.post(
            "/api/receituario",
            headers={"Authorization": f"Bearer {token}"},
            json={"destinatario": {"nome": "Paciente de Teste"},
                  "itens": [{"descricao": "Dipirona 500mg"}]},
        )
        assert r.status_code == 201, r.text
        return r.json()["documentos"][0]["id"]

    def test_corrigir_para_rce_exige_motivo(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id = self._criar_documento(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/revisar",
            headers={"Authorization": f"Bearer {token}"},
            json={"confirmar": True, "corrigir_para": "RCE"},
        )
        assert r.status_code == 422, r.text

    def test_corrigir_para_rce_com_motivo_funciona(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id = self._criar_documento(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/revisar",
            headers={"Authorization": f"Bearer {token}"},
            json={"confirmar": True, "corrigir_para": "RCE", "motivo": "É anabolizante, não é comum."},
        )
        assert r.status_code == 200, r.text
        corpo = r.json()
        assert corpo["tipo"] == "RCE"
        assert corpo["tipo_ativo"] is False
        assert corpo["classificacao_corrigida_de"] == "COMUM"
        assert corpo["motivo_correcao"] == "É anabolizante, não é comum."

    def test_corrigir_para_tipo_desconhecido_devolve_422(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id = self._criar_documento(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/revisar",
            headers={"Authorization": f"Bearer {token}"},
            json={"confirmar": True, "corrigir_para": "NAO_EXISTE", "motivo": "teste"},
        )
        assert r.status_code == 422

    def test_bloqueio_de_tipo_inativo_nao_culpa_assinatura_digital(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id = self._criar_documento(client, token)
        client.post(
            f"/api/receituario/documentos/{doc_id}/revisar",
            headers={"Authorization": f"Bearer {token}"},
            json={"confirmar": True, "corrigir_para": "RCE", "motivo": "teste"},
        )

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/emitir",
            headers={"Authorization": f"Bearer {token}"},
            json={"metodo": "MANUAL"},
        )
        assert r.status_code == 409, r.text
        bloqueios = " ".join(r.json()["detail"]["bloqueios"]).lower()
        assert "sncr" in bloqueios
        assert "assinatura digital" not in bloqueios


class TestEmitirReceituario:
    def test_emitir_manual_produz_pdf_e_persiste(self, client, criar_usuario, db):
        _, token = criar_usuario(role="admin")
        doc_id = _criar_e_revisar_receita(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/emitir",
            headers={"Authorization": f"Bearer {token}"},
            json={"metodo": "MANUAL"},
        )
        assert r.status_code == 200, r.text
        assert r.content.startswith(b"%PDF")

        registro = db.query(DocumentoEmitido).filter(
            DocumentoEmitido.tipo == "prescription_document", DocumentoEmitido.referencia_id == doc_id,
        ).one()
        assert registro.metodo == "MANUAL"
        assert registro.nivel == "nenhuma"
        assert registro.sha256 == hashlib.sha256(r.content).hexdigest()
        assert registro.assinado_em is None

        auditoria = db.query(AuditLog).filter(
            AuditLog.entity == "prescription_document", AuditLog.entity_id == str(doc_id),
            AuditLog.action == "emitir_documento_receita",
        ).one()
        assert auditoria.detail["metodo"] == "MANUAL"
        assert auditoria.detail["sha256"] == registro.sha256

        envio = client.post(
            f"/api/receituario/documentos/{doc_id}/enviar-email",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "paciente@teste.local"},
        )
        assert envio.status_code == 409
        assert "assinatura qualificada ICP-Brasil" in envio.json()["detail"]

    def test_emitir_provedor_indisponivel_recusa_sem_gerar_nada(self, client, criar_usuario, db):
        """CLICKSIGN continua sem adaptador — diferente de VIDAAS/GOVBR/etc.,
        que passaram a ter o fluxo manual do Assinador ITI (Trabalho 14)."""
        _, token = criar_usuario(role="admin")
        doc_id = _criar_e_revisar_receita(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/emitir",
            headers={"Authorization": f"Bearer {token}"},
            json={"metodo": "CLICKSIGN"},
        )
        assert r.status_code == 409, r.text
        detail = r.json()["detail"]
        assert detail["nada_foi_simulado"] is True
        assert any("Clicksign" in b or "CLICKSIGN" in b for b in detail["bloqueios"])

        assert db.query(DocumentoEmitido).count() == 0

    def test_emitir_metodo_desconhecido_devolve_422(self, client, criar_usuario):
        _, token = criar_usuario(role="admin")
        doc_id = _criar_e_revisar_receita(client, token)

        r = client.post(
            f"/api/receituario/documentos/{doc_id}/emitir",
            headers={"Authorization": f"Bearer {token}"},
            json={"metodo": "NAO_EXISTE"},
        )
        assert r.status_code == 422


class TestGerarDocumento:
    def _criar_template_e_gerar(self, client, token):
        r = client.post(
            "/api/document-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Atestado padrão", "doc_type": "atestado", "body": "Atesto que o paciente precisa de repouso."},
        )
        assert r.status_code == 201, r.text
        template_id = r.json()["id"]

        r = client.post(
            "/api/document-templates/gerar",
            headers={"Authorization": f"Bearer {token}"},
            json={"template_id": template_id, "variables": {}},
        )
        assert r.status_code == 201, r.text
        return r.json()["id"]

    def test_primeiro_download_manual_emite_e_persiste_hash_estavel(self, client, criar_usuario, db):
        _, token = criar_usuario(role="admin")
        gerado_id = self._criar_template_e_gerar(client, token)

        r1 = client.get(
            f"/api/document-templates/gerados/{gerado_id}/pdf?metodo=MANUAL",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r1.status_code == 200, r1.text
        assert r1.content.startswith(b"%PDF")

        r2 = client.get(
            f"/api/document-templates/gerados/{gerado_id}/pdf?metodo=VIDAAS",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r2.status_code == 200
        assert hashlib.sha256(r2.content).hexdigest() == hashlib.sha256(r1.content).hexdigest()

        assert db.query(DocumentoEmitido).filter(
            DocumentoEmitido.tipo == "generated_document", DocumentoEmitido.referencia_id == gerado_id,
        ).count() == 1

        auditoria = db.query(AuditLog).filter(
            AuditLog.entity == "generated_document", AuditLog.entity_id == str(gerado_id),
        ).all()
        assert len(auditoria) == 1
        assert auditoria[0].detail["metodo"] == "MANUAL"

    def test_primeiro_download_provedor_indisponivel_recusa(self, client, criar_usuario, db):
        _, token = criar_usuario(role="admin")
        gerado_id = self._criar_template_e_gerar(client, token)

        r = client.get(
            f"/api/document-templates/gerados/{gerado_id}/pdf?metodo=CLICKSIGN",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 409, r.text
        assert r.json()["detail"]["nada_foi_simulado"] is True
        assert db.query(DocumentoEmitido).count() == 0
