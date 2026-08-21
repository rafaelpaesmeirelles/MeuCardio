from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from app.models.assinatura import DocumentoEmitido
from app.services.assinatura import validacao_publica


ROOT = Path(__file__).resolve().parents[2]


def test_codigo_novo_tem_128_bits_e_legado_fica_validacao_only():
    novo = validacao_publica.novo_codigo_documento(
        tipo="prescription_document", referencia_id=123,
    )
    prefixo, token = novo.codigo.split("-", 1)
    assert prefixo == "R123"
    assert len(token) == 32
    assert len(novo.hash_persistido) == 64
    assert validacao_publica.codigo_permite_download(novo.codigo) is True

    legado = validacao_publica.codigo_documento(
        tipo="prescription_document", referencia_id=123, criado_por=7,
    )
    assert len(legado.split("-", 1)[1]) == 16
    assert validacao_publica.codigo_permite_download(legado) is False
    assert validacao_publica.normalizar_codigo(f"  {legado.lower()}  ") == legado


def test_capability_nova_e_unica_por_emissao_e_localiza_artefato_exato(db, criar_usuario):
    user, _token = criar_usuario(email="capability-emissao@teste.local")
    primeiro = validacao_publica.novo_codigo_documento(
        tipo="prescription_document", referencia_id=500,
    )
    segundo = validacao_publica.novo_codigo_documento(
        tipo="prescription_document", referencia_id=500,
    )
    assert primeiro.codigo != segundo.codigo

    r1 = DocumentoEmitido(
        tipo="prescription_document", referencia_id=500, metodo="MANUAL", nivel="nenhuma",
        arquivo_nome="primeiro.enc", sha256="a" * 64, bytes_tam=1,
        validation_token_hash=primeiro.hash_persistido, criado_por=user.id,
    )
    r2 = DocumentoEmitido(
        tipo="prescription_document", referencia_id=500, metodo="MANUAL", nivel="nenhuma",
        arquivo_nome="segundo.enc", sha256="b" * 64, bytes_tam=1,
        validation_token_hash=segundo.hash_persistido, criado_por=user.id,
    )
    db.add_all([r1, r2])
    db.commit()

    assert validacao_publica.localizar(db, primeiro.codigo).id == r1.id
    assert validacao_publica.localizar(db, segundo.codigo).id == r2.id


def test_validacao_expoe_certificado_real_e_distingue_assinatura_no_corvia(monkeypatch):
    agora = datetime.now(timezone.utc)
    pdf = b"%PDF-1.4 corvia signed bytes"
    import hashlib

    registro = SimpleNamespace(
        metodo="A1_ARQUIVO",
        nivel="qualificada",
        assinado_em=agora,
        sha256=hashlib.sha256(pdf).hexdigest(),
        criado_em=agora - timedelta(seconds=2),
    )
    assinatura = SimpleNamespace(
        intacta=True,
        estrutura_valida=True,
        cobre_documento_inteiro=True,
        titular_cn="MEDICO TESTE",
        emissor_cn="AC TESTE ICP-BRASIL",
        numero_serie="123456789",
        valido_de=(agora - timedelta(days=30)).replace(tzinfo=None),
        valido_ate=(agora + timedelta(days=30)).replace(tzinfo=None),
        assinado_em=agora,
        politicas_certificado=("2.16.76.1.2.1.1",),
        qualificada_icp_brasil=True,
    )

    monkeypatch.setattr(validacao_publica.emissao, "ler_bytes", lambda _registro: pdf)
    monkeypatch.setattr(validacao_publica.verificacao_pdf, "verificar", lambda _pdf: assinatura)

    resultado = validacao_publica.validar(registro)
    assert resultado.valido is True
    assert resultado.fluxo_assinatura == "corvia_local"
    assert resultado.numero_serie == "123456789"
    assert resultado.emissor_certificado == "AC TESTE ICP-BRASIL"
    assert resultado.certificado_valido_no_momento_assinatura is True
    assert resultado.qualificada_icp_brasil is True


def test_portal_publico_nao_expoe_conteudo_clinico_e_oferece_duas_acoes():
    api = (ROOT / "backend/app/api/documentos_publicos.py").read_text(encoding="utf-8")
    pagina = (ROOT / "frontend/src/pages/ValidarDocumento.tsx").read_text(encoding="utf-8")

    assert '@router.get("/validar/{codigo}/pdf")' in api
    assert "codigo_permite_download" in api
    assert '"pdf_original_url"' in api
    assert '"validacao_independente_url"' in api
    assert '"prescritor"' in api
    assert '"numero_serie_certificado"' in api
    assert '"certificado_valido_no_momento_assinatura"' in api

    bloco = api[api.index('@router.get("/validar/{codigo}")'):api.index('@router.get("/validar/{codigo}/pdf")')]
    assert '"itens"' not in bloco
    assert '"cid"' not in bloco
    assert '"destinatario"' not in bloco

    assert "Baixar PDF original assinado" in pagina
    assert "Validar independentemente no ITI" in pagina
    assert "Emissão CorVIA confirmada" in pagina
