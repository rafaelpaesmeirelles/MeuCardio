# -*- coding: utf-8 -*-
"""Geração de PDF dos documentos clínicos — receita, atestado e laudo.

Renderizador escolhido pelo Rafael em 29/07/2026: **ReportLab**, para todos os
documentos do sistema. Python puro, sem biblioteca de sistema, e com controle de
coordenada — que é o que formulário regulado exige, porque os modelos oficiais
têm layout fixo a reproduzir.

Nota de arquitetura que evita uma decisão errada depois: **este módulo não sabe
assinar, e não precisa saber.** A assinatura PAdES é aplicada sobre o PDF pronto,
com `pyHanko` em modo de assinatura interrompida — prepara o campo, entrega o
hash ao assinante remoto e embute o CMS de volta, que é o fluxo do certificado em
nuvem VIDAAS. Renderizar e assinar são camadas separadas de propósito.

O que este módulo **não** faz hoje, e a razão:

- **Não desenha a Notificação de Receita nem a Receita de Controle Especial.**
  Os modelos oficiais têm layout fixo publicado pela Anvisa, e reproduzi-los de
  memória produziria um formulário parecido e inválido. Enquanto o modelo não
  for lido do documento oficial, só o receituário comum é gerado.
- **Não imprime numeração.** Ela vem do SNCR, e o prescritor ainda não está
  cadastrado.

Cabeçalho/rodapé (Tarefa 29, 30/07/2026, pedido do Rafael): logo da Corvia +
dados da empresa no canto superior esquerdo, dados completos do profissional
no canto superior direito, e bloco de assinatura no rodapé (identificação do
profissional + local/data + campo para assinatura digital ou carimbo). O
endereço do médico que aparece — residencial ou profissional — é escolha
feita na hora de emitir, não um padrão fixo (ver `endereco_exibido` em
`models/receituario.py`/`models/clinical_docs.py`): por isso este módulo
recebe um `endereco: dict | None` já resolvido pelo chamador, e nunca decide
sozinho qual dos dois usar.
"""
from __future__ import annotations

import io
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.services.pdf.marca import LOGO, logo_disponivel
from app.services.professional_profile import (
    logo_path, professional_name, workplace_lines,
)

log = logging.getLogger("meucardio.pdf_documento")

FUSO = ZoneInfo("America/Sao_Paulo")

# Paleta oficial da Corvia. O `tokens.css` é a fonte da verdade; estes valores
# são a cópia para o PDF, que não consome CSS. Trocar a paleta exige mexer aqui
# também — está registrado no CLAUDE.md junto dos outros três lugares.
NAVY = (0x0B / 255, 0x2E / 255, 0x45 / 255)
CINZA = (0.42, 0.42, 0.42)
LINHA = (0.80, 0.80, 0.80)

MARGEM = 20 * mm
LARGURA, ALTURA = A4
LARGURA_LOGO = 34 * mm

# Dados da empresa que opera a Corvia — fixos, aparecem em todo documento
# emitido pela plataforma, independente de qual médico emite (é o emissor
# legal do serviço, não o consultório de cada médico). Fornecidos pelo
# Rafael em 30/07/2026; nunca editar sem instrução dele.
EMPRESA = {
    "razao_social": "Meirelles e Maluf Serviços Médicos e Biomédicos Ltda.",
    "cnpj": "53.382.596/0001-06",
    "logradouro": "Av. 11",
    "numero": "423",
    "bairro": "Centro",
    "cidade": "Itapagipe",
    "uf": "MG",
    "cep": "38240-000",
}


def _endereco_linhas(end: dict) -> list[str]:
    """Formata um endereço (residencial/profissional do médico, ou o da
    empresa) em até duas linhas legíveis."""
    linha1 = end.get("logradouro") or ""
    if end.get("numero"):
        linha1 = f"{linha1}, {end['numero']}" if linha1 else end["numero"]
    if end.get("complemento"):
        linha1 = f"{linha1} — {end['complemento']}" if linha1 else end["complemento"]
    if end.get("bairro"):
        linha1 = f"{linha1} — {end['bairro']}" if linha1 else end["bairro"]

    partes2 = []
    if end.get("cidade"):
        partes2.append(f"{end['cidade']}/{end['uf']}" if end.get("uf") else end["cidade"])
    if end.get("cep"):
        partes2.append(f"CEP {end['cep']}")
    linha2 = " — ".join(partes2)

    linha3 = f"Tel. {end['telefone']}" if end.get("telefone") else ""

    return [linha for linha in (linha1, linha2, linha3) if linha]


