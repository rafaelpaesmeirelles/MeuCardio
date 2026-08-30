---
title: "Fluxograma: retirar o AAS aos 3 meses e manter ticagrelor — a via TWILIGHT"
slug: fluxograma-twilight-aspirina-drop-aos-3-meses
theme: "Doença coronariana"
kind: fluxograma
summary: "Árvore operacional da via TWILIGHT: só entra quem completou 3 meses de DAPT com ticagrelor sem evento maior; distingue o corte de 1 mês (ULTIMATE-DAPT/TARGET-FIRST), a retirada hospitalar (NEO-MINDSET, não usar) e a monoterapia crônica clopidogrel versus AAS (HOST-EXAM/SMART-CHOICE 3)."
review_status: revisado
fonte_producao: grok
review_note: "Produção científica contínua em 29/08/2026. Árvore ancorada no abstract do TWILIGHT (PMID 31556978, efetch PubMed nesta revisão editorial) e nos documentos da casa ULTIMATE-DAPT, NEO-MINDSET, TARGET-FIRST, MASTER-DAPT e fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp. Não reproduz classes ESC 2023 de duração de DAPT (tabela não relida nesta revisão editorial). A via de FA + anticoagulante está explicitamente fora. Revisão científica concluída em 30/08/2026."
source_refs:
  - "Mehran R, et al. Ticagrelor with or without Aspirin in High-Risk Patients after PCI (TWILIGHT). N Engl J Med. 2019;381(21):2032-2042. DOI: 10.1056/NEJMoa1908419. PMID: 31556978. NCT02270242."
  - "Documento da casa fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp — árvore genérica ESC 2023; esta árvore isola o ramo ticagrelor-monoterapia aos 3 meses, que aquela não nomeia."
  - "Documentos da casa: ultimate-dapt-ticagrelor-monoterapia-apos-1-mes-acs-pci; neo-mindset-retirada-precoce-aspirina-apos-pci-sca; target-first-monoterapia-p2y12-apos-revascularizacao-completa-no-iam-baixo-risco; master-dapt-dapt-abreviada-em-alto-risco-hemorragico; host-exam-clopidogrel-versus-aspirina-monoterapia-manutencao-pos-pci."
---

# Fluxograma: retirar o AAS aos 3 meses e manter ticagrelor — a via TWILIGHT

O fluxograma genérico de duração da DAPT da casa organiza SCA versus eletivo e risco hemorrágico. Ele **não nomeia** a estratégia de **tirar o AAS e manter ticagrelor potente**. Esta árvore isola essa via e diz **quando não usá-la**.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em DAPT com ticagrelor + AAS<br/>após PCI"] --> D1{"Anticoagulação oral concomitante<br/>(FA, válvula, TVP/TEP)?"}

  D1 -->|"Sim"| C0(["Sai desta árvore.<br/>Via de terapia tripla/dupla com DOAC"])

  D1 -->|"Não"| D2{"Ainda internado ou com menos de 1 mês<br/>após a PCI?"}

  D2 -->|"Sim"| C1(["Não tirar o AAS agora.<br/>NEO-MINDSET: não inferioridade isquêmica<br/>não demonstrada na retirada hospitalar"])

  D2 -->|"Não"| D3{"Completou 1 mês sem evento,<br/>é SCA/IAM de baixo risco e a pergunta<br/>é cortar já no 1º mês?"}

  D3 -->|"Sim — SCA estável no 1º mês"| C2(["Via ULTIMATE-DAPT / TARGET-FIRST:<br/>considerar ticagrelor ou P2Y12 isolado<br/>a partir do 1º mês — documentos próprios"])

  D3 -->|"Não — alto risco, ou a pergunta é aos 3 meses"| D4{"Completou 3 meses de DAPT com ticagrelor<br/>SEM sangramento maior e SEM evento isquêmico?"}

  D4 -->|"Não — sangrou ou reinfartou no trimestre"| C3(["Não é população TWILIGHT.<br/>Reavaliar DAPT, causa do evento e risco"])

  D4 -->|"Sim"| D5{"Alto risco isquêmico OU hemorrágico<br/>no sentido do TWILIGHT,<br/>e o P2Y12 atual é ticagrelor?"}

  D5 -->|"Não — P2Y12 é clopidogrel/prasugrel,<br/>ou risco não se enquadra"| C4(["Não extrapolar o TWILIGHT.<br/>Voltar ao fluxograma genérico de DAPT"])

  D5 -->|"Sim"| C5(["Suspender o AAS e manter ticagrelor<br/>em monoterapia até ~15 meses da PCI.<br/>TWILIGHT: BARC 2/3/5 4,0% vs 7,1%;<br/>morte/IAM/AVC 3,9% vs 3,9%"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**MASTER-DAPT encurta a DAPT por alto risco hemorrágico e depois deixa um antiplaquetário só — não necessariamente ticagrelor.** É outra pergunta.

**HOST-EXAM e SMART-CHOICE 3 comparam clopidogrel versus AAS na manutenção crônica, depois que a DAPT já acabou.** Entrar nessa comparação só depois dos 6–18 meses (HOST-EXAM) ou da DAPT padrão (SMART-CHOICE 3). Não misturar com o trimestre do TWILIGHT.

**Desescalonar ticagrelor para clopidogrel e manter DAPT** é o ramo C5 do fluxograma genérico, não esta via.

## Mensagem prática

A via TWILIGHT só abre **depois de 3 meses sem evento**, em quem já estava em **ticagrelor**, e consiste em **tirar o AAS — não o P2Y12 potente**.
