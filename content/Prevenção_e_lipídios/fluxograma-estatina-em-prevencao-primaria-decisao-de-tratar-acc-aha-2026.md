---
title: "Fluxograma: Estatina em Prevenção Primária — Decisão de Tratar pela ACC/AHA 2026 (PREVENT-ASCVD)"
slug: fluxograma-estatina-em-prevencao-primaria-decisao-de-tratar-acc-aha-2026
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Blumenthal RS, Morris PB, Gaudino M, et al. 2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Dyslipidemia. J Am Coll Cardiol. 2026;87(19):2624-2757. DOI: 10.1016/j.jacc.2025.11.016. PMID: 41824590."
  - "Blumenthal RS, Morris PB, Gaudino M, et al. 2026 Guideline on the Management of Dyslipidemia. Circulation. Published online March 13, 2026. DOI: 10.1161/CIR.0000000000001423."
  - "Derivado de acc-aha-2026-diretriz-dislipidemia-prevent-lpa-apob-e-metas-ldl.md, já publicado no acervo (Prevenção e lipídios)."
---

# Fluxograma: Estatina em Prevenção Primária — Decisão de Tratar pela ACC/AHA 2026 (PREVENT-ASCVD)

O fluxograma já publicado nesta pasta ("Dislipidemia — categoria de risco, meta de LDL-C e escalonamento") cobre a diretriz **ESC/EAS 2025**: como o SCORE2 define a categoria de risco e a meta de LDL-C, e como escalonar o tratamento hipolipemiante depois que a estatina já foi iniciada. Este fluxograma cobre uma pergunta anterior e sob outra diretriz — a **ACC/AHA 2026** —: **quando considerar iniciar** a terapia redutora de LDL em prevenção primária, antes de qualquer meta numérica entrar em jogo.

A diferença estrutural entre as duas diretrizes é o que torna este segundo ângulo necessário: a americana de 2026 substitui as antigas Pooled Cohort Equations pelas equações **PREVENT-ASCVD**, mantém condições que dispensam o cálculo de risco (diabetes, doença renal crônica, HIV), separa a hipercolesterolemia grave (LDL-C ou ApoB muito elevados) como via própria, e usa o escore de cálcio coronariano (CAC) apenas para **reclassificar** quando a decisão permanece incerta — não como rastreamento indiscriminado.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto de 30 a 79 anos, sem doença aterosclerótica<br/>estabelecida, em avaliação de prevenção primária<br/>de risco cardiovascular (ACC/AHA 2026)"] --> D1{"Idade entre 40 e 75 anos, com diabetes,<br/>doença renal crônica estágio 3 ou 4,<br/>ou infecção por HIV?"}

  D1 -->|"Sim"| C1(["Terapia redutora de LDL recomendada<br/>independentemente do risco estimado<br/>e do LDL-C basal"])

  D1 -->|"Não"| D2{"LDL-C de 190 mg/dL ou mais<br/>e/ou ApoB de 140 mg/dL ou mais?"}

  D2 -->|"Sim"| P1["Investigar causa secundária; considerar<br/>hipercolesterolemia familiar e rastreamento<br/>em cascata quando apropriado"]
  P1 --> D3{"Paciente jovem com LDL-C de 160 mg/dL<br/>ou mais, ou história familiar forte de<br/>doença aterosclerótica prematura?"}
  D3 -->|"Sim"| C2(["Considerar farmacoterapia hipolipemiante<br/>mais precocemente, dado o alto risco de<br/>exposição cumulativa ao longo da vida"])
  D3 -->|"Não"| C3(["Terapia redutora de LDL baseada no risco<br/>global e na exposição cumulativa; alto risco<br/>aterosclerótico ao longo da vida já está<br/>estabelecido por este nível de LDL-C/ApoB"])

  D2 -->|"Não"| D4{"Paciente com mais de 75 anos?"}
  D4 -->|"Sim"| C4(["Farmacoterapia pode ser considerada, em<br/>conjunto com estilo de vida, risco global,<br/>fragilidade, expectativa de benefício<br/>e preferência do paciente"])
  D4 -->|"Não"| P2["Calcular o risco de doença aterosclerótica<br/>cardiovascular em 10 anos pelas equações<br/>PREVENT-ASCVD (substituem as antigas<br/>Pooled Cohort Equations)"]
  P2 --> D5{"Risco estimado em 10 anos<br/>pelo PREVENT-ASCVD"}
  D5 -->|"3% a menos de 5%"| C5(["Terapia redutora de LDL pode ser<br/>considerada, após discussão compartilhada<br/>entre clínico e paciente"])
  D5 -->|"5% a menos de 10%"| C6(["Terapia redutora de LDL deve ser<br/>considerada, após discussão<br/>individualizada"])
  D5 -->|"Menos de 3%, ou 10% ou mais"| D6{"Decisão terapêutica ainda incerta,<br/>e paciente elegível para escore de cálcio<br/>coronariano (homens a partir de 40 anos,<br/>mulheres a partir de 45 anos)?"}
  D6 -->|"Sim"| P3["Usar o escore de cálcio coronariano (CAC)<br/>seletivamente para reclassificar o risco<br/>(modelo Calculate-Personalize-Reclassify)"]
  P3 --> D7{"O CAC reclassifica o risco para a faixa<br/>de discussão terapêutica<br/>(3% a menos de 10%)?"}
  D7 -->|"Sim"| C7(["Reclassificado: aplicar a decisão de<br/>discussão compartilhada ou individualizada<br/>correspondente à nova faixa de risco"])
  D7 -->|"Não"| C8(["Sem indicação adicional de terapia<br/>hipolipemiante baseada em risco nesta<br/>reavaliação; manter ênfase em estilo<br/>de vida e reavaliação periódica"])
  D6 -->|"Não"| C9(["Sem indicação de terapia hipolipemiante<br/>baseada em risco nesta avaliação; manter<br/>ênfase em estilo de vida e reavaliação periódica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## O que a árvore não mostra

**Lp(a) deve ser medida ao menos uma vez** em todo adulto, independentemente do ramo desta árvore — não muda a decisão inicial de tratar, mas reclassifica risco quando elevada (1,4 vez o risco em 125 nmol/L ou mais; cerca de 2 vezes em 250 nmol/L ou mais) e reforça a intensificação dos fatores modificáveis.

**ApoB** é ferramenta de refinamento, não de decisão inicial: mais útil quando há discordância entre LDL-C e a carga de partículas aterogênicas (triglicerídeos acima de 200 mg/dL, diabetes, LDL-C já abaixo de 70 mg/dL sem meta secundária atingida).

**Hipertrigliceridemia** não é um ramo à parte para prevenção aterosclerótica: a estatina continua sendo a base farmacológica mesmo nesse cenário. Triglicerídeos de 1.000 mg/dL ou mais justificam terapia específica adicional, mas com o objetivo distinto de prevenir pancreatite, não de reduzir placa.

**Esta diretriz americana não deve ser lida como equivalente à ESC/EAS 2025.** As duas convergem em princípios, mas usam estruturas e algoritmos próprios — uma meta ou classe de recomendação de uma sociedade não deve ser atribuída à outra por analogia, e o fluxograma de escalonamento hipolipemiante já publicado nesta pasta segue a estrutura europeia, não esta.