def _local(endereco: dict | None) -> str | None:
    if not endereco or not endereco.get("cidade"):
        return None
    return f"{endereco['cidade']}/{endereco['uf']}" if endereco.get("uf") else endereco["cidade"]


def resolver_endereco(user, escolha: str | None) -> dict | None:
    """Resolve o dict de endereço a partir da escolha do médico na hora de
    emitir ('residencial' | 'profissional' | None) — usado pelos três
    lugares que montam PDF (emissão de receita, geração de documento a
    partir de modelo, e o link público que reabre os dois depois).
    Telefone só entra no endereço profissional: é o único que a Lei
    9.965/2000 exige, e endereço residencial não tem telefone cadastrado."""
    if escolha == "residencial":
        if not user.home_street and not user.home_city:
            return None
        return {
            "logradouro": user.home_street, "numero": user.home_number,
            "complemento": user.home_complement, "bairro": user.home_neighborhood,
            "cidade": user.home_city, "uf": user.home_state, "cep": user.home_zip,
        }
    if escolha == "profissional":
        if not user.practice_street and not user.practice_city:
            return None
        return {
            "logradouro": user.practice_street, "numero": user.practice_number,
            "complemento": user.practice_complement, "bairro": user.practice_neighborhood,
            "cidade": user.practice_city, "uf": user.practice_state, "cep": user.practice_zip,
            "telefone": user.practice_phone,
        }
    return None


def _registro(medico: dict) -> str:
    partes = []
    if medico.get("council_name"):
        partes.append(f"{medico['council_name']}-{medico.get('council_state', '')} "
                      f"{medico.get('council_number', '')}".strip())
    if medico.get("rqe"):
        partes.append(f"RQE {medico['rqe']}")
    return "  ·  ".join(partes)


def _fundo_logo(c: canvas.Canvas, x: float, y: float, largura: float, altura: float) -> None:
    """Pinta branco atrás de uma logo antes de desenhá-la — o fundo do
    próprio documento (a página inteira é branca, `_cabecalho`/`_rodape`
    nunca colorem a área da logo). Existe por causa da logo PESSOAL: o
    upload aceita JPEG (`app/api/auth.py:ASSINATURAS`), formato que não tem
    canal alfa — nunca tem "fundo definido" (transparente). Sem isto, o
    fundo que vier de dentro do arquivo (branco, cinza, o que for) aparece
    como veio; com isto, pelo menos garante que bate com o branco da
    página em vez de depender do arquivo do médico estar bem recortado."""
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, largura, altura, fill=1, stroke=0)


def _logo(c: canvas.Canvas, x: float, y_topo: float) -> float:
    """Desenha a logo no canto superior esquerdo e devolve a altura ocupada
    (0 se o arquivo não existir — ausência de logo não derruba a geração de
    um documento clínico, só o deixa sem a marca no topo)."""
    if not logo_disponivel():
        return 0.0
    img = ImageReader(str(LOGO))
    largura_px, altura_px = img.getSize()
    altura = LARGURA_LOGO * altura_px / largura_px
    _fundo_logo(c, x, y_topo - altura, LARGURA_LOGO, altura)
    c.drawImage(img, x, y_topo - altura, width=LARGURA_LOGO, height=altura,
                mask="auto", preserveAspectRatio=True)
    return altura


def _bloco_empresa(c: canvas.Canvas, x: float, y: float) -> float:
    c.setFillColorRGB(*CINZA)
    c.setFont("Helvetica-Bold", 7.5)
    for linha in _quebrar(c, EMPRESA["razao_social"], "Helvetica-Bold", 7.5, 75 * mm):
        c.drawString(x, y, linha)
        y -= 3.6 * mm
    c.setFont("Helvetica", 7.5)
    c.drawString(x, y, f"CNPJ {EMPRESA['cnpj']}")
    y -= 3.6 * mm
    for linha in _endereco_linhas(EMPRESA):
        c.drawString(x, y, linha)
        y -= 3.6 * mm
    return y


LARGURA_LOGO_PESSOAL = 24 * mm


def _caminho_logo_pessoal(document_logo_url: str | None) -> Path | None:
    return logo_path(document_logo_url)


