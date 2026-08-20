"""Validação ponta-a-ponta do provedor A1_ARQUIVO, encomendada pelo Rafael
antes do lançamento (12/08/2026) — SEM alterar nenhum arquivo de produção.

Este arquivo é só de LEITURA/EXERCÍCIO do que já existe: reaproveita
`_gerar_pfx()` no mesmo padrão de `test_assinatura_provedor_a1.py`/
`test_assinatura_api.py` (que por sua vez segue o padrão de
`test_corvia_mail.py`/`test_verificacao_pdf.py`, citado no pedido), e chama
só rotas HTTP reais via `TestClient` — nunca a função Python isolada, para
provar o fluxo de ponta a ponta como o médico realmente usa (cadastrar
certificado em Minha Conta → emitir documento em Documentos → baixar PDF
assinado).

Cobre os itens do pedido que os dois arquivos de teste já existentes
(`test_assinatura_provedor_a1.py`, `test_assinatura_api.py`) NÃO cobriam:
- item 2: senha nunca aparece em log, em nenhum ponto do fluxo completo;
- item 4/5: emissão real de documento (`/api/document-templates/gerar-livre`
  + `/gerados/{id}/pdf?metodo=A1_ARQUIVO`) com verificação criptográfica
  externa do PDF assinado (`verificacao_pdf.verificar`, mesmo pyhanko que o
  projeto já usa para conferir a própria assinatura);
- item 6: certificado JÁ EXPIRADO rejeitado com clareza (não existia teste
  disso em nenhum arquivo — só senha errada e arquivo inválido já estavam
  cobertos em `test_assinatura_api.py`); e nenhum vazamento de stack trace
  interno na resposta HTTP para arquivo/senha inválidos;
- item 7: revogação/substituição comparando o CN extraído do PDF ASSINADO
  (não só o metadado do banco) antes e depois da troca;
- item 8 (isolamento cross-user no fluxo de EMISSÃO, não só no de status já
  coberto): usuário B não consegue assinar nem ler documento de A.
"""
from __future__ import annotations

import datetime
import io
import logging

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from app.core.config import settings
from app.models.assinatura import DocumentoEmitido
from app.models.receituario import PrescriptionType
from app.models.subscription import Subscription
from app.services.assinatura import verificacao_pdf


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _gerar_pfx(
    *,
    senha: str = "senha123",
    cn: str = "DR TESTE DA SILVA:12345678900",
    dias_validade: int = 365,
    ja_expirado: bool = False,
) -> bytes:
    """Mesma técnica de `test_assinatura_provedor_a1.py`/`test_assinatura_api.py`
    (autoassinado, sem cadeia ICP-Brasil real — decisão já tomada pelo
    Rafael para esta validação). `ja_expirado=True` gera um certificado cuja
    validade terminou no passado, para exercitar a rejeição."""
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    agora = datetime.datetime.now(datetime.timezone.utc)
    if ja_expirado:
        inicio = agora - datetime.timedelta(days=400)
        fim = agora - datetime.timedelta(days=30)
    else:
        inicio = agora - datetime.timedelta(days=1)
        fim = agora + datetime.timedelta(days=dias_validade)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(nome)
        .issuer_name(nome)
        .public_key(chave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(inicio)
        .not_valid_after(fim)
        .sign(chave, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"teste", key=chave, cert=certificado, cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(senha.encode()),
    )


@pytest.fixture(autouse=True)
def _diretorio_certificados(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "certificados_dir", str(tmp_path / "certificados"))
    monkeypatch.setattr(settings, "documentos_dir", str(tmp_path / "documentos"))


def _conectar_certificado(client, token: str, pfx: bytes, senha: str, *, certificadora=None):
    return client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", pfx, "application/x-pkcs12")},
        data={"senha": senha, **({"certificadora": certificadora} if certificadora else {})},
        headers=_headers(token),
    )


