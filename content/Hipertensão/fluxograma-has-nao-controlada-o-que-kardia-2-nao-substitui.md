---
title: 'Fluxograma: HAS não controlada — o que o KARDIA-2 não substitui'
slug: fluxograma-has-nao-controlada-o-que-kardia-2-nao-substitui
theme: Hipertensão
kind: fluxograma
review_status: revisado
source_refs:
- 'Desai AS, Karns AD, Badariene J, et al.; KARDIA-2 Study Group. Add-On Treatment With Zilebesiran for Inadequately Controlled
  Hypertension: The KARDIA-2 Randomized Clinical Trial. JAMA. 2025;334(1):46-55. DOI 10.1001/jama.2025.6681. PMID 40434761.
  PMC12120674. NCT05103332.'
- 'Bakris GL, Saxena M, Gupta A, et al.; KARDIA-1 Study Group. RNA Interference With Zilebesiran for Mild to Moderate Hypertension:
  The KARDIA-1 Randomized Clinical Trial. JAMA. 2024;331(9):740-749. DOI 10.1001/jama.2024.0728. PMID 38363577. PMC10873804.
  NCT04936035.'
- 'McEvoy JW, McCarthy CP, Bruno RM, et al.; ESC Scientific Document Group. 2024 ESC Guidelines for the management of elevated
  blood pressure and hypertension. Eur Heart J. 2024 Oct 7;45(38):3912-4018. DOI: 10.1093/eurheartj/ehae178. PMID: 39210715.'
- 'Jones DW, Ferdinand KC, Taler SJ, et al. 2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM Guideline for
  the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults. J Am Coll Cardiol. 2025;86(18):1567-1678.
  DOI: 10.1016/j.jacc.2025.05.007. PMID: 40815242. Também Circulation. 2025;152:e114-e218. DOI: 10.1161/CIR.0000000000001356.'
- Alnylam. Programa clínico de zilebesiran e ZENITH fase3. https://investors.alnylam.com/press-release?id=29321 ; https://www.alnylam.com/alnylam-rnai-pipeline
  . Consultado 09/09/2026.
review_note: KARDIA2 primário e AHA2025 resistência conferidos. Corrigido atraso perigoso por exigir MAPA/adesão antes de
  qualquer tratamento; explicitados segurança do ARM e emergência. Atualizado programa à fase3, sem benefícioCV inventado.
  Conexões temáticas selecionadas e links por slugs da fila conferidos.
summary: Árvore do caminho usual da hipertensão não controlada. KARDIA-2 (fase 2) mostrou que uma dose única subcutânea de
  zilebesiran 600 mg, em add-on a indapamida, anlodipino ou olmesartana, reduziu a PAS média ambulatorial de 24 horas aos
  3 meses versus placebo (−12,1 mm Hg na indapamida; −9,7 mm Hg no anlodipino; −4,5 mm Hg na olmesartana). Não é ensaio de
  desfecho cardiovascular. Zilebesiran não é padrão atual, não substitui primeira linha e não entra como atalho para pular
  adesão, MAPA/MRPA, secundária, tríade ou quarta linha.
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: HAS não controlada — o que o KARDIA-2 não substitui

Árvore do **caminho usual** da hipertensão não controlada. KARDIA-2 (fase 2) mostrou que uma dose única subcutânea de zilebesiran 600 mg, em add-on a indapamida, anlodipino ou olmesartana, reduziu a PAS média ambulatorial de 24 horas aos 3 meses versus placebo (−12,1 mm Hg na indapamida; −9,7 mm Hg no anlodipino; −4,5 mm Hg na olmesartana). **Não é ensaio de desfecho cardiovascular.** Zilebesiran **não é padrão atual**, não substitui primeira linha e não entra como atalho para pular adesão, MAPA/MRPA, secundária, tríade ou quarta linha.

