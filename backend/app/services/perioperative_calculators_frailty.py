"""Triagem de fragilidade para o módulo perioperatório.

Fonte de produção: ChatGPT.
A FRAIL Scale é listada entre os instrumentos validados de fragilidade pela
diretriz AHA/ACC perioperatória de 2024.
"""

from __future__ import annotations

from app.services.calculators import Calculator, Field

SOURCE_PRODUCTION = "chatgpt"


def _frail(d: dict) -> dict:
    score = sum(
        1
        for key in (
            "fadiga",
            "resistencia",
            "deambulacao",
            "cinco_ou_mais_doencas",
            "perda_peso_5pct",
        )
        if bool(d.get(key))
    )
    categoria = "robusto" if score == 0 else ("pre_fragil" if score <= 2 else "fragil")
    return {"score": score, "max": 5, "categoria": categoria}


def _frail_txt(r: dict) -> str:
    rotulo = {"robusto": "robusto", "pre_fragil": "pré-frágil", "fragil": "frágil"}[r["categoria"]]
    return (
        f"FRAIL Scale {r['score']}/5 — {rotulo}. A AHA/ACC 2024 considera útil a avaliação "
        "pré-operatória de fragilidade com instrumento validado em pacientes ≥65 anos e em "
        "pacientes mais jovens com fragilidade percebida submetidos a cirurgia não cardíaca "
        "de risco elevado. Fragilidade modifica o planejamento perioperatório, mas não é "
        "equivalente a uma probabilidade percentual de MACE."
    )


FRAILTY_PERIOPERATIVE_REGISTRY: dict[str, Calculator] = {
    "frail-scale-perioperatorio": Calculator(
        slug="frail-scale-perioperatorio",
        name="FRAIL Scale — fragilidade perioperatória",
        theme="Perioperatório",
        purpose="Triagem rápida de fragilidade como modificador de risco no pré-operatório.",
        fields=[
            Field(
                "fadiga",
                "Fadiga: sentiu-se cansado todo ou a maior parte do tempo nas últimas 4 semanas",
                "boolean",
            ),
            Field(
                "resistencia",
                "Resistência: dificuldade para subir 10 degraus sozinho, sem parar e sem auxílio",
                "boolean",
            ),
            Field(
                "deambulacao",
                "Deambulação: dificuldade para caminhar várias centenas de jardas sozinho e sem auxílio",
                "boolean",
            ),
            Field(
                "cinco_ou_mais_doencas",
                "Doenças: 5 ou mais das 11 condições da FRAIL Scale",
                "boolean",
                help=(
                    "Hipertensão, diabetes, câncer (exceto câncer de pele menor), doença pulmonar "
                    "crônica, infarto, insuficiência cardíaca, angina, asma, artrite, AVC e doença renal."
                ),
            ),
            Field(
                "perda_peso_5pct",
                "Perda de peso ≥5% nos últimos 12 meses",
                "boolean",
            ),
        ],
        reference=(
            "Morley JE, Malmstrom TK, Miller DK. A simple frailty questionnaire (FRAIL) predicts "
            "outcomes in middle aged African Americans. J Nutr Health Aging. 2012;16(7):601-608. "
            "PMID 22836700. PMCID PMC4515112. DOI 10.1007/s12603-012-0084-2. Aplicação "
            "perioperatória: Thompson A, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM "
            "Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. "
            "Circulation. 2024;150:e351-e442. PMID 39316661. DOI 10.1161/CIR.0000000000001285."
        ),
        compute=_frail,
        interpret=_frail_txt,
        limitations=[
            "É instrumento de triagem de fragilidade, não calculadora de MACE ou mortalidade cirúrgica percentual.",
            "O artigo de validação original não foi uma coorte cirúrgica; seu uso perioperatório decorre da recomendação de avaliar fragilidade com instrumento validado.",
            "Resultados pré-frágil/frágil devem levar à avaliação clínica do impacto funcional, cognitivo, nutricional e dos objetivos do cuidado, não ao cancelamento automático da cirurgia.",
        ],
    ),
}
