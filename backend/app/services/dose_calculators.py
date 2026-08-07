"""Calculadora de Doses Cardiológicas (pedido do Rafael, 07/08/2026).

Registro de calculadoras de DOSE — diferente das de escore/risco já existentes
em `calculators.py` (que pontuam e classificam risco): aqui a saída é uma dose,
volume ou taxa de infusão a administrar. Reaproveita o mesmo `Field`/
`Calculator`/`run()` de `calculators.py` — mesma tela (`Calculadora.tsx`),
mesmo endpoint (`/api/calculators/{slug}`), zero código novo de API — só
entram novos registros no `REGISTRY`, mesclados em `calculators.py`.

Cobertura inicial (pedido do Rafael: "concentrar conteúdo inicialmente" em três
áreas — a lista cresce depois, mesmo padrão de toda outra frente do produto):
**Cardiologia Geral**, **Cardiologia Pediátrica** e **Medicina Intensiva**.
`theme` de cada entrada é sempre `"Doses — <Área>"`, o que permite ao frontend
agrupar/filtrar por área sem precisar de campo novo no schema.

Regra do projeto, reafirmada aqui com mais peso que em qualquer outra
calculadora: "erro em calculadora clínica é pior que lacuna de conteúdo" — e
aqui o erro é uma DOSE, não um escore. Cada faixa de dose tem fonte citada em
`reference`; onde a fonte é secundária (bula agregada, cartão de referência
institucional) em vez de primária (diretriz/bula do fabricante), isso está
declarado explicitamente no próprio `reference`, nunca escondido. Nenhuma
calculadora BLOQUEIA um valor fora da faixa usual — ela avisa (`fora_da_faixa`
no resultado) porque cenário clínico real às vezes justifica dose fora do
"habitual", e a decisão é sempre do médico.
"""

from __future__ import annotations

from .calculators import Calculator, Field

