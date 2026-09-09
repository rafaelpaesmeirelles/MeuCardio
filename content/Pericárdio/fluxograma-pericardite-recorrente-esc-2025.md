---
kind: fluxograma
published: true
review_note: Conferidos ICAP, CORP, CORP-2, AIRTRIP/RHAPSODY e ESC 2025 integral.
  ICAP incluiu lesão cardíaca/tecido conjuntivo; corrigida exclusão canônica e narrativa
  de subida de classe. Ajustado peso ≤70/>70 no CORP-2 e retiradas estimativas secundárias
  não verificadas. Confirmado IIa C do anti-IL-1 com RMC, corticoide e mínimo de exercício
  ≥1 mês até remissão. Fluxo distingue etapa de corticoide, resgate e fenótipos; imunossupressão/BB
  não indiscriminados em instabilidade. Não atribuído registro Anvisa não verificado.
review_status: revisado
slug: fluxograma-pericardite-recorrente-esc-2025
source_refs:
- 'Schulz-Menger J, Collini V, Gröschel J, et al. 2025 ESC Guidelines for the management
  of myocarditis and pericarditis. Eur Heart J. 2025;46(40):3952-4041. DOI: 10.1093/eurheartj/ehaf192.
  PMID: 40878297.'
- 'Brucato A, Imazio M, Gattorno M, et al. Effect of Anakinra on Recurrent Pericarditis
  Among Patients With Colchicine Resistance and Corticosteroid Dependence: The AIRTRIP
  Randomized Clinical Trial. JAMA. 2016;316(18):1906-1912. DOI: 10.1001/jama.2016.15826.
  PMID: 27825009.'
- 'Klein AL, Imazio M, Cremer P, et al. Phase 3 Trial of Interleukin-1 Trap Rilonacept
  in Recurrent Pericarditis. N Engl J Med. 2021;384(1):31-41. DOI: 10.1056/NEJMoa2027892.
  PMID: 33200890. NCT03737110.'
- ESC miocardite/pericardite 2025, texto integral. https://www.myocarditisfoundation.org/wp-content/uploads/2025/09/ehaf192.pdf
theme: Pericárdio
title: 'Fluxograma: pericardite recorrente — ESC 2025, AIRTRIP e RHAPSODY'
---

# Fluxograma: pericardite recorrente — ESC 2025, AIRTRIP e RHAPSODY

Pergunta desta árvore: **neste paciente com pericardite, a ESC 2025 (e os ensaios AIRTRIP/RHAPSODY) informam o próximo anti-inflamatório?** Folhas verdes são condutas. A lógica é qualitativa: primeiro episódio com AINE + colchicina; recorrência com a mesma primeira linha; corticoide só se falha ou contraindicação; anti-IL-1 quando há dependência de corticoide e/ou resistência à colchicina. Não copia dose da Tabela 13. Não aplica a tamponamento, a pericardite purulenta nem à neoplásica — esses ramos saem da porta interventiva.

A ESC 2015 já colocava AAS/AINE + colchicina no primeiro episódio e reservava corticoide. A ESC 2025 não reverte isso: colchicina permanece **I A** como primeira linha adjunta; AAS/AINE com IBP ficam **I B**; corticoide **não** é primeira escolha (**III C**). O que entra de novo, com classe, é o anti-IL-1 (anakinra ou rilonacept) depois da falha — sustentado por AIRTRIP e RHAPSODY, não por opinião solta.

## Árvore de decisão

