---
title: "Fluxograma: FA persistente ou permanente — controle de frequência ou de ritmo?"
slug: fluxograma-fa-persistente-frequencia-vs-ritmo
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: PMIDs conferidos via PubMed E-utilities (ESC 2024 AF-CARE 39210723; AHA/ACC/ACCP/HRS 2023 38033089; EAST-AFNET 4 32865375; AFFIRM 12466506; CASTLE-AF 29385358); recorte não coberto pelos fluxogramas já publicados no acervo (o fluxograma AF-CARE ESC 2024 trata a etapa 'reduzir sintomas' apenas como decisão binária ablação-vs-resto, sem detalhar tempo de diagnóstico, EAST-AFNET 4, idade/fragilidade ou IC-FEr)."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS (AF-CARE). European Heart Journal. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723."
  - "Joglar JA, Chung MK, Armbruster AL, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. Circulation. 2024;149(1):e1-e156. DOI: 10.1161/CIR.0000000000001193. PMID: 38033089."
  - "Kirchhof P, Camm AJ, Goette A, et al; EAST-AFNET 4 Trial Investigators. Early Rhythm-Control Therapy in Patients with Atrial Fibrillation. New England Journal of Medicine. 2020;383(14):1305-1316. DOI: 10.1056/NEJMoa2019422. PMID: 32865375."
  - "Wyse DG, Waldo AL, DiMarco JP, et al; AFFIRM Investigators. A Comparison of Rate Control and Rhythm Control in Patients with Atrial Fibrillation. New England Journal of Medicine. 2002;347(23):1825-1833. DOI: 10.1056/NEJMoa021328. PMID: 12466506."
  - "Marrouche NF, Brachmann J, Andresen D, et al; CASTLE-AF Investigators. Catheter Ablation for Atrial Fibrillation with Heart Failure. New England Journal of Medicine. 2018;378(5):417-427. DOI: 10.1056/NEJMoa1707855. PMID: 29385358."
---

# Fluxograma: FA persistente ou permanente — controle de frequência ou de ritmo?

Na FA paroxística a discussão costuma ser resolvida cedo, a favor do ritmo. Na FA
**persistente ou permanente**, a escolha inicial entre controlar a frequência
ou tentar restaurar e manter o ritmo sinusal é mais disputada — e depende de
quando o diagnóstico foi feito, não apenas da duração do episódio atual. O
EAST-AFNET 4 mudou essa conversa ao mostrar benefício de eventos cardiovasculares
com controle de ritmo **precoce** (mediana de 36 dias desde o diagnóstico),
enquanto o AFFIRM — décadas antes, em FA já estabelecida — não encontrou
vantagem de sobrevida do ritmo sobre a frequência. As diretrizes ESC 2024
(AF-CARE) e AHA/ACC/ACCP/HRS 2023 convergem em individualizar por essa janela
temporal, associada a sintomas, idade/fragilidade e presença de IC-FEr.

## Árvore de decisão

