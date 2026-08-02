---
title: "Fluxograma: Emergência hipertensiva — diferenciação de urgência e conduta por síndrome-alvo"
slug: fluxograma-emergencia-hipertensiva
theme: "Hipertensão"
kind: fluxograma
summary: "Separa emergência hipertensiva (lesão aguda de órgão-alvo) de urgência hipertensiva (PA alta sem lesão aguda, conduta ambulatorial), e dentro da emergência ramifica o fármaco IV e a velocidade de redução da PA por síndrome-alvo: dissecção de aorta, AVC isquêmico, AVC hemorrágico, edema agudo de pulmão, eclâmpsia e crise por catecolaminas."
review_status: revisado
source_refs: ["Hypertensive Emergency · StatPearls (NCBI Bookshelf) · https://www.ncbi.nlm.nih.gov/books/NBK470371/", "CLUE: a randomized comparative effectiveness trial of IV nicardipine versus labetalol use in the emergency department · PMC · https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3219031/", "2022 ACC/AHA/AATS/ACR/ASA/SCA/SCAI/SIR/STS/SVM Guideline for the Diagnosis and Management of Aortic Disease · resumo Ten Points to Remember · American College of Cardiology · https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2022/11/01/12/21/2022-guideline-on-aortic-disease-2-gl-ad", "Powers WJ, et al. Guidelines for the Early Management of Patients With Acute Ischemic Stroke: 2019 Update to the 2018 Guidelines · Stroke · 2019 · 50:e344-e418 · doi: 10.1161/STR.0000000000000211", "2022 Guideline for the Management of Patients With Spontaneous Intracerebral Hemorrhage · American Heart Association/American Stroke Association · Stroke · 2022 · doi: 10.1161/STR.0000000000000407", "Tratamento da pré-eclâmpsia baseado em evidências · Revista Brasileira de Ginecologia e Obstetrícia (RBGO) · SciELO · https://www.scielo.br/j/rbgo/a/fNqBksfSmYfTHmTmLTnf3RJ/", "Treatment of hypertensive emergencies · PMC · https://pmc.ncbi.nlm.nih.gov/articles/PMC5440310/", "Sodium nitroprusside for control of severe hypertensive disease of pregnancy: a case report and discussion of potential toxicity · American Journal of Obstetrics and Gynecology · https://www.ajog.org/article/0002-9378(84)90192-3/fulltext"]
---

# Fluxograma: Emergência hipertensiva

