---
title: "Fluxograma: Sequenciamento e Titulação da Terapia Quádrupla na ICFEr"
slug: fluxograma-sequenciamento-titulacao-terapia-quadrupla-icfer
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Nenhum PMID/DOI novo foi introduzido nesta sessão. Todas as referências reutilizadas já estavam publicadas e verificadas nesta mesma pasta: CONSENSUS PMID 2883575, PARADIGM-HF PMID 25176015, DAPA-HF PMID 31535829, EMPEROR-Reduced PMID 32865377, RALES PMID 10471456, EMPHASIS-HF PMID 21073363, STRONG-HF PMID 36356631, DIAMOND PMID 35900838 e Atualização Focada 2023 da ESC PMID 37622666. O STRONG-HF testou titulação rápida de IECA/BRA/ARNI, betabloqueador e antagonista mineralocorticoide após internação por IC; iSGLT2 não era obrigatório no protocolo. Portanto, ele sustenta acompanhamento intensivo pós-alta, não uma exigência de iniciar simultaneamente os quatro pilares nem um intervalo universal para dobrar doses. A lógica de sequenciamento por barreira de segurança permanece qualitativa e individualizada."
source_refs: ["CONSENSUS Trial Study Group. Effects of enalapril on mortality in severe congestive heart failure (CONSENSUS). N Engl J Med. 1987;316(23):1429-1435. DOI: 10.1056/NEJM198706043162301. PMID: 2883575", "McMurray JJ, Packer M, Desai AS, et al; PARADIGM-HF Investigators and Committees. Angiotensin-neprilysin inhibition versus enalapril in heart failure. N Engl J Med. 2014;371(11):993-1004. DOI: 10.1056/NEJMoa1409077. PMID: 25176015", "McMurray JJV, Solomon SD, Inzucchi SE, et al; DAPA-HF Trial Committees and Investigators. Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction. N Engl J Med. 2019;381(21):1995-2008. DOI: 10.1056/NEJMoa1911303. PMID: 31535829", "Packer M, Anker SD, Butler J, et al; EMPEROR-Reduced Trial Investigators. Cardiovascular and Renal Outcomes with Empagliflozin in Heart Failure. N Engl J Med. 2020;383(15):1413-1424. DOI: 10.1056/NEJMoa2022190. PMID: 32865377", "Pitt B, Zannad F, Remme WJ, et al; RALES Investigators. The effect of spironolactone on morbidity and mortality in patients with severe heart failure. N Engl J Med. 1999;341(10):709-717. DOI: 10.1056/NEJM199909023411001. PMID: 10471456", "Zannad F, McMurray JJ, Krum H, et al; EMPHASIS-HF Study Group. Eplerenone in patients with systolic heart failure and mild symptoms. N Engl J Med. 2011;364(1):11-21. DOI: 10.1056/NEJMoa1009492. PMID: 21073363", "Mebazaa A, Davison B, Chioncel O, et al. Safety, tolerability and efficacy of up-titration of guideline-directed medical therapies for acute heart failure (STRONG-HF): a multinational, open-label, randomised trial. Lancet. 2022;400(10367):1938-1952. DOI: 10.1016/S0140-6736(22)02076-1. PMID: 36356631", "Butler J, Anker SD, Lund LH, et al. Patiromer for the management of hyperkalemia in heart failure with reduced ejection fraction: the DIAMOND trial. Eur Heart J. 2022;43(41):4362-4373. DOI: 10.1093/eurheartj/ehac401. PMID: 35900838", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666"]
---

# Fluxograma: Sequenciamento e Titulação da Terapia Quádrupla na ICFEr

A diretriz atual não exige uma ordem fixa de introdução dos quatro pilares da
ICFEr (bloqueio do SRAA, betabloqueador, antagonista mineralocorticoide e
inibidor de SGLT2). A atualização focada 2023 da ESC recomenda estratégia
intensiva de início e rápida titulação da terapia baseada em evidências antes
da alta e nas primeiras seis semanas após internação por IC; o STRONG-HF não
incluiu iSGLT2 como componente obrigatório. Mas
quando o paciente tem uma barreira de segurança já visível na primeira
consulta — pressão arterial limítrofe, frequência cardíaca ou condução
limítrofes, função renal ou potássio limítrofes —, a ordem de introdução deixa
de ser indiferente: cada pilar tem um perfil de efeito adverso diferente, e
usar isso para decidir qual entra primeiro reduz a chance de suspender uma
classe por intolerância evitável.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Diagnóstico confirmado de ICFEr<br/>(FEVE ≤ 40%): indicação de iniciar<br/>a terapia quádrupla"]
  D1{"Paciente hemodinamicamente instável<br/>agora (congestão não tratada,<br/>hipotensão sintomática, hipercalemia,<br/>injúria renal aguda)?"}
  C1(["Estabilizar a intercorrência aguda<br/>primeiro — tratar a congestão, corrigir<br/>potássio e função renal; iniciar os<br/>quatro pilares assim que estabilizado,<br/>retomando esta mesma árvore de decisão"])
  D2{"Há barreira específica que limita<br/>iniciar as quatro classes ao mesmo<br/>tempo — PA limítrofe, FC/condução<br/>limítrofes, ou TFGe/potássio<br/>limítrofes?"}
  P1["Introduzir prontamente os quatro<br/>pilares, em sequência individualizada<br/>ou concomitante quando seguro — iSGLT2<br/>não exige titulação; iniciar as demais<br/>classes em doses toleráveis"]
  C2(["Sequenciar por segurança: iniciar<br/>primeiro iSGLT2 e antagonista<br/>mineralocorticoide (menor efeito<br/>hipotensor imediato); introduzir<br/>IECA/ARNI e betabloqueador em dose<br/>mínima, com intervalo maior entre as<br/>introduções — ver fluxograma dedicado<br/>de hipotensão sintomática"])
  C3(["Sequenciar por segurança: iniciar<br/>iSGLT2, antagonista mineralocorticoide<br/>e IECA/ARNI primeiro; betabloqueador em<br/>dose mínima com monitorização de FC e<br/>ECG, avaliando necessidade de<br/>marca-passo antes de escalar a dose"])
  C4(["Sequenciar por segurança: iniciar<br/>iSGLT2 e betabloqueador primeiro (menor<br/>impacto renal/potássio imediato);<br/>IECA/ARNI e antagonista<br/>mineralocorticoide em dose mínima, com<br/>controle de potássio e TFGe em 1 a 2<br/>semanas antes de qualquer titulação"])
  D3{"Na reavaliação precoce após cada<br/>mudança: PA, FC, potássio e TFGe<br/>toleraram a dose atual?"}
  C5(["Titular uma ou mais classes conforme<br/>tolerância até doses-alvo ou máximas<br/>toleradas; individualizar intervalo e<br/>incremento, com monitorização clínica e<br/>laboratorial apropriada"])
  D4{"Qual parâmetro limitou a titulação?"}
  C6(["Hipotensão sintomática: seguir o<br/>fluxograma dedicado de manejo da<br/>hipotensão limitando titulação de<br/>IECA/ARNI"])
  C7(["Hipercalemia: considerar quelante de<br/>potássio antes de reduzir a dose do<br/>bloqueador do SRAA ou do antagonista<br/>mineralocorticoide (DIAMOND)"])
  C8(["Bradicardia ou distúrbio de condução:<br/>reduzir a dose do betabloqueador e<br/>priorizar a titulação dos demais<br/>pilares"])
  C9(["Piora renal isolada, leve a moderada:<br/>manter a dose atual — não suspender por<br/>elevação isolada e leve de creatinina —<br/>e reavaliar em 1 a 2 semanas"])

  R0 --> D1
  D1 -->|"Sim"| C1
  D1 -->|"Não"| D2
  D2 -->|"Não, sem barreira relevante"| P1
  D2 -->|"PA limítrofe / hipotensão"| C2
  D2 -->|"FC/condução limítrofes"| C3
  D2 -->|"TFGe ou potássio limítrofes"| C4
  P1 --> D3
  C2 --> D3
  C3 --> D3
  C4 --> D3
  D3 -->|"Sim, toleraram"| C5
  D3 -->|"Não, algum parâmetro limitou"| D4
  D4 -->|"Hipotensão sintomática"| C6
  D4 -->|"Hipercalemia"| C7
  D4 -->|"Bradicardia/distúrbio de condução"| C8
  D4 -->|"Piora renal isolada, leve/moderada"| C9

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## O que a árvore não mostra

**Não há corte numérico validado** de PA, FC ou TFGe que defina "limítrofe" —
a decisão é clínica, apoiada no julgamento do médico à beira do leito, não em
um escore. Onde a evidência já define um número (ex. dose inicial do enalapril
reduzida para 2,5 mg em paciente de alto risco, no CONSENSUS), isso está
registrado nos documentos de origem citados, não repetido aqui.

**Doses exatas e esquemas de titulação por fármaco** não são o objeto deste
fluxograma — consulte os documentos de cada pilar nesta pasta
(`inibicao-do-sraa-na-icfer-consensus-solvd-e-paradigm-hf.md`,
`betabloqueadores-na-icfer-a-base-de-evidencia-cibis-ii-merit-hf-e-copernicus.md`,
`antagonistas-mineralocorticoides-na-icfer-rales-e-emphasis-hf.md`,
`inibidores-de-sglt2-na-icfer-dapa-hf-e-emperor-reduced.md`).

**Interações entre barreiras simultâneas** (ex. paciente com PA limítrofe *e*
potássio limítrofe ao mesmo tempo) não são resolvidas por esta árvore — o
diagrama trata cada barreira isoladamente; a combinação exige julgamento
clínico individualizado, tipicamente priorizando a barreira de maior risco
imediato.

**Reavaliação contínua fora dos pontos marcados na árvore** — sinais de
descompensação, nova intercorrência aguda ou mudança de outro fármaco
concomitante reabrem o processo de decisão a qualquer momento, não apenas nas
consultas de 1-2 semanas representadas no diagrama.
