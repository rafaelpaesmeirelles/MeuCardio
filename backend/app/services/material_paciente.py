"""Gera material educativo para o paciente com identidade profissional estável.

A logo e os dados do assinante ocupam um cabeçalho reservado, repetido nas
páginas internas. O conteúdo nunca invade essa área; a primeira página mantém a
marca Corvia à esquerda e coloca a identidade profissional no canto superior
direito, seguindo a hierarquia usada em receitas e documentos.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.patient_material import PatientMaterial

from .pdf import Documento, largura_texto, quebrar
from .pdf.marca import BRANCO, FIO, NAVY, NEUTRO, TEAL, TINTA_TEAL, TINTA_VERMELHA, VERMELHO
from .professional_profile import (
    logo_needs_dark_plate_path,
    logo_path,
    professional_name,
    rendered_logo_png,
    workplace_lines,
)


class DocumentoProfissional(Documento):
    """Documento retrato com cabeçalho reservado para o assinante."""

    topo = Documento.altura - 116.0

    def __init__(self, *args, medico: dict, **kwargs):
        super().__init__(*args, **kwargs)
        self.medico = medico
        self.nome_profissional = professional_name(medico)
        self.registro_profissional = _registro(medico)
        self.linhas_trabalho = workplace_lines(medico)
        self.logo_original = logo_path(medico.get("document_logo_url"))
        self.logo_precisa_placa_escura = logo_needs_dark_plate_path(self.logo_original)
        self.logo_profissional = rendered_logo_png(medico.get("document_logo_url"))

    def _desenhar_logo_profissional(
        self,
        caminho: Path | None,
        x_centro: float,
        y_topo: float,
        largura_max: float = 86.0,
        altura_max: float = 48.0,
    ) -> tuple[float, float]:
        if caminho is None:
            return 0.0, 0.0
        try:
            nome_imagem = "LogoProfissionalMaterial"
            self.pdf.imagem(nome_imagem, str(caminho), 0, 0, 0, 0)
            self.pdf.atual.pop()
            imagem = self.pdf.imagens[nome_imagem]
            largura = largura_max
            altura = largura * imagem["altura"] / max(1, imagem["largura"])
            if altura > altura_max:
                altura = altura_max
                largura = altura * imagem["largura"] / max(1, imagem["altura"])
            self.pdf.imagem(
                nome_imagem,
                str(caminho),
                x_centro - largura / 2,
                y_topo - altura,
                largura,
                altura,
            )
            return largura, altura
        except (OSError, ValueError):
            return 0.0, 0.0

    def identidade_primeira_pagina(self) -> float:
        """Logo central e identidade completa à direita, em colunas reservadas."""
        direita = self.largura - self.margem
        topo = self.altura - 34
        _, altura_logo = self._desenhar_logo_profissional(
            self.logo_profissional,
            self.largura / 2,
            topo,
            largura_max=90,
            altura_max=50,
        )
        y = topo - 6
        largura_bloco = direita - (self.largura / 2 + 56)
        campos = [
            (self.nome_profissional, 8.5, True, NAVY),
            (self.registro_profissional, 7.3, False, TEAL),
            (self.medico.get("profession"), 7.0, False, NEUTRO),
            (self.medico.get("specialty"), 7.0, False, NEUTRO),
            *((linha, 7.0, False, NEUTRO) for linha in self.linhas_trabalho),
        ]
        for texto, tamanho, negrito, cor in campos:
            if not texto:
                continue
            for linha in quebrar(texto, largura_bloco, tamanho, negrito):
                x = direita - largura_texto(linha, tamanho, negrito)
                self.pdf.texto(x, y, linha, tamanho, cor, negrito=negrito)
                y -= tamanho + 3.5
        return min(y, topo - altura_logo)

    def capa_profissional(self, titulo: str, subtitulo: str, etiqueta: str = "") -> None:
        """Capa cuja faixa superior reserva as duas identidades lado a lado."""
        self.abrir_pagina(com_cabecalho=False)
        self.pdf.retangulo(0, self.altura - 7, self.largura, 7, VERMELHO)

        altura_corvia = self._logo(self.margem, self.altura - 40, 140)
        base_corvia = self.altura - 40 - altura_corvia
        base_profissional = self.identidade_primeira_pagina()
        self.y = min(base_corvia, base_profissional) - 26

        for linha in quebrar(titulo, self.util, 21, True):
            self._garantir(40)
            self.pdf.texto(self.margem, self.y - 21, linha, 21, NAVY, negrito=True)
            self.y -= 27
        self.pdf.linha(self.margem, self.y - 2, self.margem + 46, self.y - 2, VERMELHO, 2.2)
        self.y -= 20

        if subtitulo:
            for linha in quebrar(subtitulo, self.util, 11):
                self._garantir(24)
                self.pdf.texto(self.margem, self.y - 11, linha, 11, TEAL)
                self.y -= 16
        if etiqueta:
            self.y -= 6
            largura = largura_texto(etiqueta.upper(), 7.5, True) + 22
            self.pdf.retangulo(self.margem, self.y - 6, largura, 19, TINTA_TEAL)
            self.pdf.texto(
                self.margem + 11,
                self.y,
                etiqueta.upper(),
                7.5,
                TEAL,
                negrito=True,
                espaco_extra=1.1,
            )
            self.y -= 16
        self.y -= 14

    def _cabecalho(self) -> None:
        topo = self.altura - 30
        self._logo(self.margem, topo, 84)
        direita = self.largura - self.margem
        base_identidade = self.identidade_primeira_pagina()
        linha_y = min(self.altura - 92, base_identidade - 12)
        self.pdf.linha(self.margem, linha_y, direita, linha_y, FIO)
        self.y = linha_y - 24


def _registro(medico: dict) -> str:
    conselho = " ".join(
        parte for parte in (
            medico.get("council_name"),
            medico.get("council_number"),
        ) if parte
    )
    if medico.get("council_state"):
        conselho = f"{conselho}/{medico['council_state']}".strip("/")
    if medico.get("rqe"):
        conselho = " · ".join(parte for parte in (conselho, f"RQE {medico['rqe']}") if parte)
    return conselho


def gerar(material: PatientMaterial, medico: dict) -> bytes:
    nome = professional_name(medico)
    documento = DocumentoProfissional(
        titulo=material.titulo,
        autor=nome or "CorVIA",
        assunto="Material educativo para o paciente",
        rodape="Material educativo · não substitui a consulta médica",
        medico=medico,
    )
    documento.capa_profissional(
        material.titulo,
        material.subtitulo or "",
    )

    for secao in (material.secoes or []):
        if secao.get("titulo"):
            documento.titulo(secao["titulo"])
        for paragrafo in secao.get("paragrafos", []):
            documento.paragrafo(paragrafo)
        if secao.get("itens"):
            documento.itens(secao["itens"])

    if material.sinais_de_alerta:
        documento.titulo("Quando procurar ajuda sem esperar")
        documento.paragrafo(
            "Se qualquer um dos sinais abaixo aparecer, procure atendimento de "
            "urgência. Não espere a próxima consulta e não dirija até o hospital — "
            "chame o serviço de emergência."
        )
        for sinal in material.sinais_de_alerta:
            documento.destaque(
                sinal,
                cor_fundo=TINTA_VERMELHA,
                cor_barra=VERMELHO,
            )

    if material.perguntas:
        documento.titulo("Perguntas para levar à próxima consulta")
        documento.paragrafo(
            "Anotar antes ajuda: na hora da consulta é comum esquecer justamente "
            "o que mais incomodava."
        )
        documento.itens(material.perguntas)

    documento.espaco(6)
    documento.destaque(
        "Este material explica a condição em termos gerais e não substitui a "
        "consulta médica. Ele não contém dose, receita nem orientação de "
        "tratamento individual — o que vale para você é o que foi combinado com "
        "o seu médico.",
        cor_fundo=TINTA_TEAL,
        cor_barra=TEAL,
        rotulo="Importante",
    )

    if material.fontes:
        documento.titulo("De onde vem esta informação")
        documento.itens(list(material.fontes))

    documento._garantir(30)
    hoje = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y")
    nota = (
        f"Material gerado no CorVIA em {hoje}. Em caso de dúvida sobre o seu caso, "
        "procure o profissional que entregou este documento."
    )
    for linha in quebrar(nota, documento.util, 8):
        documento._garantir(12)
        documento.pdf.texto(documento.margem, documento.y - 8, linha, 8, NEUTRO, italico=True)
        documento.y -= 12

    return documento.salvar_bytes()
