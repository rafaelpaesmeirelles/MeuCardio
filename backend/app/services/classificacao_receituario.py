# -*- coding: utf-8 -*-
"""Classificação do receituário: de itens prescritos para documentos a emitir.

O núcleo é `classificar()`, função pura sobre dados simples — sem ORM, sem
sessão, sem I/O. A substância genérica decide a classificação regulatória; a
descrição comercial escolhida pelo prescritor permanece separada e intacta.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

TIPO_COMUM = "COMUM"


def normalizar(nome: str) -> str:
    """Normaliza nomes para casamento entre medicamentos, CMED e listas.

    O prefixo de sal/éster (formato "<SAL/ÉSTER> DE <SUBSTÂNCIA>", como a CMED
    grava) precisa ser removido para casar contra o nome-base das listas da
    Portaria 344/98 (ex.: `ControlledSubstance.nome_normalizado`, que é
    `normalizar("Testosterona")`). Lista conferida uma a uma contra
    `controlados/listas-344-98.json`: nenhum item da norma começa com um
    destes prefixos + " de " — ampliar a lista não corta o próprio nome de
    nenhuma substância regulada, só o sal/éster de apresentação comercial.

    Achado real que motivou a ampliação (09/08/2026): "UNDECILATO DE
    TESTOSTERONA" (Nebido, Lista C5) não normalizava para "testosterona" —
    caía em TIPO_COMUM, sem exigir Receita de Controle Especial. Os ésteres de
    andrógenos/anabolizantes abaixo (undecilato, cipionato, enantato,
    propionato, fenilpropionato/fempropionato — as duas grafias, CMED não é
    consistente —, isocaproato, decanoato, valerato) cobrem as apresentações
    comerciais reais de Testosterona, Nandrolona, Drostanolona e Boldenona
    (todas Lista C5). Varredura do mesmo tipo achou mais três gaps do mesmo
    defeito em outras listas, cada um confirmado como o nome real de
    apresentação comercial de uma substância já presente na norma: `citrato`
    (Citrato de Fentanila, Lista A1 — opioide, é a forma mais prescrita),
    `fumarato` (Fumarato de Quetiapina, Lista C1), `hemitartarato`
    (Hemitartarato de Zolpidem, Lista B1) e `dimesilato` (Dimesilato de
    Lisdexanfetamina, Lista A3).
    """
    n = unicodedata.normalize("NFD", nome or "")
    n = "".join(c for c in n if unicodedata.category(c) != "Mn").lower()
    n = re.sub(r"\([^)]*\)", " ", n)
    n = re.sub(r"^\s*(cloridrato|besilato|maleato|sulfato|sodica|sodico|"
               r"potassica|calcica|mesilato|tartarato|succinato|acetato|"
               r"fosfato|nitrato|bromidrato|undecilato|cipionato|enantato|"
               r"propionato|fenilpropionato|fempropionato|isocaproato|"
               r"decanoato|valerato|citrato|fumarato|hemitartarato|"
               r"dimesilato)\s+de\s+", " ", n)
    n = re.sub(r"[^a-z0-9 ]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


@dataclass
class ItemPrescrito:
    """Item clínico com texto escolhido e substância regulatória independentes."""
    descricao: str
    substancia: str | None = None
    apresentacao: str | None = None
    quantidade: str | None = None
    posologia: str | None = None
    uso_continuo: bool = False
    lista: str | None = None
    brand_name: str | None = None
    manufacturer: str | None = None
    ggrem: str | None = None
    pmc_snapshot: float | None = None
    uf: str | None = None
    cmed_version: str | None = None
    drug_id: int | None = None
    # Preenchido só quando o item veio do catálogo prescritivo amplo (CMED)
    # SEM `Drug` clínico correspondente — rastreabilidade até a linha exata
    # da planilha que originou a `substancia` usada na classificação.
    cmed_apresentacao_id: int | None = None


@dataclass
class Substancia:
    nome: str
    lista: str
    tipo_sncr: str | None
    proscrita: bool = False


@dataclass
class Regra:
    lista: str
    texto_normativo: str
    tipo_resultante: str | None
    codificada: bool = False
    condicao: dict = field(default_factory=dict)

    def alcanca(self, substancia_normalizada: str) -> bool:
        alvos = self.condicao.get("substancias") or []
        if not alvos:
            return True
        return any(normalizar(a) == substancia_normalizada for a in alvos)


@dataclass
class ItemClassificado:
    item: ItemPrescrito
    tipo: str | None
    lista: str | None = None
    motivo: str = ""
    pendencia: str | None = None
    recusado: bool = False


@dataclass
class DocumentoPlanejado:
    tipo: str
    itens: list[ItemPrescrito]
    pendencias: list[str] = field(default_factory=list)


@dataclass
class Resultado:
    documentos: list[DocumentoPlanejado]
    recusados: list[ItemClassificado]
    exige_revisao: bool


def _condicao_casa(condicao: dict, item: ItemPrescrito) -> bool:
    forma = condicao.get("forma")
    teto = condicao.get("mg_por_unidade_max")
    if forma is None and teto is None:
        return True
    apres = normalizar(item.apresentacao or "")
    if not apres:
        return False
    if forma and normalizar(forma) not in apres:
        return False
    if teto is not None:
        achados = re.findall(r"(\d+(?:[.,]\d+)?)\s*mg", apres)
        if not achados:
            return False
        if max(float(a.replace(",", ".")) for a in achados) > float(teto):
            return False
    return True


def classificar(
    itens: list[ItemPrescrito],
    substancias: dict[str, Substancia],
    regras: list[Regra],
) -> Resultado:
    classificados: list[ItemClassificado] = []

    for item in itens:
        if not item.substancia:
            classificados.append(ItemClassificado(
                item=item, tipo=None,
                motivo="Item sem substância resolvida na base estruturada.",
                pendencia="Selecione o medicamento na base para permitir a "
                          "classificação — texto livre não pode ser classificado.",
            ))
            continue

        sub = substancias.get(normalizar(item.substancia))
        if sub is None:
            classificados.append(ItemClassificado(
                item=item, tipo=TIPO_COMUM,
                motivo="Substância não consta das listas da Portaria 344/98.",
            ))
            continue

        if sub.proscrita:
            classificados.append(ItemClassificado(
                item=item, tipo=None, lista=sub.lista, recusado=True,
                motivo=f"Substância proscrita (Lista {sub.lista}) — não há "
                       f"receituário que autorize a prescrição.",
            ))
            continue

        chave_sub = normalizar(sub.nome)
        aplicaveis = [r for r in regras if r.lista == sub.lista and r.alcanca(chave_sub)]
        codificada_que_casa = next(
            (r for r in aplicaveis if r.codificada and _condicao_casa(r.condicao, item)), None
        )
        if codificada_que_casa:
            classificados.append(ItemClassificado(
                item=item, tipo=codificada_que_casa.tipo_resultante, lista=sub.lista,
                motivo=f"Regra de adendo da Lista {sub.lista} sobrepõe o tipo padrão.",
            ))
            continue

        nao_codificadas = [r for r in aplicaveis if not r.codificada]
        if nao_codificadas:
            classificados.append(ItemClassificado(
                item=item, tipo=sub.tipo_sncr, lista=sub.lista,
                motivo=f"Tipo padrão da Lista {sub.lista}, ainda não confirmado.",
                pendencia=(
                    f"A Lista {sub.lista} tem {len(nao_codificadas)} regra(s) de adendo "
                    f"ainda não codificada(s) que podem mudar o tipo deste documento. "
                    f"Confira a apresentação contra o texto da norma antes de emitir."
                ),
            ))
            continue

        classificados.append(ItemClassificado(
            item=item, tipo=sub.tipo_sncr, lista=sub.lista,
            motivo=f"Tipo da Lista {sub.lista}, sem adendo aplicável.",
        ))

    recusados = [c for c in classificados if c.recusado]
    por_tipo: dict[str, DocumentoPlanejado] = {}
    for c in classificados:
        if c.recusado:
            continue
        tipo = c.tipo or TIPO_COMUM
        c.item.lista = c.lista
        doc = por_tipo.setdefault(tipo, DocumentoPlanejado(tipo=tipo, itens=[]))
        doc.itens.append(c.item)
        if c.pendencia:
            doc.pendencias.append(f"{c.item.descricao}: {c.pendencia}")

    documentos = [por_tipo[t] for t in sorted(por_tipo)]
    exige_revisao = bool(recusados) or any(d.pendencias for d in documentos)
    return Resultado(documentos=documentos, recusados=recusados, exige_revisao=exige_revisao)
