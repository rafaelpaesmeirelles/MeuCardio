---
title: "Diretriz CKM AHA/ACC/ADA/ASN 2026 — estágios, PREVENT e tratamento integrado"
slug: diretriz-ckm-aha-acc-ada-asn-2026-estagios-prevent-e-tratamento-integrado
theme: "Diabetes e cardiologia"
kind: diretriz
summary: "Framework 2026 da síndrome cardiovascular–renal–metabólica: estadiamento 0–4, uso do PREVENT, obesidade, diabetes, DRC e insuficiência cardíaca em uma única árvore de decisão."
review_status: pendente_revisao
fonte_producao: chatgpt
source_refs: ["Ndumele CE, Rodriguez F, Dixon DL, et al. 2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome. J Am Coll Cardiol. 2026;87(22S):e1889-e2007. DOI: 10.1016/j.jacc.2026.03.056. PMID: 42265997.", "Circulation version DOI: 10.1161/CIR.0000000000001453."]
---

# Diretriz CKM 2026

A diretriz AHA/ACC/ADA/ASN de 2026 formaliza a **síndrome cardiovascular–renal–metabólica (CKM)** como um continuum que conecta adiposidade, diabetes, doença renal crônica e doença cardiovascular. A proposta é abandonar o manejo fragmentado em silos e definir **estágio + risco absoluto + terapias com benefício multissistêmico**.

## Estadiamento CKM

A diretriz recomenda estadiar jovens e adultos para prevenir progressão e, quando possível, promover regressão de estágio.

De forma conceitual:

- **Estágio 0:** sem fatores de risco CKM relevantes;
- **Estágio 1:** excesso ou disfunção do tecido adiposo, sem outros grandes fatores metabólicos/renais;
- **Estágio 2:** fatores metabólicos e/ou doença renal, sem doença cardiovascular clínica;
- **Estágio 3:** doença cardiovascular subclínica ou risco cardiovascular previsto muito alto;
- **Estágio 4:** doença cardiovascular clínica em contexto CKM.

A classificação detalhada deve seguir a tabela oficial da diretriz; este documento não transforma o resumo conceitual acima em substituto do estadiamento formal.

## PREVENT entra no centro do algoritmo

Para indivíduos nos estágios CKM 0–3, a diretriz recomenda quantificação de risco pelas equações **PREVENT**, estimando risco em 10 e 30 anos de:

- ASCVD;
- insuficiência cardíaca;
- doença cardiovascular total.

Dois limiares destacados pelo documento:

- risco de DCV em 10 anos **≥20%** pode funcionar como um critério para **estágio CKM 3**;
- risco em 10 anos **≥7,5%** ajuda a priorizar farmacoterapias preventivas.

A fórmula PREVENT não é reproduzida neste documento. Para implementação como calculadora interativa, os coeficientes oficiais completos precisam ser importados e validados contra a ferramenta/publicação original; até isso ocorrer: **VERIFICAÇÃO HUMANA NECESSÁRIA**.

## Por que IC faz parte do risco CKM

A diretriz amplia prevenção para além de aterosclerose. Obesidade, diabetes e DRC também elevam risco de IC, e o PREVENT estima esse desfecho especificamente.

Na IC com FE reduzida, a diretriz destaca benefícios cardiovasculares e renais do bloqueio do SRAA/ARNI e SGLT2 como componentes da terapia quádrupla com betabloqueador e ARM.

Na IC com FE levemente reduzida/preservada:

- SGLT2 é colocado como terapia de primeira linha orientada por diretriz;
- terapias baseadas em GLP-1 ganham papel em pacientes com obesidade ou outros fatores CKM;
- nsMRA deve ser considerado em diabetes tipo 2 + DRC para reduzir eventos cardiovasculares e perda de função renal quando apropriado.

## Árvore de decisão — estadiar e tratar CKM

```mermaid
flowchart TD
    A[Paciente em prevenção ou com doença CV] --> B[Avaliar adiposidade, PA, glicemia/diabetes, lipídios, rim e DCV]
    B --> C{Há doença cardiovascular clínica?}
    C -- Sim --> D[CKM estágio 4: prevenção secundária + tratamento metabólico/renal integrado]
    C -- Não --> E{Há DCV subclínica ou risco PREVENT 10 anos ≥20%?}
    E -- Sim --> F[CKM estágio 3: intensificar prevenção baseada em risco]
    E -- Não --> G{Há fatores metabólicos relevantes e/ou DRC?}
    G -- Sim --> H[CKM estágio 2]
    G -- Não --> I{Há excesso/disfunção adiposa?}
    I -- Sim --> J[CKM estágio 1]
    I -- Não --> K[CKM estágio 0]
    H --> L[Calcular PREVENT 10 e 30 anos]
    J --> L
    K --> L
    L --> M{Risco 10 anos ≥7,5% ou condição que já indique farmacoterapia?}
    M -- Sim --> N[Priorizar terapias preventivas com benefício CV/renal/metabólico]
    M -- Não --> O[Estilo de vida + controle de fatores + reavaliação]
    N --> P[Reavaliar estágio, função renal, peso, PA, diabetes e sinais de IC]
    O --> P
```

## Árvore de decisão — CKM no paciente com insuficiência cardíaca

```mermaid
flowchart TD
    A[Paciente com IC] --> B[Caracterizar FEVE + obesidade + diabetes + DRC]
    B --> C{ICFER?}
    C -- Sim --> D[Implementar terapia quádrupla baseada em evidência e otimizar fatores CKM]
    C -- Não --> E{ICFElr/ICFEp?}
    E -- Sim --> F[SGLT2 como eixo de GDMT]
    F --> G{Obesidade relevante?}
    G -- Sim --> H[Considerar terapia GLP-1 baseada em evidência/indicação]
    G -- Não --> I[Seguir tratamento de IC e comorbidades]
    F --> J{DM2 + DRC?}
    J -- Sim --> K[Considerar nsMRA com benefício comprovado quando elegível]
    J -- Não --> I
```

## O que muda na prática

1. Risco de IC deve ser considerado junto ao risco aterosclerótico.
2. PREVENT substitui abordagens antigas de risco em várias decisões preventivas contemporâneas.
3. Obesidade deixa de ser apenas “fator de risco” e passa a ser alvo terapêutico dentro do continuum CKM.
4. Terapias devem ser escolhidas por benefício cardiovascular/renal/metabólico, não apenas por um marcador isolado como HbA1c.
5. Estadiamento deve ser repetido ao longo da vida; progressão não é inevitável.

## Armadilhas

- Chamar CKM de sinônimo de síndrome metabólica.
- Calcular apenas ASCVD e ignorar risco de IC.
- Usar PREVENT sem respeitar população/variáveis e horizonte para os quais foi validado.
- Tratar diabetes, rim, obesidade e coração em planos desconectados.
- Considerar estágio CKM uma etiqueta fixa, sem possibilidade de regressão/progressão.

## Regra prática

**CKM transforma quatro consultas paralelas — peso, diabetes, rim e coração — em uma única trajetória de risco.** Estagie, quantifique risco com PREVENT quando indicado e escolha intervenções pelo benefício integrado.