# --------------------------------------------------------- infusão contínua --
# Uma função só, testada por análise dimensional, para toda droga cuja dose se
# expresse como taxa (peso-ajustada por minuto, peso-ajustada por hora, ou
# fixa por minuto) — em vez de reimplementar a mesma conta droga a droga, o
# que multiplicaria o risco de erro de fórmula sem ganho nenhum. `unidade_dose`
# decide o fator de peso e o fator de tempo; `unidade_concentracao` decide se
# a concentração informada (mg/mL ou U/mL) precisa virar mcg/mL antes de
# dividir — só a vasopressina usa U, todo o resto usa mcg.
INFUSOES: dict[str, dict] = {
    "noradrenalina": {
        "nome": "Noradrenalina (norepinefrina)",
        "contexto": "Choque séptico/vasoplégico — vasopressor de 1ª linha",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 0.01, "faixa_max": 0.5,
        "faixa_nota": (
            "0,01–0,5 mcg/kg/min cobre o uso inicial habitual. A partir de "
            "0,25–0,5 mcg/kg/min a Surviving Sepsis Campaign 2021 sugere "
            "associar vasopressina em vez de só escalar a dose; não há teto "
            "único de consenso para choque refratário — doses maiores existem "
            "na prática e a faixa aqui é a de início/manutenção habitual, não "
            "um limite absoluto."
        ),
    },
    "adrenalina": {
        "nome": "Adrenalina (epinefrina) — infusão contínua",
        "contexto": "Choque séptico refratário/cardiogênico — 2ª linha após noradrenalina",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 0.01, "faixa_max": 1.0,
        "faixa_nota": "0,01–1 mcg/kg/min, faixa amplamente citada; sem teto único de consenso.",
    },
    "dobutamina": {
        "nome": "Dobutamina",
        "contexto": "Suporte inotrópico — baixo débito, choque cardiogênico",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 2.0, "faixa_max": 20.0,
        "faixa_nota": (
            "2–20 mcg/kg/min é a faixa de manutenção habitual (3–5 mcg/kg/min "
            "costuma já dar resposta clínica adequada); dose de início pode "
            "ser 0,5–1 mcg/kg/min, e a bula descreve teto de até 40 mcg/kg/min."
        ),
    },
    "dopamina": {
        "nome": "Dopamina",
        "contexto": "Suporte inotrópico/vasopressor — uso hoje menos frequente que noradrenalina",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 2.0, "faixa_max": 20.0,
        "faixa_nota": "2–20 mcg/kg/min. Exige acesso venoso central.",
    },
    "milrinona": {
        "nome": "Milrinona",
        "contexto": "Inodilatador — baixo débito com resistência vascular elevada",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 0.125, "faixa_max": 0.75,
        "faixa_nota": (
            "0,125–0,75 mcg/kg/min é a faixa de uso habitual; a bula descreve "
            "teto de até 1,5 mcg/kg/min, pouco usado na prática por risco de "
            "hipotensão e arritmia. Ajustar para função renal reduzida — a "
            "milrinona tem eliminação predominantemente renal."
        ),
    },
    "vasopressina": {
        "nome": "Vasopressina",
        "contexto": "Choque séptico — associada à noradrenalina, dose fixa (não titulada por peso)",
        "unidade_dose": "U/min",
        "unidade_concentracao": "U/mL",
        "faixa_min": 0.01, "faixa_max": 0.04,
        "faixa_nota": (
            "0,01–0,04 U/min. Diferente dos demais vasopressores desta lista: "
            "não é titulada progressivamente para efeito — a prática mais "
            "comum é dose FIXA (0,03–0,04 U/min), acrescentada à noradrenalina "
            "em vez de substituí-la. Fonte primária: NEJM 2008;358:877-887 "
            "(estudo VASST) e Surviving Sepsis Campaign 2021."
        ),
    },
    "nitroglicerina": {
        "nome": "Nitroglicerina",
        "contexto": "Edema agudo de pulmão, isquemia miocárdica, controle pressórico",
        "unidade_dose": "mcg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 5.0, "faixa_max": 100.0,
        "faixa_nota": (
            "5–100 mcg/min. Dose FIXA (não ajustada por peso) — comece em "
            "5 mcg/min e titule a cada 3–5 min. Alguns protocolos descrevem "
            "teto de até 200 mcg/min em uso refratário."
        ),
    },
    "nitroprussiato": {
        "nome": "Nitroprussiato de sódio",
        "contexto": "Emergência hipertensiva, pós-carga elevada",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 0.1, "faixa_max": 2.0,
        "faixa_nota": (
            "0,1–2 mcg/kg/min (dose mínima habitualmente eficaz próxima de "
            "0,5 mcg/kg/min). Risco de intoxicação por cianeto/tiocianato em "
            "doses altas e uso prolongado (>48h), sobretudo com função renal "
            "reduzida — monitorizar."
        ),
    },
    "propofol": {
        "nome": "Propofol (sedação contínua)",
        "contexto": "Sedação em ventilação mecânica",
        "unidade_dose": "mcg/kg/min",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 5.0, "faixa_max": 50.0,
        "faixa_nota": (
            "5–50 mcg/kg/min (= 0,3–3 mg/kg/h) é a faixa de manutenção "
            "habitual. Evitar >70 mcg/kg/min por período prolongado (>48h) "
            "pelo risco de síndrome de infusão do propofol (PRIS) — "
            "considerar trocar a estratégia de sedação nesse cenário."
        ),
    },
    "fentanil": {
        "nome": "Fentanil (analgesia/sedação contínua)",
        "contexto": "Analgesia contínua em ventilação mecânica",
        "unidade_dose": "mcg/kg/h",
        "unidade_concentracao": "mg/mL",
        "faixa_min": 1.0, "faixa_max": 2.0,
        "faixa_nota": (
            "Dose inicial habitual 1–2 mcg/kg/h, titulada por escala de "
            "sedação/analgesia — não há teto único consensual na literatura "
            "consultada; doses maiores em uso prolongado são comuns na "
            "prática por tolerância. Ajustar a faixa aqui é uma prioridade "
            "explícita da próxima rodada de revisão desta calculadora."
        ),
    },
}


