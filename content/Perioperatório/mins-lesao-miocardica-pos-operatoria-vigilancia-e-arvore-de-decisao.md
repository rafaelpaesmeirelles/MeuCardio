---
title: "MINS: lesão miocárdica após cirurgia não cardíaca — vigilância e conduta"
slug: mins-lesao-miocardica-pos-operatoria-vigilancia-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude/Grupo A em 08/08/2026: fonte primaria conferida no PubMed via E-utilities (titulo/revista/data exatos) ou DOI conferido contra a diretriz/consenso real quando muito recente para ter PMID; checado contra o corpus canonico para excluir duplicacao de escore/estudo ja publicado; doses cruzadas contra conhecimento clinico estabelecido, sem divergencia encontrada."
revisado_por_voce: false
summary: "Reconhecimento de myocardial injury after noncardiac surgery (MINS), vigilância com troponina, diferenciais, prognóstico do VISION e árvore de decisão pós-operatória."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
  - "Writing Committee for the VISION Study Investigators; Devereaux PJ, Biccard BM, Sigamani A, et al. Association of Postoperative High-Sensitivity Troponin Levels With Myocardial Injury and 30-Day Mortality Among Patients Undergoing Noncardiac Surgery. JAMA. 2017;317(16):1642-1651. PMID: 28444280. DOI: 10.1001/jama.2017.4360."
  - "Devereaux PJ, Duceppe E, Guyatt G, et al; MANAGE Investigators. Dabigatran in patients with myocardial injury after non-cardiac surgery (MANAGE): an international, randomised, placebo-controlled trial. Lancet. 2018;391(10137):2325-2334. PMID: 29900874. DOI: 10.1016/S0140-6736(18)30832-8."
---

# MINS — myocardial injury after noncardiac surgery

A elevação de troponina após cirurgia não cardíaca é frequente e muitas vezes **clinicamente silenciosa**. O conceito de MINS procura identificar lesão miocárdica de provável mecanismo isquêmico relacionada ao período perioperatório, mesmo quando o paciente não apresenta dor torácica ou alterações eletrocardiográficas clássicas.

O primeiro passo diante de troponina elevada, porém, não é rotular automaticamente MINS: é **confirmar o padrão temporal e procurar causas isquêmicas e não isquêmicas de lesão miocárdica**.

## O que o VISION mostrou

Na análise JAMA 2017 do VISION, **21.842 pacientes com idade ≥45 anos** submetidos a cirurgia não cardíaca com internação tiveram hs-cTnT medida 6–12 horas após a cirurgia e diariamente nos primeiros três dias.

A mortalidade em 30 dias aumentou progressivamente com o pico pós-operatório de hs-cTnT:

| Pico de hs-cTnT | Mortalidade em 30 dias |
|---|---:|
| <20 ng/L | 0,5% |
| 20 a <65 ng/L | 3,0% |
| 65 a <1000 ng/L | 9,1% |
| ≥1000 ng/L | 29,6% |

No estudo, um padrão de **hs-cTnT 20 a <65 ng/L com aumento absoluto ≥5 ng/L**, ou **hs-cTnT ≥65 ng/L**, associou-se de forma importante à mortalidade em 30 dias mesmo sem manifestação isquêmica clínica típica.

**Importante:** esses pontos de corte são específicos da metodologia de hs-cTnT empregada no VISION e **não devem ser transplantados automaticamente para todos os ensaios de troponina**.

Entre os pacientes classificados como MINS no VISION, a grande maioria não apresentou sintomas isquêmicos. Isso sustenta a importância de uma estratégia de vigilância selecionada em pacientes perioperatórios de maior risco.

## Árvore de decisão — troponina pós-operatória elevada

