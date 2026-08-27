"""Gates de segurança arrítmica para Cardiologia Intensiva/UCO.

Separa torsades de pointes (TV polimórfica associada a QT longo) da TV
polimórfica com QT normal. A ferramenta não calcula energia, magnésio,
eletrólitos, isoproterenol ou parâmetros de pacing.
"""

from __future__ import annotations

import math

from .calculators import Calculator, Field


REFERENCIAS_TORSADES = (
    "American Heart Association. 2025 Guidelines for CPR and ECC, Part 9: Adult "
    "Advanced Life Support. Circulation. 2025;152(Suppl 2):S538-S577. "
    "doi:10.1161/CIR.0000000000001376 — TV polimórfica sustentada: choque não "
    "sincronizado imediato (COR 1, LOE B-NR); magnésio pode ser considerado em "
    "recorrências associadas a QT longo/torsades (COR 2b, LOE C-LD); magnésio "
    "rotineiro não é recomendado na TV polimórfica com QT normal (COR 3: No "
    "Benefit, LOE C-LD). ILCOR 2025 Consensus on Science With Treatment "
    "Recommendations. Circulation. 2025;152(Suppl 1):S72-S115. "
    "doi:10.1161/CIR.0000000000001360 — acquired long-QT polymorphic WCT may be "
    "treated with magnesium; pacing or isoprenaline may be considered when "
    "bradycardia/pause precipitated, while isoprenaline should be avoided in "
    "familial long-QT."
)


def _numero_opcional(dados: dict, chave: str) -> float | None:
    valor = dados.get(chave)
    if valor in (None, ""):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"Valor inválido em {chave}.") from None
    if not math.isfinite(numero):
        raise ValueError(f"Informe valor finito em {chave}.")
    return numero


def _avaliar_torsades(dados: dict) -> dict:
    tv_polimorfica = bool(dados.get("tv_polimorfica_atual"))
    sustentada = bool(dados.get("episodio_sustentado"))
    qt_longo_conhecido = bool(dados.get("qt_longo_conhecido_ou_suspeito"))
    bradicardia_pausa = bool(dados.get("bradicardia_ou_pausa_precipitante"))
    hipocalemia = bool(dados.get("hipocalemia_documentada"))
    hipomagnesemia = bool(dados.get("hipomagnesemia_documentada"))
    farmaco_qt = bool(dados.get("farmaco_prolonga_qt"))
    isquemia = bool(dados.get("isquemia_aguda_suspeita"))
    lqts_congenito = bool(dados.get("lqts_congenito_conhecido"))
    qtc = _numero_opcional(dados, "qtc_ms")

    if qtc is not None and not 250 <= qtc <= 800:
        raise ValueError("Informe QTc entre 250 e 800 ms.")
    if sustentada and not tv_polimorfica:
        raise ValueError("Marque episódio sustentado somente quando TV polimórfica estiver presente.")
    if lqts_congenito and not qt_longo_conhecido:
        raise ValueError("LQTS congênito conhecido implica QT longo conhecido/suspeito no contexto da ferramenta.")

    qtc_alto_risco = qtc is not None and qtc > 500
    contexto_qt_longo = qt_longo_conhecido or qtc_alto_risco

    if tv_polimorfica and sustentada:
        prioridade = (
            "EMERGÊNCIA ELÉTRICA: TV polimórfica sustentada é considerada instável e requer "
            "choque não sincronizado imediato. Medidas farmacológicas não devem atrasar a desfibrilação."
        )
        risco = "emergencia"
    elif tv_polimorfica:
        prioridade = (
            "ALTO RISCO DE RECORRÊNCIA: episódio de TV polimórfica não sustentada exige definição "
            "rápida do QT basal/contexto e correção das causas reversíveis."
        )
        risco = "prioritario"
    elif qtc_alto_risco and bradicardia_pausa:
        prioridade = (
            "QTc >500 ms com bradicardia/pausas: combinação de alto risco para torsades; remover "
            "fatores adquiridos, corrigir eletrólitos e buscar avaliação especializada imediata."
        )
        risco = "prioritario"
    elif contexto_qt_longo:
        prioridade = (
            "QT longo conhecido/suspeito sem TV polimórfica atual: foco em prevenção, revisão de "
            "medicamentos, eletrólitos e gatilhos, com monitorização conforme risco."
        )
        risco = "vigilancia"
    else:
        prioridade = (
            "Sem evidência declarada de QT longo/torsades. Se houver TV polimórfica com QT normal, "
            "investigar especialmente isquemia e outras etiologias; magnésio rotineiro não é recomendado."
        )
        risco = "contextual"

    if tv_polimorfica and contexto_qt_longo:
        fenotipo = "TV polimórfica associada a QT longo — compatível com torsades de pointes no contexto clínico"
        magnesio = (
            "Magnésio IV pode ser considerado para suprimir/prevenir recorrências de torsades; "
            "não depende da presença de hipomagnesemia sérica documentada. A ferramenta não calcula dose."
        )
    elif tv_polimorfica and not contexto_qt_longo:
        fenotipo = "TV polimórfica sem QT longo documentado — não rotular automaticamente como torsades"
        magnesio = (
            "Magnésio rotineiro não é recomendado para TV polimórfica com QT normal. Priorizar "
            "desfibrilação quando sustentada e investigação/tratamento da etiologia, frequentemente isquemia."
        )
    elif contexto_qt_longo:
        fenotipo = "substrato de QT longo sem TV polimórfica atual"
        magnesio = (
            "Magnésio não é uma meta laboratorial isolada; corrigir deficiência documentada e usar o "
            "fluxo de torsades caso TV polimórfica apareça/recorra."
        )
    else:
        fenotipo = "sem fenótipo de torsades definido pelos dados informados"
        magnesio = "Não há indicação de magnésio antiarrítmico inferida pela ferramenta."

    reversiveis: list[str] = []
    if hipocalemia:
        reversiveis.append("hipocalemia documentada — corrigir conforme protocolo e monitorização")
    if hipomagnesemia:
        reversiveis.append("hipomagnesemia documentada — corrigir conforme protocolo e função renal")
    if farmaco_qt:
        reversiveis.append("medicamento que prolonga QT — revisar/suspender/substituir quando clinicamente apropriado")
    if bradicardia_pausa:
        reversiveis.append("bradicardia/pausas — possível gatilho de torsades adquirida")
    if isquemia:
        reversiveis.append("isquemia aguda possível — especialmente relevante se QT não estiver prolongado")
    if not reversiveis:
        reversiveis.append("nenhum fator reversível foi declarado; revisar eletrólitos, fármacos, isquemia e história familiar")

    if bradicardia_pausa and tv_polimorfica and contexto_qt_longo:
        if lqts_congenito:
            frequencia = (
                "LQTS congênito/familiar: não extrapolar isoproterenol usado em torsades adquirida; "
                "buscar eletrofisiologia/especialista para estratégia de frequência e tratamento específico."
            )
        else:
            frequencia = (
                "Torsades adquirida precipitada por bradicardia/pausas: consulta especializada para "
                "overdrive pacing ou isoproterenol pode ser considerada; nenhuma frequência/dose é automatizada."
            )
    else:
        frequencia = "Sem indicação de estratégia de aumento de frequência inferida automaticamente."

    return {
        "fenotipo": fenotipo,
        "prioridade": prioridade,
        "risco": risco,
        "papel_do_magnesio": magnesio,
        "fatores_reversiveis": reversiveis,
        "estrategia_frequencia": frequencia,
        "qtc_alto_risco": qtc_alto_risco,
        "fora_da_faixa": tv_polimorfica or contexto_qt_longo or bool(reversiveis[:-1]),
    }


