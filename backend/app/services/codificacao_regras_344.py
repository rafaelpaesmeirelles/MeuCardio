# -*- coding: utf-8 -*-
"""Codificação das regras de adendo da Portaria 344/98 em condição de máquina.

Cada entrada aqui é uma leitura humana de um item de adendo, com a decisão
explícita de codificar ou não. **Não codificar é resultado legítimo** — e é o
resultado certo sempre que a condição normativa depende de informação que a
apresentação do medicamento não carrega.

O erro que importa evitar tem direção: aplicar uma regra que não deveria valer
rebaixa o documento (emite Receita de Controle Especial onde a norma exige
Notificação de Receita A). Por isso, na dúvida, `codificada = False` — o item cai
para revisão humana, e o médico decide com o texto da norma na mão.

Chave = (lista, número do item no adendo), que é como a norma se refere a si mesma.
"""

# `substancias` delimita o alcance e é preenchido SEMPRE, inclusive nas regras
# não codificadas: sem isso, uma regra crua sobre codeína faria todo item da
# Lista A2 cair em revisão, e a pendência viraria ruído.
CODIFICACAO: dict[tuple[str, str], dict] = {
    # ---------------------------------------------------------------- A1 --
    ("A1", "2"): dict(
        codificada=False,
        substancias=["difenoxilato"],
        motivo="A condição não é só a dose de difenoxilato (2,5 mg por unidade): "
               "exige que a quantidade de sulfato de atropina seja de pelo menos "
               "1,0% da quantidade de difenoxilato. É uma RELAÇÃO entre dois "
               "componentes, e a apresentação não a expressa de forma confiável.",
    ),
    ("A1", "3"): dict(
        codificada=False,
        substancias=["ópio", "opio"],
        motivo="O teto é de concentração — até 5 mg de morfina anidra POR MILILITRO "
               "—, não por unidade posológica. O vocabulário de condição só tem "
               "teto por unidade; codificar isso como mg/unidade inverteria o "
               "critério.",
    ),
    ("A1", "5"): dict(
        codificada=True, tipo_resultante="RCE",
        substancias=["oxicodona"],
        condicao={"forma": "liberação controlada", "mg_por_unidade_max": 40},
        motivo="Condição fechada e legível na apresentação: forma farmacêutica de "
               "comprimido de liberação controlada e não mais que 40 mg por "
               "unidade posológica.",
    ),
    ("A1", "8"): dict(
        codificada=False,
        substancias=["buprenorfina"],
        motivo="A norma distingue adesivo transdérmico EM MATRIZ POLIMÉRICA, sem "
               "reservatório de substância ativa, do adesivo com reservatório. "
               "Isso é detalhe de construção do sistema transdérmico e não "
               "aparece na apresentação.",
    ),
    # ---------------------------------------------------------------- A2 --
    ("A2", "2"): dict(
        codificada=False,
        substancias=["acetildiidrocodeína", "codeína", "diidrocodeína", "etilmorfina",
                     "folcodina", "nicodicodina", "norcodeína"],
        motivo="Há duas condições: até 100 mg de entorpecente por unidade E "
               "concentração de até 2,5% NAS PREPARAÇÕES DE FORMAS INDIVISÍVEIS. "
               "A segunda depende de classificar a forma como divisível ou não, "
               "o que não está na apresentação. Codificar só a primeira "
               "rebaixaria indevidamente preparações acima de 2,5%.",
    ),
    ("A2", "3"): dict(
        codificada=True, tipo_resultante="RCE",
        substancias=["tramadol"],
        condicao={"mg_por_unidade_max": 100},
        motivo="Condição única e explícita: quantidade que não exceda 100 mg de "
               "tramadol por unidade posológica. A norma inclui as preparações "
               "misturadas a outros componentes, então não há restrição de forma.",
    ),
    ("A2", "4"): dict(
        codificada=False,
        substancias=["dextropropoxifeno"],
        motivo="Mesma estrutura do item 2 da A2: teto por unidade E limite de "
               "concentração de 2,5% em preparações indivisíveis. A segunda "
               "condição não é avaliável pela apresentação.",
    ),
    ("A2", "5"): dict(
        codificada=True, tipo_resultante="RCE",
        substancias=["nalbufina"],
        condicao={"mg_por_unidade_max": 10},
        motivo="Condição única e explícita: não exceder 10 mg de cloridrato de "
               "nalbufina por unidade posológica.",
    ),
    ("A2", "6"): dict(
        codificada=False,
        substancias=["propiram"],
        motivo="Exige associação a, no mínimo, igual quantidade de metilcelulose. "
               "É uma relação entre componentes que a apresentação não expressa.",
    ),
    # ---------------------------------------------------------------- B1 --
    ("B1", "2"): dict(
        codificada=True, tipo_resultante="RCE",
        substancias=["fenobarbital", "metilfenobarbital", "barbital", "barbexaclona"],
        condicao={},
        motivo="Regra INCONDICIONAL sobre a substância: 'os medicamentos que "
               "contenham fenobarbital, metilfenobarbital, barbital e "
               "barbexaclona ficam sujeitos a prescrição da Receita de Controle "
               "Especial'. Não há condição de dose nem de forma a avaliar.",
    ),
    ("B1", "9"): dict(
        codificada=True, tipo_resultante="RCE",
        substancias=["perampanel"],
        condicao={},
        motivo="Regra incondicional sobre a substância, na mesma forma do item 2.",
    ),
}


def chave_do_texto(lista: str, texto: str) -> tuple[str, str] | None:
    """A norma numera seus próprios itens ('2)', '3)'). É a chave estável — o
    texto muda de quebra de linha entre extrações, o número não."""
    texto = texto.lstrip()
    numero = ""
    for c in texto:
        if c.isdigit():
            numero += c
        else:
            break
    return (lista, numero) if numero else None
