"""Ensaios locais das correções CIE/CI/EXP; sem banco, rede, envio ou assinatura real."""
from __future__ import annotations

import base64
from email import policy
from email.parser import BytesParser
from io import BytesIO
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

from app.services import calculators as calc, external_mail, apple_mail, yahoo_mail
from app.services.assinatura import smime
from app.services.mail_attachments import MailAttachment
from app.services.exportacao_conteudo import ConteudoExportavel, SecaoExportacao, _secoes_markdown, _sem_markdown, gerar_pdf, catalogo
from app.services.exportacao_office import gerar_docx, gerar_pptx
from app.services.export_links import absolute_link, link_runs, linked_lines, plain_text
from app.services.pdf.layout import Documento, quebrar
from app.services.pdf.nucleo import largura_texto
from app.api import exportacao_universal as api
from app.models.content import Document
from app.models.user import User
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/correcoes-auditoria-20260912/provas-ciencia"
OUT.mkdir(parents=True, exist_ok=True)
checks = []


def checked(name, detail):
    checks.append({"verificacao": name, "resultado": "passou", "evidencia": detail})


# Registros sintéticos já auditados, comparando resultados completos anteriores.
rows = json.loads((ROOT / "docs/auditoria-integral-20260912/ciencia-calculadoras.json").read_text(encoding="utf-8"))
samples = {r["slug"]: r for r in rows if r["verificacao"] == "executou_cenario_sintetico"}
for slug, row in samples.items():
    assert calc.run(slug, row["cenario"]) == row["resultado"], slug
checked("CIE-03: fórmulas preservadas", f"{len(samples)} cenários com resultados completos idênticos à auditoria")
rejections = 0
for slug, row in samples.items():
    definition = calc.REGISTRY[slug]
    for field in definition.fields:
        invalid = []
        if field.type == "number":
            invalid = [float("nan"), float("inf"), True, [], "não numérico"]
            if field.min is not None:
                invalid.append(field.min - 1)
            if field.max is not None:
                invalid.append(field.max + 1)
        elif field.type == "select":
            invalid = ["opção inexistente"]
        elif field.type == "boolean":
            invalid = ["false", 1]
        for value in invalid:
            try:
                calc.validate_payload(definition, {**row["cenario"], field.name: value})
            except calc.CalculatorInputError:
                rejections += 1
            else:
                raise AssertionError((slug, field.name, value))
checked("CIE-03: entradas inválidas", f"{rejections} rejeições focais de tipos, enumerações, finitude e limites declarados")
infusion = next(d for d in calc.REGISTRY.values() if any(f.required_when for f in d.fields))
weight = next(f for f in infusion.fields if f.required_when)
base = dict(samples[infusion.slug]["cenario"])
drug_field = next(f for f in infusion.fields if f.name == "droga")
weight_based = set(weight.required_when["droga"])
for option in drug_field.options:
    payload = {**base, "droga": option["value"]}
    payload.pop("peso", None)
    try:
        calc.validate_payload(infusion, payload)
    except calc.CalculatorInputError:
        assert option["value"] in weight_based
    else:
        assert option["value"] not in weight_based
checked("CIE-03: peso condicional", "Peso exigido somente nas infusões cujo esquema usa kg; limites terapêuticos usuais continuam avisos")


# As consultas são construídas, mas nenhum banco é acessado.
class CatalogQuery:
    def __init__(self, rows=()): self.rows = list(rows)
    def filter(self, *args):
        for expr in args:
            key = getattr(getattr(expr, "left", None), "key", None)
            value = getattr(getattr(expr, "right", None), "value", None)
            if key == "slug": self.rows = [row for row in self.rows if row.slug == value]
            if key == "published": self.rows = [row for row in self.rows if row.published]
        return self
    def options(self, *args): return self
    def order_by(self, *args): return self
    def distinct(self): return self
    def limit(self, *args): raise AssertionError("Corte prematuro no catálogo")
    def yield_per(self, size): return iter(self.rows)
    def all(self): return self.rows