def _infusao_continua(d: dict) -> dict:
    droga = d.get("droga")
    info = INFUSOES.get(droga)
    if not info:
        raise ValueError("Selecione um fármaco da lista.")

    peso = d.get("peso")
    dose_alvo = float(d["dose_alvo"])
    quantidade = float(d["quantidade_no_frasco"])
    volume = float(d["volume_da_solucao"])
    if volume <= 0 or quantidade <= 0 or dose_alvo <= 0:
        raise ValueError("Quantidade, volume e dose alvo precisam ser maiores que zero.")

    por_peso = "kg" in info["unidade_dose"]
    por_hora = info["unidade_dose"].endswith("/h")

    if por_peso and not peso:
        raise ValueError(f"{info['nome']} é dosada por peso — informe o peso do paciente.")
    peso_kg = float(peso) if peso else None

    # Concentração na mesma unidade da dose: mg/mL -> mcg/mL (×1000); U/mL
    # fica como está (só a vasopressina usa U).
    concentracao = quantidade / volume
    if info["unidade_concentracao"] == "mg/mL":
        concentracao *= 1000  # mg/mL -> mcg/mL

    fator_tempo = 1 if por_hora else 60
    numerador = dose_alvo * (peso_kg if por_peso else 1) * fator_tempo
    ml_h = numerador / concentracao
    gotas_min = ml_h / 3  # equipo macrogotas padrão, 20 gtt/mL: gtt/min = mL/h ÷ 3

    fora_da_faixa = not (info["faixa_min"] <= dose_alvo <= info["faixa_max"])

    return {
        "farmaco": info["nome"],
        "dose_alvo": dose_alvo,
        "unidade_dose": info["unidade_dose"],
        "ml_h": round(ml_h, 2),
        "gotas_min": round(gotas_min, 1),
        "faixa_usual_min": info["faixa_min"],
        "faixa_usual_max": info["faixa_max"],
        "fora_da_faixa": fora_da_faixa,
    }


def _infusao_continua_txt(r: dict) -> str:
    aviso = (
        f" ⚠️ Dose informada ({r['dose_alvo']} {r['unidade_dose']}) está FORA da faixa "
        f"usual ({r['faixa_usual_min']}–{r['faixa_usual_max']} {r['unidade_dose']}) — "
        "confira antes de prescrever; pode ser intencional em cenário clínico "
        "específico, mas confirme."
        if r["fora_da_faixa"] else ""
    )
    return (
        f"{r['farmaco']}: {r['ml_h']} mL/h (≈ {r['gotas_min']} gotas/min em equipo "
        f"macrogotas, 20 gtt/mL) para {r['dose_alvo']} {r['unidade_dose']}."
        f"{aviso}"
    )


_OPCOES_DROGA = [{"value": k, "label": v["nome"]} for k, v in INFUSOES.items()]