```mermaid
flowchart TD
  R0["FA persistente ou permanente confirmada<br/>comorbidades e anticoagulação já endereçadas (AF-CARE, etapas C e A)"] --> D1{"Diagnóstico de FA feito há 1 ano ou menos E condição cardiovascular associada (IC, doença arterial coronariana, valvopatia ou múltiplos fatores de risco)?"}

  D1 -->|"Sim (janela do EAST-AFNET 4)"| D2{"FEVE ≤35% com IC sintomática (NYHA II-IV), cardiodesfibrilador implantado, refratária ou intolerante a antiarrítmico?"}
  D2 -->|"Sim"| C1(["Ablação por cateter como estratégia de ritmo<br/>CASTLE-AF: reduz morte ou hospitalização por IC (28,5% vs 44,6%; HR 0,62) e mortalidade por qualquer causa (HR 0,53) vs. terapia medicamentosa, nesta população específica de IC-FEr com desfibrilador"])

  D2 -->|"Não"| D3{"Idade avançada com múltiplas comorbidades limitando tolerância a antiarrítmico/ablação, ou preferência explícita do paciente por evitar terapia de ritmo?"}
  D3 -->|"Sim"| C2(["Controle de frequência como estratégia inicial, mesmo dentro da janela precoce<br/>individualizar por fragilidade (ESC 2024 AF-CARE, AHA/ACC/ACCP/HRS 2023); reavaliar se sintomas persistirem"])
  D3 -->|"Não"| C3(["Controle de ritmo precoce: antiarrítmico ou ablação por cateter<br/>EAST-AFNET 4: reduz desfecho composto de morte cardiovascular, AVC ou hospitalização por IC/SCA (3,9 vs 5,0 por 100 pacientes-ano; HR 0,79; p=0,005), sem diferença de sintomas ou função de VE em 2 anos"])

  D1 -->|"Não (FA de longa data, sem condição cardiovascular associada, ou diagnóstico há mais de 1 ano)"| D4{"Sintomas significativos (EHRA classe 2b ou maior) apesar de frequência ventricular controlada, ou preferência do paciente por tentar ritmo sinusal?"}

  D4 -->|"Sim"| D5{"Contraindicação relevante a antiarrítmico e/ou ablação (ex. átrio muito dilatado, alto risco de complicação, disfunção tireoidiana não corrigida)?"}
  D5 -->|"Sim"| C4(["Manter controle de frequência otimizado (betabloqueador, ou verapamil/diltiazem, ou digoxina)<br/>reavaliar contraindicação periodicamente na etapa E do AF-CARE"])
  D5 -->|"Não"| C5(["Controle de ritmo por sintomas (antiarrítmico ou ablação), fora da janela precoce<br/>objetivo é alívio sintomático — AFFIRM não mostrou ganho de sobrevida do ritmo sobre a frequência em FA já estabelecida, então a decisão aqui é guiada por sintoma e preferência, não por redução de eventos"])

  D4 -->|"Não (assintomático ou bem tolerado sob controle de frequência)"| C6(["Controle de frequência como estratégia definitiva<br/>AFFIRM: mortalidade em 5 anos de 21,3% com frequência vs. 23,8% com ritmo (HR 1,15; p=0,08), sem benefício de sobrevida do ritmo — não perseguir ritmo sinusal sem sintoma ou condição cardiovascular que o justifique"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Por que a janela temporal decide antes da idade ou do sintoma

O ponto que separa este fluxograma de uma simples lista "ritmo se sintomático,
frequência se não" é a ordem das perguntas. A primeira pergunta não é sobre
sintoma — é sobre **quando** a FA foi diagnosticada e se há uma condição
cardiovascular associada, porque é essa combinação que define a população do
EAST-AFNET 4 (diagnóstico mediano de 36 dias, critério de inclusão de até 1
ano). Dentro dessa janela, o controle de ritmo precoce reduz eventos
cardiovasculares — não apenas sintomas — e por isso a recomendação pesa a
favor do ritmo mesmo em paciente pouco sintomático, salvo fragilidade que
limite a terapia. Fora da janela, em FA já estabelecida, o benefício
observado no AFFIRM não existe, e a escolha volta a ser guiada por sintoma e
preferência — não por expectativa de reduzir morte ou AVC.

## IC-FEr é uma bifurcação à parte, não um sintoma a mais

A presença de IC com fração de ejeção reduzida e desfibrilador implantado, na
população do CASTLE-AF, isola um subgrupo em que a ablação por cateter reduz
mortalidade por qualquer causa e hospitalização por IC de forma mais robusta
do que o observado no EAST-AFNET 4 em população mais ampla. Por isso esse
subgrupo aparece como pergunta separada, antes da avaliação de idade e
fragilidade — a indicação de ritmo por ablação nesse contexto não depende da
mesma ponderação de risco-benefício aplicada ao restante da árvore.

## O que este fluxograma não substitui

A escolha entre controle de frequência e de ritmo pressupõe que as etapas C
(comorbidades) e A (anticoagulação) do AF-CARE já foram endereçadas — este
fluxograma cobre apenas a etapa R (reduzir sintomas), e não repete os critérios
de anticoagulação por CHA2DS2-VA nem a técnica de ablação, já detalhados nos
fluxogramas "Fibrilação Atrial — trajetória AF-CARE (ESC 2024)" e "Indicação de
ablação por cateter na FA (ESC 2024)" deste acervo.
