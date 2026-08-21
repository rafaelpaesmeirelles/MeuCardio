from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from app.services.assinatura import validacao_publica


ROOT = Path(__file__).resolve().parents[2]


def test_codigo_novo_tem_128_bits_e_legado_fica_validacao_only():
    codigo = validacao_publica.codigo_documento(
        tipo="prescription_document", referencia_id=123, criado_por=7,
    )
    prefixo, mac = codigo.split("-", 1)
    assert prefixo == "R123"
    assert len(mac) == 32
    assert validacao_publica.codigo_permite_download(codigo) is True

    legado = f"R123-{mac[:16]}"
    assert validacao_publica.codigo_permite_download(legado) is False
    assert validacao_publica.normalizar_codigo(f"  {legado.lower()}  ") == legado


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
        valido_de=agora - timedelta(days=30),
        valido_ate=agora + timedelta(days=30),
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

    # O payload público de validação não inclui itens, CID nem destinatário.
    bloco = api[api.index('@router.get("/validar/{codigo}")'):api.index('@router.get("/validar/{codigo}/pdf")')]
    assert '"itens"' not in bloco
    assert '"cid"' not in bloco
    assert '"destinatario"' not in bloco

    assert "Baixar PDF original assinado" in pagina
    assert "Validar independentemente no ITI" in pagina
    assert "Emissão CorVIA confirmada" in pagina