_INFUSAO_CONTINUA = Calculator(
    slug="infusao-continua-peso",
    name="Infusão contínua — vasopressores, inotrópicos e sedativos",
    theme="Doses — Medicina Intensiva",
    purpose="Calcula a taxa de infusão (mL/h e gotas/min) a partir da dose-alvo e da diluição preparada.",
    fields=[
        Field("droga", "Fármaco", "select", options=_OPCOES_DROGA),
        Field("peso", "Peso do paciente", "number", "kg", min=1, max=300,
              help="Só necessário para fármacos dosados por peso — deixe em branco para os demais (nitroglicerina, vasopressina)."),
        Field("dose_alvo", "Dose-alvo", "number",
              help="Na unidade do fármaco escolhido — veja a faixa usual mostrada no resultado."),
        Field("quantidade_no_frasco", "Quantidade do fármaco na solução preparada", "number", "mg (U para vasopressina)", min=0.001,
              help="Ex.: 4 mg de noradrenalina diluída em 250 mL — informe aqui \"4\". Para vasopressina, informe em unidades (U)."),
        Field("volume_da_solucao", "Volume total da solução", "number", "mL", min=1,
              help="Ex.: os 250 mL de soro em que o fármaco foi diluído."),
    ],
    compute=_infusao_continua,
    interpret=_infusao_continua_txt,
    reference=(
        "Faixas de dose por fármaco, fonte a fonte: noradrenalina/adrenalina/vasopressina — "
        "Surviving Sepsis Campaign 2021 (Evans L et al. Crit Care Med. 2021;49(11):e1063-e1143) "
        "e Russell JA et al. N Engl J Med. 2008;358(9):877-887 (VASST); dobutamina/dopamina/"
        "milrinona/nitroglicerina/nitroprussiato — bula do fabricante e cartões de referência "
        "de UTI (LITFL Critical Care Compendium, Drugs.com Professional Monograph — fontes "
        "secundárias, não a bula/diretriz original, declarado aqui de propósito); propofol/"
        "fentanil — Drugs.com Professional Monograph e protocolo de sedação de UTI publicado "
        "(Rozendaal FW et al. Intensive Care Med. 2009;35(2):291-8, para a taxa inicial de fentanil)."
    ),
    kind="dose",
    limitations=[
        "As faixas são de uso HABITUAL, não limites farmacológicos absolutos — a calculadora "
        "avisa quando a dose sai da faixa, mas nunca bloqueia: a decisão clínica é do médico.",
        "Concentração da solução deve ser exatamente a que foi preparada — confira o rótulo "
        "da bomba antes de aceitar o resultado.",
        "Não substitui o protocolo institucional de diluição padrão do seu serviço, quando existir um.",
        "A faixa de fentanil e a de vasopressina vêm de fonte mais limitada que as demais — "
        "revisão adicional prevista nas próximas rodadas de conteúdo desta calculadora.",
    ],
)