def _logo_pessoal(
    c: canvas.Canvas, x_direita: float, y: float, medico: dict,
) -> tuple[float, float]:
    """Logo pessoal/do consultório do médico (Tarefa 29, pedido do Rafael em
    30/07/2026) — desenhada JUNTO da logo da Corvia, no bloco profissional,
    não em vez dela. Ausência ou arquivo ilegível não derruba a geração do
    documento, mesma filosofia da logo da Corvia."""
    caminho = _caminho_logo_pessoal(medico.get("document_logo_url"))
    if not caminho:
        return x_direita, y
    try:
        img = ImageReader(str(caminho))
        largura_px, altura_px = img.getSize()
        escala = min(
            LARGURA_LOGO_PESSOAL / max(1, largura_px),
            (18 * mm) / max(1, altura_px),
        )
        largura = largura_px * escala
        altura = altura_px * escala
        x = x_direita - largura
        y_base = y - altura
        # O arquivo é aplicado como foi enviado, sobre o branco do papel: sem
        # placa escura, moldura ou contorno artificial. O texto profissional
        # usa uma coluna própria à esquerda e nunca fica sob a imagem.
        _fundo_logo(c, x, y_base, largura, altura)
        c.drawImage(img, x, y_base,
                    width=largura, height=altura, mask="auto", preserveAspectRatio=True)
        return x - 5 * mm, y_base
    except OSError:
        log.warning("Logo pessoal em %s não pôde ser lida — documento seguiu sem ela.", caminho)
        return x_direita, y


def _bloco_profissional(c: canvas.Canvas, x_direita: float, y: float, medico: dict,
                        endereco: dict | None) -> float:
    x_texto, y_base_logo = _logo_pessoal(c, x_direita, y, medico)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawRightString(x_texto, y, professional_name(medico))
    y -= 4.6 * mm

    c.setFont("Helvetica", 8.5)
    c.setFillColorRGB(*CINZA)
    if medico.get("profession"):
        c.drawRightString(x_texto, y, medico["profession"])
        y -= 3.8 * mm
    if medico.get("specialty"):
        c.drawRightString(x_texto, y, medico["specialty"])
        y -= 3.8 * mm
    for linha in workplace_lines(medico):
        c.drawRightString(x_texto, y, linha)
        y -= 3.6 * mm

    registro = _registro(medico)
    if registro:
        c.drawRightString(x_texto, y, registro)
        y -= 3.8 * mm

    if endereco:
        for linha in _endereco_linhas(endereco):
            c.drawRightString(x_texto, y, linha)
            y -= 3.6 * mm

    return min(y, y_base_logo)


def _cabecalho(c: canvas.Canvas, medico: dict, titulo: str, endereco: dict | None = None) -> float:
    topo = ALTURA - MARGEM

    altura_logo = _logo(c, MARGEM, topo)
    y_empresa = _bloco_empresa(c, MARGEM, topo - altura_logo - 4 * mm)
    y_profissional = _bloco_profissional(c, LARGURA - MARGEM, topo, medico, endereco)

    y = min(y_empresa, y_profissional) - 4 * mm
    c.setStrokeColorRGB(*LINHA)
    c.setLineWidth(0.7)
    c.line(MARGEM, y, LARGURA - MARGEM, y)
    y -= 8 * mm

    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(LARGURA / 2, y, titulo)
    return y - 9 * mm


def _bloco_paciente(c: canvas.Canvas, y: float, destinatario: dict) -> float:
    c.setFillColorRGB(*CINZA)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGEM, y, "PACIENTE")
    y -= 5 * mm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)
    c.drawString(MARGEM, y, destinatario.get("nome") or "")
    if destinatario.get("endereco"):
        y -= 5 * mm
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(*CINZA)
        c.drawString(MARGEM, y, destinatario["endereco"])
    return y - 9 * mm


def _quebrar(c: canvas.Canvas, texto: str, fonte: str, tam: float, largura: float) -> list[str]:
    """Quebra por largura real do glifo, não por contagem de caractere — nome de
    medicamento e posologia variam demais para estimativa por média."""
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        if c.stringWidth(teste, fonte, tam) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas or [""]


