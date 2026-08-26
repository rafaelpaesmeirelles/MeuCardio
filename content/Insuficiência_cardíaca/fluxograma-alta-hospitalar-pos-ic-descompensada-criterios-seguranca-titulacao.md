---
title: "Fluxograma: Critérios de Segurança para Alta e Titulação Pós-Alta na Insuficiência Cardíaca Descompensada"
slug: fluxograma-alta-hospitalar-pos-ic-descompensada-criterios-seguranca-titulacao
theme: "Insuficiência cardíaca"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "PMID/DOI conferidos via PubMed E-utilities (esummary) nesta sessão, em 26/08/2026: STRONG-HF PMID 36356631 (Lancet 2022;400(10367):1938-1952) e a recomendação de Classe I/Nível B de estratégia intensiva de início e titulação rápida pré-alta nos primeiros 6 semanas pós-internação, citada quase literalmente do documento já publicado nesta mesma pasta (safety-tolerability-and-efficacy-of-up-titration-of-guideline-directed-medical-therapies-for-acute-heart-failure-strong-hf.md); ESC Focused Update 2023 PMID 37622666 (Eur Heart J 2023;44(37):3627-3639); ESC Guidelines 2021 PMID 34447992 (Eur Heart J 2021, McDonagh TA et al.), cujo Consensus/Table de critérios pré-alta (euvolemia, ausência de diurético/vasoativo endovenoso nas últimas 24h, função renal e eletrólitos estáveis, terapia oral otimizada e consulta precoce agendada) é reproduzido de forma qualitativa, sem número que a fonte não sustente; AHA/ACC/HFSA 2022 PMID 35363499 (Circulation 2022;145(18):e895-e1032), cuja recomendação de iniciar GDMT antes da alta e reavaliar/titular precocemente após a alta é Classe I. Conferido o corpus desta pasta antes de escrever: os fluxogramas já publicados (fluxograma-sequenciamento-titulacao-terapia-quadrupla-icfer.md e fluxograma-hipotensao-sintomatica-titulacao-ieca-arni-icfer.md) tratam do momento ambulatorial de sequenciamento e da barreira de hipotensão, respectivamente — nenhum trata do momento da ALTA hospitalar em si (critérios de segurança para liberar o paciente e estrutura do acompanhamento pós-alta); este fluxograma referencia os dois em vez de repetir o conteúdo deles. Nenhum corte numérico de PA/FC/TFGe é inventado onde a fonte não define um valor exato — a decisão fica qualitativa, no mesmo padrão já adotado nos outros fluxogramas desta pasta."
source_refs: ["Mebazaa A, Davison B, Chioncel O, et al. Safety, tolerability and efficacy of up-titration of guideline-directed medical therapies for acute heart failure (STRONG-HF): a multinational, open-label, randomised trial. Lancet. 2022;400(10367):1938-1952. DOI: 10.1016/S0140-6736(22)02076-1. PMID: 36356631", "2023 Focused Update of the 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2023;44(37):3627-3639. DOI: 10.1093/eurheartj/ehad195. PMID: 37622666", "McDonagh TA, Metra M, Adamo M, et al. 2021 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure. Eur Heart J. 2021;42(36):3599-3726. DOI: 10.1093/eurheartj/ehab368. PMID: 34447992", "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure: A Report of the American College of Cardiology/American Heart Association Joint Committee on Clinical Practice Guidelines. Circulation. 2022;145(18):e895-e1032. DOI: 10.1161/CIR.0000000000001063. PMID: 35363499"]
---

# Fluxograma: Critérios de Segurança para Alta e Titulação Pós-Alta na Insuficiência Cardíaca Descompensada

