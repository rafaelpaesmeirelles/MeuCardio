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
dados da empresa no canto superior esquerdo, logo profissional centralizada
no topo e dados completos do profissional no canto superior direito. O bloco
de assinatura fica no rodapé (identificação do
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
from app.services.pdf.marca import COBRE, LOGO, NAVY, logo_disponivel
from app.services.pdf.identidade_institucional import EMPRESA as EMPRESA, desenhar_identidade_institucional
from app.services.pdf.wrapping import wrap_text
from app.services.professional_profile import (
    logo_path, professional_name, workplace_lines,
)
from app.services.receita_controle_especial import _logo_corvia, _logo_profissional

log = logging.getLogger("meucardio.pdf_documento")

FUSO = ZoneInfo("America/Sao_Paulo")

# A marca vem da paleta comum; linhas do formulário e avisos ficam neutros/semânticos.
CINZA = (0.42, 0.42, 0.42)
LINHA = (0.80, 0.80, 0.80)

MARGEM = 20 * mm
LARGURA, ALTURA = A4
LARGURA_LOGO = 40 * mm

# EMPRESA remains re-exported here for existing email/document callers.


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
    upload aceita JPEG (`app/api/auth.py`), formato que não tem
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
    return desenhar_identidade_institucional(c, x, y, 65 * mm)


LARGURA_LOGO_PESSOAL = 30 * mm


def _caminho_logo_pessoal(document_logo_url: str | None) -> Path | None:
    return logo_path(document_logo_url)


def _logo_pessoal(
    c: canvas.Canvas, x_centro: float, y: float, medico: dict,
) -> tuple[float, float]:
    """Logo do profissional centralizada no topo, preservando a proporção.

    Arquivo ausente ou ilegível não impede a geração do documento.
    """
    caminho = _caminho_logo_pessoal(medico.get("document_logo_url"))
    if not caminho:
        return x_centro, y
    try:
        img = ImageReader(str(caminho))
        largura_px, altura_px = img.getSize()
        escala = min(
            LARGURA_LOGO_PESSOAL / max(1, largura_px),
            (22 * mm) / max(1, altura_px),
        )
        largura = largura_px * escala
        altura = altura_px * escala
        x = x_centro - largura / 2
        y_base = y - altura
        # O arquivo é aplicado como foi enviado, sobre o branco do papel: sem
        # placa escura, moldura ou contorno artificial. O texto profissional
        # usa uma coluna própria à direita e nunca fica sob a imagem.
        _fundo_logo(c, x, y_base, largura, altura)
        c.drawImage(img, x, y_base,
                    width=largura, height=altura, mask="auto", preserveAspectRatio=True)
        return x_centro, y_base
    except (OSError, ValueError):
        log.warning("Logo pessoal em %s não pôde ser lida — documento seguiu sem ela.", caminho)
        return x_centro, y


def _bloco_profissional(c: canvas.Canvas, x_direita: float, y: float, medico: dict,
                        endereco: dict | None, *, largura_texto: float | None = None) -> float:
    x_texto = x_direita
    # Empresa e profissional ocupam colunas independentes. Antes deste limite,
    # `drawRightString()` recebia linhas inteiras (local de trabalho e endereco)
    # e as projetava por cima da coluna da empresa. A logo pessoal reduzia ainda
    # mais o espaco sem que o texto fosse quebrado. A fronteira abaixo preserva
    # um respiro central fixo, com ou sem logo pessoal.
    x_esquerda = LARGURA / 2 + 20 * mm
    if largura_texto is None:
        largura_texto = max(35 * mm, x_texto - x_esquerda)

    def desenhar(texto: str, fonte: str, tamanho: float, entrelinha: float) -> None:
        nonlocal y
        c.setFont(fonte, tamanho)
        for linha in _quebrar(c, texto, fonte, tamanho, largura_texto):
            c.drawRightString(x_texto, y, linha)
            y -= entrelinha

    # Hierarquia visual aprovada: identidade e registro primeiro, depois
    # atuação/local/endereço. Mantém a paleta CorVIA e apenas melhora ritmo,
    # alinhamento e leitura do bloco oposto à marca institucional.
    c.setFillColorRGB(*NAVY)
    desenhar(professional_name(medico), "Helvetica-Bold", 11.2, 4.8 * mm)

    registro = _registro(medico)
    if registro:
        desenhar(registro, "Helvetica-Bold", 8.6, 3.8 * mm)

    c.setStrokeColorRGB(*LINHA)
    c.setLineWidth(0.6)
    largura_separador = min(42 * mm, largura_texto)
    c.line(x_texto - largura_separador, y + 1.2 * mm, x_texto, y + 1.2 * mm)
    y -= 2.2 * mm

    c.setFillColorRGB(*CINZA)
    if medico.get("profession"):
        desenhar(medico["profession"], "Helvetica", 8.3, 3.7 * mm)
    if medico.get("specialty"):
        desenhar(medico["specialty"], "Helvetica", 8.5, 3.7 * mm)
    for linha in workplace_lines(medico):
        desenhar(linha, "Helvetica", 8.2, 3.5 * mm)

    if endereco:
        for linha in _endereco_linhas(endereco):
            desenhar(linha, "Helvetica", 8.1, 3.5 * mm)

    return y


def _cabecalho_receituario(c: canvas.Canvas, medico: dict, titulo: str,
                          endereco: dict | None) -> float:
    """Prescription-only issuer box; generic clinical documents keep their layout."""
    topo = ALTURA - MARGEM
    c.setStrokeColorRGB(*LINHA)
    c.setLineWidth(0.7)
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(LARGURA / 2, topo - 5 * mm, "IDENTIFICAÇÃO DO EMITENTE")
    c.line(MARGEM, topo - 8 * mm, LARGURA - MARGEM, topo - 8 * mm)
    topo_conteudo = topo - 12 * mm
    y_profissional = _bloco_profissional(
        c, LARGURA - MARGEM - 3 * mm, topo_conteudo, medico, endereco,
        largura_texto=58 * mm,
    )
    altura_identidade = max(34 * mm, topo_conteudo - y_profissional)
    _logo_corvia(c, MARGEM + 3 * mm, topo_conteudo + 1 * mm,
                 altura_area=altura_identidade)
    _logo_profissional(c, medico, MARGEM + (3 + 60 + 4 + 19) * mm,
                       topo_conteudo + 1 * mm, altura_area=altura_identidade)
    base = topo_conteudo - altura_identidade - 3 * mm
    c.setStrokeColorRGB(*LINHA)
    c.line(MARGEM, base, LARGURA - MARGEM, base)
    # Adjacent sub-block identifies the platform operator, not the prescriber.
    y = desenhar_identidade_institucional(
        c, MARGEM + 3 * mm, base - 4 * mm, LARGURA - 2 * MARGEM - 6 * mm,
    )
    base = y - 1 * mm
    c.rect(MARGEM, base, LARGURA - 2 * MARGEM, topo - base, fill=0, stroke=1)
    y = base - 8 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 14)
    for linha in _quebrar(c, titulo, "Helvetica-Bold", 14, LARGURA - 2 * MARGEM):
        c.drawCentredString(LARGURA / 2, y, linha)
        y -= 6 * mm
    return y - 3 * mm