def _itens(c: canvas.Canvas, y: float, itens: list[dict]) -> float:
    util = LARGURA - 2 * MARGEM
    for n, item in enumerate(itens, start=1):
        if y < 62 * mm:                       # não deixa o item colar no rodapé (mais alto desde a Tarefa 29)
            c.showPage()
            y = ALTURA - MARGEM
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 10.5)
        titulo = item.get("descricao") or item.get("substancia") or ""
        if item.get("apresentacao"):
            titulo = f"{titulo} — {item['apresentacao']}"
        for linha in _quebrar(c, f"{n}. {titulo}", "Helvetica-Bold", 10.5, util):
            c.drawString(MARGEM, y, linha)
            y -= 5 * mm
        if item.get("quantidade"):
            c.setFont("Helvetica", 9.5)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            for linha in _quebrar(c, f"Quantidade: {item['quantidade']}", "Helvetica", 9.5, util - 6 * mm):
                c.drawString(MARGEM + 6 * mm, y, linha)
                y -= 4.4 * mm
        if item.get("uso_continuo"):
            c.setFont("Helvetica-Bold", 9.5)
            c.setFillColorRGB(*NAVY)
            for linha in _quebrar(
                c,
                "USO CONTÍNUO — tratamento por tempo indeterminado. Dispensar a quantidade máxima permitida pela legislação sanitária aplicável, observada a posologia prescrita.",
                "Helvetica-Bold", 9.5, util - 6 * mm,
            ):
                c.drawString(MARGEM + 6 * mm, y, linha)
                y -= 4.4 * mm
        if item.get("posologia"):
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            for linha in _quebrar(c, item["posologia"], "Helvetica", 10, util - 6 * mm):
                c.drawString(MARGEM + 6 * mm, y, linha)
                y -= 4.6 * mm
        y -= 3 * mm
    return y


def _assinatura_rodape(metodo: str, provedor_nome: str | None, medico: dict, sujeito: str) -> tuple[str, str | None]:
    """Decide a legenda da linha de assinatura e o aviso vermelho a partir do
    MÉTODO escolhido na emissão (Tarefa 4) — este módulo continua sem saber
    assinar, só sabe representar no papel o que já foi decidido em
    `app/services/assinatura/`. `sujeito` é "prescritor" ou "emissor",
    conforme o tipo de documento (mesma distinção que o aviso fixo já fazia).

    `MANUAL` é hoje o único caminho que realmente acontece — mantém o aviso
    vermelho, porque o documento de fato sai sem assinatura válida e o
    profissional precisa saber que ainda tem de assinar de próprio punho.
    O ramo "assinado" existe pronto para quando um provedor real entrar
    (Fase 2): nesse caso o aviso desaparece, porque deixa de ser verdade."""
    if metodo == "MANUAL":
        return (
            "Carimbo e assinatura do profissional",
            f"Documento sem assinatura digital — requer assinatura do {sujeito}.",
        )
    nome = medico.get("full_name") or ""
    provedor = provedor_nome or metodo
    return (f"Assinado digitalmente por {nome} — {provedor}", None)


def _rodape(c: canvas.Canvas, medico: dict, endereco: dict | None, via: str | None, aviso: str | None,
           data_emissao: datetime, legenda: str) -> None:
    """Bloco de assinatura (Tarefa 29): identificação do profissional, local
    e data, e — algumas linhas abaixo — o campo para assinatura digital ou
    para carimbo e assinatura manual. Nessa ordem porque foi assim que o
    Rafael descreveu o pedido, e é a convenção de documento formal
    brasileiro (identificação primeiro, assinatura por último).

    `data_emissao` vem de `emitido_em`/`criado_em`, nunca de `datetime.now()`
    (Tarefa 4): o mesmo documento pode ser regerado ou reaberto por link
    público mais de uma vez, e o PDF precisa sair byte-a-byte igual toda
    vez — condição para poder assinar e para o hash guardado em
    `DocumentoEmitido.sha256` continuar batendo."""
    y = 52 * mm

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 9.5)
    nome = professional_name(medico)
    c.drawCentredString(LARGURA / 2, y, nome)
    y -= 4.4 * mm

    c.setFont("Helvetica", 8.5)
    c.setFillColorRGB(*CINZA)
    if medico.get("profession"):
        c.drawCentredString(LARGURA / 2, y, medico["profession"])
        y -= 4 * mm
    if medico.get("specialty"):
        c.drawCentredString(LARGURA / 2, y, medico["specialty"])
        y -= 4 * mm

    registro = _registro(medico)
    if registro:
        c.drawCentredString(LARGURA / 2, y, registro)
        y -= 4 * mm

    local = _local(endereco)
    data = data_emissao.astimezone(FUSO).strftime("%d/%m/%Y")
    c.drawCentredString(LARGURA / 2, y, f"{local}, {data}" if local else data)
    y -= 10 * mm  # "algumas linhas abaixo", antes do campo de assinatura

    c.setStrokeColorRGB(*LINHA)
    c.line(LARGURA / 2 - 35 * mm, y, LARGURA / 2 + 35 * mm, y)
    c.setFont("Helvetica", 7.5)
    c.setFillColorRGB(*CINZA)
    c.drawCentredString(LARGURA / 2, y - 4 * mm, legenda)

    if via:
        c.setFont("Helvetica", 7.5)
        c.drawRightString(LARGURA - MARGEM, 10 * mm, via)
    if aviso:
        c.setFillColorRGB(0.55, 0.15, 0.15)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(MARGEM, 6 * mm, aviso)


