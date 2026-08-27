"""Calculadoras operacionais para Cardiologia Intensiva e Unidade Coronariana.

Os instrumentos deste módulo fazem conferências matemáticas rastreáveis. Eles
deliberadamente não prescrevem parâmetros, fármacos ou diluições institucionais:
essas decisões dependem da fisiologia, da formulação disponível e da avaliação
à beira leito.
"""

from __future__ import annotations

from .calculators import Calculator, Field
from .dose_calculators_choque_cardiogenico2025_chatgpt import AGENTES


FONTE_PRODUCAO = "chatgpt"

REFERENCIAS_VENTILACAO = (
    "ARDS Network. Ventilation with lower tidal volumes as compared with traditional tidal "
    "volumes for acute lung injury and ARDS. N Engl J Med. 2000;342:1301-1308. "
    "doi:10.1056/NEJM200005043421801; Fan E et al. ATS/ESICM/SCCM Clinical Practice "
    "Guideline: Mechanical Ventilation in Adult Patients with ARDS. Am J Respir Crit Care "
    "Med. 2017;195:1253-1263. PMID:28459336; Qadir N et al. An Update on Management of "
    "Adult Patients with ARDS: An Official ATS Clinical Practice Guideline. Am J Respir Crit "
    "Care Med. 2024;209:24-36. doi:10.1164/rccm.202311-2011ST; Goodfellow LT et al. "
    "AARC Clinical Practice Guideline: Patient-Ventilator Assessment. Respir Care. "
    "2024;69:1042-1054. PMID:39048148; Ferreira JC et al. Brazilian guidelines for "
    "mechanical ventilation 2024. Crit Care Sci. 2025;37:e20250242en. "
    "doi:10.62675/2965-2774.20250242-en."
)

REFERENCIAS_CONFERENCIA_INFUSAO = (
    "Institute for Safe Medication Practices (ISMP). Guidelines for Optimizing Safe "
    "Implementation and Use of Smart Infusion Pumps. 2020. "
    "https://www.ismp.org/system/files?file=resources%2F2020-10%2FISMP176C-"
    "Smart+Infusion+Pumps-100620.pdf; ISMP. List of High-Alert Medications in Acute Care "
    "Settings. 2024. https://www.ismp.org/Tools/institutionalhighAlert.asp; Sinha SS et al. "
    "2025 Concise Clinical "
    "Guidance: An ACC Expert Consensus Statement on the Evaluation and Management of "
    "Cardiogenic Shock. J Am Coll Cardiol. 2025;85:1618-1641. "
    "doi:10.1016/j.jacc.2025.02.018. https://www.jacc.org/doi/10.1016/j.jacc.2025.02.018; "
    "DailyMed. Norepinephrine Bitartrate in Sodium Chloride Injection, prescribing "
    "information, consulted 2026-08-27. https://dailymed.nlm.nih.gov/dailymed/"
    "drugInfo.cfm?setid=6363e9b4-29df-4553-904d-a563e5adda6e."
)


def _ventilacao_protetora(dados: dict) -> dict:
    sexo = dados["sexo_biologico"]
    altura_cm = float(dados["altura_cm"])
    volume_corrente_ml = float(dados["volume_corrente_ml"])
    pressao_plato = float(dados["pressao_plato_cmh2o"])
    peep_total = float(dados["peep_total_cmh2o"])

    if sexo not in {"masculino", "feminino"}:
        raise ValueError("Selecione o sexo biológico usado na equação de peso predito.")
    if not 120 <= altura_cm <= 220:
        raise ValueError("Informe altura entre 120 e 220 cm.")
    if volume_corrente_ml <= 0 or pressao_plato < 0 or peep_total < 0:
        raise ValueError("Volume corrente deve ser positivo; pressões não podem ser negativas.")
    if pressao_plato < peep_total:
        raise ValueError("Pressão de platô não pode ser menor que a PEEP total.")

    constante = 50.0 if sexo == "masculino" else 45.5
    peso_predito = constante + 0.91 * (altura_cm - 152.4)
    volume_por_kg = volume_corrente_ml / peso_predito
    pressao_distensao = pressao_plato - peep_total
    volume_abaixo = volume_por_kg < 4
    volume_acima = volume_por_kg > 8
    plato_elevada = pressao_plato >= 30

    if volume_abaixo:
        alerta_volume = "abaixo de 4 mL/kg de peso predito — revisar indicação e medidas"
    elif volume_acima:
        alerta_volume = "acima de 8 mL/kg de peso predito — revisar estratégia protetora"
    else:
        alerta_volume = "dentro da faixa protetora de referência de 4–8 mL/kg"

    alerta_plato = (
        "pressão de platô ≥30 cmH2O — reavaliar estratégia e qualidade da medida"
        if plato_elevada
        else "pressão de platô abaixo de 30 cmH2O"
    )

    return {
        "peso_predito_kg": round(peso_predito, 2),
        "vt_referencia_6_ml_kg": round(peso_predito * 6, 1),
        "faixa_vt_4_a_8_ml_kg": f"{peso_predito * 4:.1f}–{peso_predito * 8:.1f} mL",
        "vt_atual_ml_kg": round(volume_por_kg, 2),
        "pressao_distensao_cmh2o": round(pressao_distensao, 1),
        "alerta_volume": alerta_volume,
        "alerta_plato": alerta_plato,
        "fora_da_faixa": volume_abaixo or volume_acima or plato_elevada,
    }