def _cabecalho(c: canvas.Canvas, medico: dict, titulo: str, endereco: dict | None = None,
               *, prescricao: bool = False) -> float:
    if prescricao:
        return _cabecalho_receituario(c, medico, titulo, endereco)
    topo = ALTURA - MARGEM

    altura_logo = _logo(c, MARGEM, topo)
    y_empresa = _bloco_empresa(c, MARGEM, topo - altura_logo - 4 * mm)
    _, y_logo = _logo_pessoal(c, LARGURA / 2, topo, medico)
    y_profissional = _bloco_profissional(c, LARGURA - MARGEM, topo, medico, endereco)

    y = min(y_empresa, y_profissional, y_logo) - 4 * mm
    c.setStrokeColorRGB(*COBRE)
    c.setLineWidth(0.7)
    c.line(MARGEM, y, LARGURA - MARGEM, y)
    y -= 8 * mm

    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 14)
    for linha in _quebrar(c, titulo, "Helvetica-Bold", 14, LARGURA - 2 * MARGEM):
        c.drawCentredString(LARGURA / 2, y, linha)
        y -= 6 * mm
    return y - 3 * mm


def _quebrar(c: canvas.Canvas, texto: str, fonte: str, tam: float, largura: float) -> list[str]:
    """Quebra por largura real do glifo, não por contagem de caractere — nome de
    medicamento e posologia variam demais para estimativa por média."""
    return wrap_text(texto, largura, lambda linha: c.stringWidth(linha, fonte, tam))


