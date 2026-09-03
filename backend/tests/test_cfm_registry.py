from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import httpx
import pytest

from app.services.cfm_registry import (
    CFM_NOT_FOUND_CODE,
    CFM_WEBSERVICE_DEFAULT_URL,
    UFS,
    CfmDatasetError,
    CfmWebserviceClient,
    CfmWebserviceError,
    descobrir_form_acesso,
    parse_consultar_response,
    validar_totalzip,
)


def _totalzip(*, extra_ba: str | None = None, omitir: str | None = None) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for uf in sorted(UFS):
            if uf == omitir:
                continue
            linhas = [f"1!{uf}!MEDICO {uf}!PRINCIPAL!Ativo!CARDIOLOGIA - RQE Nº 123\r\n"]
            if uf == "BA" and extra_ba:
                linhas.append(extra_ba)
            archive.writestr(f"{uf}.txt", "".join(linhas).encode("utf-8"))
    return buffer.getvalue()


def _soap_sucesso() -> bytes:
    return b"""<?xml version='1.0' encoding='UTF-8'?>
<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>
 <soap:Body>
  <ConsultarResponse xmlns='http://servico.cfm.org.br/'>
   <return>
    <crm>12345</crm>
    <uf>SP</uf>
    <nome>MEDICO TESTE</nome>
    <dataAtualizacao>02/09/2026</dataAtualizacao>
    <situacao><codigo>A</codigo><descricao>REGULAR</descricao></situacao>
    <tipoInscricao><codigo>P</codigo><descricao>PRINCIPAL</descricao></tipoInscricao>
    <especialidade>CARDIOLOGIA - RQE NÂ    <especialidade>CARDIOLOGIA - RQE N\xc2º    <especialidade>CARDIOLOGIA - RQE N\xc2\xba 123</especialidade>
    <especialidade>CLINICA MEDICA - RQE NÂ    <especialidade>CLINICA MEDICA - RQE N\xc2º    <especialidade>CLINICA MEDICA - RQE N\xc2\xba 456</especialidade>
   </return>
  </ConsultarResponse>
 </soap:Body>
</soap:Envelope>"""


def _soap_erro(codigo: str) -> bytes:
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>
 <soap:Body><ConsultarResponse xmlns='http://servico.cfm.org.br/'><return>
  <codigoErro>{codigo}</codigoErro><descricaoErro>erro controlado</descricaoErro>
 </return></ConsultarResponse></soap:Body>
</soap:Envelope>""".encode()


def test_totalzip_exige_as_27_ufs_e_preserva_crm_anomalo() -> None:
    payload = _totalzip(extra_ba="-999090!BA!REGISTRO LEGADO!PRINCIPAL!Ativo!\r\n")
    digest, total, invalidos = validar_totalzip(payload)
    assert len(digest) == 64
    assert total == 28
    assert invalidos == 1

    with pytest.raises(CfmDatasetError, match="incompleto"):
        validar_totalzip(_totalzip(omitir="AC"))


def test_form_download_exige_post_e_mesmo_host() -> None:
    html = """
    <html><body><form method='post' action='/listamedicos/download/verificar'>
      <input type='hidden' name='_token' value='abc'>
      <input type='text' name='codigoAcesso'>
      <button type='submit'>Baixar</button>
    </form></body></html>
    """
    action, hidden, campo = descobrir_form_acesso(html)
    assert action == "https://sistemas.cfm.org.br/listamedicos/download/verificar"
    assert hidden == {"_token": "abc"}
    assert campo == "codigoAcesso"


def test_parse_consultar_response_lê_campos_e_especialidades_repetidas() -> None:
    resultado = parse_consultar_response(_soap_sucesso())
    assert resultado.crm_exibicao == "12345"
    assert resultado.uf == "SP"
    assert resultado.nome == "MEDICO TESTE"
    assert resultado.situacao_codigo == "A"
    assert resultado.is_regular is True
    assert resultado.tipo_inscricao_codigo == "P"
    assert resultado.data_atualizacao.isoformat() == "2026-09-02"
    assert len(resultado.especialidades) == 2


def test_http_200_com_codigo_erro_continua_sendo_erro_cfm() -> None:
    with pytest.raises(CfmWebserviceError) as info:
        parse_consultar_response(_soap_erro(CFM_NOT_FOUND_CODE))
    assert info.value.codigo == CFM_NOT_FOUND_CODE
    assert info.value.transient is False


def test_webservice_reexecuta_apenas_erro_transitorio_e_nao_vaza_chave_na_url() -> None:
    chamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        chamadas.append(request)
        assert "segredo-teste" not in str(request.url)
        assert request.headers["content-type"].startswith("text/xml")
        assert request.headers["soapaction"] == '""'
        if len(chamadas) == 1:
            return httpx.Response(200, content=_soap_erro("2030"))
        return httpx.Response(200, content=_soap_sucesso())

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    try:
        ws = CfmWebserviceClient(
            chave="segredo-teste",
            url=CFM_WEBSERVICE_DEFAULT_URL,
            client=client,
        )
        resultado = ws.consultar("12345", "sp", max_attempts=2)
    finally:
        client.close()
    assert resultado.is_regular is True
    assert len(chamadas) == 2


def test_erro_de_configuracao_nao_expoe_chave() -> None:
    chave = "segredo-super-sensivel"
    with pytest.raises(CfmWebserviceError) as info:
        CfmWebserviceClient(chave=chave, url="https://example.com/ws")
    assert chave not in str(info.value)