A alta hospitalar por IC descompensada é o ponto de maior risco de todo o curso da
doença — parte relevante das reinternações e óbitos precoces acontece nas
primeiras semanas após a saída do hospital. O STRONG-HF e a atualização focada
2023 da ESC mudaram o que se espera desse momento: não basta o paciente estar
sem congestão — a alta segura exige terapia quádrupla iniciada (ou com plano
escrito de titulação), consulta de reavaliação precoce **já agendada e
confirmada antes de sair do hospital**, e um resumo de alta que funcione como
protocolo de titulação, não como relato do que foi feito durante a internação.
Este fluxograma trata exatamente desse recorte: os critérios de segurança para
liberar a alta e a estrutura mínima do acompanhamento pós-alta — não o
sequenciamento farmacológico em si (ver `fluxograma-sequenciamento-titulacao-terapia-quadrupla-icfer.md`,
nesta mesma pasta) nem o manejo específico da hipotensão sintomática (ver
`fluxograma-hipotensao-sintomatica-titulacao-ieca-arni-icfer.md`).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente internado por IC descompensada,<br/>congestão tratada, sendo avaliado<br/>para alta hospitalar"]
  D1{"Critérios clínicos de estabilidade<br/>preenchidos? (sem diurético/vasoativo<br/>endovenoso nas últimas 24h, PA e FC<br/>estáveis sem hipotensão sintomática,<br/>função renal e potássio estáveis<br/>ou em melhora, saturação adequada)"}
  C1(["Manter internado — não dar alta.<br/>Reavaliar diariamente os critérios<br/>de estabilidade; retomar esta árvore<br/>assim que preenchidos (ESC 2021)"])
  D2{"Terapia quádrupla já iniciada ou com<br/>plano de titulação documentado antes<br/>da alta (ESC 2023 / STRONG-HF /<br/>AHA-ACC-HFSA 2022, Classe I)?"}
  C2(["Iniciar a terapia quádrupla em dose<br/>baixa antes da alta, seguindo o<br/>fluxograma de sequenciamento e<br/>titulação desta pasta — não autorizar<br/>a alta sem ao menos iniciar as classes<br/>sem contraindicação"])
  D3{"Há barreira de segurança limitando<br/>dose plena imediata (PA limítrofe/<br/>hipotensão, FC ou condução limítrofes,<br/>TFGe ou potássio limítrofes)?"}
  C3(["Documentar plano escalonado de<br/>titulação pós-alta específico da<br/>barreira identificada — para PA<br/>limítrofe/hipotensão, seguir o<br/>fluxograma dedicado de hipotensão<br/>sintomática desta pasta antes de<br/>liberar a alta"])
  D4{"Consulta de reavaliação (presencial<br/>ou telemática) agendada e CONFIRMADA<br/>para 1 a 2 semanas após a alta<br/>(estratégia de alta intensidade,<br/>STRONG-HF)?"}
  C4(["Não autorizar a alta até a consulta<br/>precoce estar agendada e confirmada —<br/>vínculo assistencial é pré-requisito<br/>da alta segura, não recomendação a<br/>ser cumprida depois"])
  D5{"Resumo de alta documenta peso seco<br/>atual, dose de cada um dos quatro<br/>pilares, meta de titulação e sinais<br/>de alarme explicados ao paciente?"}
  C5(["Completar o resumo de alta com plano<br/>escrito de titulação (dose atual, meta,<br/>prazo) e lista de sinais de alarme<br/>para o paciente antes de liberá-lo"])
  C6(["Autorizar a alta com plano estruturado<br/>de titulação rápida pós-alta: reavaliar<br/>clínica, PA, FC, potássio e TFGe a cada<br/>consulta e dobrar a dose tolerada até a<br/>meta ou a dose máxima, em até 6 semanas<br/>(STRONG-HF / ESC 2023, Classe I Nível B)"])

  R0 --> D1
  D1 -->|"Não, ainda instável"| C1
  D1 -->|"Sim, critérios preenchidos"| D2
  D2 -->|"Não"| C2
  D2 -->|"Sim"| D3
  D3 -->|"Sim, há barreira"| C3
  D3 -->|"Não, sem barreira relevante"| D4
  D4 -->|"Não"| C4
  D4 -->|"Sim, confirmada"| D5
  D5 -->|"Não"| C5
  D5 -->|"Sim"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**Não há corte numérico validado** de PA, FC, TFGe ou potássio que defina
"limítrofe" no nó D3 — nenhuma das quatro fontes citadas define esse número de
forma isolada e generalizável; a decisão é clínica, apoiada no julgamento à
beira do leito. Onde a fonte define um prazo (o intervalo de 1-2 semanas do
STRONG-HF, a janela de 6 semanas da recomendação Classe I/Nível B da ESC 2023),
isso está registrado no nó correspondente.

**A janela de 1-2 semanas do nó D4 vem do desenho do STRONG-HF** (visitas
quinzenais, média de 4,8 consultas no braço de alta intensidade) e da
recomendação da ESC 2023, que fala em consultas "frequentes e cuidadosas nas
primeiras 6 semanas" — não é um número único fixo por todas as diretrizes, e o
fluxograma o usa como referência prática, não como limite absoluto.

**Organizar a transição de cuidado não substitui titular a terapia.** O ensaio
PACT-HF (`transicao-hospital-domicilio-na-ic-o-ensaio-pact-hf.md`, nesta mesma
pasta) testou visitas domiciliares e acompanhamento estruturado sem exigir
mudança de prescrição, e teve resultado neutro (HR 0,92 para o desfecho composto
em 3 anos) — os próprios autores atribuem isso à ausência de diferença real na
adoção de terapia guiada por diretriz entre os grupos. É por isso que este
fluxograma amarra a consulta precoce (D4) a um resumo de alta com plano de
titulação explícito (D5): agendar a consulta sem o plano de dose repete o
mecanismo que fez o PACT-HF não funcionar.

**Doses exatas e esquemas de titulação por fármaco** não são objeto deste
fluxograma — consulte `fluxograma-sequenciamento-titulacao-terapia-quadrupla-icfer.md`
e os documentos de cada pilar nesta pasta.

**Reavaliação de intercorrência aguda fora dos pontos marcados na árvore** —
nova descompensação, evento clínico ou mudança de fármaco concomitante reabre o
processo de decisão a qualquer momento, inclusive depois da alta já autorizada.
