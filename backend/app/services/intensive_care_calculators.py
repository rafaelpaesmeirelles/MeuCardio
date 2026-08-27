"""Calculadoras operacionais para Cardiologia Intensiva e Unidade Coronariana.

Os instrumentos deste módulo fazem conferências matemáticas rastreáveis. Eles
deliberadamente não prescrevem parâmetros, fármacos ou diluições institucionais:
essas decisões dependem da fisiologia, da formulação disponível e da avaliação
à beira leito.
"""

from __future__ import annotations

import math

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

REFERENCIAS_SCAI = (
    "Naidu SS et al. SCAI SHOCK Stage Classification Expert Consensus Update: A Review "
    "and Incorporation of Validation Studies. J Soc Cardiovasc Angiogr Interv. "
    "2022;1(1):100008. doi:10.1016/j.jscai.2021.100008. "
    "https://www.scai.org/publications/clinical-documents/scai-shock-stages-"
    "classification-expert-consensus-update-review-and; Kapur NK et al. Criteria for "
    "Defining Stages of Cardiogenic Shock Severity. J Am Coll Cardiol. 2022;80:185-198. "
    "doi:10.1016/j.jacc.2022.04.049. https://pubmed.ncbi.nlm.nih.gov/35835491/; "
    "Sinha SS et al. 2025 Concise Clinical Guidance: An ACC Expert Consensus Statement on "
    "the Evaluation and Management of Cardiogenic Shock. J Am Coll Cardiol. "
    "2025;85:1618-1641. doi:10.1016/j.jacc.2025.02.018; Ton VK et al. Serial Shock "
    "Severity Assessment Within 72 Hours After Admission Predicts Hospital Mortality in "
    "Cardiogenic Shock. J Am Coll Cardiol. 2024;84:123-136. "
    "doi:10.1016/j.jacc.2024.04.069."
)

REFERENCIAS_ACIDOSE_METABOLICA = (
    "Albert MS, Dell RB, Winters RW. Quantitative displacement of acid-base equilibrium "
    "in metabolic acidosis. Ann Intern Med. 1967;66:312-322. "
    "doi:10.7326/0003-4819-66-2-312. PMID:6016545; Figge J, Jabor A, Kazda A, "
    "Fencl V. Anion gap and hypoalbuminemia. Crit Care Med. 1998;26:1807-1810. "
    "doi:10.1097/00003246-199811000-00019. PMID:9824071; American Thoracic Society. "
    "Interpretation of Arterial Blood Gases (ABGs), clinical education resource, "
    "consulted 2026-08-27. https://www.thoracic.org/professionals/clinical-resources/"
    "critical-care/clinical-education/abgs.php."
)