def _emitir_documento_livre(client, token: str, *, titulo="Documento de teste E2E") -> int:
    resposta = client.post(
        "/api/document-templates/gerar-livre",
        json={"titulo": titulo, "corpo": "Corpo de teste do documento livre.", "patient_name": "Paciente Teste"},
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()["id"]


def _baixar_pdf_assinado(client, token: str, gid: int, metodo="A1_ARQUIVO"):
    return client.get(
        f"/api/document-templates/gerados/{gid}/pdf",
        params={"metodo": metodo},
        headers=_headers(token),
    )


# --------------------------------------------------------------------------
# Item 4/5 — fluxo real ponta a ponta: cadastra certificado sintético →
# emite documento → assina com A1_ARQUIVO → baixa o PDF → confirma
# criptograficamente (fora do próprio provedor) que a assinatura é íntegra.
# --------------------------------------------------------------------------


def test_fluxo_completo_emite_e_assina_documento_real_com_a1(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)

    pfx = _gerar_pfx(cn="DR FLUXO COMPLETO:11122233344")
    resp_cert = _conectar_certificado(client, token, pfx, "senha123", certificadora="Certisign")
    assert resp_cert.status_code == 201, resp_cert.text
    assert resp_cert.json()["titular_cn"] == "DR FLUXO COMPLETO:11122233344"

    gid = _emitir_documento_livre(client, token)

    resposta = _baixar_pdf_assinado(client, token, gid)
    assert resposta.status_code == 200, resposta.text
    assert resposta.headers["content-type"] == "application/pdf"
    pdf_bytes = resposta.content
    assert pdf_bytes[:4] == b"%PDF"

    # Verificação EXTERNA, independente do provedor que assinou — mesma
    # ferramenta (pyhanko) que o projeto já usa para conferir assinatura
    # antes de divulgar por e-mail (divulgacao_email.py).
    achado = verificacao_pdf.verificar(pdf_bytes)
    assert achado is not None, "PDF baixado não contém nenhuma assinatura embutida"
    assert achado.intacta is True
    assert achado.estrutura_valida is True
    assert achado.cobre_documento_inteiro is True
    assert achado.titular_cn == "DR FLUXO COMPLETO:11122233344"

    # Reconsultar o mesmo documento serve os MESMOS bytes já assinados (não
    # gera um PDF novo/diferente a cada leitura).
    segunda_leitura = _baixar_pdf_assinado(client, token, gid)
    assert segunda_leitura.content == pdf_bytes


def test_fluxo_completo_emite_rce_e_assina_com_a1(client, db, criar_usuario):
    """Regressão: a RCE revisada era bloqueada antes de chegar ao provedor A1."""
    user, token = criar_usuario(full_name="Dr. Rafael Teste", role="admin")
    _subscribe(db, user.id)
    user.council_name = "CRM"
    user.council_number = "138266"
    user.council_state = "SP"
    user.practice_street = "Rua Tibiriçá"
    user.practice_number = "1172"
    user.practice_city = "Ribeirão Preto"
    user.practice_state = "SP"
    tipo_rce = db.query(PrescriptionType).filter(PrescriptionType.codigo == "RCE").one()
    tipo_rce.ativo = True
    tipo_rce.exige_numeracao_sncr = False
    db.commit()

    certificado = _gerar_pfx(cn="DR RAFAEL TESTE:11122233344")
    conectado = _conectar_certificado(client, token, certificado, "senha123", certificadora="Valid")
    assert conectado.status_code == 201, conectado.text

    criada = client.post(
        "/api/receituario",
        headers=_headers(token),
        json={
            "destinatario": {
                "nome": "Paciente Teste",
                "endereco": "Rua do Paciente, 10, Ribeirão Preto/SP",
                "documento": "123.456.789-00",
            },
            "itens": [{
                "descricao": "Medicamento de teste",
                "apresentacao": "comprimidos",
                "quantidade": "30 comprimidos",
                "quantidade_extenso": "trinta comprimidos",
                "posologia": "Tomar 1 comprimido ao dia.",
                "orientacao": "",
                "uso_continuo": False,
            }],
        },
    )
    assert criada.status_code == 201, criada.text
    documento_id = criada.json()["documentos"][0]["id"]

    revisada = client.post(
        f"/api/receituario/documentos/{documento_id}/revisar",
        headers=_headers(token),
        json={
            "confirmar": True,
            "corrigir_para": "RCE",
            "motivo": "Teste direcionado do fluxo de controle especial.",
        },
    )
    assert revisada.status_code == 200, revisada.text

    emitida = client.post(
        f"/api/receituario/documentos/{documento_id}/emitir",
        headers=_headers(token),
        json={"metodo": "A1_ARQUIVO"},
    )
    assert emitida.status_code == 200, emitida.text
    assert emitida.content.startswith(b"%PDF")

    assinatura = verificacao_pdf.verificar(emitida.content)
    assert assinatura is not None
    assert assinatura.intacta is True
    assert assinatura.estrutura_valida is True
    assert assinatura.cobre_documento_inteiro is True
    assert assinatura.titular_cn == "DR RAFAEL TESTE:11122233344"

    registro = db.query(DocumentoEmitido).filter(
        DocumentoEmitido.tipo == "prescription_document",
        DocumentoEmitido.referencia_id == documento_id,
    ).one()
    assert registro.metodo == "A1_ARQUIVO"
    assert registro.nivel == "qualificada"
    assert registro.assinado_em is not None


def test_pdf_assinado_com_a1_bate_com_o_conteudo_gravado_no_banco(client, db, criar_usuario):
    """Confere que o registro em `documentos_emitidos` (sha256, bytes_tam,
    metodo, nivel) corresponde exatamente ao PDF que o médico baixa —
    sem isso, a auditoria de "o que foi realmente assinado" não teria como
    provar nada."""
    import hashlib

    from app.services.assinatura import emissao as assinatura_emissao

    user, token = criar_usuario()
    _subscribe(db, user.id)
    _conectar_certificado(client, token, _gerar_pfx(), "senha123")
    gid = _emitir_documento_livre(client, token)

    resposta = _baixar_pdf_assinado(client, token, gid)
    assert resposta.status_code == 200

    registro = assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=gid)
    assert registro is not None
    assert registro.metodo == "A1_ARQUIVO"
    assert registro.nivel == "qualificada"
    assert registro.assinado_em is not None
    assert registro.sha256 == hashlib.sha256(resposta.content).hexdigest()
    assert registro.bytes_tam == len(resposta.content)