class _FluxoClinico:
    """Paginate each line and restore font after Canvas.showPage resets it."""

    def __init__(self, c: canvas.Canvas, medico: dict, titulo: str, endereco: dict | None,
                 *, prescricao: bool = False):
        self.c, self.medico, self.titulo, self.endereco = c, medico, titulo, endereco
        self.prescricao = prescricao
        self.y = _cabecalho(c, medico, titulo, endereco, prescricao=prescricao)
        linhas = _linhas_rodape(c, medico, endereco, "00/00/0000")
        self.base_rodape = max(62 * mm, 45 * mm + sum(linha[3] for linha in linhas[:-1]))

    def garantir(self, altura: float) -> None:
        if self.y - altura >= self.base_rodape:
            return
        self.c.setFont("Helvetica", 7)
        self.c.setFillColorRGB(*CINZA)
        self.c.drawRightString(LARGURA - MARGEM, 12 * mm, f"Página {self.c.getPageNumber()} · continua")
        self.c.showPage()
        self.y = _cabecalho(self.c, self.medico, self.titulo, self.endereco, prescricao=self.prescricao)

    def texto(self, texto: str, fonte: str = "Helvetica", tamanho: float = 10.5,
              entrelinha: float = 5 * mm, recuo: float = 0,
              cor: tuple = (0, 0, 0)) -> None:
        for linha in _quebrar(self.c, texto, fonte, tamanho, LARGURA - 2 * MARGEM - recuo):
            self.garantir(entrelinha)
            self.c.setFillColorRGB(*cor)
            self.c.setFont(fonte, tamanho)
            self.c.drawString(MARGEM + recuo, self.y, linha)
            self.y -= entrelinha


def _itens(fluxo: _FluxoClinico, itens: list[dict]) -> None:
    for n, item in enumerate(itens, start=1):
        fluxo.garantir(15 * mm)
        titulo = item.get("descricao") or item.get("substancia") or ""
        if item.get("apresentacao"):
            titulo = f"{titulo} — {item['apresentacao']}"
        fluxo.texto(f"{n}. {titulo}", "Helvetica-Bold")
        if item.get("quantidade"):
            fluxo.texto(f"Quantidade: {item['quantidade']}", tamanho=9.5,
                        entrelinha=4.4 * mm, recuo=6 * mm, cor=(0.2, 0.2, 0.2))
        if item.get("uso_continuo"):
            fluxo.texto(
                "USO CONTÍNUO — tratamento por tempo indeterminado. Dispensar a quantidade máxima permitida pela legislação sanitária aplicável, observada a posologia prescrita.",
                "Helvetica-Bold", 9.5, entrelinha=4.4 * mm, recuo=6 * mm, cor=NAVY,
            )
        if item.get("posologia"):
            fluxo.texto(item["posologia"], tamanho=10, entrelinha=4.6 * mm,
                        recuo=6 * mm, cor=(0.2, 0.2, 0.2))
        if item.get("orientacao"):
            fluxo.texto(f"Orientações: {item['orientacao']}", tamanho=10,
                        entrelinha=4.6 * mm, recuo=6 * mm, cor=(0.2, 0.2, 0.2))
        fluxo.y -= 3 * mm


# Mesmo conjunto de `provedor._MANUAL_EXTERNO` (Trabalho 14) — repetido
# aqui, não importado, porque este módulo de renderização não depende do
# pacote `assinatura/` para nada além disto, e um `set` de 6 strings não
# justifica esse acoplamento novo.
_METODOS_MANUAL_EXTERNO = {"GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID", "A3_TOKEN"}


