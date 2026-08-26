---
title: "Fluxograma: MINS — lesão miocárdica pós-operatória, vigilância com troponina e conduta"
slug: fluxograma-mins-lesao-miocardica-pos-operatoria
theme: "Perioperatório"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC/ACS/ASNC/HRS/SCA/SCCT/SCMR/SVM Guideline for Perioperative Cardiovascular Management for Noncardiac Surgery. Circulation. 2024;150:e351-e442. PMID: 39316661. DOI: 10.1161/CIR.0000000000001285."
  - "Writing Committee for the VISION Study Investigators; Devereaux PJ, Biccard BM, Sigamani A, et al. Association of Postoperative High-Sensitivity Troponin Levels With Myocardial Injury and 30-Day Mortality Among Patients Undergoing Noncardiac Surgery. JAMA. 2017;317(16):1642-1651. PMID: 28444280. DOI: 10.1001/jama.2017.4360."
  - "Devereaux PJ, Duceppe E, Guyatt G, et al; MANAGE Investigators. Dabigatran in patients with myocardial injury after non-cardiac surgery (MANAGE): an international, randomised, placebo-controlled trial. Lancet. 2018;391(10137):2325-2334. PMID: 29900874. DOI: 10.1016/S0140-6736(18)30832-8."
  - "Derivado do documento já publicado no acervo 'MINS: lesão miocárdica após cirurgia não cardíaca — vigilância e conduta' (content/Perioperatório/mins-lesao-miocardica-pos-operatoria-vigilancia-e-arvore-de-decisao.md), que cita as mesmas três fontes acima."
---

# Fluxograma: MINS — lesão miocárdica pós-operatória, vigilância com troponina e conduta

Troponina elevada no pós-operatório significa **lesão miocárdica**, não necessariamente trombose coronária — e a maioria dos pacientes com MINS (myocardial injury after noncardiac surgery) é assintomática. Rotular automaticamente "MINS" diante de qualquer troponina alterada pula uma etapa obrigatória: primeiro diferenciar instabilidade aguda e causa não isquêmica, só depois considerar MINS propriamente dito.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente no pós-operatório de cirurgia não cardíaca"] --> D1{"Há indicação de vigilância com troponina pelo risco clínico/protocolo adotado?"}
  D1 -->|"Não"| C1(["Vigilância clínica habitual; dosar troponina apenas se surgirem sintomas ou sinais"])
  D1 -->|"Sim"| P1["Dosar troponina conforme o protocolo perioperatório (ex.: pré-operatório, 24h e 48h após a cirurgia)"]
  P1 --> D2{"Troponina acima do limite de referência ou com elevação dinâmica relevante?"}
  D2 -->|"Não"| C2(["Continuar a vigilância clínica e o manejo pós-operatório habitual"])
  D2 -->|"Sim"| P2["Reavaliar imediatamente: sintomas, ECG, pressão arterial, frequência cardíaca, saturação, hemoglobina e contexto clínico"]
  P2 --> D3{"Há supradesnivelamento de ST, isquemia persistente, choque ou arritmia instável?"}
  D3 -->|"Sim"| C3(["Tratar como síndrome coronariana aguda/instabilidade aguda; acionar a cardiologia e considerar estratégia de reperfusão"])
  D3 -->|"Não"| P3["Investigar o mecanismo da lesão: infarto tipo 1, desequilíbrio oferta-demanda, tromboembolismo pulmonar, sepse, insuficiência cardíaca aguda, taquiarritmia, miocardite ou outra causa"]
  P3 --> D4{"Causa não isquêmica claramente predominante (sepse, tromboembolismo pulmonar, miocardite, taquiarritmia grave ou outra)?"}
  D4 -->|"Sim"| C4(["Tratar a causa específica; não rotular automaticamente como MINS isquêmico"])
  D4 -->|"Não, provável mecanismo isquêmico"| P4["Considerar MINS e definir o fenótipo: infarto tipo 1, desequilíbrio oferta-demanda ou lesão isquêmica sem infarto clínico"]
  P4 --> P5["Corrigir precipitantes (anemia, hipoxemia, hipotensão, taquicardia, dor) e revisar a prevenção cardiovascular secundária"]
  P5 --> D5{"O risco hemorrágico e o contexto cirúrgico permitem considerar intensificação antitrombótica?"}
  D5 -->|"Não"| C5(["Evitar intensificação antitrombótica automática; acompanhar clinicamente"])
  D5 -->|"Sim"| C6(["Individualizar a decisão de terapia antitrombótica (ex.: dabigatrana 110 mg 2x/dia, conforme o MANAGE), ponderando risco hemorrágico e mecanismo da lesão"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**O que o VISION mostrou sobre gravidade:** em 21.842 pacientes com hs-cTnT seriada, a mortalidade em 30 dias subiu de 0,5% (pico <20 ng/L) para 29,6% (pico ≥1000 ng/L) — a maioria dos casos classificados como MINS não teve nenhum sintoma isquêmico típico, o que justifica a vigilância seriada em vez de dosar troponina só diante de queixa.

**Em ambos os ramos finais (C5 e C6), planejar seguimento cardiovascular ambulatorial após a alta é considerado razoável pela AHA/ACC 2024** — independentemente de a decisão antitrombótica ter sido intensificar ou não.

**O MANAGE testou dabigatrana 110 mg 2x/dia em pacientes selecionados com MINS**, com redução do desfecho vascular composto sem sinal de aumento significativo de sangramento maior no ensaio — mas essa dose é a intervenção testada, não uma prescrição automática para qualquer troponina elevada; a decisão depende de hemostasia cirúrgica, função renal, risco hemorrágico e mecanismo provável da lesão.