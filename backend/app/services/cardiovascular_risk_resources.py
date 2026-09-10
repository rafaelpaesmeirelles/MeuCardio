"""Acessos oficiais de risco cardiovascular, sem copiar motores licenciados.

O status externo impede execução e geração de laudo pelo endpoint genérico.
Nenhum dado clínico é transmitido no link. Fontes consultadas em 2026-09-10.
"""
from app.services.calculators import Calculator

CARDIOVASCULAR_RISK_RESOURCES = {
    "prevent": Calculator(
        slug="prevent", name="PREVENT — SBC / AHA / ACC", theme="Prevenção e lipídios",
        purpose="Risco cardiovascular na prevenção primária: aterosclerose (ASCVD), doença cardiovascular total e insuficiência cardíaca em 10 e 30 anos. Ferramenta oficial externa.",
        fields=[], kind="assessment", status="referencia_externa",
        external_url="https://tools.acc.org/CVD-Risk-Estimator-Plus/",
        reference="Khan SS et al. Circulation. 2024;149:430–449. DOI: 10.1161/CIRCULATIONAHA.123.067626. Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose 2025, SBC. DOI: 10.36660/abc.20250640. American Heart Association PREVENT 1.0.0; CVD Risk Estimator Plus, American College of Cardiology. https://professional.heart.org/en/guidelines-and-statements/about-prevent-calculator",
        limitations=[
            "Prevenção primária, sem doença cardiovascular estabelecida: 30–79 anos; estimativa de 30 anos somente entre 30 e 59 anos na ferramenta oficial.",
            "ASCVD, doença cardiovascular total e insuficiência cardíaca são desfechos distintos. Não somar percentuais nem aplicar os mesmos limiares de tratamento a todos os resultados.",
            "A SBC 2025 recomenda PREVENT-ASCVD em 10 anos para 30–79 anos sem doença cardiovascular prévia (recomendação forte; certeza alta).",
            "Desenvolvido em população dos Estados Unidos; contextualizar a aplicação no Brasil. CEP brasileiro não equivale ao índice de privação social dos Estados Unidos.",
            "Não estima diretamente o benefício causal de iniciar tratamento. A escolha terapêutica depende da diretriz adotada e da avaliação clínica.",
        ],
    ),
    "score2": Calculator(
        slug="score2", name="SCORE2 — ESC", theme="Prevenção e lipídios",
        purpose="Risco cardiovascular de primeiro evento fatal ou não fatal em 10 anos na prevenção primária. Ferramenta oficial externa HeartScore, para 40–69 anos.",
        fields=[], kind="assessment", status="referencia_externa",
        external_url="https://www.heartscore.org/en_GB/",
        reference="SCORE2 working group and ESC Cardiovascular risk collaboration. Eur Heart J. 2021;42:2439–2454. DOI: 10.1093/eurheartj/ehab309. HeartScore, European Society of Cardiology.",
        limitations=[
            "Para pessoas aparentemente saudáveis, sem doença cardiovascular conhecida ou diabetes. Não utilizar para reclassificar doença renal crônica relevante ou hipercolesterolemia familiar como baixo risco.",
            "As quatro calibrações correspondem a regiões europeias. O Brasil não pertence a essas regiões; não selecionar automaticamente uma calibração europeia como se validada no Brasil.",
            "Os limiares de estratificação da ESC variam com a idade. SCORE2 não é intercambiável com PREVENT, Framingham ou SCORE2-Diabetes.",
        ],
    ),
    "score2-op": Calculator(
        slug="score2-op", name="SCORE2-OP — ESC, pessoas idosas", theme="Prevenção e lipídios",
        purpose="Risco cardiovascular na prevenção primária em pessoas de 70–89 anos, considerando mortalidade competitiva. Ferramenta oficial externa HeartScore.",
        fields=[], kind="assessment", status="referencia_externa",
        external_url="https://www.heartscore.org/en_GB/",
        reference="SCORE2-OP working group and ESC Cardiovascular risk collaboration. Eur Heart J. 2021;42:2455–2467. DOI: 10.1093/eurheartj/ehab312. HeartScore, European Society of Cardiology.",
        limitations=[
            "Utilizar a versão específica para pessoas idosas; não extrapolar SCORE2 de adultos mais jovens.",
            "Para prevenção primária em pessoas aparentemente saudáveis. Diabetes, doença cardiovascular estabelecida e condições de alto risco requerem avaliação específica.",
            "Calibrado para regiões europeias, sem calibração brasileira oferecida. Interpretar considerando fragilidade, comorbidades, expectativa de vida e preferências do paciente.",
        ],
    ),
}

CARDIOVASCULAR_RISK_RESOURCES["score2-diabetes"] = Calculator(
    slug="score2-diabetes", name="SCORE2-Diabetes — ESC", theme="Prevenção e lipídios",
    purpose="Risco cardiovascular em 10 anos no diabetes tipo 2. Acesso à página oficial do aplicativo ESC CVD Risk Calculation, onde o modelo está disponível.",
    fields=[], kind="assessment", status="referencia_externa",
    external_url="https://www.escardio.org/Education/Practice-Tools/CVD-prevention-toolbox/esc-cvd-risk-calculation-app",
    reference="SCORE2-Diabetes Working Group and ESC Cardiovascular Risk Collaboration. Eur Heart J. 2023;44:2544–2556. DOI: 10.1093/eurheartj/ehad260. ESC CVD Risk Calculation App.",
    limitations=[
        "Desenvolvido para diabetes tipo 2, 40–69 anos, sem doença cardiovascular prévia; não utilizar SCORE2 comum como substituto.",
        "Idade ao diagnóstico do diabetes, HbA1c e função renal integram a estimativa. Doença cardiovascular estabelecida ou lesão grave de órgão-alvo exige estratificação própria.",
        "Calibrado para regiões europeias. Não há calibração brasileira nessa ferramenta; não extrapolar para diabetes tipo 1 ou idades fora do domínio.",
        "O acesso abre a página oficial de distribuição do aplicativo ESC, não um cálculo dentro do CorVIA.",
    ],
)

# A existência está documentada pela própria SBC; endereço executável ainda não
# confirmado. Não atribuir à ferramenta coeficientes/versão que não verificamos.
CARDIOVASCULAR_RISK_RESOURCES["sbc-risco-cardiovascular"] = Calculator(
    slug="sbc-risco-cardiovascular", name="SBC — Calculadora para Estratificação de Risco Cardiovascular",
    theme="Prevenção e lipídios",
    purpose="Ferramenta própria do Departamento de Aterosclerose da SBC. Endereço e versão operacional em confirmação; cálculo ainda indisponível no CorVIA.",
    fields=[], kind="assessment", status="verificacao_humana_necessaria",
    reference="Sociedade Brasileira de Cardiologia, Departamento de Aterosclerose, histórico da gestão 2016–2017. https://www.portal.cardiol.br/entidades/da",
    limitations=[
        "O portal oficial confirma o desenvolvimento da calculadora, mas não fornece um endereço executável verificável na consulta de 10/09/2026.",
        "Não é uma renomeação de Framingham ou PREVENT. Modelo, versão e condições de incorporação ainda precisam ser confirmados na fonte oficial.",
    ],
)
