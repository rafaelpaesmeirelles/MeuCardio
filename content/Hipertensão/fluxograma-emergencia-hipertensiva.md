---
title: "Fluxograma: Emergência hipertensiva — diferenciação de urgência e conduta por síndrome-alvo"
slug: fluxograma-emergencia-hipertensiva
theme: "Hipertensão"
kind: fluxograma
summary: "Separa emergência hipertensiva (lesão aguda de órgão-alvo) de urgência hipertensiva (PA alta sem lesão aguda, conduta ambulatorial), e dentro da emergência ramifica o fármaco IV e a velocidade de redução da PA por síndrome-alvo: dissecção de aorta, AVC isquêmico, AVC hemorrágico, edema agudo de pulmão, eclâmpsia e crise por catecolaminas."
review_status: revisado
source_refs: ["Jones DW, Ferdinand KC, Taler SJ, et al. 2025 AHA/ACC Multisociety Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults. J Am Coll Cardiol. 2025;86(18):1567-1678. DOI: 10.1016/j.jacc.2025.05.007. PMID: 40815242 — diretriz vigente para definição e manejo geral da hipertensão no adulto", "van den Born BJM, Lip GYH, Brguljan-Hitij J, et al. ESC Council on hypertension position document on the management of hypertensive emergencies. Eur Heart J Cardiovasc Pharmacother. 2019;5(1):37-46. DOI: 10.1093/ehjcvp/pvy032. PMID: 30165588 — metas e fármacos IV por lesão de órgão-alvo; corrigendum de doses: DOI 10.1093/ehjcvp/pvy040, PMID 30339228", "Isselbacher EM, Preventza O, Black JH 3rd, et al. 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease. Circulation. 2022;146(24):e334-e482. DOI: 10.1161/CIR.0000000000001106. PMID: 36322642 — síndrome aórtica aguda: PAS abaixo de 120 mmHg ou menor valor que preserve perfusão, FC 60-80 bpm e beta-bloqueador IV antes de vasodilatador", "Powers WJ, Rabinstein AA, Ackerson T, et al. Guidelines for the Early Management of Patients With Acute Ischemic Stroke: 2019 Update. Stroke. 2019;50(12):e344-e418. DOI: 10.1161/STR.0000000000000211. PMID: 31662037 — limiares pressóricos para trombólise e hipertensão permissiva", "Greenberg SM, Ziai WC, Cordonnier C, et al. 2022 Guideline for the Management of Patients With Spontaneous Intracerebral Hemorrhage. Stroke. 2022;53(7):e282-e361. DOI: 10.1161/STR.0000000000000407. PMID: 35579034 — alvo 140 mmHg com manutenção em 130-150 para HIC leve/moderada e PAS 150-220; incerteza em apresentações graves", "ACOG Committee Opinion No. 767: Emergent Therapy for Acute-Onset, Severe Hypertension During Pregnancy and the Postpartum Period. Obstet Gynecol. 2019;133(2):e174-e180. DOI: 10.1097/AOG.0000000000003075. PMID: 30575639 — tratar em 30-60 minutos com labetalol IV, hidralazina IV ou nifedipina oral de liberação imediata"]
review_note: "Revisão de 26/08/2026: removido o marcador humano do ramo de hemorragia intracerebral por explicitar que não há meta universal validada fora do cenário leve/moderado com PAS 150-220 mmHg. Corrigidos: alvo da HIC para 140 com manutenção 130-150; nifedipina obstétrica de liberação imediata por via oral, nunca sublingual; frase invertida sobre bloqueio beta/alfa na crise catecolaminérgica; fentolamina sem dose copiada de fonte secundária; e limiar inicial, que não deve excluir emergência por elevação aguda abaixo de 180/120 quando há lesão de órgão-alvo."
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
  R0["Pressão muito elevada ou aumento abrupto<br/>associado a sintomas/sinais de alarme;<br/>não exigir corte fixo antes de buscar lesão"]
  R0 --> P1["Avaliar sintomas, exame físico e exames<br/>dirigidos a lesão aguda de órgão-alvo"]

  P1 --> D1{"Há lesão aguda de órgão-alvo?<br/>(AVC, dissecção de aorta, EAP,<br/>encefalopatia, eclâmpsia, SCA etc.)"}

  D1 -->|"Não — só PA elevada"| C1(["Urgência hipertensiva, não é emergência:<br/>reduzir a PA por via oral, de forma gradual,<br/>em ambulatório ou observação breve —<br/>sem anti-hipertensivo IV"])

  D1 -->|"Sim — lesão aguda presente"| D2{"Qual síndrome-alvo predomina?"}

  D2 -->|"Dissecção aguda de aorta"| D3{"Betabloqueador IV<br/>contraindicado?"}

  D3 -->|"Não"| C2(["Betabloqueador IV primeiro (esmolol,<br/>metoprolol ou labetalol); associar<br/>vasodilatador IV (nicardipina, clevidipina<br/>ou nitroprussiato) se a PA persistir alta;<br/>meta PAS <120 mmHg (ou a menor PA<br/>que mantenha perfusão de órgãos) e<br/>FC 60-80 bpm, em minutos"])

  D3 -->|"Sim"| C3(["Bloqueador de canal de cálcio não-<br/>diidropiridínico IV (diltiazem ou<br/>verapamil) para controle de FC, associando<br/>vasodilatador IV; mesma meta de<br/>PAS <120 mmHg e FC 60-80 bpm"])

  D2 -->|"AVC isquêmico agudo"| D4{"Candidato a trombólise IV (rtPA)?"}

  D4 -->|"Sim"| C4(["Reduzir e manter PA <185/110 mmHg<br/>antes do trombolítico, e <180/105 mmHg<br/>nas 24 horas seguintes (labetalol<br/>ou nicardipina IV)"])

  D4 -->|"Não"| C5(["Hipertensão permissiva: tratar só se<br/>PA ≥220/120 mmHg ou houver comorbidade<br/>que exija meta menor (ex. dissecção de<br/>aorta, IAM, EAP); reduzir com cautela<br/>nas primeiras 24 horas"])

  D2 -->|"AVC hemorrágico<br/>(hemorragia intracerebral)"| D5{"PAS entre 150 e 220 mmHg,<br/>quadro leve a moderado e<br/>sem contraindicação?"}

  D5 -->|"Sim"| C6(["Iniciar redução com alvo de PAS 140 mmHg<br/>e manutenção suave na faixa 130-150;<br/>reduzir abaixo de 130 mmHg<br/>é potencialmente prejudicial"])

  D5 -->|"Não"| C7(["HIC grave, grande, com necessidade cirúrgica<br/>ou fora da faixa estudada: benefício e segurança<br/>da redução intensiva não estão estabelecidos;<br/>individualizar com neurologia/neurocirurgia,<br/>evitando picos e grandes oscilações"])

  D2 -->|"Edema agudo de pulmão"| C8(["Nitroglicerina ou nitroprussiato IV<br/>associado a diurético de alça e suporte<br/>ventilatório conforme congestão;<br/>meta imediata de PAS <140 mmHg;<br/>não iniciar/aumentar betabloqueador<br/>durante descompensação instável"])

  D2 -->|"Gestação/puerpério com PA<br/>persistente ≥160/110 mmHg"| C9(["Tratar em 30-60 min: labetalol IV,<br/>hidralazina IV ou nifedipina oral de<br/>liberação imediata se acesso IV indisponível;<br/>reduzir para PAS <160 e PAD <110 mmHg;<br/>magnésio conforme protocolo obstétrico<br/>para profilaxia/tratamento de convulsão"])

  D2 -->|"Excesso de catecolaminas<br/>(PPGL ou intoxicação estimulante)"| C10(["Nunca iniciar betabloqueador antes de<br/>alfa-bloqueio no PPGL; usar fentolamina<br/>ou vasodilatador IV titulável e seguir<br/>o fluxo específico. Em cocaína/metanfetamina<br/>com intoxicação aguda: benzodiazepínico<br/>primeiro; vasodilatador se necessário"])

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
| Dissecção aguda de aorta | PAS <120 mmHg ou menor valor que preserve perfusão; FC 60-80 bpm | Betabloqueador IV primeiro; vasodilatador IV associado | Vasodilatador isolado antes do controle de FC (taquicardia reflexa propaga a dissecção) |
| AVC isquêmico, candidato a trombólise | PA <185/110 mmHg antes do rtPA; <180/105 mmHg nas 24h seguintes | Labetalol ou nicardipina IV | — |
| AVC isquêmico, sem trombólise | Permissiva até 220/120 mmHg nas primeiras 24h | Tratar só acima do limiar, ou se houver comorbidade que exija menos | Redução agressiva precoce |
| Hemorragia intracerebral, PAS 150-220 mmHg, leve-moderada | Alvo 140 mmHg; manter 130-150 mmHg | Agente IV titulável, com controle suave e sustentado | Reduzir <130 mmHg; aplicar esse alvo automaticamente à HIC grave |
| Edema agudo de pulmão hipertensivo | PAS <140 mmHg, com reavaliação imediata de perfusão | Nitroglicerina ou nitroprussiato IV, diurético de alça e suporte ventilatório conforme fenótipo | Iniciar ou aumentar betabloqueador na descompensação instável |
| Gestação/puerpério com PA persistente ≥160/110 mmHg | PAS <160 e PAD <110 mmHg em 30-60 min | Hidralazina IV, labetalol IV ou nifedipina oral de liberação imediata; magnésio conforme indicação obstétrica | Nifedipina sublingual |
| Crise por PPGL | Individualizada por órgão-alvo e transição possível para choque | Fentolamina ou vasodilatador IV titulável; ver fluxo dedicado | Betabloqueador antes de alfa-bloqueio |
| Intoxicação aguda por cocaína/metanfetamina | Individualizada por órgão-alvo | Benzodiazepínico primeiro; associar vasodilatador se necessário | Betabloqueador quando há sinais de intoxicação aguda sem vasodilatador coronariano |