Emergência e urgência hipertensiva não se distinguem pelo valor da pressão, e
sim pela presença de **lesão aguda de órgão-alvo**. Uma vez confirmada a
emergência, a escolha do anti-hipertensivo IV e a velocidade de redução da PA
mudam conforme a síndrome — a dissecção de aorta exige queda rápida e
agressiva de PA e FC, enquanto o AVC isquêmico tolera pressão bem mais alta
por mais tempo. Este documento complementa o protocolo geral de emergência
hipertensiva já publicado nesta biblioteca, detalhando essa bifurcação inicial
e o recorte por síndrome-alvo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente com pressão arterial muito elevada<br/>PAS ≥180 e/ou PAD ≥120 mmHg"]
  R0 --> P1["Avaliar sintomas, exame físico e exames<br/>dirigidos a lesão aguda de órgão-alvo"]

  P1 --> D1{"Há lesão aguda de órgão-alvo?<br/>(AVC, dissecção de aorta, EAP,<br/>encefalopatia, eclâmpsia, SCA etc.)"}

  D1 -->|"Não — só PA elevada"| C1(["Urgência hipertensiva, não é emergência:<br/>reduzir a PA por via oral, de forma gradual,<br/>em ambulatório ou observação breve —<br/>sem anti-hipertensivo IV"])

  D1 -->|"Sim — lesão aguda presente"| D2{"Qual síndrome-alvo predomina?"}

  D2 -->|"Dissecção aguda de aorta"| D3{"Betabloqueador IV<br/>contraindicado?"}

  D3 -->|"Não"| C2(["Betabloqueador IV primeiro (esmolol,<br/>metoprolol ou labetalol); associar<br/>vasodilatador IV (nicardipina, clevidipina<br/>ou nitroprussiato) se a PA persistir alta;<br/>meta PAS ~100-120 mmHg (ou a menor PA<br/>que mantenha perfusão de órgãos) e<br/>FC <60-80 bpm, em minutos"])

  D3 -->|"Sim"| C3(["Bloqueador de canal de cálcio não-<br/>diidropiridínico IV (diltiazem ou<br/>verapamil) para controle de FC, associando<br/>vasodilatador IV; mesma meta de<br/>PAS ~100-120 mmHg e FC <60-80 bpm"])

  D2 -->|"AVC isquêmico agudo"| D4{"Candidato a trombólise IV (rtPA)?"}

  D4 -->|"Sim"| C4(["Reduzir e manter PA <185/110 mmHg<br/>antes do trombolítico, e <180/105 mmHg<br/>nas 24 horas seguintes (labetalol<br/>ou nicardipina IV)"])

  D4 -->|"Não"| C5(["Hipertensão permissiva: tratar só se<br/>PA ≥220/120 mmHg ou houver comorbidade<br/>que exija meta menor (ex. dissecção de<br/>aorta, IAM, EAP); reduzir com cautela<br/>nas primeiras 24 horas"])

  D2 -->|"AVC hemorrágico<br/>(hemorragia intracerebral)"| D5{"PAS entre 150 e 220 mmHg,<br/>quadro leve a moderado e<br/>sem contraindicação?"}

  D5 -->|"Sim"| C6(["Reduzir a PAS para a faixa de<br/>130-140 mmHg — reduzir abaixo de<br/>130 mmHg é potencialmente prejudicial"])

  D5 -->|"Não"| C7(["VERIFICAÇÃO HUMANA NECESSÁRIA — meta<br/>pressórica fora da faixa validada<br/>(PAS >220 mmHg, quadro grave ou<br/>contraindicação); individualizar"])

  D2 -->|"Edema agudo de pulmão"| C8(["Nitroglicerina, nitroprussiato ou<br/>clevidipina IV; não usar betabloqueador<br/>(piora a função de bomba); reduzir 20-25%<br/>na primeira hora, depois gradualmente<br/>até 160/100 mmHg em 2-6 horas"])

  D2 -->|"Eclâmpsia ou<br/>pré-eclâmpsia grave"| C9(["Sulfato de magnésio IV em todos os<br/>casos (profilaxia/tratamento de<br/>convulsão), junto com hidralazina IV,<br/>labetalol IV ou nifedipina VO/SL para a<br/>crise pressórica; meta PAS 140-155 e<br/>PAD 90-105 mmHg; evitar nitroprussiato<br/>salvo sem alternativa (risco de<br/>cianeto fetal)"])

  D2 -->|"Crise por excesso de<br/>catecolaminas (feocromocitoma,<br/>cocaína, IMAO)"| C10(["Evitar betabloqueador isolado (bloqueio<br/>alfa desacompanhado agrava a hipertensão);<br/>usar fentolamina (bolus IV de 5 mg,<br/>repetido a cada 10 min conforme<br/>necessário), nicardipina ou clevidipina"])

  D2 -->|"Encefalopatia hipertensiva ou outra<br/>lesão aguda sem protocolo específico acima"| C11(["Reduzir a PA média em 20-25% na<br/>primeira 1-2 horas; depois gradualmente<br/>para 160/100-110 mmHg em 2-6 horas, e<br/><140/90 mmHg em 24-48 horas, com<br/>agente IV de ação rápida e fácil<br/>titulação (labetalol, nicardipina,<br/>esmolol, nitroprussiato, clevidipina<br/>ou outros)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11 conduta;
```

## O que vale para todo ramo de emergência, e por isso não está na árvore

**Ambiente monitorado**, com aferição frequente da PA — idealmente por
cateter arterial invasivo quando a infusão IV é titulada continuamente — e
reavaliação constante da dose. A característica que une os agentes eficazes
não é a droga específica, e sim ação rápida e fácil titulação.

**Fora da dissecção de aorta, não é necessário — nem desejável — normalizar a
pressão com urgência.** Reduções mais agressivas do que a meta de cada
síndrome arriscam hipoperfusão, sobretudo em quem tem hipertensão crônica e a
autorregulação de órgão deslocada para pressões mais altas.

**Investigar e tratar a causa desencadeante em paralelo**, quando houver uma:
suspender estimulante simpaticomimético na crise por catecolaminas, tratar a
convulsão associada na eclâmpsia, buscar a etiologia da lesão de órgão-alvo
antes de dar alta da fase aguda.

## Metas e fármacos por síndrome, em resumo

| Síndrome-alvo | Meta de PA/FC | Fármaco(s) de escolha | Evitar |
|---|---|---|---|
| Dissecção aguda de aorta | PAS ~100-120 mmHg e FC <60-80 bpm, em minutos | Betabloqueador IV primeiro; vasodilatador IV associado | Vasodilatador isolado antes do controle de FC (taquicardia reflexa propaga a dissecção) |
| AVC isquêmico, candidato a trombólise | PA <185/110 mmHg antes do rtPA; <180/105 mmHg nas 24h seguintes | Labetalol ou nicardipina IV | — |
| AVC isquêmico, sem trombólise | Permissiva até 220/120 mmHg nas primeiras 24h | Tratar só acima do limiar, ou se houver comorbidade que exija menos | Redução agressiva precoce |
| AVC hemorrágico, PAS 150-220 mmHg, leve-moderado | PAS 130-140 mmHg | — | Reduzir <130 mmHg (potencialmente prejudicial) |
| Edema agudo de pulmão | 20-25% na 1ª hora; depois 160/100 mmHg em 2-6h | Nitroglicerina, nitroprussiato ou clevidipina IV | Betabloqueador (piora a função de bomba) |
| Eclâmpsia / pré-eclâmpsia grave | PAS 140-155 mmHg, PAD 90-105 mmHg | Hidralazina IV, labetalol IV ou nifedipina VO/SL; sulfato de magnésio para convulsão | Nitroprussiato, salvo sem alternativa (risco de cianeto fetal) |
| Crise por catecolaminas | — | Fentolamina (bolus 5 mg IV a cada 10 min), nicardipina ou clevidipina | Betabloqueador isolado (bloqueio alfa desacompanhado) |