REFERENCIAS_OXIGENACAO_SDRA = (
    "Matthay MA et al. A New Global Definition of Acute Respiratory Distress "
    "Syndrome. Am J Respir Crit Care Med. 2024;209:37-47. "
    "doi:10.1164/rccm.202303-0558WS. PMID:37487152; ARDS Definition Task Force. "
    "Acute respiratory distress syndrome: the Berlin Definition. JAMA. "
    "2012;307:2526-2533. doi:10.1001/jama.2012.5669. PMID:22797452; Qadir N "
    "et al. An Update on Management of Adult Patients with ARDS: An Official ATS "
    "Clinical Practice Guideline. Am J Respir Crit Care Med. 2024;209:24-36. "
    "doi:10.1164/rccm.202311-2011ST. PMID:38032683."
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
    dose_pretendida = float(dados["dose_pretendida"])
    quantidade = float(dados["quantidade_soluto"])
    volume = float(dados["volume_total_ml"])
    velocidade = float(dados["velocidade_bomba_ml_h"])
    tolerancia = float(dados["tolerancia_percentual"])
    contexto_acc = bool(dados.get("contexto_choque_cardiogenico"))

    entradas_numericas = [dose_pretendida, quantidade, volume, velocidade, tolerancia]
    if not all(math.isfinite(valor) for valor in entradas_numericas):
        raise ValueError("Informe somente valores numéricos finitos.")
    if dose_pretendida <= 0 or quantidade <= 0 or volume <= 0 or velocidade < 0:
        raise ValueError(
            "Dose pretendida, quantidade e volume devem ser positivos; a velocidade não pode ser negativa."
        )
    if tolerancia not in {2.0, 5.0, 10.0}:
        raise ValueError("Selecione tolerância operacional de 2%, 5% ou 10%.")
    peso: float | None = None
    if agente["unidade"] == "mcg/kg/min":
        try:
            peso = float(dados["peso_kg"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Informe peso entre 1 e 400 kg para doses ponderais.") from None
        if not math.isfinite(peso) or not 1 <= peso <= 400:
            raise ValueError("Informe peso entre 1 e 400 kg para doses ponderais.")

    if agente["unidade"] == "U/min":
        concentracao_numerica = quantidade / volume
        dose_entregue = concentracao_numerica * velocidade / 60
        velocidade_esperada = dose_pretendida * 60 / concentracao_numerica
        concentracao = f"{concentracao_numerica:.4f} U/mL"
    else:
        concentracao_numerica = quantidade * 1000 / volume
        if agente["unidade"] == "mcg/kg/min":
            assert peso is not None
            dose_entregue = concentracao_numerica * velocidade / 60 / peso
            velocidade_esperada = dose_pretendida * peso * 60 / concentracao_numerica
        else:
            dose_entregue = concentracao_numerica * velocidade / 60
            velocidade_esperada = dose_pretendida * 60 / concentracao_numerica
        concentracao = f"{concentracao_numerica:.2f} mcg/mL"

    desvio = abs(dose_entregue - dose_pretendida) / dose_pretendida * 100
    conferencia_ok = desvio <= tolerancia or math.isclose(
        desvio, tolerancia, rel_tol=1e-12, abs_tol=1e-12
    )
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
            required=False,
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


def _numero_opcional(dados: dict, nome: str) -> float | None:
    bruto = dados.get(nome)
    if bruto in (None, ""):
        return None
    valor = float(bruto)
    if not math.isfinite(valor):
        raise ValueError("Informe somente valores numéricos finitos.")
    return valor


def _estadiamento_scai(dados: dict) -> dict:
    em_risco = bool(dados.get("em_risco_sem_instabilidade"))
    instabilidade = bool(dados.get("instabilidade_sem_hipoperfusao"))
    hipoperfusao = bool(dados.get("hipoperfusao_requer_intervencao"))
    deterioracao = bool(dados.get("deterioracao_apos_intervencao"))
    extremis = bool(dados.get("colapso_extremis"))
    modificador_a = bool(dados.get("parada_com_risco_anoxico"))

    if not any((em_risco, instabilidade, hipoperfusao, deterioracao, extremis)):
        raise ValueError(
            "Selecione ao menos um padrão clínico; o estágio não pode ser inferido apenas por números."
        )

    lactato = _numero_opcional(dados, "lactato_mmol_l")
    ph = _numero_opcional(dados, "ph_arterial")
    pas = _numero_opcional(dados, "pas_mmhg")
    pam = _numero_opcional(dados, "pam_mmhg")
    frequencia = _numero_opcional(dados, "frequencia_cardiaca_bpm")

    if lactato is not None and not 0 <= lactato <= 30:
        raise ValueError("Informe lactato entre 0 e 30 mmol/L.")
    if ph is not None and not 6.5 <= ph <= 7.8:
        raise ValueError("Informe pH arterial entre 6,50 e 7,80.")
    for valor, nome, limite in (
        (pas, "PAS", 400),
        (pam, "PAM", 300),
        (frequencia, "frequência cardíaca", 350),
    ):
        if valor is not None and not 0 <= valor <= limite:
            raise ValueError(f"{nome} deve estar entre 0 e {limite}.")

    if extremis:
        estagio, nome_estagio = "E", "extremis"
        criterio = "colapso circulatório refratário, pulso quase ausente ou RCP em curso"
    elif deterioracao:
        estagio, nome_estagio = "D", "deteriorando"
        criterio = "hipoperfusão/instabilidade persistente após a intervenção inicial ou escalada de suporte"
    elif hipoperfusao:
        estagio, nome_estagio = "C", "choque clássico"
        criterio = (
            "hipoperfusão que requer intervenção farmacológica ou mecânica para restaurar "
            "perfusão, além de reposição volêmica isolada"
        )
    elif instabilidade:
        estagio, nome_estagio = "B", "choque iniciando"
        criterio = "hipotensão relativa ou taquicardia sem hipoperfusão"
    else:
        estagio, nome_estagio = "A", "em risco"
        criterio = "risco de choque sem instabilidade ou hipoperfusão atuais"

    inconsistencias: list[str] = []
    if estagio in {"A", "B"} and lactato is not None and lactato > 2:
        inconsistencias.append(
            "lactato >2 mmol/L pode indicar hipoperfusão ou outra causa; reavaliar antes de manter A/B"
        )
    if estagio == "A" and (
        (pas is not None and pas < 90)
        or (pam is not None and pam < 60)
        or (frequencia is not None and frequencia > 100)
    ):
        inconsistencias.append(
            "sinais vitais informados sustentam instabilidade; revisar se o padrão B está presente"
        )
    if estagio != "E" and (
        (lactato is not None and lactato > 8) or (ph is not None and ph < 7.2)
    ):
        inconsistencias.append(
            "lactato >8 mmol/L ou pH <7,20 é marcador de gravidade extrema; avaliar o conjunto clínico para estágio E"
        )
    medidas = []
    if pas is not None:
        medidas.append(f"PAS {pas:g} mmHg")
    if pam is not None:
        medidas.append(f"PAM {pam:g} mmHg")
    if frequencia is not None:
        medidas.append(f"FC {frequencia:g} bpm")
    if lactato is not None:
        medidas.append(f"lactato {lactato:g} mmol/L")
    if ph is not None:
        medidas.append(f"pH {ph:g}")

    rotulo = f"SCAI {estagio}{'+A' if modificador_a else ''}"
    alerta = (
        " | ".join(inconsistencias)
        if inconsistencias
        else "sem conflito explícito entre o padrão clínico selecionado e as medidas informadas"
    )
    return {
        "estagio_sugerido": f"{estagio} — {nome_estagio}",
        "rotulo_para_documentacao": rotulo,
        "criterio_determinante": criterio,
        "modificador_a": (
            "aplicado — parada com potencial lesão cerebral anóxica"
            if modificador_a
            else "não aplicado"
        ),
        "medidas_de_apoio": ", ".join(medidas) if medidas else "não informadas",
        "alerta_de_consistencia": alerta,
        "reavaliacao": (
            "Registrar horário e repetir o estágio após intervenção, mudança de suporte ou deterioração; "
            "documentar estágio inicial e máximo."
        ),
        "fora_da_faixa": bool(inconsistencias),
    }


def _interpretar_scai(resultado: dict) -> str:
    return (
        f"{resultado['rotulo_para_documentacao']} — {resultado['estagio_sugerido']}. "
        f"Critério determinante: {resultado['criterio_determinante']}. Modificador de parada: "
        f"{resultado['modificador_a']}. Medidas de apoio: {resultado['medidas_de_apoio']}. "
        f"Consistência: {resultado['alerta_de_consistencia']}. {resultado['reavaliacao']}"
    )


_ESTADIAMENTO_SCAI = Calculator(
    slug="estadiamento-scai-choque-cardiogenico",
    name="Choque cardiogênico — estadiamento SCAI e reavaliação seriada",
    theme="Terapia intensiva",
    purpose=(
        "Organiza o padrão clínico em SCAI A–E, verifica coerência com medidas objetivas "
        "opcionais e documenta o modificador de parada com risco anóxico."
    ),
    fields=[
        Field(
            "em_risco_sem_instabilidade",
            "A — paciente em risco, sem instabilidade ou hipoperfusão atuais",
            "boolean",
        ),
        Field(
            "instabilidade_sem_hipoperfusao",
            "B — hipotensão relativa ou taquicardia, ainda sem hipoperfusão",
            "boolean",
            help="A diferença decisiva entre B e C é a presença de hipoperfusão.",
        ),
        Field(
            "hipoperfusao_requer_intervencao",
            "C — hipoperfusão requer intervenção farmacológica ou mecânica além de volume isolado",
            "boolean",
            help="Hipoperfusão que resolve apenas com reposição volêmica não preenche este critério de estágio C.",
        ),
        Field(
            "deterioracao_apos_intervencao",
            "D — instabilidade/hipoperfusão persiste após intervenção inicial ou exige escalada",
            "boolean",
            help="O consenso original usa ausência de resposta após pelo menos 30 minutos de observação.",
        ),
        Field(
            "colapso_extremis",
            "E — colapso refratário, pulso quase ausente ou RCP em curso",
            "boolean",
        ),
        Field(
            "parada_com_risco_anoxico",
            "Modificador +A — parada com potencial lesão cerebral anóxica",
            "boolean",
            help="Marcar quando não segue comandos ou há coma/GCS <9 após RCE; parada breve com recuperação neurológica não basta.",
        ),
        Field("pas_mmhg", "Pressão arterial sistólica", "number", "mmHg", min=0, max=400, required=False),
        Field("pam_mmhg", "Pressão arterial média", "number", "mmHg", min=0, max=300, required=False),
        Field(
            "frequencia_cardiaca_bpm",
            "Frequência cardíaca",
            "number",
            "bpm",
            min=0,
            max=350,
            required=False,
        ),
        Field("lactato_mmol_l", "Lactato", "number", "mmol/L", min=0, max=30, required=False),
        Field("ph_arterial", "pH arterial", "number", min=6.5, max=7.8, required=False),
    ],
    compute=_estadiamento_scai,
    interpret=_interpretar_scai,
    reference=REFERENCIAS_SCAI,
    kind="assessment",
    limitations=[
        "Assistente de documentação, não escore prognóstico nem indicação automática de vasoativo, revascularização ou suporte circulatório mecânico.",
        "O SCAI 2022 é consenso multissocietário; seus critérios foram validados sobretudo em coortes observacionais, não em ensaio randomizado de estratégia terapêutica.",
        "O padrão clínico predominante determina o estágio; lactato, pH e pressão isolados apenas apoiam ou sinalizam discordância e podem refletir outras causas.",
        "O estágio é dinâmico. Registrar momento inicial, reavaliar após intervenções e mudanças clínicas e documentar o estágio máximo alcançado.",
        "O modificador +A não significa qualquer parada: aplica-se quando há potencial lesão cerebral anóxica, como coma ou ausência de resposta a comandos após RCE.",
        "Etiologia, fenótipo hemodinâmico, idade, fragilidade e falência não cardíaca modificam risco fora do eixo A–E e exigem avaliação separada.",
        "A proposta SCAI 2026 em consulta pública não foi usada como padrão final; a ferramenta segue o consenso publicado e endossado de 2022, validado em 27/08/2026.",
    ],
)


def _acidose_metabolica(dados: dict) -> dict:
    nomes = ("ph", "paco2_mmhg", "bicarbonato_meq_l", "sodio_meq_l", "cloro_meq_l")
    try:
        ph, paco2, bicarbonato, sodio, cloro = (float(dados[nome]) for nome in nomes)
    except (KeyError, TypeError, ValueError):
        raise ValueError("Informe pH, PaCO₂, bicarbonato, sódio e cloro.") from None

    if not all(math.isfinite(valor) for valor in (ph, paco2, bicarbonato, sodio, cloro)):
        raise ValueError("Informe somente valores numéricos finitos.")
    if not 6.5 <= ph <= 7.8:
        raise ValueError("Informe pH entre 6,50 e 7,80.")
    if not 5 <= paco2 <= 150:
        raise ValueError("Informe PaCO₂ entre 5 e 150 mmHg.")
    if not 1 <= bicarbonato <= 24:
        raise ValueError(
            "Esta ferramenta aplica Winter somente à acidose metabólica: informe bicarbonato entre 1 e 24 mEq/L."
        )
    if not 80 <= sodio <= 200:
        raise ValueError("Informe sódio entre 80 e 200 mEq/L.")
    if not 40 <= cloro <= 180:
        raise ValueError("Informe cloro entre 40 e 180 mEq/L.")

    albumina = _numero_opcional(dados, "albumina_g_dl")
    limite_ag = _numero_opcional(dados, "limite_superior_ag_meq_l")
    referencia_ag_sem_potassio = bool(dados.get("referencia_ag_sem_potassio_confirmada"))
    try:
        albumina_referencia = float(dados.get("albumina_referencia_g_dl", 4.0))
    except (TypeError, ValueError):
        raise ValueError("Selecione albumina de referência de 4,0 ou 4,4 g/dL.") from None
    if albumina is not None and not 0.5 <= albumina <= 6:
        raise ValueError("Informe albumina entre 0,5 e 6,0 g/dL.")
    if albumina_referencia not in {4.0, 4.4}:
        raise ValueError("Selecione albumina de referência de 4,0 ou 4,4 g/dL.")
    if limite_ag is not None and not 0 <= limite_ag <= 40:
        raise ValueError("Informe limite superior do ânion gap entre 0 e 40 mEq/L.")
    if limite_ag is not None and not referencia_ag_sem_potassio:
        raise ValueError(
            "Confirme que o limite laboratorial informado corresponde ao ânion gap sem potássio."
        )

    winter_central = 1.5 * bicarbonato + 8
    winter_inferior = winter_central - 2
    winter_superior = winter_central + 2
    if paco2 < winter_inferior:
        compensacao = (
            "PaCO₂ abaixo da faixa esperada: considerar alcalose respiratória associada, "
            "após confirmar amostra, tempo e contexto clínico"
        )
        discordante = True
    elif paco2 > winter_superior:
        compensacao = (
            "PaCO₂ acima da faixa esperada: considerar acidose respiratória associada, "
            "após confirmar amostra, tempo e contexto clínico"
        )
        discordante = True
    else:
        compensacao = (
            "PaCO₂ compatível com a compensação esperada pela fórmula de Winter; "
            "isso não exclui outro distúrbio misto"
        )
        discordante = False

    if ph < 7.35:
        estado_ph = "acidemia (pH <7,35)"
    elif ph > 7.45:
        estado_ph = "alcalemia (pH >7,45); revisar distúrbio misto antes de interpretar"
    else:
        estado_ph = "pH entre 7,35 e 7,45; faixa normal não exclui distúrbio misto"

    anion_gap = sodio - (cloro + bicarbonato)
    anion_gap_corrigido: float | str
    if albumina is None:
        anion_gap_corrigido = "não calculado — albumina não informada"
        ag_para_comparar = anion_gap
        rotulo_ag = "ânion gap observado"
    else:
        anion_gap_corrigido = round(
            anion_gap + 2.5 * (albumina_referencia - albumina), 1
        )
        ag_para_comparar = float(anion_gap_corrigido)
        rotulo_ag = "ânion gap corrigido por albumina"

    if limite_ag is None:
        comparacao_ag = (
            f"{rotulo_ag} sem classificação automática — compare com o intervalo do laboratório "
            "e confirme se o método inclui potássio"
        )
        ag_elevado = False
    elif ag_para_comparar > limite_ag:
        comparacao_ag = (
            f"{rotulo_ag} acima do limite informado ({limite_ag:g} mEq/L); investigar ânions "
            "não medidos no contexto clínico"
        )
        ag_elevado = True
    else:
        comparacao_ag = (
            f"{rotulo_ag} não excede o limite informado ({limite_ag:g} mEq/L); isso não exclui "
            "acidose nem causa mista"
        )
        ag_elevado = False

    return {
        "estado_do_ph": estado_ph,
        "paco2_esperada_winter_mmhg": f"{winter_inferior:.1f}–{winter_superior:.1f}",
        "paco2_observada_mmhg": round(paco2, 1),
        "avaliacao_da_compensacao": compensacao,
        "anion_gap_sem_potassio_meq_l": round(anion_gap, 1),
        "anion_gap_corrigido_albumina_meq_l": anion_gap_corrigido,
        "comparacao_com_referencia_do_laboratorio": comparacao_ag,
        "fora_da_faixa": discordante or ag_elevado,
    }


def _interpretar_acidose_metabolica(resultado: dict) -> str:
    return (
        f"{resultado['estado_do_ph']}. PaCO₂ esperada por Winter: "
        f"{resultado['paco2_esperada_winter_mmhg']} mmHg; observada: "
        f"{resultado['paco2_observada_mmhg']} mmHg. "
        f"{resultado['avaliacao_da_compensacao']}. Ânion gap sem K: "
        f"{resultado['anion_gap_sem_potassio_meq_l']} mEq/L; corrigido por albumina: "
        f"{resultado['anion_gap_corrigido_albumina_meq_l']}. "
        f"{resultado['comparacao_com_referencia_do_laboratorio']}."
    )


_ACIDOSE_METABOLICA = Calculator(
    slug="acidose-metabolica-winter-anion-gap-uco",
    name="Acidose metabólica — Winter e ânion gap corrigido",
    theme="Terapia intensiva",
    purpose=(
        "Em acidose metabólica clinicamente estabelecida, calcula a faixa esperada de PaCO₂ "
        "pela fórmula de Winter e o ânion gap sem potássio, com correção opcional por albumina."
    ),
    fields=[
        Field("ph", "pH da gasometria", "number", min=6.5, max=7.8),
        Field("paco2_mmhg", "PaCO₂ observada", "number", "mmHg", min=5, max=150),
        Field("bicarbonato_meq_l", "Bicarbonato", "number", "mEq/L", min=1, max=24),
        Field("sodio_meq_l", "Sódio", "number", "mEq/L", min=80, max=200),
        Field("cloro_meq_l", "Cloro", "number", "mEq/L", min=40, max=180),
        Field(
            "albumina_g_dl",
            "Albumina sérica",
            "number",
            "g/dL",
            min=0.5,
            max=6,
            required=False,
            help="Opcional; quando informada, corrige o ânion gap pelo fator de Figge (2,5 mEq/L por 1 g/dL).",
        ),
        Field(
            "albumina_referencia_g_dl",
            "Albumina de referência usada pelo serviço",
            "select",
            "g/dL",
            options=[
                {"value": 4.0, "label": "4,0 g/dL"},
                {"value": 4.4, "label": "4,4 g/dL"},
            ],
            help="A correção usa referência menos albumina observada; confirme o valor adotado localmente.",
        ),
        Field(
            "limite_superior_ag_meq_l",
            "Limite superior do ânion gap sem potássio no laboratório",
            "number",
            "mEq/L",
            min=0,
            max=40,
            required=False,
            help="Opcional; use somente o intervalo do método Na − (Cl + HCO₃), sem potássio.",
        ),
        Field(
            "referencia_ag_sem_potassio_confirmada",
            "Confirmo que o limite informado é para ânion gap sem potássio",
            "boolean",
            help="Obrigatório quando um limite é informado; um intervalo com K não é comparável a este cálculo.",
        ),
    ],
    compute=_acidose_metabolica,
    interpret=_interpretar_acidose_metabolica,
    reference=REFERENCIAS_ACIDOSE_METABOLICA,
    kind="assessment",
    limitations=[
        "Use somente quando a acidose metabólica estiver clinicamente estabelecida; a ferramenta não define o distúrbio primário a partir de um único número.",
        "Compensação esperada não é diagnóstico. PaCO₂ fora da faixa apenas sinaliza que distúrbio respiratório associado, erro pré-analítico, diferença temporal ou mudança ventilatória devem ser considerados.",
        "Use eletrólitos e albumina obtidos no mesmo momento da gasometria sempre que possível; diferenças de amostra e tempo podem produzir relações artificiais.",
        "O ânion gap é calculado sem potássio. Intervalos variam por analisador; a classificação automática só ocorre quando o usuário informa o limite superior do próprio laboratório.",
        "A correção de Figge ajusta o efeito da albumina, mas não identifica o ânion não medido nem substitui lactato, cetonas, função renal, toxicologia e avaliação da causa.",
        "Ventilação mecânica, dor, sepse, gestação, hepatopatia e intoxicações podem modificar a PaCO₂; correlacione com o momento clínico e parâmetros ventilatórios.",
    ],
)


def _avaliacao_oxigenacao_sdra(dados: dict) -> dict:
    pao2 = float(dados["pao2_mmhg"])
    fio2_percentual = float(dados["fio2_percentual"])
    suporte = dados["suporte_respiratorio"]
    peep = _numero_opcional(dados, "peep_cpap_cmh2o")
    fluxo = _numero_opcional(dados, "fluxo_cnaf_l_min")

    if not all(math.isfinite(valor) for valor in (pao2, fio2_percentual)):
        raise ValueError("Informe somente valores numéricos finitos.")
    if not 20 <= pao2 <= 800:
        raise ValueError("Informe PaO₂ entre 20 e 800 mmHg.")
    if not 21 <= fio2_percentual <= 100:
        raise ValueError("Informe FiO₂ entre 21% e 100%.")
    if suporte not in {"invasiva", "vni_cpap", "cnaf", "oxigenio_convencional"}:
        raise ValueError("Selecione um suporte respiratório válido.")
    if peep is not None and not 0 <= peep <= 30:
        raise ValueError("Informe PEEP/CPAP entre 0 e 30 cmH₂O.")
    if fluxo is not None and not 0 <= fluxo <= 100:
        raise ValueError("Informe fluxo da CNAF entre 0 e 100 L/min.")

    relacao_pf = pao2 / (fio2_percentual / 100)
    if relacao_pf > 300:
        faixa_pf = ">300 mmHg — não preenche o limiar de hipoxemia da definição global"
    elif relacao_pf > 200:
        faixa_pf = "200–300 mmHg — faixa leve apenas na categoria intubada"
    elif relacao_pf > 100:
        faixa_pf = "100–200 mmHg — faixa moderada apenas na categoria intubada"
    else:
        faixa_pf = "≤100 mmHg — faixa grave apenas na categoria intubada"

    if suporte == "invasiva":
        categoria = "intubada"
        suporte_ok = peep is not None and peep >= 5
        detalhe_suporte = (
            f"ventilação invasiva com PEEP {peep:g} cmH₂O"
            if peep is not None
            else "ventilação invasiva sem PEEP informada"
        )
        gate_suporte = "PEEP ≥5 cmH₂O"
    elif suporte == "vni_cpap":
        categoria = "não intubada"
        suporte_ok = peep is not None and peep >= 5
        detalhe_suporte = (
            f"VNI/CPAP com pressão expiratória {peep:g} cmH₂O"
            if peep is not None
            else "VNI/CPAP sem pressão expiratória informada"
        )
        gate_suporte = "pressão expiratória ≥5 cmH₂O"
    elif suporte == "cnaf":
        categoria = "não intubada"
        suporte_ok = fluxo is not None and fluxo >= 30
        detalhe_suporte = (
            f"CNAF com fluxo {fluxo:g} L/min"
            if fluxo is not None
            else "CNAF sem fluxo informado"
        )
        gate_suporte = "fluxo ≥30 L/min"
    else:
        categoria = "fora das categorias de suporte em ambiente com recursos"
        suporte_ok = False
        detalhe_suporte = "oxigênio convencional/baixo fluxo"
        gate_suporte = "CNAF ≥30 L/min, VNI/CPAP ≥5 cmH₂O ou ventilação invasiva com PEEP ≥5 cmH₂O"

    criterios = {
        "fator predisponente agudo": bool(dados.get("fator_predisponente_agudo")),
        "início ou piora em até 1 semana": bool(dados.get("inicio_ate_uma_semana")),
        "opacidades bilaterais compatíveis": bool(dados.get("opacidades_bilaterais")),
        "edema não primariamente cardiogênico/sobrecarga": bool(
            dados.get("edema_nao_primariamente_cardiogenico")
        ),
        "hipoxemia não primariamente por atelectasia": bool(
            dados.get("hipoxemia_nao_primariamente_atelectasia")
        ),
    }
    ausentes = [nome for nome, confirmado in criterios.items() if not confirmado]
    hipoxemia_ok = relacao_pf <= 300

    if not hipoxemia_ok:
        status = (
            "NÃO PREENCHE O LIMIAR DE OXIGENAÇÃO: a razão P/F é maior que 300 mmHg. "
            "Isso não exclui outra causa de insuficiência respiratória."
        )
    elif not suporte_ok:
        status = (
            f"GATE DE SUPORTE NÃO PREENCHIDO: {detalhe_suporte}; para esta categoria, "
            f"a definição global requer {gate_suporte}. Não classificar SDRA por esta ferramenta."
        )
    elif ausentes:
        status = (
            "CRITÉRIOS CLÍNICOS/DE IMAGEM INCOMPLETOS: oxigenação e suporte atingem o "
            "limiar, mas faltam confirmações explícitas: " + "; ".join(ausentes) + "."
        )
    else:
        status = (
            f"CONJUNTO DECLARADO COMPATÍVEL COM OS CRITÉRIOS OPERACIONAIS DA CATEGORIA "
            f"{categoria.upper()}. Isto não é diagnóstico automático: confirme causa, imagem, "
            "hemodinâmica, simultaneidade PaO₂/FiO₂ e evolução à beira leito."
        )

    alerta_cardiogenico = (
        "Gate cardiogênico confirmado: o edema foi declarado como não exclusiva ou "
        "primariamente explicado por insuficiência cardíaca/sobrecarga. SDRA e edema "
        "cardiogênico podem coexistir; documente o raciocínio."
        if criterios["edema não primariamente cardiogênico/sobrecarga"]
        else "BLOQUEIO CARDIOGÊNICO: não foi confirmado que insuficiência cardíaca/sobrecarga "
        "deixam de ser a explicação exclusiva ou principal. Não rotular SDRA."
    )

    return {
        "relacao_pao2_fio2_mmhg": round(relacao_pf, 1),
        "faixa_da_relacao_pf": faixa_pf,
        "suporte_avaliado": detalhe_suporte,
        "categoria_global_avaliada": categoria,
        "status_dos_criterios": status,
        "alerta_edema_cardiogenico": alerta_cardiogenico,
        "criterios_ausentes": ausentes or "nenhum entre os campos declarados",
        "fora_da_faixa": not (hipoxemia_ok and suporte_ok and not ausentes),
    }


def _interpretar_oxigenacao_sdra(resultado: dict) -> str:
    return (
        f"Razão PaO₂/FiO₂ = {resultado['relacao_pao2_fio2_mmhg']} mmHg. "
        f"{resultado['faixa_da_relacao_pf']}. Suporte: {resultado['suporte_avaliado']}. "
        f"{resultado['status_dos_criterios']} {resultado['alerta_edema_cardiogenico']}"
    )


_OXIGENACAO_SDRA = Calculator(
    slug="oxigenacao-pao2-fio2-sdra-uco",
    name="Oxigenação na UCO — PaO₂/FiO₂ e gates para SDRA",
    theme="Terapia intensiva",
    purpose=(
        "Calcula a razão PaO₂/FiO₂ e confere, sem diagnosticar automaticamente, os gates "
        "de suporte, tempo, fator predisponente, imagem e origem não primariamente cardiogênica."
    ),
    fields=[
        Field("pao2_mmhg", "PaO₂ arterial", "number", "mmHg", min=20, max=800),
        Field(
            "fio2_percentual",
            "FiO₂ no mesmo momento da gasometria",
            "number",
            "%",
            min=21,
            max=100,
            help="Informe percentual, por exemplo 40 para FiO₂ 0,40; não use 0,40.",
        ),
        Field(
            "suporte_respiratorio",
            "Suporte respiratório no momento da PaO₂",
            "select",
            options=[
                {"value": "invasiva", "label": "Ventilação mecânica invasiva"},
                {"value": "vni_cpap", "label": "VNI ou CPAP"},
                {"value": "cnaf", "label": "Cânula nasal de alto fluxo (CNAF)"},
                {"value": "oxigenio_convencional", "label": "Oxigênio convencional/baixo fluxo"},
            ],
        ),
        Field(
            "peep_cpap_cmh2o",
            "PEEP ou pressão expiratória da VNI/CPAP",
            "number",
            "cmH₂O",
            min=0,
            max=30,
            required=False,
            help="Obrigatória para avaliar ventilação invasiva, VNI ou CPAP; não é usada para CNAF.",
        ),
        Field(
            "fluxo_cnaf_l_min",
            "Fluxo total da CNAF",
            "number",
            "L/min",
            min=0,
            max=100,
            required=False,
            help="Obrigatório para avaliar CNAF; a definição global usa o limiar de 30 L/min.",
        ),
        Field(
            "fator_predisponente_agudo",
            "Há fator predisponente agudo documentado (ex.: pneumonia, sepse, aspiração, trauma, transfusão ou choque)",
            "boolean",
        ),
        Field(
            "inicio_ate_uma_semana",
            "Insuficiência respiratória iniciou ou piorou em até 1 semana do fator/sintomas",
            "boolean",
        ),
        Field(
            "opacidades_bilaterais",
            "Imagem mostra opacidades bilaterais não explicadas por derrame, atelectasia ou massa",
            "boolean",
            help="Radiografia/TC; a definição global também admite ultrassom por operador treinado.",
        ),
        Field(
            "edema_nao_primariamente_cardiogenico",
            "Edema não é exclusiva ou primariamente explicado por insuficiência cardíaca/sobrecarga",
            "boolean",
            help="Gate obrigatório na UCO; SDRA e edema cardiogênico podem coexistir.",
        ),
        Field(
            "hipoxemia_nao_primariamente_atelectasia",
            "Hipoxemia/troca gasosa não é primariamente explicada por atelectasia",
            "boolean",
        ),
    ],
    compute=_avaliacao_oxigenacao_sdra,
    interpret=_interpretar_oxigenacao_sdra,
    reference=REFERENCIAS_OXIGENACAO_SDRA,
    kind="assessment",
    limitations=[
        "A razão P/F isolada não diagnostica SDRA e pode variar com FiO₂, PEEP, recrutamento, posição e momento da coleta.",
        "PaO₂ e FiO₂ precisam representar o mesmo momento. FiO₂ estimada em oxigênio convencional/baixo fluxo é imprecisa; por segurança, essa modalidade não preenche o gate de suporte em ambiente com recursos.",
        "As faixas leve, moderada e grave são exibidas somente como faixas da razão e pertencem à categoria intubada da definição global; não graduam automaticamente o paciente não intubado.",
        "Insuficiência cardíaca e sobrecarga volêmica precisam de avaliação objetiva quando a origem do edema não está clara. SDRA pode coexistir com edema cardiogênico, mas a relação não deve ser presumida.",
        "A ferramenta não seleciona FiO₂, PEEP, modo ventilatório, prona, bloqueio neuromuscular ou ECMO; condutas dependem de avaliação clínica e protocolo local.",
        "A categoria modificada para ambientes com recursos limitados não é automatizada aqui, porque seu contexto e disponibilidade diagnóstica exigem julgamento próprio.",
    ],
)


INTENSIVE_CARE_CALCULATOR_REGISTRY: dict[str, Calculator] = {
    _VENTILACAO_PROTETORA.slug: _VENTILACAO_PROTETORA,
    _CONFERENCIA_BOMBA.slug: _CONFERENCIA_BOMBA,
    _ESTADIAMENTO_SCAI.slug: _ESTADIAMENTO_SCAI,
    _ACIDOSE_METABOLICA.slug: _ACIDOSE_METABOLICA,
    _OXIGENACAO_SDRA.slug: _OXIGENACAO_SDRA,
}