documents = [NS(slug=f"demo-{i}", title=f"Artigo demonstrativo {i}", theme="Tema", kind="artigo", published=True) for i in range(2601)]
documents[-1].title = "Marcador exclusivo depois do antigo limite"
documents.append(NS(slug="retido", title=documents[-1].title, theme="Tema", kind="artigo", published=False))
fake_db = NS(query=lambda model: CatalogQuery(documents if model is Document else []))
found = catalogo(fake_db, q="Marcador exclusivo", tipo="documento", limite=120)
assert len(found) == 1 and found[0]["slug"] == "demo-2600", found
found = catalogo(fake_db, tipo="documento", slug="demo-2600", limite=1)
assert found[0]["slug"] == "demo-2600"
checked("CI-16: catálogo inteiro", "Item 2.601 encontrado por pesquisa e slug; item não publicado excluído; nenhuma consulta usa limit antes do filtro")


attachment = MailAttachment("amostra.pdf", b"%PDF-1.4\nARQUIVO SINTETICO", "application/pdf")
def attachment_from_mime(raw):
    message = BytesParser(policy=policy.default).parsebytes(raw)
    parts = list(message.iter_attachments())
    assert len(parts) == 1
    assert parts[0].get_filename() == attachment.filename
    assert parts[0].get_payload(decode=True) == attachment.content
    return message

requests = []
def request(*args, **kwargs):
    requests.append(kwargs)
    return NS(json=lambda: {"id": "synthetic-id"})
with patch.object(external_mail, "_request", request):
    external_mail.send_message(None, NS(provider="google_calendar"), to="destino@example.com", subject="Amostra", html="<p>Exemplo</p>", attachments=[attachment])
    raw = requests[-1]["json"]["raw"]
    attachment_from_mime(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))
    external_mail.send_message(None, NS(provider="microsoft_365"), to="destino@example.com", subject="Amostra", html="<p>Exemplo</p>", attachments=[attachment])
    graph_file = requests[-1]["json"]["message"]["attachments"][0]
    assert base64.b64decode(graph_file["contentBytes"]) == attachment.content
checked("CI-17: anexos Google/Microsoft", "MIME e JSON inspecionados em fakes; bytes e nome preservados; nenhuma chamada de rede")

smtp_messages = []
class FakeSMTP:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def starttls(self): pass
    def login(self, *args): pass
    def send_message(self, message, **kwargs): smtp_messages.append(message.as_bytes())
    def sendmail(self, *args): raise AssertionError("Não se esperava mensagem assinada real")
for module in (apple_mail, yahoo_mail):
    with patch.object(module, "_credenciais", return_value=("origem@example.com", "fake")), patch.object(module.smtplib, "SMTP", FakeSMTP):
        module.send_message({}, to="destino@example.com", subject="Amostra", html="<p>Exemplo</p>", attachments=[attachment])
    attachment_from_mime(smtp_messages[-1])
checked("CI-17: anexos iCloud/Yahoo", "SMTP substituído integralmente por fake local; MIME preserva o arquivo")

signed_input = []
class FakeSignature:
    def set_data(self, data): signed_input.append(data); return self
    def add_signer(self, *args): return self
    def add_certificate(self, *args): return self
    def sign(self, *args): return b"FAKE SIGNATURE ONLY"
fake_cert = NS(dados=NS(certificado=None, chave_privada=None, cadeia=[]))
with patch.object(smime, "carregar_para_assinar", return_value=fake_cert), patch.object(smime.pkcs7, "PKCS7SignatureBuilder", FakeSignature):
    assert smime.montar_corpo_assinado(None, None, html="<p>Exemplo</p>", attachments=[attachment]) == b"FAKE SIGNATURE ONLY"
attachment_from_mime(signed_input[0])
with patch.object(smime, "montar_mensagem_assinada", side_effect=smime.SmimeIndisponivel("Sem certificado")), patch.object(external_mail, "_request", side_effect=AssertionError("Envio indevido")):
    try:
        external_mail.send_message(None, NS(provider="google_calendar", display_name="origem@example.com", external_account_id=None), to="destino@example.com", subject="Amostra", html="", attachments=[attachment], user=NS(), assinar_smime=True)
    except external_mail.ExternalMailError as error:
        assert error.status_code == 409
    else:
        raise AssertionError("Não deve enviar sem a assinatura obrigatória")