def _interpretar_ventilacao(resultado: dict) -> str:
    return (
        f"Peso corporal predito {resultado['peso_predito_kg']} kg; volume de referência a "
        f"6 mL/kg = {resultado['vt_referencia_6_ml_kg']} mL e faixa 4–8 mL/kg = "
        f"{resultado['faixa_vt_4_a_8_ml_kg']}. O volume informado corresponde a "
        f"{resultado['vt_atual_ml_kg']} mL/kg. Pressão de distensão calculada = "
        f"{resultado['pressao_distensao_cmh2o']} cmH2O. {resultado['alerta_volume']}; "
        f"{resultado['alerta_plato']}."
    )


_VENTILACAO_PROTETORA = Calculator(
    slug="ventilacao-protetora-uco",
    name="Ventilação protetora — peso predito, volume corrente e pressões",
    theme="Terapia intensiva",
    purpose=(
        "Calcula peso corporal predito, faixa de volume corrente protetor, volume entregue "
        "por kg e pressão de distensão para apoiar a reavaliação ventilatória do adulto."
    ),
    fields=[
        Field(
            "sexo_biologico",
            "Sexo biológico usado na equação",
            "select",
            options=[
                {"value": "masculino", "label": "Masculino"},
                {"value": "feminino", "label": "Feminino"},
            ],
            help="A equação histórica de peso corporal predito usa constantes distintas por sexo biológico.",
        ),
        Field("altura_cm", "Altura", "number", "cm", min=120, max=220),
        Field(
            "volume_corrente_ml",
            "Volume corrente entregue",
            "number",
            "mL",
            min=50,
            max=2000,
            help="Use o volume efetivamente entregue e reavalie após mudanças de modo ou mecânica.",
        ),
        Field(
            "pressao_plato_cmh2o",
            "Pressão de platô",
            "number",
            "cmH₂O",
            min=0,
            max=80,
            help="Medir com pausa inspiratória e sem esforço respiratório que invalide a medida.",
        ),
        Field(
            "peep_total_cmh2o",
            "PEEP total",
            "number",
            "cmH₂O",
            min=0,
            max=50,
            help="Inclua PEEP intrínseca quando presente; a diferença para o platô estima pressão de distensão.",
        ),
    ],
    compute=_ventilacao_protetora,
    interpret=_interpretar_ventilacao,
    reference=REFERENCIAS_VENTILACAO,
    kind="dose",
    limitations=[
        "Ferramenta educacional e de conferência; não seleciona modo ventilatório, frequência, FiO₂ ou PEEP e não substitui avaliação à beira leito.",
        "A recomendação forte de 4–8 mL/kg de peso predito e platô <30 cmH₂O provém de pacientes com SDRA; em outros fenótipos, individualizar sem abandonar a prevenção de lesão pulmonar.",
        "Pressão de distensão é exibida para avaliação. A diretriz AARC 2024 recomenda sua aferição apenas condicionalmente, com baixa certeza; por isso a calculadora não impõe um limiar terapêutico.",
        "Pressão de platô exige pausa inspiratória adequada e ausência de esforço; assincronia, vazamento e medida inadequada podem invalidar o resultado.",
        "PEEP deve ser individualizada em instabilidade hemodinâmica, disfunção de ventrículo direito e fisiologia obstrutiva.",
    ],
)