## Limites

- O número da pressão não define sozinho uma emergência. Dissecção aórtica,
  eclâmpsia e outras lesões agudas podem exigir tratamento abaixo de 180/120
  mmHg; já pressão acima desse valor sem lesão aguda não autoriza queda IV
  rápida.
- A meta de hemorragia intracerebral vale para apresentação **leve a moderada**
  com PAS inicial entre 150 e 220 mmHg. Na HIC grave, grande, cirúrgica ou com
  PAS fora dessa faixa, a diretriz não estabelece benefício da mesma estratégia
  intensiva; priorizam-se controle suave, perfusão e decisão neurocrítica.
- “Catecolaminas” não é um protocolo único. PPGL e intoxicação estimulante
  compartilham riscos, mas diferem no tratamento inicial; por isso aparecem em
  linhas e fluxos separados.

## Tudo com Tudo

- [Emergência hipertensiva e triagem de hipertensão secundária](emergencia-hipertensiva-e-triagem-de-hipertensao-secundaria.md)
- [Crise hipertensiva por feocromocitoma/paraganglioma](fluxograma-crise-hipertensiva-adrenergica-do-feocromocitoma.md)
- [Diretriz ACC/AHA 2025 de hipertensão no adulto](acc-aha-2025-diretriz-hipertensao-arterial-adultos.md)
- [Nitroprussiato: limites e toxicidade](nitroprussiato-na-emergencia-hipertensiva-tetos-e-toxicidade-pela-bula-brasileira.md)
- [Fluxograma de dor torácica e SCA por cocaína](../Saúde_mental_e_cardiologia/fluxograma-dor-toracica-aguda-com-uso-recente-confirmado-ou-suspeito-de-cocaina.md)