checked("CI-17: S/MIME", "Anexo incluído antes da assinatura, com construtor criptográfico fake; falha de certificado bloqueia transporte")

integration = NS(id=19, owner_id=42, provider="google_calendar", capabilities={"send_mail": True}, display_name="origem@example.com", external_account_id=None)
user = NS(id=42, investidor=False, email_assinatura_digital_ativa=True)
db = NS(add=lambda *args: None, commit=lambda: None)
query = NS(filter=lambda *args: query, first=lambda: integration)
order_query = NS(order_by=lambda *args: NS(all=lambda: [integration]))
pedido = api.PedidoEnvioEmail(itens=[{"tipo": "documento", "slug": "amostra"}], para="destino@example.com", conta_id="19")
generated = api.ArquivoGerado(nome="amostra.pdf", titulo="Amostra", conteudo=attachment.content, quantidade=1, itens=[], formato="pdf", media_type="application/pdf")
captured = []
with patch.object(api, "assinatura_email_ativa", return_value=True), patch.object(api, "_integracoes_de_envio", return_value=query), patch.object(api, "_gerar_do_pedido", return_value=generated), patch.object(api, "montar_assinatura_html", return_value=None), patch.object(api.external_mail, "send_message", side_effect=lambda *a, **kw: captured.append(kw) or {"id":"fake"}):
    result = api.enviar_conteudo_por_email(pedido, db=db, user=user)
    assert result["message_id"] == "fake" and captured[0]["attachments"][0].content == attachment.content
    assert captured[0]["assinar_smime"] is True
    integration.capabilities = {}
    captured.clear()
    try: api.enviar_conteudo_por_email(pedido, db=db, user=user)
    except api.HTTPException as error: assert error.status_code == 409
    else: raise AssertionError("Conta sem send_mail aceita")
    assert not captured
    integration.capabilities = {"send_mail": True}
    query.first = lambda: None
    try: api.enviar_conteudo_por_email(pedido, db=db, user=user)
    except api.HTTPException as error: assert error.status_code == 409
    else: raise AssertionError("Conta ausente/fora de escopo aceita")
with patch.object(api, "assinatura_email_ativa", return_value=True), patch.object(api, "_integracoes_de_envio", return_value=order_query):
    status = api.disponibilidade_corvia_mail(db=db, user=user)
    assert status["contas"][0]["id"] == "19" and status["disponivel"]
filters = []
api._integracoes_de_envio(NS(query=lambda model: NS(filter=lambda *args: filters.extend(args))), user)
compiled = " ".join(str(f.compile(compile_kwargs={"literal_binds": True})) for f in filters)
assert "owner_id = 42" in compiled and "enabled IS true" in compiled and "status = 'connected'" in compiled
checked("CI-17: seleção e permissão", "API fake entrega anexo ao transporte escolhido, lista conta S/MIME e recusa conta ausente/sem envio; SQL escopa titular, conexão e habilitação")