O programa permanece investigacional e já avançou ao ZENITH, ensaio de desfechos cardiovasculares de fase 3. KARDIA-1/2 são os ensaios de fase 2 resumidos aqui; as doses estudadas não equivalem a prescrição aprovada. [Desenvolvimento clínico](https://www.alnylam.com/alnylam-rnai-pipeline).

Nós verdes (estádio) são condutas. Losangos são decisões. Cada nó tem um único pai: o texto se repete em vez de fechar um ciclo.

Esta árvore é ambulatorial: suspeita de emergência hipertensiva ou lesão aguda de órgão exige avaliação imediata. Potássio, TFGe e contraindicações devem ser avaliados antes de ARM; investigar aldosteronismo na resistência, mesmo sem hipocalemia.

## Árvore de decisão

```mermaid
flowchart TD
  R0["HAS não controlada"] --> D1{"Adesão ao esquema atual confirmada?"}
  D1 -->|Não| C1(["Corrigir adesão e avaliar necessidade de tratamento concomitante. Não chamar de resistente quem não toma o que já foi prescrito"])
  D1 -->|Sim| D2{"PA confirmada fora do consultório — MAPA ou MRPA?"}
  D2 -->|Não| C2(["Obter MAPA ou MRPA para confirmar o fenótipo; não adiar tratamento de PA grave ou emergência"])
  D2 -->|Sim e elevada| D3{"Causa secundária considerada?"}
  D3 -->|Não investigada e há pistas| C3(["Investigar secundária. Não rotular resistente sem essa etapa"])
  D3 -->|Sim ou sem pistas| P1["Combinar três classes: tiazida-like, BCC diidropiridínico, IECA ou BRA"]
  P1 --> D4{"Ainda não controlada com as três classes em doses adequadas?"}
  D4 -->|Não| C4(["Manter a combinação. Reavaliar adesão e PA fora do consultório"])
  D4 -->|Sim| P2["Otimizar dose e adicionar quarta linha: espironolactona quando possível — caminho usual de HAS resistente"]
  P2 --> D5{"Ainda não controlada após a quarta linha?"}
  D5 -->|Não| C5(["Manter o esquema otimizado. Reavaliar adesão, potássio, função renal e PA fora do consultório"])
  D5 -->|Sim| C6(["HAS resistente: seguir o caminho usual. Zilebesiran é investigacional; KARDIA-2 foi fase 2 — não é padrão atual nem substituto da primeira linha"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## Como ler a árvore

O primeiro ramal é **adesão**, não fármaco novo. KARDIA-2 randomizou quem já estava em run-in de um anti-hipertensivo de primeira linha. Saltar a confirmação de que o paciente toma o esquema atual para “ir ao siRNA” não é o que o ensaio autoriza.

O segundo ramal é **medida fora do consultório**. HAS não controlada no consultório isolado pode ser efeito do avental branco. Intensificar classe sem MAPA ou MRPA mistura fenótipos.

O terceiro ramal é **causa secundária**. Aldosteronismo primário, estenose de artéria renal, apneia do sono e coarctação não se resolvem com RNA de interferência. A árvore não lista o protocolo completo de secundária — só impede o rótulo de resistente sem essa pergunta.

O quarto ramal é a **tríade** (tiazida-like, BCC diidropiridínico, IECA ou BRA). Essa combinação é o padrão de não controlada; KARDIA-2 testou zilebesiran **sobre uma** dessas classes, não no lugar das três.

O quinto ramal é a **quarta linha usual** da HAS resistente — espironolactona quando possível, com vigilância de potássio e função renal. Não inventar classe de recomendação neste texto. Outras opções de quarta linha seguem a diretriz local vigente, não este fluxograma.

O último estádio deixa zilebesiran **fora** do padrão: fase 2, surrogato pressórico, add-on investigacional. A hipótese de adesão (injeção trimestral ou semestral versus comprimido diário) **não** é desfecho do ensaio.

## O que a árvore não mostra

- Dose prescritível de zilebesiran — 600 mg SC é a do KARDIA-2; não há, aqui, esquema de manutenção.
- Escolha entre indapamida, clortalidona e hidroclorotiazida, ou entre IECA e BRA.
- Protocolo completo de hipertensão secundária.
- Comparação com denervação renal.
- Desfecho de infarto, AVC ou morte — KARDIA-2 e KARDIA-1 não medem isso.

## Tudo com Tudo

- [Fluxograma: HAS resistente após otimização — o que vem depois](/biblioteca/fluxograma-has-resistente-apos-otimizacao-o-que-vem-depois)
- [Fluxograma: iniciar fármaco na HAS — AHA/ACC 2025 e PREVENT ≥7,5%](/biblioteca/fluxograma-inicio-de-farmaco-aha-2025-prevent)
- [KARDIA-2: zilebesiran (RNA de interferência) na HAS não controlada](/biblioteca/zilebesiran-kardia-2-rna-interferencia-na-has-nao-controlada)
- [Zilebesiran (KARDIA-1 e KARDIA-2): siRNA contra o angiotensinogênio — surrogato pressórico](/biblioteca/zilebesiran-kardia-sirna-angiotensinogenio)