# ------------------------------------------------------- heparina não fracionada
def _heparina_nf(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    bolus_ui = round(peso * 80)
    infusao_ui_h = round(peso * 18)
    return {"peso": peso, "bolus_ui": bolus_ui, "infusao_ui_h": infusao_ui_h}


def _heparina_nf_txt(r: dict) -> str:
    return (
        f"Bolus inicial: {r['bolus_ui']} UI IV. Infusão de manutenção inicial: "
        f"{r['infusao_ui_h']} UI/h. Colher TTPa em 6 horas e ajustar pelo nomograma do "
        "seu serviço, visando TTPa 1,5–2,3× o controle (faixa do nomograma original de "
        "Raschke) — os incrementos de ajuste por faixa de TTPa variam por protocolo "
        "institucional e não estão reproduzidos aqui por não terem sido confirmados contra "
        "a tabela original nesta rodada de revisão."
    )


_HEPARINA_NF = Calculator(
    slug="heparina-nao-fracionada-nomograma",
    name="Heparina não fracionada — dose inicial peso-ajustada",
    theme="Doses — Cardiologia Geral",
    purpose="Bolus e infusão inicial pelo nomograma clássico peso-ajustado.",
    fields=[Field("peso", "Peso do paciente", "number", "kg", min=1, max=300)],
    compute=_heparina_nf,
    interpret=_heparina_nf_txt,
    reference=(
        "Raschke RA et al. The weight-based heparin dosing nomogram compared with a "
        "standard care nomogram: a randomized controlled trial. Ann Intern Med. "
        "1993;119(9):874-881."
    ),
    kind="dose",
    limitations=[
        "Calcula só a dose INICIAL (bolus + infusão de partida) — o ajuste subsequente por "
        "faixa de TTPa segue o nomograma/protocolo do seu serviço, não reproduzido aqui.",
        "Em obesidade importante, o nomograma peso-ajustado pode superestimar a dose — "
        "muitos serviços usam peso ajustado ou tetos de bolus/infusão; confira o protocolo local.",
        "Não usar em suspeita de trombocitopenia induzida por heparina (HIT).",
    ],
)


# ---------------------------------------------------------------------- enoxaparina
def _enoxaparina(d: dict) -> dict:
    peso = float(d["peso"])
    indicacao = d["indicacao"]
    clcr_baixo = bool(d.get("clcr_menor_30"))
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")

    if indicacao == "tratamento_tev_sca":
        if clcr_baixo:
            dose_mg = round(peso * 1, 1)
            texto = f"{dose_mg} mg SC 1x/dia (ajuste renal, ClCr < 30 mL/min)."
        else:
            dose_mg = round(peso * 1, 1)
            texto = f"{dose_mg} mg SC a cada 12 horas."
    else:  # profilaxia
        dose_mg = 20 if clcr_baixo else 40
        texto = f"{dose_mg} mg SC 1x/dia" + (" (ajuste renal, ClCr < 30 mL/min)." if clcr_baixo else ".")

    return {"peso": peso, "indicacao": indicacao, "dose_mg": dose_mg, "texto": texto, "clcr_baixo": clcr_baixo}


def _enoxaparina_txt(r: dict) -> str:
    return r["texto"]


_ENOXAPARINA = Calculator(
    slug="enoxaparina-dose",
    name="Enoxaparina — dose terapêutica ou profilática",
    theme="Doses — Cardiologia Geral",
    purpose="Dose por peso e indicação, com ajuste para função renal reduzida.",
    fields=[
        Field("peso", "Peso do paciente", "number", "kg", min=1, max=300),
        Field("indicacao", "Indicação", "select", options=[
            {"value": "tratamento_tev_sca", "label": "Tratamento de TEV ou SCA (1 mg/kg 12/12h)"},
            {"value": "profilaxia", "label": "Profilaxia de TEV (dose fixa)"},
        ]),
        Field("clcr_menor_30", "ClCr < 30 mL/min", "boolean",
              help="Ajusta a dose para insuficiência renal grave."),
    ],
    compute=_enoxaparina,
    interpret=_enoxaparina_txt,
    reference=(
        "Bula profissional de enoxaparina sódica (ex.: Versa®, Eurofarma) e literatura de "
        "ajuste antitrombótico em insuficiência renal."
    ),
    kind="dose",
    limitations=[
        "Em ClCr 30–50 mL/min a bula não recomenda ajuste de dose por rotina, mas orienta "
        "vigilância clínica cuidadosa — não reproduzido no cálculo, aplicar critério clínico.",
        "Dose de SCA com fibrinolítico em IAMCSST tem componente de bolus IV inicial "
        "(30 mg em menores de 75 anos) não incluído neste cálculo — confira o protocolo "
        "específico de reperfusão.",
        "Não ajustado para obesidade extrema nem para gestação.",
    ],
)


# ----------------------------------------------------------------------- digoxina
def _digoxina(d: dict) -> dict:
    peso = float(d["peso"])
    clcr_reduzido = bool(d.get("clcr_reduzido"))
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    impregnacao_min = round(peso * 8, 2)
    impregnacao_max = round(peso * 12, 2)
    manutencao_min = round(peso * 3, 2)
    manutencao_max = round(peso * 5, 2)
    if clcr_reduzido:
        manutencao_min = round(manutencao_min * 0.5, 2)
        manutencao_max = round(manutencao_max * 0.5, 2)
    return {
        "peso": peso, "impregnacao_min_mcg": impregnacao_min, "impregnacao_max_mcg": impregnacao_max,
        "manutencao_min_mcg": manutencao_min, "manutencao_max_mcg": manutencao_max,
        "clcr_reduzido": clcr_reduzido,
    }


def _digoxina_txt(r: dict) -> str:
    ajuste = " (já reduzida pela metade por função renal diminuída — reavalie com nível sérico)" if r["clcr_reduzido"] else ""
    return (
        f"Dose de impregnação total: {r['impregnacao_min_mcg']}–{r['impregnacao_max_mcg']} mcg, "
        "fracionada (50% na primeira dose, 25% + 25% a cada 6–8 horas, com reavaliação clínica "
        f"entre as doses). Manutenção diária: {r['manutencao_min_mcg']}–{r['manutencao_max_mcg']} "
        f"mcg/dia{ajuste}. Monitorizar nível sérico e sinais de toxicidade — janela terapêutica estreita."
    )


_DIGOXINA = Calculator(
    slug="digoxina-dose",
    name="Digoxina — impregnação e manutenção",
    theme="Doses — Cardiologia Geral",
    purpose="Dose de ataque fracionada e manutenção diária por peso, com ajuste renal.",
    fields=[
        Field("peso", "Peso do paciente", "number", "kg", min=1, max=300),
        Field("clcr_reduzido", "Função renal reduzida (ClCr < 60 mL/min)", "boolean",
              help="A digoxina é eliminada predominantemente por via renal — reduz a manutenção pela metade como ponto de partida."),
    ],
    compute=_digoxina,
    interpret=_digoxina_txt,
    reference="Bula profissional de digoxina — esquema clássico de impregnação e manutenção por peso.",
    kind="dose",
    limitations=[
        "Janela terapêutica estreita — o cálculo é ponto de partida, não substitui nível sérico "
        "(alvo geralmente 0,5–0,9 ng/mL na insuficiência cardíaca) e avaliação clínica.",
        "Ajuste renal aqui é uma redução simplificada de 50%; a bula recomenda calcular por "
        "clearance de creatinina real — usar como estimativa inicial, não valor final.",
        "Interações relevantes (amiodarona, verapamil, claritromicina, entre outras) elevam o "
        "nível sérico e não estão incorporadas neste cálculo.",
    ],
)


# ------------------------------------------------- pediatria: adrenalina em PCR
def _adrenalina_pcr_pediatrica(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    dose_mg = round(peso * 0.01, 3)
    dose_mg = min(dose_mg, 1.0)  # dose máxima única 1 mg
    volume_ml_1_10000 = round(dose_mg * 10, 2)  # 1:10.000 = 0,1 mg/mL
    return {"peso": peso, "dose_mg": dose_mg, "volume_ml": volume_ml_1_10000}


def _adrenalina_pcr_pediatrica_txt(r: dict) -> str:
    return (
        f"{r['dose_mg']} mg IV/IO ({r['volume_ml']} mL da diluição 1:10.000, 0,1 mg/mL) — "
        "repetir a cada 3–5 minutos durante a reanimação. Dose máxima única: 1 mg. Via "
        "endotraqueal (só se IV/IO indisponíveis) usa dose 10× maior (0,1 mg/kg), diluição "
        "1:1.000 — não calculada aqui, confirme antes de usar essa via."
    )


_ADRENALINA_PCR_PED = Calculator(
    slug="adrenalina-pcr-pediatrica",
    name="Adrenalina — parada cardiorrespiratória pediátrica",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Dose IV/IO por peso na PCR pediátrica (PALS).",
    fields=[Field("peso", "Peso da criança", "number", "kg", min=1, max=100)],
    compute=_adrenalina_pcr_pediatrica,
    interpret=_adrenalina_pcr_pediatrica_txt,
    reference=(
        "Topjian AA et al. Part 4: Pediatric Basic and Advanced Life Support: 2020 American "
        "Heart Association Guidelines for CPR and ECC. Circulation. 2020;142(16_suppl_2):S469-S523."
    ),
    kind="dose",
    limitations=[
        "Dose alta de adrenalina (0,1 mg/kg IV/IO) NÃO deve ser usada em PCR pediátrica — "
        "estudos não mostraram benefício e sugerem pior desfecho neurológico.",
        "Não substitui o algoritmo completo de RCP pediátrica (compressões, via aérea, ritmo).",
    ],
)


# --------------------------------------------- pediatria: amiodarona em PCR
def _amiodarona_pcr_pediatrica(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    dose_mg = round(peso * 5, 1)
    dose_mg_maxima_dia = round(peso * 15, 1)
    return {"peso": peso, "dose_mg": dose_mg, "dose_mg_maxima_dia": dose_mg_maxima_dia}


def _amiodarona_pcr_pediatrica_txt(r: dict) -> str:
    return (
        f"{r['dose_mg']} mg IV/IO em bolus, para FV/TV sem pulso refratária ao choque — "
        f"pode repetir até 2 vezes (dose cumulativa máxima {r['dose_mg_maxima_dia']} mg/dia). "
        "Dose única máxima absoluta (mesmo em criança grande): 300 mg, equivalente à dose "
        "de adulto."
    )


_AMIODARONA_PCR_PED = Calculator(
    slug="amiodarona-pcr-pediatrica",
    name="Amiodarona — PCR pediátrica refratária (FV/TV sem pulso)",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Dose de bolus por peso na FV/TV sem pulso refratária ao choque.",
    fields=[Field("peso", "Peso da criança", "number", "kg", min=1, max=100)],
    compute=_amiodarona_pcr_pediatrica,
    interpret=_amiodarona_pcr_pediatrica_txt,
    reference=(
        "Topjian AA et al. Part 4: Pediatric Basic and Advanced Life Support: 2020 American "
        "Heart Association Guidelines for CPR and ECC. Circulation. 2020;142(16_suppl_2):S469-S523."
    ),
    kind="dose",
    limitations=["Só para FV/TV sem pulso refratária ao choque — não usar em outros ritmos de PCR."],
)


# ------------------------------------------ pediatria: cardioversão/desfibrilação
def _choque_pediatrico(d: dict) -> dict:
    peso = float(d["peso"])
    tipo = d["tipo"]
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    if tipo == "desfibrilacao":
        primeira = round(peso * 2, 1)
        subsequente = round(peso * 4, 1)
        teto = round(peso * 10, 1)
    else:  # cardioversao
        primeira = round(peso * 0.75, 1)  # ponto médio de 0,5-1 J/kg, exibido como faixa no texto
        subsequente = round(peso * 2, 1)
        teto = None
    return {"peso": peso, "tipo": tipo, "primeira": primeira, "subsequente": subsequente, "teto": teto}


def _choque_pediatrico_txt(r: dict) -> str:
    if r["tipo"] == "desfibrilacao":
        return (
            f"Desfibrilação (FV/TV sem pulso) — 1º choque: {round(r['peso']*2,1)} J (2 J/kg). "
            f"Choques seguintes: {r['subsequente']} J (4 J/kg), podendo escalar acima disso até "
            f"o teto de {r['teto']} J (10 J/kg) ou a dose de adulto, o que for menor."
        )
    return (
        f"Cardioversão sincronizada (taquiarritmia instável) — 1ª tentativa: "
        f"{round(r['peso']*0.5,1)}–{round(r['peso']*1,1)} J (0,5–1 J/kg). Se ineficaz, escalar "
        f"para {r['subsequente']} J (2 J/kg)."
    )


_CHOQUE_PED = Calculator(
    slug="choque-eletrico-pediatrico",
    name="Desfibrilação e cardioversão pediátrica — dose por peso",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Energia (J) por peso para desfibrilação (FV/TV sem pulso) ou cardioversão sincronizada.",
    fields=[
        Field("peso", "Peso da criança", "number", "kg", min=1, max=100),
        Field("tipo", "Situação", "select", options=[
            {"value": "desfibrilacao", "label": "Desfibrilação — FV/TV sem pulso"},
            {"value": "cardioversao", "label": "Cardioversão sincronizada — taquiarritmia instável com pulso"},
        ]),
    ],
    compute=_choque_pediatrico,
    interpret=_choque_pediatrico_txt,
    reference=(
        "Topjian AA et al. Part 4: Pediatric Basic and Advanced Life Support: 2020 American "
        "Heart Association Guidelines for CPR and ECC. Circulation. 2020;142(16_suppl_2):S469-S523."
    ),
    kind="dose",
    limitations=["Não substitui a indicação correta do ritmo — confirme o traçado antes do choque."],
)


# --------------------------------------------------- pediatria: adenosina (TSV)
def _adenosina_pediatrica(d: dict) -> dict:
    peso = float(d["peso"])
    numero_dose = int(d["numero_dose"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    if numero_dose == 1:
        dose_mg = min(round(peso * 0.1, 2), 6)
    else:
        dose_mg = min(round(peso * 0.2, 2), 12)
    return {"peso": peso, "numero_dose": numero_dose, "dose_mg": dose_mg}


def _adenosina_pediatrica_txt(r: dict) -> str:
    return (
        f"{'1ª' if r['numero_dose'] == 1 else '2ª'} dose: {r['dose_mg']} mg IV/IO em bolus "
        "RÁPIDO, seguido imediatamente de flush de soro fisiológico — a meia-vida é de "
        "segundos, e infusão lenta não funciona. "
        + ("Dose máxima desta etapa: 6 mg." if r["numero_dose"] == 1 else "Dose máxima desta etapa: 12 mg.")
    )


_ADENOSINA_PED = Calculator(
    slug="adenosina-tsv-pediatrica",
    name="Adenosina — taquicardia supraventricular pediátrica",
    theme="Doses — Cardiologia Pediátrica",
    purpose="1ª e 2ª dose por peso na TSV com pulso.",
    fields=[
        Field("peso", "Peso da criança", "number", "kg", min=1, max=100),
        Field("numero_dose", "Qual dose", "select", options=[
            {"value": 1, "label": "1ª dose (0,1 mg/kg)"},
            {"value": 2, "label": "2ª dose, se a 1ª não reverteu (0,2 mg/kg)"},
        ]),
    ],
    compute=_adenosina_pediatrica,
    interpret=_adenosina_pediatrica_txt,
    reference=(
        "Topjian AA et al. Part 4: Pediatric Basic and Advanced Life Support: 2020 American "
        "Heart Association Guidelines for CPR and ECC. Circulation. 2020;142(16_suppl_2):S469-S523."
    ),
    kind="dose",
    limitations=[
        "Só para TSV COM pulso — em TSV instável com deterioração hemodinâmica, cardioversão "
        "sincronizada é a conduta, não adenosina.",
        "Efeito muito breve (segundos) — precisa de bolus rápido e flush imediato, em acesso o "
        "mais próximo possível da circulação central quando disponível.",
    ],
)


# --------------------------------------------------------- pediatria: atropina
def _atropina_pediatrica(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    dose_mg = max(round(peso * 0.02, 3), 0.1)
    dose_mg = min(dose_mg, 0.5)
    return {"peso": peso, "dose_mg": dose_mg}


def _atropina_pediatrica_txt(r: dict) -> str:
    return (
        f"{r['dose_mg']} mg IV/IO, para bradicardia sintomática por tônus vagal aumentado ou "
        "bloqueio AV primário (não para bradicardia por hipóxia — aí a prioridade é "
        "oxigenação/ventilação, não atropina). Dose mínima 0,1 mg (dose menor pode causar "
        "bradicardia paradoxal); dose máxima única 0,5 mg. Pode repetir 1 vez."
    )


_ATROPINA_PED = Calculator(
    slug="atropina-bradicardia-pediatrica",
    name="Atropina — bradicardia sintomática pediátrica",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Dose IV/IO por peso, com piso e teto de segurança.",
    fields=[Field("peso", "Peso da criança", "number", "kg", min=1, max=100)],
    compute=_atropina_pediatrica,
    interpret=_atropina_pediatrica_txt,
    reference=(
        "Topjian AA et al. Part 4: Pediatric Basic and Advanced Life Support: 2020 American "
        "Heart Association Guidelines for CPR and ECC. Circulation. 2020;142(16_suppl_2):S469-S523."
    ),
    kind="dose",
    limitations=[
        "Bradicardia pediátrica é mais comumente por hipóxia do que por causa vagal/AV — "
        "corrigir via aérea e oxigenação é sempre a prioridade antes ou junto da atropina.",
    ],
)


DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [
        _INFUSAO_CONTINUA, _HEPARINA_NF, _ENOXAPARINA, _DIGOXINA,
        _ADRENALINA_PCR_PED, _AMIODARONA_PCR_PED, _CHOQUE_PED, _ADENOSINA_PED, _ATROPINA_PED,
    ]
}