```mermaid
flowchart TD
    A["Paciente no pós-operatório de cirurgia não cardíaca"] --> B{"Há indicação de vigilância com troponina<br/>pelo risco clínico/protocolo adotado?"}
    B -->|"Não"| C["Vigilância clínica habitual;<br/>dosar troponina se surgirem sintomas/sinais"]
    B -->|"Sim"| D["Dosar troponina conforme protocolo perioperatório"]
    D --> E{"Troponina acima do limite de referência<br/>ou elevação dinâmica relevante?"}
    E -->|"Não"| F["Continuar vigilância clínica e manejo pós-operatório"]
    E -->|"Sim"| G["Reavaliar imediatamente:<br/>sintomas, ECG, PA, FC, SpO2, Hb e contexto clínico"]
    G --> H{"Há supra de ST, isquemia persistente,<br/>choque ou arritmia instável?"}
    H -->|"Sim"| I["Tratar como SCA/instabilidade aguda;<br/>acionar cardiologia e estratégia de reperfusão quando indicada"]
    H -->|"Não"| J["Investigar mecanismo da lesão miocárdica"]
    J --> K{"Causa não isquêmica predominante?"}
    K -->|"Sepse/TEP/miocardite/taquiarritmia grave/outro"| L["Tratar causa específica;<br/>não rotular automaticamente como MINS isquêmico"]
    K -->|"Não / provável mecanismo isquêmico"| M["Considerar MINS e definir fenótipo:<br/>IAM tipo 1, desequilíbrio oferta-demanda ou lesão isquêmica sem IAM clínico"]
    M --> N["Corrigir precipitantes: anemia, hipoxemia,<br/>hipotensão, taquicardia, dor e outras demandas"]
    N --> O["Revisar prevenção cardiovascular secundária<br/>e fatores de risco"]
    O --> P{"Risco hemorrágico e cirúrgico permitem<br/>considerar estratégia antitrombótica?"}
    P -->|"Não"| Q["Evitar intensificação antitrombótica automática;<br/>acompanhar e reavaliar"]
    P -->|"Sim"| R["Discussão individualizada;<br/>AHA/ACC 2024: terapia antitrombótica pode ser considerada"]
    Q --> S["Planejar seguimento cardiovascular após alta"]
    R --> S
```

## Diferencial de troponina elevada no pós-operatório

Troponina elevada significa **lesão miocárdica**, não necessariamente trombose coronária. A investigação deve integrar, entre outros:

- síndrome coronariana aguda;
- desequilíbrio entre oferta e demanda de oxigênio — hipotensão, anemia, hipoxemia, taquicardia;
- embolia pulmonar;
- sepse/choque distributivo;
- insuficiência cardíaca aguda;
- taquiarritmia sustentada;
- miocardite ou outras causas de lesão miocárdica, conforme o contexto.

## O que fazer após MINS estável

A AHA/ACC 2024 reconhece MINS como marcador de risco aumentado e recomenda uma abordagem etiológica e de prevenção cardiovascular. Entre as recomendações da diretriz:

- **seguimento cardiovascular ambulatorial é razoável** após MINS;
- **terapia antitrombótica pode ser considerada** em pacientes selecionados, após ponderação do risco hemorrágico e do contexto cirúrgico.

Isso não significa anticoagular rotineiramente todo paciente com troponina elevada.

## MANAGE — por que o estudo importa

O MANAGE randomizou pacientes com MINS para **dabigatrana 110 mg por via oral duas vezes ao dia** ou placebo. O estudo mostrou redução do desfecho vascular composto com dabigatrana sem sinal de aumento significativo do desfecho principal de segurança hemorrágica na comparação do ensaio.

A interpretação correta é:

- o MANAGE fornece evidência de que uma estratégia antitrombótica pode beneficiar **pacientes selecionados com MINS**;
- a dose de dabigatrana é a **intervenção testada no ensaio**, não uma prescrição automática para qualquer elevação de troponina;
- decisão depende de hemostasia cirúrgica, função renal, risco hemorrágico, mecanismo provável da lesão, interações e contraindicações.

## Regra prática

**Troponina elevada no pós-operatório exige uma pergunta causal antes de uma prescrição.** Primeiro diferencie SCA/instabilidade, desequilíbrio oferta-demanda e causas não isquêmicas. Depois, no MINS estável, trate precipitantes, reavalie prevenção cardiovascular e planeje seguimento; antitrombótico é decisão individualizada, não reflexo automático de um valor de troponina.