def _conferencia_bomba(dados: dict) -> dict:
    chave = dados["agente"]
    if chave not in AGENTES:
        raise ValueError("Selecione um agente disponível para conferência.")

    agente = AGENTES[chave]
    peso = float(dados["peso_kg"])
    dose_pretendida = float(dados["dose_pretendida"])
    quantidade = float(dados["quantidade_soluto"])
    volume = float(dados["volume_total_ml"])
    velocidade = float(dados["velocidade_bomba_ml_h"])
    tolerancia = float(dados["tolerancia_percentual"])
    contexto_acc = bool(dados.get("contexto_choque_cardiogenico"))

    if dose_pretendida <= 0 or quantidade <= 0 or volume <= 0 or velocidade < 0:
        raise ValueError(
            "Dose pretendida, quantidade e volume devem ser positivos; a velocidade não pode ser negativa."
        )
    if tolerancia not in {2.0, 5.0, 10.0}:
        raise ValueError("Selecione tolerância operacional de 2%, 5% ou 10%.")
    if agente["unidade"] == "mcg/kg/min" and not 1 <= peso <= 400:
        raise ValueError("Informe peso entre 1 e 400 kg para doses ponderais.")

    if agente["unidade"] == "U/min":
        concentracao_numerica = quantidade / volume
        dose_entregue = concentracao_numerica * velocidade / 60
        velocidade_esperada = dose_pretendida * 60 / concentracao_numerica
        concentracao = f"{concentracao_numerica:.4f} U/mL"
    else:
        concentracao_numerica = quantidade * 1000 / volume
        if agente["unidade"] == "mcg/kg/min":
            dose_entregue = concentracao_numerica * velocidade / 60 / peso
            velocidade_esperada = dose_pretendida * peso * 60 / concentracao_numerica
        else:
            dose_entregue = concentracao_numerica * velocidade / 60
            velocidade_esperada = dose_pretendida * 60 / concentracao_numerica
        concentracao = f"{concentracao_numerica:.2f} mcg/mL"

    desvio = abs(dose_entregue - dose_pretendida) / dose_pretendida * 100
    conferencia_ok = desvio <= tolerancia
    fora_acc = contexto_acc and not agente["min"] <= dose_entregue <= agente["max"]

    status = (
        "CONFERÊNCIA MATEMÁTICA DENTRO DA TOLERÂNCIA"
        if conferencia_ok
        else "DIVERGÊNCIA — PAUSAR E RECONFERIR PRESCRIÇÃO, SOLUÇÃO E BOMBA"
    )
    faixa_acc = (
        f"{agente['min']}–{agente['max']} {agente['unidade']}"
        if contexto_acc
        else "não aplicada — contexto de choque cardiogênico não selecionado"
    )
    alerta_acc = (
        "Dose calculada fora da faixa contextual da Tabela 2 do ACC 2025."
        if fora_acc
        else (
            "Dose calculada dentro da faixa contextual da Tabela 2 do ACC 2025."
            if contexto_acc
            else "Faixa terapêutica não avaliada; a tolerância escolhida compara apenas números."
        )
    )

    return {
        "status_conferencia": status,
        "agente": agente["nome"],
        "concentracao_calculada": concentracao,
        "dose_pretendida": round(dose_pretendida, 6),
        "dose_entregue_calculada": round(dose_entregue, 6),
        "unidade_dose": agente["unidade"],
        "velocidade_programada_ml_h": round(velocidade, 3),
        "velocidade_esperada_ml_h": round(velocidade_esperada, 3),
        "desvio_percentual_absoluto": round(desvio, 2),
        "tolerancia_operacional_percentual": tolerancia,
        "faixa_acc_2025": faixa_acc,
        "alerta_contextual": alerta_acc,
        "fora_da_faixa": (not conferencia_ok) or fora_acc,
    }


