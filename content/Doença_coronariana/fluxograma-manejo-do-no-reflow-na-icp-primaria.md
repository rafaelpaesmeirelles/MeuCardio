---
title: "Fluxograma: Manejo do no-reflow durante a ICP primária"
slug: fluxograma-manejo-do-no-reflow-na-icp-primaria
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: chatgpt
summary: "Do reconhecimento do no-reflow (fluxo TIMI reduzido sem lesão mecânica residual) ao manejo escalonado com vasodilatador intracoronário seletivo, suporte hemodinâmico e o limite real da terapia disponível quando o fluxo não responde."
review_status: revisado
review_note: "PMIDs conferidos nesta sessão via PubMed E-utilities (esearch/esummary): 39077094 (Pelliccia F et al., Pathophysiology and Treatment of the No-Reflow Phenomenon in ST-Segment Elevation Myocardial Infarction, Rev Cardiovasc Med. 2023;24(12):365) e 25853743 (TOTAL trial, Jolly SS et al., NEJM. 2015;372(15):1389-1398) — título, revista, ano e volume/páginas batendo exatamente com o texto do documento. Doses exatas de vasodilatador intracoronário não são detalhadas (variam por protocolo institucional) e isso está declarado abaixo."
source_refs: ["Pelliccia F, Niccoli G, Zimarino M, et al. Pathophysiology and Treatment of the No-Reflow Phenomenon in ST-Segment Elevation Myocardial Infarction · Reviews in Cardiovascular Medicine · 2023 · 24(12):365 · PMID: 39077094", "Jolly SS, Cairns JA, Yusuf S, et al. Randomized trial of primary PCI with or without routine manual thrombectomy (TOTAL) · New England Journal of Medicine · 2015 · 372(15):1389-1398 · PMID: 25853743"]
---

# Fluxograma: Manejo do no-reflow durante a ICP primária

No-reflow é o fluxo coronariano reduzido (TIMI menor que 3) ou a perfusão
miocárdica insuficiente (blush reduzido) **depois** de a artéria culpada já
estar mecanicamente aberta na ICP primária — ou seja, não é falha em abrir a
artéria, é falha da microcirculação distal em receber o fluxo restaurado. O
primeiro passo, sistematicamente esquecido sob pressão de sala, é afastar
causa mecânica corrigível antes de tratar como no-reflow verdadeiro. O
fluxograma abaixo organiza essa sequência.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Fluxo TIMI menor que 3 ou blush miocárdico reduzido<br/>após abertura mecânica da artéria culpada na ICP primária,<br/>sem lesão residual óbvia explicando o achado"] --> D1{"Há causa mecânica corrigível (dissecção,<br/>trombo residual volumoso, espasmo focal visível,<br/>malposição de stent)?"}

  D1 -->|"Sim"| C1(["Corrigir a causa mecânica identificada (nova<br/>insuflação, stent adicional, aspiração de trombo se<br/>carga alta) antes de tratar como no-reflow"])

  D1 -->|"Não — provável obstrução<br/>microvascular (no-reflow)"| D2{"Paciente hemodinamicamente estável?"}

  D2 -->|"Não"| C2(["Suporte hemodinâmico (vasopressor e, se<br/>refratário, suporte circulatório mecânico) antes<br/>ou junto do vasodilatador intracoronário,<br/>em dose cautelosa"])

  D2 -->|"Sim"| P1["Vasodilatador intracoronário seletivo, distal à<br/>lesão: adenosina, verapamil ou nitroprussiato de<br/>sódio, em bólus repetidos"]

  P1 --> D3{"Fluxo TIMI 3 (ou melhora substancial do<br/>blush) restabelecido após o vasodilatador?"}

  D3 -->|"Sim"| C3(["Concluir o procedimento; manter vigilância<br/>para reoclusão e tratamento clínico padrão do infarto"])

  D3 -->|"Não"| D4{"Já foram tentadas pelo menos duas classes de<br/>vasodilatador intracoronário (ex. adenosina e<br/>verapamil), sem resposta?"}

  D4 -->|"Sim"| C4(["No-reflow refratário: considerar suporte<br/>circulatório mecânico, otimizar o suporte clínico e<br/>aceitar fluxo subótimo — sem terapia adicional com<br/>benefício comprovado"])

  D4 -->|"Não"| C5(["Repetir ou associar outro vasodilatador<br/>intracoronário (trocar ou combinar agente) e<br/>reavaliar o fluxo"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**Doses exatas não estão especificadas de propósito.** Adenosina, verapamil e
nitroprussiato de sódio intracoronários têm protocolos de bólus que variam
por instituição e por apresentação farmacêutica disponível — a diretriz e a
literatura de revisão descrevem faixas, não uma dose única e universal.
Consultar o protocolo local antes de administrar.

**Trombectomia por aspiração de rotina não é recomendada, e isso não é uma
omissão.** O ensaio TOTAL, com mais de 10 mil pacientes, mostrou que a
aspiração manual de rotina não reduz desfechos cardiovasculares e aumenta o
risco de acidente vascular cerebral em 30 dias — por isso ela só aparece
dentro de D1, como manobra para trombo residual volumoso identificado, nunca
como profilaxia de no-reflow.

**A prevenção começa antes da abertura da artéria**, e não está representada
aqui: pré-tratamento com vasodilatador em lesões de alta carga trombótica,
escolha entre tromboaspiração seletiva e balão direto, e o próprio tempo de
isquemia total são fatores de risco para no-reflow que atuam antes do ponto
em que esta árvore começa.

**Não há hierarquia comprovada entre adenosina, verapamil e nitroprussiato.**
A escolha costuma depender de disponibilidade e de contraindicação (por
exemplo, bloqueio atrioventricular avançado limita o uso de verapamil) — a
árvore trata as três como intercambiáveis dentro do mesmo passo, o que
reflete a ausência de comparação direta de qualidade na literatura.
