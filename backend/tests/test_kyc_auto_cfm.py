from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.kyc import KycVerification
from app.services.kyc import auto_flow, auto_validation, verificacao


class _CfmOk:
    crm_exibicao = "138266"
    uf = "SP"
    nome = "RAFAEL PAES MEIRELLES"
    situacao_codigo = "A"
    situacao_texto = "REGULAR"
    tipo_inscricao_codigo = "P"
    tipo_inscricao_texto = "PRINCIPAL"
    especialidades = ("CARDIOLOGIA - RQE Nº 134798",)
    data_atualizacao = date(2026, 9, 2)
    is_regular = True


class _Ws:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def consultar(self, numero_crm, uf):
        assert str(numero_crm) == "138266"
        assert uf == "SP"
        return _CfmOk()


def _docs():
    return verificacao.DocumentosSubmissao(
        doc_profissional_frente=b"prof-frente",
        doc_profissional_verso=b"prof-verso",
        selfie=b"selfie",
        doc_pessoal_frente=b"pessoal-frente",
        doc_pessoal_verso=b"pessoal-verso",
    )


def _medico(user):
    user.full_name = "Rafael Paes Meirelles"
    user.council_name = "CRM"
    user.council_number = "138266"
    user.council_state = "SP"
    user.crm = "138266"
    user.rqe = "134798"
    user.cpf = "123.456.789-09"
    user.birth_date = date(1980, 1, 2)
    return user


def test_validacao_medico_aprova_quando_cfm_e_documentos_conferem(monkeypatch, criar_usuario):
    user, _ = criar_usuario()
    _medico(user)
    monkeypatch.setattr(settings, "cfm_webservice_chave", "segredo-teste")
    monkeypatch.setattr(auto_validation, "CfmWebserviceClient", lambda: _Ws())

    def texto(content):
        if content and content.startswith(b"prof"):
            return "RAFAEL PAES MEIRELLES CRM SP 138266"
        return "RAFAEL PAES MEIRELLES CPF 123.456.789-09 NASC 02/01/1980"

    monkeypatch.setattr(auto_validation, "extrair_texto_documento", texto)
    resultado = auto_validation.validar_medico(user, _docs())
    assert resultado.decisao == "aprovado"
    assert resultado.checks["cfm_regular"] is True
    assert resultado.checks["nome_doc_profissional"] is True
    assert resultado.checks["cpf_doc_pessoal"] is True


def test_divergencia_objetiva_de_nome_cfm_reprova(monkeypatch, criar_usuario):
    user, _ = criar_usuario()
    _medico(user)
    monkeypatch.setattr(settings, "cfm_webservice_chave", "segredo-teste")

    class Outro(_CfmOk):
        nome = "OUTRA PESSOA COMPLETAMENTE DIFERENTE"

    class WsOutro(_Ws):
        def consultar(self, numero_crm, uf):
            return Outro()

    monkeypatch.setattr(auto_validation, "CfmWebserviceClient", lambda: WsOutro())
    resultado = auto_validation.validar_medico(user, _docs())
    assert resultado.decisao == "reprovado"
    assert resultado.checks["nome_cadastro_cfm"] is False


def test_ocr_inconclusivo_nao_reprova_em_definitivo(monkeypatch, criar_usuario):
    user, _ = criar_usuario()
    _medico(user)
    monkeypatch.setattr(settings, "cfm_webservice_chave", "segredo-teste")
    monkeypatch.setattr(auto_validation, "CfmWebserviceClient", lambda: _Ws())
    monkeypatch.setattr(auto_validation, "extrair_texto_documento", lambda _content: (_ for _ in ()).throw(RuntimeError("ocr")))
    resultado = auto_validation.validar_medico(user, _docs())
    assert resultado.decisao == "manual"
    assert resultado.conselho_status == "ativo_confirmado"


def test_fluxo_aprovado_libera_sem_revisao_humana(monkeypatch, db, criar_usuario):
    user, _ = criar_usuario()
    _medico(user)

    def submissao(_db, _user, _docs):
        row = KycVerification(owner_id=user.id, status="aguardando_revisao")
        db.add(row)
        db.flush()
        return row

    monkeypatch.setattr(verificacao, "submeter", submissao)
    monkeypatch.setattr(
        auto_validation,
        "validar_medico",
        lambda _user, _docs: auto_validation.ResultadoAutoKyc(
            decisao="aprovado",
            motivo="ok",
            conselho_status="ativo_confirmado",
            conselho_detalhe="ok",
            verificado_em=datetime.now(timezone.utc),
            checks={"cfm_regular": True},
        ),
    )
    row = auto_flow.submeter_com_auto_validacao(db, user, _docs())
    db.commit()
    assert row.status == "aprovado"
    assert row.aprovado_por is None
    assert verificacao.liberado_para_uso(row) is True
    assert db.query(AuditLog).filter(AuditLog.action == "kyc_auto_aprovado").count() == 1


def test_fluxo_reprovado_fica_bloqueado_na_fila_e_notifica_admin(monkeypatch, db, criar_usuario):
    user, _ = criar_usuario()
    _medico(user)

    def submissao(_db, _user, _docs):
        row = KycVerification(owner_id=user.id, status="liberado_conselho_ok")
        db.add(row)
        db.flush()
        return row

    avisos = []
    monkeypatch.setattr(verificacao, "submeter", submissao)
    monkeypatch.setattr(
        auto_validation,
        "validar_medico",
        lambda _user, _docs: auto_validation.ResultadoAutoKyc(
            decisao="reprovado",
            motivo="nome divergente do CFM",
            conselho_status="ativo_confirmado",
            conselho_detalhe="divergência objetiva",
            verificado_em=datetime.now(timezone.utc),
            checks={"nome_cadastro_cfm": False},
        ),
    )
    monkeypatch.setattr(auto_flow.notificar, "notificar_admins_kyc_manual", lambda *a, **kw: avisos.append(kw))
    row = auto_flow.submeter_com_auto_validacao(db, user, _docs())
    db.commit()
    assert row.status == "aguardando_revisao"
    assert row.liberado_em is None
    assert verificacao.liberado_para_uso(row) is False
    assert row in verificacao.listar_pendentes(db)
    assert avisos and "Reprovação automática" in avisos[0]["motivo"]
    assert db.query(AuditLog).filter(AuditLog.action == "kyc_auto_reprovado").count() == 1