def _interpretar_conferencia_bomba(resultado: dict) -> str:
    return (
        f"{resultado['status_conferencia']}. {resultado['agente']}: a bomba a "
        f"{resultado['velocidade_programada_ml_h']} mL/h, na concentração calculada de "
        f"{resultado['concentracao_calculada']}, entrega "
        f"{resultado['dose_entregue_calculada']} {resultado['unidade_dose']}; a dose "
        f"pretendida é {resultado['dose_pretendida']} {resultado['unidade_dose']}. "
        f"Desvio absoluto {resultado['desvio_percentual_absoluto']}% (tolerância operacional "
        f"selecionada {resultado['tolerancia_operacional_percentual']}%). Velocidade "
        f"matematicamente esperada: {resultado['velocidade_esperada_ml_h']} mL/h. "
        f"{resultado['alerta_contextual']}"
    )


_CONFERENCIA_BOMBA = Calculator(
    slug="conferencia-bomba-infusao-uco",
    name="Dupla conferência da bomba — dose entregue versus prescrita",
    theme="Terapia intensiva",
    purpose=(
        "Recalcula a dose efetivamente entregue a partir da quantidade preparada, volume e "
        "velocidade da bomba, comparando-a com a dose pretendida em uma etapa independente."
    ),
    fields=[
        Field(
            "agente",
            "Agente",
            "select",
            options=[
                {"value": chave, "label": f"{item['nome']} — {item['unidade']}"}
                for chave, item in AGENTES.items()
            ],
            help="Confirme o agente no rótulo da solução, na prescrição e no canal da bomba.",
        ),
        Field(
            "peso_kg",
            "Peso documentado",
            "number",
            "kg",
            min=1,
            max=400,
            help="Usado somente quando a unidade do agente é mcg/kg/min.",
        ),
        Field(
            "dose_pretendida",
            "Dose pretendida/prescrita",
            "number",
            help="Use a unidade exibida junto ao agente; não transcreva a velocidade em mL/h.",
        ),
        Field(
            "quantidade_soluto",
            "Quantidade total do fármaco na solução",
            "number",
            "mg ou U",
            help="Informe mg para agentes em mcg; somente para vasopressina informe unidades (U).",
        ),
        Field("volume_total_ml", "Volume total da solução", "number", "mL", min=0.1),
        Field(
            "velocidade_bomba_ml_h",
            "Velocidade programada na bomba",
            "number",
            "mL/h",
            min=0,
        ),
        Field(
            "tolerancia_percentual",
            "Tolerância operacional para a comparação",
            "select",
            options=[
                {"value": "5", "label": "5% — conferência padrão"},
                {"value": "2", "label": "2% — conferência estrita"},
                {"value": "10", "label": "10% — somente se protocolo local permitir"},
            ],
            help="Não é margem terapêutica: define apenas quando a ferramenta sinaliza divergência matemática.",
        ),
        Field(
            "contexto_choque_cardiogenico",
            "Aplicar também faixa contextual do ACC 2025 para choque cardiogênico",
            "boolean",
            help="Não marque para outros fenótipos; as faixas do consenso não são universais.",
        ),
    ],
    compute=_conferencia_bomba,
    interpret=_interpretar_conferencia_bomba,
    reference=REFERENCIAS_CONFERENCIA_INFUSAO,
    kind="dose",
    limitations=[
        "A conferência só é independente se os dados forem obtidos novamente da prescrição, do rótulo da solução e da bomba, sem copiar o resultado de outro cálculo.",
        "Tolerância operacional não é margem terapêutica. Mesmo dentro da tolerância, confirme paciente, fármaco, concentração, dose, canal, linha e resposta clínica.",
        "Não verifica identidade, diluente, compatibilidade, estabilidade, validade, via/acesso, volume residual, peso desatualizado ou biblioteca de limites da bomba inteligente.",
        "Não fornece diluição padrão: apresentações prontas e concentrações variam por produto e instituição; valide bula, farmácia e protocolo local.",
        "As faixas de dose do ACC 2025 são exibidas somente quando o usuário declara contexto de choque cardiogênico; não são limites universais nem substituem titulação hemodinâmica.",
        "Dupla conferência manual seletiva não substitui código de barras, biblioteca de redução de erros de dose, integração bomba-prontuário e outras barreiras sistêmicas.",
    ],
)


INTENSIVE_CARE_CALCULATOR_REGISTRY: dict[str, Calculator] = {
    _VENTILACAO_PROTETORA.slug: _VENTILACAO_PROTETORA,
    _CONFERENCIA_BOMBA.slug: _CONFERENCIA_BOMBA,
}