def documento_generico(titulo: str, corpo: str, medico: dict, data_emissao: datetime,
                       endereco: dict | None = None, metodo_assinatura: str = "MANUAL",
                       provedor_nome: str | None = None) -> bytes:
    """PDF de atestado/laudo gerado a partir de `DocumentTemplate` (Tarefa 29).

    Ao contrário do receituário, o corpo já chega pronto — as variáveis
    `{{...}}` já foram substituídas em `app/api/documents.py:gerar_documento`
    antes de chegar aqui. Este renderizador só formata como documento, com o
    mesmo cabeçalho/rodapé do receituário, para manter a mesma identidade
    visual em todo PDF clínico que a Corvia emite.

    `data_emissao` e `metodo_assinatura` vêm de `DocumentoEmitido` (Tarefa 4)
    — nunca do relógio nem de um default silencioso — para o PDF sair
    determinístico e o rodapé refletir o que foi de fato escolhido."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(titulo)

    y = _cabecalho(c, medico, titulo, endereco)

    util = LARGURA - 2 * MARGEM
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10.5)
    for paragrafo in corpo.split("\n"):
        if not paragrafo.strip():
            y -= 4 * mm
            continue
        if y < 62 * mm:
            c.showPage()
            y = ALTURA - MARGEM
        for linha in _quebrar(c, paragrafo, "Helvetica", 10.5, util):
            c.drawString(MARGEM, y, linha)
            y -= 5 * mm

    legenda, aviso = _assinatura_rodape(metodo_assinatura, provedor_nome, medico, "emissor")
    _rodape(c, medico, endereco, None, aviso, data_emissao, legenda)
    c.showPage()
    c.save()
    return buf.getvalue()


def receituario_comum(destinatario: dict, itens: list[dict], medico: dict, data_emissao: datetime,
                      observacoes: str = "", endereco: dict | None = None, metodo_assinatura: str = "MANUAL",
                      provedor_nome: str | None = None) -> bytes:
    """Receituário comum, uma via. Retorna os bytes do PDF.

    O aviso de rodapé é deliberado e não deve ser removido enquanto o método
    escolhido for `MANUAL`: um PDF com aparência de receita, sem assinatura
    válida, é pior que nenhum documento — o médico precisa saber que ainda
    tem de assinar. Some sozinho quando `metodo_assinatura` for um provedor
    que de fato assinou (Fase 2) — ver `_assinatura_rodape`.

    `data_emissao` vem de `DocumentoEmitido`/`emitido_em`, nunca do relógio:
    o mesmo documento é reaberto por link público depois, e precisa sair
    byte-a-byte igual toda vez (Tarefa 4).
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Receituário")

    y = _cabecalho(c, medico, "Receituário", endereco)
    y = _bloco_paciente(c, y, destinatario)
    y = _itens(c, y, itens)

    if observacoes:
        y -= 2 * mm
        c.setFillColorRGB(*CINZA)
        c.setFont("Helvetica", 8.5)
        c.drawString(MARGEM, y, "OBSERVAÇÕES")
        y -= 5 * mm
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica", 9.5)
        for linha in _quebrar(c, observacoes, "Helvetica", 9.5, LARGURA - 2 * MARGEM):
            c.drawString(MARGEM, y, linha)
            y -= 4.6 * mm

    legenda, aviso = _assinatura_rodape(metodo_assinatura, provedor_nome, medico, "prescritor")
    _rodape(c, medico, endereco, None, aviso, data_emissao, legenda)
    c.showPage()
    c.save()
    return buf.getvalue()