# --------------------------------------------------------------------------
# Item 2 — senha nunca aparece em log, em nenhum ponto do fluxo completo
# (cadastro incluindo senha errada, e emissão/assinatura de documento).
# --------------------------------------------------------------------------


def test_senha_nunca_aparece_em_log_no_fluxo_completo(client, db, criar_usuario, caplog):
    user, token = criar_usuario()
    _subscribe(db, user.id)

    senha_secreta = "SenhaSuperSecretaNaoDeveVazar!42"
    with caplog.at_level(logging.DEBUG):
        # cadastro com sucesso
        r1 = _conectar_certificado(client, token, _gerar_pfx(senha=senha_secreta), senha_secreta)
        assert r1.status_code == 201

        gid = _emitir_documento_livre(client, token)
        r2 = _baixar_pdf_assinado(client, token, gid)
        assert r2.status_code == 200

        # também no caminho de ERRO (senha errada) — é onde mais se erra
        # colocando a senha na mensagem de exceção/log "pra ajudar a
        # debugar".
        r3 = _conectar_certificado(client, token, _gerar_pfx(senha="outra"), "senha-errada-de-proposito")
        assert r3.status_code == 422

    texto_completo_dos_logs = "\n".join(r.getMessage() for r in caplog.records)
    assert senha_secreta not in texto_completo_dos_logs
    assert "senha-errada-de-proposito" not in texto_completo_dos_logs
    # Confere também os `args` brutos de cada record (caso a senha tivesse
    # sido passada como argumento de formatação, e não já interpolada).
    for r in caplog.records:
        for arg in (r.args or ()):
            assert senha_secreta != arg
            assert "senha-errada-de-proposito" != arg


