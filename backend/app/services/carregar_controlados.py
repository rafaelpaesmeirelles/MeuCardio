# -*- coding: utf-8 -*-
"""Carrega as listas da Portaria 344/98 e semeia os tipos de receituário.

Duas cargas distintas, no mesmo módulo porque nascem da mesma norma:

1. **Substâncias e regras de adendo**, de `controlados/listas-344-98.json`, que
   por sua vez foi extraído da RDC 999/2025 pelo `controlados/extrair_344.py`.
2. **Tipos de receituário**, semeados aqui porque o conjunto é pequeno, fechado
   e vem de duas fontes conferidas: o subtítulo literal de cada lista da norma e
   o Manual da API do SNCR.

Regra que governa o seed: **só entra campo com origem conferida.** Onde a fonte
não foi lida, o campo fica nulo e o motivo está escrito ao lado — validade em
dias e destinação das vias estão nos artigos da Portaria, que ainda não foram
lidos. Preencher de memória aqui produziria um documento legalmente errado com
aparência de completo.
"""
import json

from sqlalchemy.orm import Session

from app.models.receituario import ControlledSubstance, PrescriptionRule, PrescriptionType
from app.services.classificacao_receituario import normalizar
from app.services.codificacao_regras_344 import CODIFICACAO, chave_do_texto

CAMINHO_PADRAO = "/controlados/listas-344-98.json"

# Origem de cada campo, para quem for conferir:
#  - codigo/nome/cor .............. Portaria 344/98 e RDC 1.000/2025
#  - vias ......................... subtítulo literal da lista ("em duas vias")
#  - endpoint/lote ................ Manual da API do SNCR, 1ª ed., junho/2026
#  - validade_dias, destinacao .... NÃO LIDOS AINDA (artigos da Portaria)
#  - ativo ........................ só o comum; o resto espera SNCR e assinatura
TIPOS = [
    dict(codigo="COMUM", nome="Receituário comum", cor="branca", vias=1,
         exige_numeracao_sncr=False, ativo=True),
    dict(codigo="NRA", nome="Notificação de Receita A", cor="amarela", vias=1,
         exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/notificacao-receita",
         lote_min=10, lote_max=50, exige_retencao=True, ativo=False),
    dict(codigo="NRB", nome="Notificação de Receita B", cor="azul", vias=1,
         exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/notificacao-receita",
         lote_min=10, lote_max=50, exige_retencao=True, ativo=False),
    dict(codigo="NRB2", nome="Notificação de Receita B2", cor="azul", vias=1,
         exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/notificacao-receita",
         lote_min=10, lote_max=50, exige_retencao=True, ativo=False),
    dict(codigo="NRR", nome="Notificação de Receita Especial — retinoides", cor="branca",
         vias=1, exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/notificacao-receita",
         lote_min=10, lote_max=50, exige_retencao=True, ativo=False),
    dict(codigo="NRT", nome="Notificação de Receita — talidomida", cor="branca", vias=1,
         exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/notificacao-receita",
         lote_min=10, lote_max=50, exige_retencao=True, ativo=False),
    # Modelo físico Anvisa V2, vigente e obrigatório desde 18/05/2026.
    # Não contém numeração SNCR. A saída é manual/impressa em duas vias;
    # emissão eletrônica permanece bloqueada até a integração oficial.
    dict(codigo="RCE", nome="Receita de Controle Especial", cor="branca", vias=2,
         destinacao_vias=["1ª via - Retenção pela Farmácia", "2ª via - Paciente"],
         validade_dias=30, exige_numeracao_sncr=False, endpoint_sncr=None,
         lote_min=None, lote_max=None, exige_retencao=True,
         campos_obrigatorios=["emitente", "paciente_nome", "paciente_documento",
                              "prescricao", "data", "assinatura"], ativo=True),
    dict(codigo="RET", nome="Receita sujeita a retenção", cor="branca", vias=2,
         exige_numeracao_sncr=True, endpoint_sncr="/numeracoes/receita-especial-retencao",
         lote_min=1000, lote_max=1000, exige_retencao=True, ativo=False),
]


def semear_tipos(db: Session) -> dict:
    """Upsert por código. Não mexe em `ativo` de registro que já existe: ligar o
    controle especial é decisão humana, e uma recarga não pode ligá-lo sozinha —
    mesma guarda que os carregadores de conteúdo aplicam a `published`."""
    novos = atualizados = 0
    for t in TIPOS:
        existente = db.query(PrescriptionType).filter(
            PrescriptionType.codigo == t["codigo"]).first()
        if existente:
            for campo, valor in t.items():
                if campo != "ativo":
                    setattr(existente, campo, valor)
            atualizados += 1
        else:
            db.add(PrescriptionType(**t))
            novos += 1
    db.commit()
    return {"novos": novos, "atualizados": atualizados}


def carregar_listas(db: Session, caminho: str = CAMINHO_PADRAO) -> dict:
    dados = json.load(open(caminho, encoding="utf-8"))
    versao = dados["fonte"]["republicacao_consolidada"]
    norma = dados["fonte"]["norma_base"]

    # Recarga da MESMA versão substitui; versão nova convive, porque uma receita
    # emitida precisa poder dizer qual versão a classificou.
    db.query(ControlledSubstance).filter(ControlledSubstance.fonte_versao == versao).delete()
    db.query(PrescriptionRule).filter(PrescriptionRule.fonte_versao == versao).delete()

    subs = regras = 0
    vistos: set[str] = set()
    for lista in dados["listas"]:
        for bruto in lista["substancias"]:
            partes = [p.strip() for p in bruto.split("|") if p.strip()]
            nome, sinonimos = partes[0], partes[1:]
            chave = normalizar(nome)
            if not chave or chave in vistos:
                # A norma repete substância entre listas em alguns casos; a
                # unicidade do banco é por (nome_normalizado, versão), então a
                # primeira ocorrência vence e as demais são ignoradas de propósito.
                continue
            vistos.add(chave)
            db.add(ControlledSubstance(
                nome=nome, nome_normalizado=chave, sinonimos=sinonimos,
                lista=lista["lista"], tipo_sncr=lista.get("tipo_sncr"),
                proscrita=bool(lista.get("proscrita")),
                fonte_norma=norma, fonte_versao=versao,
            ))
            subs += 1

        for texto in lista.get("regras_condicionais", []):
            # A codificação é dado sobre a norma e vive versionada junto dela:
            # aplicada aqui, uma recarga nunca perde o trabalho de leitura.
            cod = CODIFICACAO.get(chave_do_texto(lista["lista"], texto) or ("", ""), {})
            condicao = dict(cod.get("condicao") or {})
            condicao["substancias"] = cod.get("substancias") or []
            if cod.get("motivo"):
                condicao["motivo_da_decisao"] = cod["motivo"]
            db.add(PrescriptionRule(
                lista=lista["lista"], texto_normativo=texto,
                tipo_resultante=cod.get("tipo_resultante"),
                codificada=bool(cod.get("codificada")), condicao=condicao,
                fonte_versao=versao,
            ))
            regras += 1

    db.commit()
    codificadas = db.query(PrescriptionRule).filter(
        PrescriptionRule.fonte_versao == versao, PrescriptionRule.codificada.is_(True)).count()
    return {"versao": versao, "substancias": subs, "regras_condicionais": regras,
            "regras_codificadas": codificadas,
            "regras_em_revisao_humana": regras - codificadas,
            "aviso": dados.get("aviso")}


def carregar(db: Session, caminho: str = CAMINHO_PADRAO) -> dict:
    return {"tipos": semear_tipos(db), "listas": carregar_listas(db, caminho)}