def _assinatura_rodape(metodo: str, provedor_nome: str | None, medico: dict, sujeito: str) -> tuple[str, str | None]:
    """Decide a legenda da linha de assinatura e o aviso vermelho a partir do
    MÉTODO escolhido na emissão (Tarefa 4) — este módulo continua sem saber
    assinar, só sabe representar no papel o que já foi decidido em
    `app/services/assinatura/`. `sujeito` é "prescritor" ou "emissor",
    conforme o tipo de documento (mesma distinção que o aviso fixo já fazia).

    A emissão aplica e valida a assinatura após a renderização; arquivos dos
    métodos externos recebem uma legenda neutra durante todo o processo."""
    if metodo == "MANUAL":
        return (
            "Carimbo e assinatura do profissional",
            f"Documento sem assinatura digital — requer assinatura do {sujeito}.",
        )
    if metodo in _METODOS_MANUAL_EXTERNO:
        # Texto DELIBERADAMENTE neutro, não condicional ao estado atual —
        # o mesmo PDF que sai daqui vai e volta do Assinador ITI (fluxo
        # manual, Trabalho 14: GOVBR e também VIDAAS/BIRDID/SAFEID/NEOID/
        # REMOTEID, quando o médico já tem certificado em nuvem e assina
        # com ele pelo próprio Assinador ITI), e a assinatura em si só é
        # aplicada FORA da Corvia. Um aviso do tipo "ainda não assinado"
        # ficaria permanentemente errado no arquivo final (a assinatura do
        # ITI é um incremento no PDF, não regera o rodapé) — por isso a
        # legenda descreve o MÉTODO, não afirma nem nega que já foi
        # assinado.
        nome = provedor_nome or metodo
        return (f"Assinatura digital — {nome} (assinador.iti.br)", None)
    nome = medico.get("full_name") or ""
    provedor = provedor_nome or metodo
    return (f"Assinado digitalmente por {nome} — {provedor}", None)


def _linhas_rodape(c: canvas.Canvas, medico: dict, endereco: dict | None, data: str) -> list[tuple]:
    local = _local(endereco)
    campos = [
        (professional_name(medico), "Helvetica-Bold", 9.5, 4.4 * mm),
        (medico.get("profession"), "Helvetica", 8.5, 4 * mm),
        (medico.get("specialty"), "Helvetica", 8.5, 4 * mm),
        (_registro(medico), "Helvetica", 8.5, 4 * mm),
        (f"{local}, {data}" if local else data, "Helvetica", 8.5, 4 * mm),
    ]
    return [(linha, fonte, tamanho, entrelinha)
            for texto, fonte, tamanho, entrelinha in campos if texto
            for linha in _quebrar(c, texto, fonte, tamanho, LARGURA - 2 * MARGEM)]


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
    data = data_emissao.astimezone(FUSO).strftime("%d/%m/%Y")
    linhas = _linhas_rodape(c, medico, endereco, data)
    y = max(52 * mm, 35 * mm + sum(linha[3] for linha in linhas[:-1]))
    for texto, fonte, tamanho, entrelinha in linhas:
        c.setFillColorRGB(*CINZA if fonte == "Helvetica" else (0, 0, 0))
        c.setFont(fonte, tamanho)
        c.drawCentredString(LARGURA / 2, y, texto)
        y -= entrelinha
    y -= 6 * mm

    # O A1 recebe uma aparencia visivel criada pelo proprio `PdfSigner`
    # exatamente nesta area. Desenhar uma linha/legenda por baixo produz a
    # sobreposicao observada no PDF final e, pior, parece um selo mesmo antes
    # da operacao criptografica. Para os demais metodos, o campo tradicional
    # continua inalterado.
    if not legenda.startswith("Assinado digitalmente por"):
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

    fluxo = _FluxoClinico(c, medico, titulo, endereco)
    for paragrafo in corpo.split("\n"):
        if not paragrafo.strip():
            fluxo.y -= 4 * mm
            continue
        fluxo.texto(paragrafo)

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

    fluxo = _FluxoClinico(c, medico, "Receituário", endereco, prescricao=True)
    fluxo.texto("PACIENTE", tamanho=8.5, cor=CINZA)
    fluxo.texto(destinatario.get("nome") or "", tamanho=11)
    if destinatario.get("endereco"):
        fluxo.texto(destinatario["endereco"], tamanho=9, cor=CINZA)
    fluxo.y -= 4 * mm
    _itens(fluxo, itens)

    if observacoes:
        fluxo.y -= 2 * mm
        fluxo.garantir(10 * mm)
        fluxo.texto("OBSERVAÇÕES", tamanho=8.5, cor=CINZA)
        fluxo.texto(observacoes, tamanho=9.5, entrelinha=4.6 * mm, cor=(0.2, 0.2, 0.2))

    legenda, aviso = _assinatura_rodape(metodo_assinatura, provedor_nome, medico, "prescritor")
    _rodape(c, medico, endereco, None, aviso, data_emissao, legenda)
    c.showPage()
    c.save()
    return buf.getvalue()