def test_senha_cifrada_no_banco_nunca_e_texto_plano(client, db, criar_usuario):
    """Confirma lendo o banco de verdade (não só o código) que
    `digital_certificates.senha_cifrada` não contém a senha em claro."""
    from app.models.assinatura import DigitalCertificate

    user, token = criar_usuario()
    _subscribe(db, user.id)
    senha_secreta = "MinhaSenhaDeCertificadoBemEspecifica99"
    _conectar_certificado(client, token, _gerar_pfx(senha=senha_secreta), senha_secreta)

    registro = db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).first()
    assert registro is not None
    assert isinstance(registro.senha_cifrada, (bytes, bytearray))
    assert senha_secreta.encode("utf-8") not in bytes(registro.senha_cifrada)


# --------------------------------------------------------------------------
# Item 6 — certificado expirado / senha incorreta / arquivo inválido falham
# com segurança: mensagem clara, HTTP correto, sem stack trace vazando.
# --------------------------------------------------------------------------


def test_certificado_expirado_e_rejeitado_no_cadastro(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx_vencido = _gerar_pfx(cn="DR VENCIDO:99999999999", ja_expirado=True)

    resposta = _conectar_certificado(client, token, pfx_vencido, "senha123")

    assert resposta.status_code == 422
    detalhe = resposta.json()["detail"]
    assert "venceu" in detalhe.lower() or "vencido" in detalhe.lower()
    # Não deixou o certificado "meio cadastrado".
    status = client.get("/api/assinatura/certificado-a1", headers=_headers(token))
    assert status.json() == {"conectado": False}


def test_certificado_que_vence_entre_cadastro_e_assinatura_bloqueia_emissao(client, db, criar_usuario):
    """Cenário mais realista que o de cima: certificado válido no momento do
    cadastro, mas cuja validade já passou no momento de EMITIR — confirma
    que `disponivel()` (chamado antes de assinar) recusa, e que a rota HTTP
    devolve 409 com o motivo, "nada foi simulado", sem gerar PDF nenhum."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    # válido por só 1 dia a partir de "agora - 1 dia" => já vencido daqui a
    # poucos segundos de folga não é confiável para teste; em vez disso,
    # cadastra um válido e depois o substitui, no banco, por um já vencido
    # (equivalente a "o tempo passou"), sem tocar em nenhum código de
    # produção — só ajuste de dado no teste.
    _conectar_certificado(client, token, _gerar_pfx(cn="DR PRESTES A VENCER:1"), "senha123")

    from datetime import timedelta

    from app.models.assinatura import DigitalCertificate
    registro = db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).first()
    registro.valido_ate = registro.valido_ate - timedelta(days=1000)
    db.commit()

    gid = _emitir_documento_livre(client, token)
    resposta = _baixar_pdf_assinado(client, token, gid)

    assert resposta.status_code == 409
    corpo = resposta.json()["detail"]
    assert corpo["nada_foi_simulado"] is True
    assert any("venceu" in b.lower() for b in corpo["bloqueios"])

    # E não ficou nenhum `DocumentoEmitido` gravado como se tivesse assinado.
    from app.services.assinatura import emissao as assinatura_emissao
    assert assinatura_emissao.buscar(db, tipo=assinatura_emissao.TIPO_DOCUMENTO, referencia_id=gid) is None


def test_senha_incorreta_no_cadastro_rejeitada_sem_vazar_detalhe_interno(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    pfx = _gerar_pfx(senha="senha-certa-do-certificado")

    resposta = _conectar_certificado(client, token, pfx, "senha-totalmente-errada")

    assert resposta.status_code == 422
    detalhe = resposta.json()["detail"]
    assert isinstance(detalhe, str)
    # Não é traceback nem nome de exceção interna do cryptography/pyhanko.
    for termo_proibido in ("Traceback", "raise ", ".py\"", "ValueError:", "cryptography.hazmat"):
        assert termo_proibido not in detalhe


def test_arquivo_nao_pkcs12_rejeitado_sem_vazar_stack_trace(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)

    resposta = client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", b"isto claramente nao e um certificado PKCS12" * 5, "application/x-pkcs12")},
        data={"senha": "qualquer-coisa"},
        headers=_headers(token),
    )

    assert resposta.status_code == 422
    detalhe = resposta.json()["detail"]
    assert isinstance(detalhe, str)
    for termo_proibido in ("Traceback", "raise ", ".py\"", "line ", "cryptography.hazmat"):
        assert termo_proibido not in detalhe


def test_arquivo_vazio_e_422_nao_500(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/assinatura/certificado-a1",
        files={"arquivo": ("certificado.pfx", b"", "application/x-pkcs12")},
        data={"senha": "qualquer"},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


# --------------------------------------------------------------------------
# Item 7 — revogação/substituição: assina antes, troca, assina depois,
# compara o CN extraído do PDF de cada lado (não só metadado do banco).
# --------------------------------------------------------------------------


def test_troca_de_certificado_reflete_no_proximo_documento_assinado(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)

    _conectar_certificado(client, token, _gerar_pfx(cn="DR CERTIFICADO ANTIGO:11111111111"), "senha123")
    gid_antes = _emitir_documento_livre(client, token, titulo="Documento antes da troca")
    pdf_antes = _baixar_pdf_assinado(client, token, gid_antes)
    assert pdf_antes.status_code == 200
    achado_antes = verificacao_pdf.verificar(pdf_antes.content)
    assert achado_antes.titular_cn == "DR CERTIFICADO ANTIGO:11111111111"

    # Troca: reenviar substitui (mesmo endpoint, não precisa remover antes —
    # `certificado_a1.salvar()` já documenta isso).
    resp_troca = _conectar_certificado(client, token, _gerar_pfx(cn="DR CERTIFICADO NOVO:22222222222"), "senha123")
    assert resp_troca.status_code == 201
    assert resp_troca.json()["titular_cn"] == "DR CERTIFICADO NOVO:22222222222"

    gid_depois = _emitir_documento_livre(client, token, titulo="Documento depois da troca")
    pdf_depois = _baixar_pdf_assinado(client, token, gid_depois)
    assert pdf_depois.status_code == 200
    achado_depois = verificacao_pdf.verificar(pdf_depois.content)
    assert achado_depois.titular_cn == "DR CERTIFICADO NOVO:22222222222"

    # O documento já emitido ANTES da troca não é reescrito/re-assinado por
    # tabela — continua servindo os mesmos bytes de antes (mesmo assert já
    # coberto acima em outro teste, reforçado aqui no contexto da troca).
    pdf_antes_de_novo = _baixar_pdf_assinado(client, token, gid_antes)
    assert pdf_antes_de_novo.content == pdf_antes.content
    achado_antes_de_novo = verificacao_pdf.verificar(pdf_antes_de_novo.content)
    assert achado_antes_de_novo.titular_cn == "DR CERTIFICADO ANTIGO:11111111111"


def test_remover_certificado_bloqueia_emissao_seguinte_ate_conectar_outro(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    _conectar_certificado(client, token, _gerar_pfx(), "senha123")
    gid1 = _emitir_documento_livre(client, token)
    assert _baixar_pdf_assinado(client, token, gid1).status_code == 200

    resp_remocao = client.delete("/api/assinatura/certificado-a1", headers=_headers(token))
    assert resp_remocao.status_code == 204

    gid2 = _emitir_documento_livre(client, token)
    resposta = _baixar_pdf_assinado(client, token, gid2)
    assert resposta.status_code == 409
    assert resposta.json()["detail"]["nada_foi_simulado"] is True


# --------------------------------------------------------------------------
# Item 3/8 — isolamento cross-user no fluxo de EMISSÃO (não só no de status,
# já coberto em test_assinatura_api.py) e ausência de URL pública.
# --------------------------------------------------------------------------


def test_usuario_b_nao_consegue_assinar_documento_de_a_com_certificado_de_a(client, db, criar_usuario):
    """B não tem certificado próprio e não pode, de forma alguma, usar o de
    A — nem ler o documento de A (404, não 403 nem 200 com dado de outro)."""
    userA, tokenA = criar_usuario(email="medico-a@teste.local")
    _subscribe(db, userA.id)
    userB, tokenB = criar_usuario(email="medico-b@teste.local")
    _subscribe(db, userB.id)

    _conectar_certificado(client, tokenA, _gerar_pfx(cn="DR A:12312312300"), "senha123")
    gid_de_a = _emitir_documento_livre(client, tokenA, titulo="Documento do médico A")

    # B não vê nem lê o documento de A.
    resposta_b = client.get(f"/api/document-templates/gerados/{gid_de_a}", headers=_headers(tokenB))
    assert resposta_b.status_code == 404

    resposta_pdf_b = _baixar_pdf_assinado(client, tokenB, gid_de_a)
    assert resposta_pdf_b.status_code == 404

    # E B, mesmo emitindo o PRÓPRIO documento, não tem como assinar com o
    # certificado de A — sem certificado próprio, recebe 409 (indisponível),
    # nunca um PDF assinado com o CN de A.
    gid_de_b = _emitir_documento_livre(client, tokenB, titulo="Documento do médico B")
    resposta_b_proprio = _baixar_pdf_assinado(client, tokenB, gid_de_b)
    assert resposta_b_proprio.status_code == 409


def test_dois_certificados_de_usuarios_diferentes_nao_se_misturam_na_assinatura(client, db, criar_usuario):
    userA, tokenA = criar_usuario(email="isolamento-a@teste.local")
    _subscribe(db, userA.id)
    userB, tokenB = criar_usuario(email="isolamento-b@teste.local")
    _subscribe(db, userB.id)

    _conectar_certificado(client, tokenA, _gerar_pfx(cn="DR ISOLAMENTO A:11111111111", senha="senha123"), "senha123")
    _conectar_certificado(client, tokenB, _gerar_pfx(cn="DR ISOLAMENTO B:22222222222", senha="senha456"), "senha456")

    gid_a = _emitir_documento_livre(client, tokenA, titulo="Doc A")
    gid_b = _emitir_documento_livre(client, tokenB, titulo="Doc B")

    pdf_a = _baixar_pdf_assinado(client, tokenA, gid_a)
    pdf_b = _baixar_pdf_assinado(client, tokenB, gid_b)
    assert pdf_a.status_code == 200
    assert pdf_b.status_code == 200

    cn_a = verificacao_pdf.verificar(pdf_a.content).titular_cn
    cn_b = verificacao_pdf.verificar(pdf_b.content).titular_cn
    assert cn_a == "DR ISOLAMENTO A:11111111111"
    assert cn_b == "DR ISOLAMENTO B:22222222222"
    assert cn_a != cn_b


def test_arquivo_de_certificado_nao_e_alcancavel_por_url_publica(client, db, criar_usuario, tmp_path):
    """Confirma, em vez de supor, que o nome de arquivo cifrado gravado no
    cofre não corresponde a nenhuma rota pública servida pela aplicação —
    a única exposição estática do projeto é `/fotos/*` (ver Caddyfile), e
    o `certificados_dir` sequer é montado no serviço `caddy`
    (docker-compose.prod.yml) nem tem qualquer rota `StaticFiles`/`mount`
    dedicada em `app/main.py` (conferido por grep, sem nenhuma ocorrência)."""
    import subprocess

    user, token = criar_usuario()
    _subscribe(db, user.id)
    _conectar_certificado(client, token, _gerar_pfx(), "senha123")

    from app.models.assinatura import DigitalCertificate
    registro = db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).first()
    assert registro is not None

    # Nenhuma rota pública/anônima da aplicação serve arquivo por nome.
    resposta_sem_auth = client.get(f"/{registro.arquivo_nome}")
    assert resposta_sem_auth.status_code == 404
    resposta_fotos = client.get(f"/fotos/{registro.arquivo_nome}")
    assert resposta_fotos.status_code == 404

    # E não há `StaticFiles`/`.mount(` no app apontando para certificados_dir.
    saida = subprocess.run(
        ["grep", "-rn", "StaticFiles\\|\\.mount(", "/root/corvia-stabilizacao/backend/app/main.py"],
        capture_output=True, text=True,
    )
    assert "certificado" not in saida.stdout.lower()
