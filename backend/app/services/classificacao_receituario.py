# -*- coding: utf-8 -*-
"""Classificação do receituário: de itens prescritos para documentos a emitir.

O núcleo é `classificar()`, função pura sobre dados simples — sem ORM, sem
sessão, sem I/O. É de propósito: esta é a lógica que decide se um paciente sai
com Notificação A amarela ou com Receita de Controle Especial, e ela precisa ser
testável sem banco de pé.

Três regras que o código implementa e que não são negociáveis:

1. **Texto livre não é classificável.** Item sem substância resolvida não é
   chutado para "comum" — vira pendência.
2. **Regra de adendo não codificada rebaixa para revisão humana**, nunca para o
   tipo da lista. Oxicodona é A1, mas em comprimido de liberação controlada até
   40 mg a norma manda Receita de Controle Especial: assumir o tipo da lista
   nesse caso emite o documento errado.
3. **Substância proscrita é recusada**, não classificada.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

TIPO_COMUM = "COMUM"


def normalizar(nome: str) -> str:
    """Mesma normalização usada no casamento com a CMED: sem acento, minúsculo,
    sem o sal entre parênteses. "Anlodipino (besilato)" e "BESILATO DE
    ANLODIPINO" precisam colidir, senão o medicamento não encontra a substância."""
    n = unicodedata.normalize("NFD", nome or "")
    n = "".join(c for c in n if unicodedata.category(c) != "Mn").lower()
    n = re.sub(r"\([^)]*\)", " ", n)                    # remove "(besilato)"
    n = re.sub(r"^\s*(cloridrato|besilato|maleato|sulfato|sodica|sodico|"
               r"potassica|calcica|mesilato|tartarato|succinato|acetato|"
               r"fosfato|nitrato|bromidrato)\s+de\s+", " ", n)
    n = re.sub(r"[^a-z0-9 ]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


@dataclass
class ItemPrescrito:
    """O que o médico escolheu. `substancia` vem da base estruturada de
    medicamentos — nunca do que ele digitou livremente.

    `lista` nasce vazia (o médico não escolhe lista) e é preenchida por
    `classificar()`, na hora de agrupar por `DocumentoPlanejado` — é o único
    lugar em que a lista da substância (ex.: "C5") fica associada ao item
    depois do agrupamento, e sem ela `app/api/receituario.py` não teria como
    saber, ao montar o snapshot de `PrescriptionDocument.itens`, quais itens
    de uma Receita de Controle Especial são anabolizantes (Lei 9.965/2000)."""
    descricao: str
    substancia: str | None = None
    apresentacao: str | None = None
    quantidade: str | None = None
    posologia: str | None = None
    lista: str | None = None


@dataclass
class Substancia:
    """Projeção de `ControlledSubstance`, sem ORM."""
    nome: str
    lista: str
    tipo_sncr: str | None
    proscrita: bool = False


@dataclass
class Regra:
    """Projeção de `PrescriptionRule`.

    `condicao["substancias"]` delimita o ALCANCE da regra e é preenchida mesmo
    quando `codificada` é falso. Sem isso, uma regra crua sobre codeína faria
    todo item da Lista A2 cair em revisão — inclusive os que ela não menciona —,
    e a pendência viraria ruído permanente que o médico aprende a ignorar. Lista
    vazia significa alcance desconhecido, e aí a regra vale para toda a lista,
    que é o lado conservador."""
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
    tipo: str | None                 # None = não foi possível decidir
    lista: str | None = None
    motivo: str = ""
    pendencia: str | None = None     # texto do que impede a decisão automática
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
    """Avalia uma condição já codificada por humano. Conservadora: se qualquer
    critério não puder ser avaliado, não casa — e o item cai em pendência pela
    regra do chamador, em vez de ser classificado por engano."""
    forma = condicao.get("forma")
    teto = condicao.get("mg_por_unidade_max")
    # Regra incondicional sobre a substância — "os medicamentos que contenham
    # fenobarbital ficam sujeitos a Receita de Controle Especial" não depende de
    # dose nem de forma. Exigir apresentação aqui mandaria para revisão humana um
    # caso que a norma decide sozinha.
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
    """`substancias` é indexado por nome normalizado. Devolve um documento por
    tipo exigido — é isto que faz receita com listas diferentes virar documentos
    separados sem caso especial."""
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
            # Não estar na 344/98 é o caso normal: a imensa maioria dos
            # medicamentos não é controlada.
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

        # Nenhuma regra codificada casou. Se ainda restam regras NÃO codificadas
        # para esta lista, não dá para afirmar que o tipo da lista é o correto.
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
        # Item indecidível não entra em documento nenhum: entra como pendência
        # do documento comum, para o médico resolver antes de emitir.
        tipo = c.tipo or TIPO_COMUM
        c.item.lista = c.lista
        doc = por_tipo.setdefault(tipo, DocumentoPlanejado(tipo=tipo, itens=[]))
        doc.itens.append(c.item)
        if c.pendencia:
            doc.pendencias.append(f"{c.item.descricao}: {c.pendencia}")

    documentos = [por_tipo[t] for t in sorted(por_tipo)]
    exige_revisao = bool(recusados) or any(d.pendencias for d in documentos)
    return Resultado(documentos=documentos, recusados=recusados, exige_revisao=exige_revisao)
