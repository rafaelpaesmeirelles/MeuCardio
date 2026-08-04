"""Tarefa 12 — gera o PDF do material educativo que o médico entrega ao paciente.

O documento é do **médico**, não da plataforma: quem entrega, quem responde
pela explicação e quem o paciente procura de volta é ele. Por isso o nome e o
registro profissional aparecem em posição de emissor, e a marca fica como
identificação de origem — a mesma ordem já adotada no cabeçalho dos documentos
impressos do sistema.

Duas seções são obrigatórias e não dependem do conteúdo cadastrado:

- **Quando procurar ajuda sem esperar.** É a parte que justifica o papel existir.
  Vai em destaque vermelho, e é a única coisa do material que precisa ser lida
  por alguém em pânico às três da manhã.
- **A ressalva de que isto não substitui a consulta**, junto da data. Material
  educativo sem data circula por anos e envelhece sem que ninguém perceba.
"""

from __future__ import annotations

from datetime import datetime, timezone
import tempfile

from PIL import Image, UnidentifiedImageError

from app.models.patient_material import PatientMaterial

from .pdf import Documento
from .pdf.marca import (
    BRANCO, NAVY, NEUTRO, TEAL, TINTA, TINTA_TEAL, TINTA_VERMELHA, VERMELHO,
)
from .professional_profile import (
    logo_needs_dark_plate_path, logo_path, professional_name, workplace_lines,
)


def gerar(material: PatientMaterial, medico: dict) -> bytes:
    nome = professional_name(medico)
    registro = " ".join(
        x for x in (medico.get("council_name"), medico.get("council_number")) if x
    )
    if medico.get("council_state"):
        registro += f"/{medico['council_state']}"
    if medico.get("rqe"):
        registro += f" · RQE {medico['rqe']}"

    d = Documento(
        titulo=material.titulo,
        autor=nome or "Corvia",
        assunto="Material educativo para o paciente",
        rodape="Material educativo · não substitui a consulta médica",
    )
    d.capa_simples(material.titulo, material.subtitulo or "",
                   etiqueta="Material para o paciente")

    # Logo profissional: o núcleo PDF aceita PNG; Pillow converte JPEG/WEBP
    # apenas em memória/arquivo temporário, sem alterar o upload original.
    caminho_logo = logo_path(medico.get("document_logo_url"))
    if caminho_logo:
        try:
            with Image.open(caminho_logo) as original:
                imagem = original.convert("RGBA")
                imagem.thumbnail((360, 160))
                largura = 92.0
                altura = largura * imagem.height / max(imagem.width, 1)
                d._garantir(altura + 28)
                y_base = d.y - altura
                fundo = NAVY if logo_needs_dark_plate_path(caminho_logo) else BRANCO
                d.pdf.retangulo(d.margem, y_base - 7, largura + 14, altura + 14, fundo)
                with tempfile.NamedTemporaryFile(suffix=".png") as temp:
                    imagem.save(temp.name, format="PNG")
                    d.pdf.imagem("LogoProfissional", temp.name, d.margem + 7, y_base, largura, altura)
                d.y = y_base - 18
        except (OSError, UnidentifiedImageError):
            pass

    # Quem entrega. Fica logo abaixo do título porque é a primeira pergunta de
    # quem recebe um papel na mão: quem me deu isto e como falo com essa pessoa.
    if nome:
        d.pdf.retangulo(d.margem, d.y - 40, d.util, 40, TINTA_TEAL)
        d.pdf.retangulo(d.margem, d.y - 40, 3.2, 40, TEAL)
        d.pdf.texto(d.margem + 16, d.y - 18, "Entregue por", 7.5, TEAL,
                    negrito=True, espaco_extra=1.1)
        d.pdf.texto(d.margem + 16, d.y - 32, nome + (f"  ·  {registro}" if registro else ""),
                    10, NAVY, negrito=True)
        d.y -= 54
        for linha in workplace_lines(medico):
            d.pdf.texto(d.margem + 16, d.y - 9, linha, 8.5, NEUTRO)
            d.y -= 13

    for secao in (material.secoes or []):
        if secao.get("titulo"):
            d.titulo(secao["titulo"])
        for p in secao.get("paragrafos", []):
            d.paragrafo(p)
        if secao.get("itens"):
            d.itens(secao["itens"])

    if material.sinais_de_alerta:
        d.titulo("Quando procurar ajuda sem esperar")
        d.paragrafo(
            "Se qualquer um dos sinais abaixo aparecer, procure atendimento de "
            "urgência. Não espere a próxima consulta e não dirija até o hospital — "
            "chame o serviço de emergência."
        )
        for sinal in material.sinais_de_alerta:
            d.destaque(sinal, cor_fundo=TINTA_VERMELHA, cor_barra=VERMELHO)

    if material.perguntas:
        d.titulo("Perguntas para levar à próxima consulta")
        d.paragrafo(
            "Anotar antes ajuda: na hora da consulta é comum esquecer justamente "
            "o que mais incomodava."
        )
        d.itens(material.perguntas)

    # Encerramento obrigatório.
    d.espaco(6)
    d.destaque(
        "Este material explica a condição em termos gerais e não substitui a "
        "consulta médica. Ele não contém dose, receita nem orientação de "
        "tratamento individual — o que vale para você é o que foi combinado com "
        "o seu médico.",
        cor_fundo=TINTA_TEAL, cor_barra=TEAL, rotulo="Importante",
    )

    if material.fontes:
        d.titulo("De onde vem esta informação")
        d.itens(list(material.fontes))

    d._garantir(30)
    hoje = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y")
    d.pdf.texto(d.margem, d.y - 8,
                f"Material gerado na Corvia em {hoje}. Em caso de dúvida sobre o "
                f"seu caso, procure o seu médico.", 8, NEUTRO, italico=True)

    return d.salvar_bytes()