def _interpretar_torsades(resultado: dict) -> str:
    return (
        f"{resultado['fenotipo']}. {resultado['prioridade']} {resultado['papel_do_magnesio']} "
        f"Fatores: {'; '.join(resultado['fatores_reversiveis'])}. "
        f"{resultado['estrategia_frequencia']}"
    )


_TORSADES = Calculator(
    slug="torsades-qt-longo-magnesio-uco",
    name="TV polimórfica/Torsades — QT longo, magnésio e gates de segurança",
    theme="Terapia intensiva",
    purpose=(
        "Separa TV polimórfica com QT longo (torsades) da TV polimórfica com QT normal, "
        "prioriza desfibrilação e confere fatores reversíveis sem calcular tratamento."
    ),
    fields=[
        Field("tv_polimorfica_atual", "Há TV polimórfica atual/recente", "boolean"),
        Field("episodio_sustentado", "O episódio é sustentado", "boolean"),
        Field("qt_longo_conhecido_ou_suspeito", "QT longo conhecido ou fortemente suspeito", "boolean"),
        Field("qtc_ms", "QTc em ritmo basal/fora da TV", "number", "ms", min=250, max=800, required=False),
        Field("bradicardia_ou_pausa_precipitante", "Bradicardia ou pausa precede/precipita episódios", "boolean"),
        Field("hipocalemia_documentada", "Hipocalemia documentada", "boolean"),
        Field("hipomagnesemia_documentada", "Hipomagnesemia documentada", "boolean"),
        Field("farmaco_prolonga_qt", "Uso/exposição a medicamento que prolonga QT", "boolean"),
        Field("isquemia_aguda_suspeita", "Isquemia aguda suspeita", "boolean"),
        Field("lqts_congenito_conhecido", "Síndrome do QT longo congênita/familiar conhecida", "boolean"),
    ],
    compute=_avaliar_torsades,
    interpret=_interpretar_torsades,
    reference=REFERENCIAS_TORSADES,
    kind="assessment",
    limitations=[
        "TV polimórfica sustentada exige desfibrilação imediata; esta ferramenta não calcula energia nem deve atrasar choque.",
        "Torsades requer contexto de QT longo. TV polimórfica com QT normal não deve ser rotulada automaticamente como torsades.",
        "Magnésio pode ser considerado para recorrência de torsades mesmo sem hipomagnesemia sérica, mas não é recomendado rotineiramente para TV polimórfica com QT normal.",
        "QTc varia com método de correção, frequência, QRS, ritmo e qualidade do ECG; um número isolado não substitui revisão do traçado.",
        "Correção de potássio/magnésio, retirada de fármaco, pacing ou isoproterenol dependem de função renal, etiologia, contexto e protocolo; nenhuma dose ou parâmetro é automatizado.",
        "Isoproterenol pode ser considerado em torsades adquirida pause-dependent sob supervisão, mas deve ser evitado no QT longo familiar/congênito conforme ILCOR; não extrapolar entre fenótipos."
    ],
)


INTENSIVE_CARE_ARRHYTHMIA_SAFETY_REGISTRY: dict[str, Calculator] = {
    _TORSADES.slug: _TORSADES,
}