```mermaid
flowchart TD
    R0["Pericardite inflamatória<br/>decisão de anti-inflamatório"] --> D1{"Primeiro episódio<br/>ou recorrência/incesante?"}

    D1 -->|"Primeiro episódio"| C1(["AAS ou AINE + colchicina.<br/>Primeira linha ESC 2025.<br/>AINE/AAS I B. Colchicina I A.<br/>Corticoide não é primeira escolha III."])

    D1 -->|"Recorrência ou incesante"| D2{"Já recebeu colchicina<br/>adjunta a AAS/AINE em curso pleno?"}

    D2 -->|"Não"| C2(["Reiniciar AAS/AINE + colchicina.<br/>Colchicina permanece I A<br/>para reduzir a próxima recorrência.<br/>Não pular para anti-IL-1."])

    D2 -->|"Sim"| D3{"Falha, contraindicação<br/>ou intolerância a AAS/AINE + colchicina?"}

    D3 -->|"Ainda não — ajuste de curso"| C3(["Completar primeira linha.<br/>Corticoide só se falha/contraindicação<br/>ou indicação específica IIa.<br/>Não reescalonar corticoide de rotina."])

    D3 -->|"Sim"| D6{"Também houve falha, contraindicação<br/>ou intolerância ao corticoide,<br/>ou dependência que exige poupador?"}

    D6 -->|"Não"| C7(["Considerar corticoide em dose baixa/moderada<br/>com colchicina, IIa C, após avaliar causas<br/>e contraindicações. Reavaliar resposta."])
    D6 -->|"Sim"| D4{"PCR elevada neste episódio<br/>ou em episódio prévio?"}

    D4 -->|"Sim"| C4(["Anti-IL-1: anakinra ou rilonacept.<br/>ESC 2025 I A após falha da primeira linha<br/>e dos corticoides, com PCR elevada.<br/>AIRTRIP e RHAPSODY sustentam a classe."])

    D4 -->|"Não / PCR não elevada"| D5{"RMC com inflamação pericárdica<br/>após falha da primeira linha e do corticoide?"}

    D5 -->|"Sim"| C5(["Considerar anti-IL-1 IIa C<br/>mesmo sem PCR elevada,<br/>se a RMC mostra inflamação.<br/>Não inventar I A neste ramo."])

    D5 -->|"Não"| C6(["Reavaliar o fenótipo.<br/>Não anti-IL-1 de rotina.<br/>Centro de pericárdio.<br/>Não é tamponamento nem neoplasia."])

    classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
    class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**Doses.** AAS 750–1000 mg, ibuprofeno 600–800 mg, anakinra e rilonacept aparecem na Tabela 13 da ESC 2025. Esta árvore **não** as recita. Abrir o PDF antes de prescrever. Gastroproteção com IBP acompanha o AINE (recomendação **I B** de AAS/AINE com IBP). Duração típica de colchicina no primeiro episódio versus na recorrência também está na Tabela 13 — não improvisar meses.

**Corticoide.** A ESC 2025 reserva dose baixa a moderada para falha/contraindicação da primeira linha ou indicação específica (IIa C). Corticoide **não** é primeira escolha (**III C**). A folha C3 não promove o corticoide a Classe I. Desmame rápido de dose alta é exatamente o que a diretriz quer evitar.

**Anti-IL-1 não é o primeiro recorrente.** A Classe **I A** da ESC 2025 para anakinra ou rilonacept exige falha da primeira linha **e** dos corticoides **e** PCR elevada, para reduzir recorrências e permitir a retirada do corticoide. O ramo C5 (RMC positiva, PCR não elevada) é **IIa C**, não I A. Não promover rilonacept a I A no primeiro episódio nem na primeira recorrência ainda sem colchicina plena.

**Fenótipos que saem da árvore.** Tamponamento e suspeita bacteriana ou neoplásica vão para pericardiocentese (**I C**). Purulenta, para drenagem cirúrgica quando a punção não é factível (**I C**). PCIS tem tabela própria (anti-inflamatório **I B**; anti-IL-1 na PCIS refratária **I B**) — não misturar com a idiopática recorrente. Miopericardite usa colchicina em **IIa B**, não esta árvore de pericardite isolada.

## Números que cabem nas folhas C4

**AIRTRIP** (Brucato et al., *JAMA* 2016; PMID 27825009). n = 21; ≥3 recorrências, PCR elevada, resistência à colchicina e dependência de corticoide. Recorrência: **2/11** (anakinra) vs **9/10** (placebo). Ensaio pequeno de retirada randomizada — informa a classe, não a dose da Tabela 13.

**RHAPSODY** (Klein et al., *N Engl J Med* 2021; PMID 33200890; NCT03737110). 61 randomizados após run-in. Recorrência na retirada: **2/30 (7%)** rilonacept vs **23/31 (74%)** placebo. HR **0,04**; IC95% **0,01–0,18**; P<0,001. Tempo mediano até a primeira recorrência no placebo: 8,6 semanas.

A recomendação ESC não comprova registro ou indicação em bula no Brasil. Antes do uso, conferir o produto e a indicação no portal oficial da Anvisa; esta ficha não afirma aprovação brasileira para pericardite.

## Tudo com Tudo

Pericárdio · Farmacologia · Cardiomiopatias · Cardio-oncologia · Comunicação clínica.

## Limite editorial

PMID 40878297 (ESC 2025), 27825009 (AIRTRIP), 33200890 (RHAPSODY). Classe **I A** de anti-IL-1 só no ramo C4 (falha da primeira linha **e** corticoides **e** PCR elevada). C5 é **IIa C**, não I A. Doses da Tabela 13 não entram na árvore. Não se afirma registro brasileiro; consulta oficial: https://www.gov.br/anvisa/pt-br/sistemas/consulta-a-registro-de-medicamentos .
AIRTRIP e RHAPSODY selecionaram respondedores após fase aberta/run-in para a retirada randomizada; os efeitos não representam início indiscriminado em qualquer recorrência. Monitorar infecção e reações locais e avaliar contraindicações à imunossupressão.