# Exportações reais locais a partir de conteúdo público no repositório.
source = (ROOT / "content/Geral/albuminuria-e-tfge-como-eixo-transversal-de-risco-cardiovascular.md").read_text(encoding="utf-8")
body = source.split("---", 2)[-1]
item = ConteudoExportavel("documento", "amostra-auditoria", "Albuminúria e TFGe como eixo transversal de risco cardiovascular", "Prevenção cardiovascular", secoes=_secoes_markdown(body))
expected = {url for sec in item.secoes for text in [*sec.paragrafos, *sec.itens, sec.destaque or ""] for _, url in link_runs(text) if url}
assert len(expected) >= 3 and all(url.startswith("https://") for url in expected)
assert "javascript:" not in _sem_markdown("[inseguro](javascript:alert)")
assert absolute_link("//outro.example/a") is None
assert absolute_link("https://nome:senha@example.com") is None
assert "foo_bar" in _sem_markdown("[Nome](/biblioteca/foo_bar)")
formats = {}
for format, generator in (("pdf", gerar_pdf), ("docx", gerar_docx), ("pptx", gerar_pptx)):
    data = generator([item], user=User(full_name="Profissional demonstrativo"), incluir_dados_assinante=False, titulo="Validação local de exportação")
    (OUT / f"exportacao-corrigida.{format}").write_bytes(data)
    targets = set()
    if format == "pdf":
        pdf = PdfReader(BytesIO(data), strict=True)
        for page in pdf.pages:
            for ref in page.get("/Annots", []):
                annotation = ref.get_object()
                targets.add(str(annotation["/A"]["/URI"]))
                x1, y1, x2, y2 = map(float, annotation["/Rect"])
                assert 0 <= x1 < x2 <= 595.3 and 0 <= y1 < y2 <= 842
        formats[format] = {"bytes": len(data), "paginas": len(pdf.pages), "hyperlinks": len(targets)}
    else:
        with zipfile.ZipFile(BytesIO(data)) as z:
            assert z.testzip() is None
            for name in z.namelist():
                if name.endswith((".xml", ".rels")):
                    root = ET.fromstring(z.read(name))
                    for elem in root.iter():
                        if elem.get("Type", "").endswith("/hyperlink"):
                            assert elem.get("TargetMode") == "External"
                            targets.add(elem.get("Target"))
            assert any(b"hyperlink" in z.read(n) or b"hlinkClick" in z.read(n) for n in z.namelist() if n.endswith(".xml"))
        formats[format] = {"bytes": len(data), "hyperlinks": len(targets)}
    assert expected <= targets, (format, expected - targets)
checked("EXP-02: três exportações locais", formats)

# A etiqueta fica abaixo da última linha do subtítulo e dentro da própria caixa.
document = Documento("Teste", "CorVIA", "Teste", "CorVIA")
texts, boxes = [], []
original_text, original_rectangle = document.pdf.texto, document.pdf.retangulo
def record_text(x,y,text,size,*args,**kwargs):
    texts.append((x,y,text,size,kwargs)); return original_text(x,y,text,size,*args,**kwargs)
def record_box(x,y,w,h,*args,**kwargs):
    boxes.append((x,y,w,h)); return original_rectangle(x,y,w,h,*args,**kwargs)
document.pdf.texto, document.pdf.retangulo = record_text, record_box
subtitle = "Subtítulo da amostra"
label = "BIBLIOTECA CIENTÍFICA CORVIA"
document.capa_simples("Título da amostra", subtitle, label)
tag = next(t for t in texts if t[2] == label)
sub = next(t for t in texts if t[2] == subtitle)
box = next(b for b in boxes if b[0] == document.margem and b[3] == 19)
assert box[1] + box[3] < sub[1]
assert box[0] <= tag[0] and tag[0] + largura_texto(label,7.5,True) + len(label)*1.1 <= box[0]+box[2]
assert box[1] <= tag[1] and tag[1]+7.5 <= box[1]+box[3]
document.capa_simples("Outro título", subtitle, label * 12)
assert all(b[0] + b[2] <= document.largura - document.margem + .01 for b in boxes if b[0] == document.margem and b[3] == 19)
checked("EXP-01: geometria da capa", "Etiqueta abaixo do subtítulo; fundo inclui espaçamento de letras; etiqueta longa quebra sem ultrapassar margem")

# Um vínculo longo mantém o destino em todas as linhas e em mais de uma página.
long_label = "conteúdo conectado " * 120
link = f"[{long_label.strip()}](/biblioteca/amostra)"
doc = Documento("Múltiplas páginas", "CorVIA", "Teste", "CorVIA")
doc.abrir_pagina()
doc.y = doc.base + 20
doc.paragrafo_com_links(link, item=True)
pdf = PdfReader(BytesIO(doc.salvar_bytes()))
assert len(pdf.pages) > 1
assert sum(len(page.get("/Annots", [])) for page in pdf.pages) > 10
assert all(str(ref.get_object()["/A"]["/URI"]).endswith("/biblioteca/amostra") for page in pdf.pages for ref in page.get("/Annots", []))
checked("EXP-02: vínculo entre páginas", "Rótulo extenso mantém URI em cada linha e página, sem corte lateral")

(OUT / "resultados.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"grupos": len(checks), "resultados": checks}, ensure_ascii=False, indent=2))
