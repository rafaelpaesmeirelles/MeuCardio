"""Calculadoras de doses cardiovasculares agudas — AHA ACLS 2025.

Produção identificável conforme INSTRUCOES_CHATGPT.md.
Nenhuma dose abaixo foi inferida de memória: todas foram conferidas contra
os algoritmos e a diretriz AHA 2025 citados em cada Calculator.reference.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

AHA_ALS_2025 = (
    "Wigginton JG, Agarwal S, Bartos JA, et al. Part 9: Advanced Life Support: "
    "2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation "
    "and Emergency Cardiovascular Care. Circulation. 2025;152(Suppl 2):S538-S577. "
    "doi:10.1161/CIR.0000000000001376."
)


# ------------------------------------------------ PCR adulta: doses fixas AHA 2025

def _pcr_adulto_dose_fixa(d: dict) -> dict:
    terapia = d["terapia"]
    if terapia == "epinefrina":
        return {
            "farmaco": "Epinefrina",
            "dose": "1 mg IV/IO",
            "intervalo": "a cada 3-5 min",
        }
    if terapia == "amiodarona_1":
        return {
            "farmaco": "Amiodarona",
            "dose": "300 mg IV/IO em bolus",
            "etapa": "1ª dose para FV/TV sem pulso refratária",
        }
    return {
        "farmaco": "Amiodarona",
        "dose": "150 mg IV/IO em bolus",
        "etapa": "2ª dose para FV/TV sem pulso refratária",
    }


def _pcr_adulto_dose_fixa_txt(r: dict) -> str:
    if r["farmaco"] == "Epinefrina":
        return (
            "Epinefrina 1 mg IV/IO a cada 3-5 minutos durante a PCR adulta. "
            "Não usar dose alta de rotina; em ritmo chocável, priorizar as tentativas iniciais "
            "de desfibrilação antes da epinefrina."
        )
    return f"{r['farmaco']}: {r['dose']} — {r['etapa']}."


_PCR_ADULTO_DOSE_FIXA = Calculator(
    slug="acls-pcr-adulto-doses-fixas-2025",
    name="ACLS 2025 — PCR adulta: epinefrina e amiodarona",
    theme="Doses — Cardiologia Geral",
    purpose="Doses fixas IV/IO do algoritmo de parada cardíaca adulta AHA 2025.",
    fields=[
        Field("terapia", "Terapia", "select", options=[
            {"value": "epinefrina", "label": "Epinefrina — dose padrão durante PCR"},
            {"value": "amiodarona_1", "label": "Amiodarona — 1ª dose em FV/TV sem pulso refratária"},
            {"value": "amiodarona_2", "label": "Amiodarona — 2ª dose em FV/TV sem pulso refratária"},
        ])
    ],
    compute=_pcr_adulto_dose_fixa,
    interpret=_pcr_adulto_dose_fixa_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Amiodarona é opção para FV/TV sem pulso refratária à desfibrilação; não é fármaco de rotina para assistolia/AESP.",
        "A dose de epinefrina não substitui desfibrilação precoce em FV/TV sem pulso.",
    ],
)


# -------------------------------------------------------- lidocaína na PCR adulta

def _lidocaina_pcr_adulto(d: dict) -> dict:
    peso = float(d["peso"])
    etapa = d["etapa"]
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    if etapa == "primeira":
        minimo, maximo = peso * 1.0, peso * 1.5
        faixa = "1-1,5 mg/kg"
    else:
        minimo, maximo = peso * 0.5, peso * 0.75
        faixa = "0,5-0,75 mg/kg"
    return {
        "farmaco": "Lidocaína",
        "etapa": etapa,
        "dose_min_mg": round(minimo, 1),
        "dose_max_mg": round(maximo, 1),
        "faixa_por_peso": faixa,
    }


def _lidocaina_pcr_adulto_txt(r: dict) -> str:
    ordinal = "1ª" if r["etapa"] == "primeira" else "2ª"
    return (
        f"Lidocaína — {ordinal} dose: {r['dose_min_mg']}-{r['dose_max_mg']} mg IV/IO "
        f"({r['faixa_por_peso']}) para FV/TV sem pulso refratária à desfibrilação."
    )


_LIDOCAINA_PCR_ADULTO = Calculator(
    slug="lidocaina-pcr-adulto-2025",
    name="Lidocaína — FV/TV sem pulso no adulto (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Calcula a 1ª ou 2ª dose de lidocaína por peso na PCR adulta chocável refratária.",
    fields=[
        Field("peso", "Peso do paciente", "number", "kg", min=20, max=300),
        Field("etapa", "Etapa", "select", options=[
            {"value": "primeira", "label": "1ª dose — 1 a 1,5 mg/kg"},
            {"value": "segunda", "label": "2ª dose — 0,5 a 0,75 mg/kg"},
        ]),
    ],
    compute=_lidocaina_pcr_adulto,
    interpret=_lidocaina_pcr_adulto_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Usar como alternativa à amiodarona na FV/TV sem pulso refratária; a AHA 2025 não demonstra superioridade definitiva entre as duas.",
        "Esta calculadora não estabelece dose cumulativa máxima porque o algoritmo AHA 2025 consultado não fornece esse número na caixa de doses.",
    ],
)


# --------------------------------------------------------------- adenosina adulta

def _adenosina_adulto(d: dict) -> dict:
    etapa = d["etapa"]
    dose = 6 if etapa == "primeira" else 12
    return {"farmaco": "Adenosina", "etapa": etapa, "dose_mg": dose}


def _adenosina_adulto_txt(r: dict) -> str:
    ordinal = "1ª" if r["etapa"] == "primeira" else "2ª"
    return (
        f"Adenosina — {ordinal} dose: {r['dose_mg']} mg em push IV rápido, seguida imediatamente "
        "de flush com solução salina."
    )


_ADENOSINA_ADULTO = Calculator(
    slug="adenosina-tsv-adulto-2025",
    name="Adenosina — TSV regular no adulto (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="1ª e 2ª dose de adenosina para taquicardia regular apropriada ao uso de bloqueio AV.",
    fields=[
        Field("etapa", "Qual dose", "select", options=[
            {"value": "primeira", "label": "1ª dose"},
            {"value": "segunda", "label": "2ª dose, se necessária"},
        ])
    ],
    compute=_adenosina_adulto,
    interpret=_adenosina_adulto_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Não administrar em taquicardia de QRS largo instável, irregularmente irregular ou polimórfica.",
        "Em QRS largo, só considerar quando o ritmo for estável, regular e monomórfico.",
        "A AHA 2025 alerta para efeito muito intenso em acesso central ou pós-transplante cardíaco; 1 mg pode ser suficiente nesses cenários, portanto a sequência padrão 6/12 mg não deve ser aplicada automaticamente.",
        "Adenosina é contraindicada em asma por risco de broncoespasmo grave segundo a AHA 2025.",
    ],
)


# --------------------------------------------------------------- atropina adulta

def _atropina_adulto(d: dict) -> dict:
    doses_previas = int(d["doses_previas"])
    total_previo = float(doses_previas)
    proxima = 1.0 if total_previo < 3.0 else 0.0
    total_apos = min(total_previo + proxima, 3.0)
    return {
        "farmaco": "Atropina",
        "doses_previas_de_1mg": doses_previas,
        "proxima_dose_mg": proxima,
        "total_apos_mg": total_apos,
        "maximo_total_mg": 3.0,
    }


def _atropina_adulto_txt(r: dict) -> str:
    if r["proxima_dose_mg"] == 0:
        return (
            "Dose máxima total de atropina do algoritmo (3 mg) já atingida. "
            "Se persiste bradicardia com comprometimento cardiopulmonar, considerar pacing "
            "transcutâneo e/ou infusão de dopamina ou epinefrina, além de consulta especializada."
        )
    return (
        f"Atropina 1 mg IV em bolus agora; repetir a cada 3-5 min se necessário. "
        f"Após esta dose, total acumulado = {r['total_apos_mg']} mg; máximo total = 3 mg."
    )


_ATROPINA_ADULTO = Calculator(
    slug="atropina-bradicardia-adulto-2025",
    name="Atropina — bradicardia sintomática no adulto (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Controla a sequência de 1 mg por dose e o teto total de 3 mg da AHA 2025.",
    fields=[
        Field("doses_previas", "Quantas doses de 1 mg já foram administradas?", "select", options=[
            {"value": 0, "label": "Nenhuma"},
            {"value": 1, "label": "1 dose (1 mg total)"},
            {"value": 2, "label": "2 doses (2 mg total)"},
            {"value": 3, "label": "3 doses (3 mg total — teto atingido)"},
        ])
    ],
    compute=_atropina_adulto,
    interpret=_atropina_adulto_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Aplicar apenas quando a bradicardia estiver associada a comprometimento cardiopulmonar e após avaliação de causas reversíveis.",
        "Não atrasar pacing ou suporte vasoativo quando a resposta à atropina for inadequada.",
    ],
)


# ----------------------------------------------- dopamina na bradicardia adulta

def _dopamina_bradicardia_adulto(d: dict) -> dict:
    peso = float(d["peso"])
    alvo = float(d["dose_alvo"])
    quantidade_mg = float(d["quantidade_mg"])
    volume_ml = float(d["volume_ml"])
    if min(peso, alvo, quantidade_mg, volume_ml) <= 0:
        raise ValueError("Todos os valores precisam ser maiores que zero.")
    concentracao_mcg_ml = quantidade_mg * 1000 / volume_ml
    ml_h = alvo * peso * 60 / concentracao_mcg_ml
    return {
        "farmaco": "Dopamina",
        "dose_alvo_mcg_kg_min": alvo,
        "ml_h": round(ml_h, 2),
        "faixa_aha_2025": "5-20 mcg/kg/min",
        "fora_da_faixa": not 5 <= alvo <= 20,
    }


def _dopamina_bradicardia_adulto_txt(r: dict) -> str:
    aviso = " ⚠️ Dose-alvo fora da faixa AHA 2025 de 5-20 mcg/kg/min." if r["fora_da_faixa"] else ""
    return f"Dopamina: {r['ml_h']} mL/h para {r['dose_alvo_mcg_kg_min']} mcg/kg/min.{aviso}"


_DOPAMINA_BRADICARDIA_ADULTO = Calculator(
    slug="dopamina-bradicardia-adulto-infusao-2025",
    name="Dopamina — infusão na bradicardia adulta (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Converte a dose-alvo AHA 2025 de dopamina em mL/h a partir da diluição preparada.",
    fields=[
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("dose_alvo", "Dose-alvo", "number", "mcg/kg/min", min=0.1, max=100),
        Field("quantidade_mg", "Quantidade de dopamina na solução", "number", "mg", min=0.1),
        Field("volume_ml", "Volume total da solução", "number", "mL", min=1),
    ],
    compute=_dopamina_bradicardia_adulto,
    interpret=_dopamina_bradicardia_adulto_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Usar quando atropina for ineficaz e como ponte para pacing/avaliação especializada quando indicado.",
        "Titrar à resposta clínica e reduzir gradualmente, conforme o algoritmo AHA 2025.",
    ],
)


# --------------------------------------------- epinefrina na bradicardia adulta

def _epinefrina_bradicardia_adulto(d: dict) -> dict:
    alvo = float(d["dose_alvo"])
    quantidade_mg = float(d["quantidade_mg"])
    volume_ml = float(d["volume_ml"])
    if min(alvo, quantidade_mg, volume_ml) <= 0:
        raise ValueError("Todos os valores precisam ser maiores que zero.")
    concentracao_mcg_ml = quantidade_mg * 1000 / volume_ml
    ml_h = alvo * 60 / concentracao_mcg_ml
    return {
        "farmaco": "Epinefrina",
        "dose_alvo_mcg_min": alvo,
        "ml_h": round(ml_h, 2),
        "faixa_aha_2025": "2-10 mcg/min",
        "fora_da_faixa": not 2 <= alvo <= 10,
    }


def _epinefrina_bradicardia_adulto_txt(r: dict) -> str:
    aviso = " ⚠️ Dose-alvo fora da faixa AHA 2025 de 2-10 mcg/min." if r["fora_da_faixa"] else ""
    return f"Epinefrina: {r['ml_h']} mL/h para {r['dose_alvo_mcg_min']} mcg/min.{aviso}"


_EPINEFRINA_BRADICARDIA_ADULTO = Calculator(
    slug="epinefrina-bradicardia-adulto-infusao-2025",
    name="Epinefrina — infusão na bradicardia adulta (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Converte a dose-alvo fixa AHA 2025 de epinefrina em mL/h a partir da diluição preparada.",
    fields=[
        Field("dose_alvo", "Dose-alvo", "number", "mcg/min", min=0.1, max=100),
        Field("quantidade_mg", "Quantidade de epinefrina na solução", "number", "mg", min=0.01),
        Field("volume_ml", "Volume total da solução", "number", "mL", min=1),
    ],
    compute=_epinefrina_bradicardia_adulto,
    interpret=_epinefrina_bradicardia_adulto_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "A dose de bradicardia é fixa em mcg/min; não confundir com esquemas mcg/kg/min usados em outros tipos de choque.",
        "Usar quando atropina for ineficaz e como ponte para pacing/avaliação especializada quando indicado.",
    ],
)


# ------------------------------------------ procainamida na TV/QRS largo estável

def _procainamida_tv_estavel(d: dict) -> dict:
    peso = float(d["peso"])
    taxa = float(d["taxa_mg_min"])
    if peso <= 0 or taxa <= 0:
        raise ValueError("Peso e taxa precisam ser maiores que zero.")
    max_total = peso * 17
    minutos_ate_max = max_total / taxa
    return {
        "farmaco": "Procainamida",
        "taxa_mg_min": taxa,
        "dose_maxima_17mg_kg_mg": round(max_total, 1),
        "tempo_ate_dose_maxima_min": round(minutos_ate_max, 1),
        "manutencao": "1-4 mg/min",
        "fora_da_faixa": not 20 <= taxa <= 50,
    }


def _procainamida_tv_estavel_txt(r: dict) -> str:
    aviso = " ⚠️ Taxa fora da faixa AHA 2025 de 20-50 mg/min." if r["fora_da_faixa"] else ""
    return (
        f"Procainamida {r['taxa_mg_min']} mg/min. Dose máxima pelo peso: "
        f"{r['dose_maxima_17mg_kg_mg']} mg (17 mg/kg), atingida em ~{r['tempo_ate_dose_maxima_min']} min "
        f"se não houver critério de parada antes. Manutenção: {r['manutencao']}.{aviso}"
    )


_PROCAINAMIDA_TV_ESTAVEL = Calculator(
    slug="procainamida-tv-estavel-adulto-2025",
    name="Procainamida — taquicardia de QRS largo estável (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Calcula a dose máxima por peso e o tempo até o teto para uma taxa de infusão escolhida.",
    fields=[
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("taxa_mg_min", "Taxa de infusão", "number", "mg/min", min=1, max=100),
    ],
    compute=_procainamida_tv_estavel,
    interpret=_procainamida_tv_estavel_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Interromper antes do teto se a arritmia for suprimida, surgir hipotensão ou o QRS aumentar >50%.",
        "Evitar procainamida em QT prolongado ou insuficiência cardíaca congestiva, conforme o algoritmo AHA 2025.",
        "Taquicardia de QRS largo hemodinamicamente instável exige cardioversão sincronizada, não infusão farmacológica prolongada.",
    ],
)


# ------------------------------------------ amiodarona na TV/QRS largo estável

def _amiodarona_tv_estavel(d: dict) -> dict:
    etapa = d["etapa"]
    if etapa == "carga":
        return {"farmaco": "Amiodarona", "dose": "150 mg IV", "tempo": "10 min"}
    return {"farmaco": "Amiodarona", "taxa": "1 mg/min", "duracao": "primeiras 6 h"}


def _amiodarona_tv_estavel_txt(r: dict) -> str:
    if "dose" in r:
        return "Amiodarona 150 mg IV em 10 minutos; pode repetir se a TV recorrer."
    return "Após a carga, infusão de amiodarona a 1 mg/min nas primeiras 6 horas."


_AMIODARONA_TV_ESTAVEL = Calculator(
    slug="amiodarona-tv-estavel-adulto-2025",
    name="Amiodarona — taquicardia de QRS largo estável (ACLS 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Dose de carga e infusão inicial da amiodarona na taquicardia de QRS largo estável.",
    fields=[
        Field("etapa", "Etapa", "select", options=[
            {"value": "carga", "label": "Carga inicial"},
            {"value": "manutencao", "label": "Infusão após a carga"},
        ])
    ],
    compute=_amiodarona_tv_estavel,
    interpret=_amiodarona_tv_estavel_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Taquicardia de QRS largo instável exige cardioversão sincronizada imediata.",
        "Evitar associação empírica de múltiplos antiarrítmicos por risco pró-arrítmico.",
    ],
)


# ------------------------------------------ controle agudo de frequência FA/flutter

def _controle_frequencia_fa(d: dict) -> dict:
    peso = float(d["peso"])
    farmaco = d["farmaco"]
    instavel = bool(d.get("instavel"))
    preexcitacao = bool(d.get("preexcitacao"))
    ic_sistolica_descompensada = bool(d.get("ic_sistolica_descompensada"))
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")

    if instavel:
        return {
            "conduta": "cardioversao_eletrica_imediata",
            "dose_farmacologica": "não calcular",
            "motivo": "instabilidade hemodinâmica atribuível à FA/flutter",
        }
    if preexcitacao:
        return {
            "conduta": "nao_usar_bloqueadores_nodais_ou_amiodarona_iv",
            "dose_farmacologica": "não calcular",
            "motivo": "FA/flutter com pré-excitação — risco de acelerar resposta ventricular e precipitar FV",
        }

    bloqueadores = {"diltiazem", "verapamil", "metoprolol", "esmolol", "propranolol"}
    if ic_sistolica_descompensada and farmaco in bloqueadores:
        return {
            "conduta": "farmaco_selecionado_nao_recomendado",
            "dose_farmacologica": "não calcular",
            "motivo": "disfunção sistólica de VE com IC descompensada",
        }

    if farmaco == "diltiazem":
        return {
            "farmaco": "Diltiazem",
            "bolus_mg": round(peso * 0.25, 1),
            "administracao": "IV em 2 min",
            "infusao": "5-10 mg/h",
        }
    if farmaco == "verapamil":
        return {
            "farmaco": "Verapamil",
            "bolus_min_mg": round(peso * 0.075, 1),
            "bolus_max_mg": round(peso * 0.15, 1),
            "administracao": "IV em 2 min; dose adicional após 30 min se sem resposta",
            "infusao_mg_kg_min": 0.005,
        }
    if farmaco == "metoprolol":
        return {"farmaco": "Metoprolol", "dose": "2,5-5 mg IV em 2 min", "repeticao": "até 3 doses"}
    if farmaco == "esmolol":
        return {
            "farmaco": "Esmolol",
            "bolus_mcg": round(peso * 500, 0),
            "administracao": "IV em 1 min",
            "infusao": "50-300 mcg/kg/min",
        }
    if farmaco == "propranolol":
        return {"farmaco": "Propranolol", "dose": "1 mg IV em 1 min", "repeticao": "até 3 doses"}
    if farmaco == "amiodarona":
        return {"farmaco": "Amiodarona", "dose": "300 mg IV em 1 h", "infusao": "10-50 mg/h por 24 h"}
    return {
        "farmaco": "Digoxina",
        "dose": "0,25 mg IV",
        "repeticao": "repetir conforme resposta até máximo 1,5 mg em 24 h",
    }


def _controle_frequencia_fa_txt(r: dict) -> str:
    if "conduta" in r:
        if r["conduta"] == "cardioversao_eletrica_imediata":
            return "Instabilidade atribuível à FA/flutter: a AHA 2025 recomenda cardioversão elétrica imediata; não usar esta calculadora para atrasar o choque."
        return f"Nenhuma dose sugerida: {r['motivo']}."
    itens = []
    for chave, valor in r.items():
        if chave != "farmaco":
            itens.append(f"{chave.replace('_', ' ')}: {valor}")
    return f"{r['farmaco']} — " + "; ".join(itens) + "."


_CONTROLE_FREQUENCIA_FA = Calculator(
    slug="controle-frequencia-fa-flutter-agudo-adulto-2025",
    name="FA/flutter com resposta rápida — doses IV e bloqueios de segurança (AHA 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Seleciona doses IV para controle agudo de frequência e bloqueia cenários em que o fármaco não deve ser usado.",
    fields=[
        Field("peso", "Peso", "number", "kg", min=20, max=300),
        Field("farmaco", "Fármaco", "select", options=[
            {"value": "diltiazem", "label": "Diltiazem"},
            {"value": "verapamil", "label": "Verapamil"},
            {"value": "metoprolol", "label": "Metoprolol"},
            {"value": "esmolol", "label": "Esmolol"},
            {"value": "propranolol", "label": "Propranolol"},
            {"value": "amiodarona", "label": "Amiodarona"},
            {"value": "digoxina", "label": "Digoxina"},
        ]),
        Field("instavel", "Instabilidade hemodinâmica atribuível à FA/flutter", "boolean",
              help="Hipotensão/choque, isquemia ou deterioração aguda atribuível à arritmia."),
        Field("preexcitacao", "FA/flutter com pré-excitação", "boolean",
              help="Bloqueadores nodais e amiodarona IV podem ser perigosos neste cenário."),
        Field("ic_sistolica_descompensada", "Disfunção sistólica de VE com IC descompensada", "boolean"),
    ],
    compute=_controle_frequencia_fa,
    interpret=_controle_frequencia_fa_txt,
    reference=AHA_ALS_2025,
    kind="dose",
    limitations=[
        "Diltiazem e verapamil devem ser evitados também em hipotensão, cardiomiopatia e síndrome coronariana aguda conforme a tabela AHA 2025; esses três modificadores adicionais não estão automatizados nesta versão.",
        "Digoxina tem início de ação lento e exige cautela em disfunção renal.",
        "Amiodarona IV pode ser útil para controle de frequência no paciente criticamente enfermo sem pré-excitação quando bloqueadores beta/cálcio não são apropriados.",
        "Não utilizar bloqueadores nodais nem amiodarona IV em FA/flutter pré-excitada.",
    ],
)


ACLS_2025_DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [
        _PCR_ADULTO_DOSE_FIXA,
        _LIDOCAINA_PCR_ADULTO,
        _ADENOSINA_ADULTO,
        _ATROPINA_ADULTO,
        _DOPAMINA_BRADICARDIA_ADULTO,
        _EPINEFRINA_BRADICARDIA_ADULTO,
        _PROCAINAMIDA_TV_ESTAVEL,
        _AMIODARONA_TV_ESTAVEL,
        _CONTROLE_FREQUENCIA_FA,
    ]
}
