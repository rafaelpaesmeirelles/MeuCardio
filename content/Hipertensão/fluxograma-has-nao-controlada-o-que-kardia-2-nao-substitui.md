---
kind: fluxograma
published: true
review_note: Conferidos PATHWAY-2, TARGET/ADVANCE/LAUNCH e KARDIA conforme o conteúdo;
  corrigidos elegibilidade e segurança dos fluxogramas, doses ADVANCE, distinção entre
  eventos atribuídos e totais, atualização KARDIA-3 e situação regulatória sem alegação
  de aprovação brasileira.
review_status: revisado
slug: fluxograma-has-nao-controlada-o-que-kardia-2-nao-substitui
source_refs:
- 'Desai AS, Karns AD, Badariene J, et al.; KARDIA-2 Study Group. Add-On Treatment
  With Zilebesiran for Inadequately Controlled Hypertension: The KARDIA-2 Randomized
  Clinical Trial. JAMA. 2025;334(1):46-55. DOI 10.1001/jama.2025.6681. PMID 40434761.
  PMC12120674. NCT05103332.'
- 'Bakris GL, Saxena M, Gupta A, et al.; KARDIA-1 Study Group. RNA Interference With
  Zilebesiran for Mild to Moderate Hypertension: The KARDIA-1 Randomized Clinical
  Trial. JAMA. 2024;331(9):740-749. DOI 10.1001/jama.2024.0728. PMID 38363577. PMC10873804.
  NCT04936035.'
- Roche/Alnylam. KARDIA-3, resultados apresentados no ESC 2025, 30/08/2025. https://assets.roche.com/f/176343/a55c689db8/01-media-investor-release-kardia-3-data-phase-3-english.pdf
theme: Hipertensão
title: 'Fluxograma: HAS não controlada — o que o KARDIA-2 não substitui'
---

# Fluxograma: HAS não controlada — o que o KARDIA-2 não substitui

Árvore do **caminho usual** da hipertensão não controlada. KARDIA-2 (fase 2) mostrou que uma dose única subcutânea de zilebesiran 600 mg, em add-on a indapamida, anlodipino ou olmesartana, reduziu a PAS média ambulatorial de 24 horas aos 3 meses versus placebo (−12,1 mm Hg na indapamida; −9,7 mm Hg no anlodipino; −4,5 mm Hg na olmesartana). **Não é ensaio de desfecho cardiovascular.** Zilebesiran **não é padrão atual**, não substitui primeira linha e não entra como atalho para pular adesão, MAPA/MRPA, secundária, tríade ou quarta linha.

Status regulatório brasileiro do zilebesiran: **VERIFICAÇÃO HUMANA NECESSÁRIA.** A dose de 600 mg SC é a do ensaio, não receita.

Nós verdes (estádio) são condutas. Losangos são decisões. Cada nó tem um único pai: o texto se repete em vez de fechar um ciclo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto não gestante com HAS não controlada, sem emergência hipertensiva"] --> D1{"Adesão ao esquema atual confirmada?"}
  D1 -->|Não| C1(["Corrigir adesão antes de adicionar fármaco. Não chamar de resistente quem não toma o que já foi prescrito"])
  D1 -->|Sim| D2{"PA confirmada fora do consultório — MAPA ou MRPA?"}
  D2 -->|Não| C2(["Obter MAPA ou MRPA. Não intensificar o esquema só com consultório isolado"])
  D2 -->|Sim e normal| C7(["Considerar efeito do avental branco; acompanhar e evitar intensificação automática"])
  D2 -->|Sim e elevada| D3{"Causa secundária considerada?"}
  D3 -->|Não investigada e há pistas| C3(["Investigar secundária. Não rotular resistente sem essa etapa"])
  D3 -->|Sim ou sem pistas| P1["Combinar três classes: tiazida-like, BCC diidropiridínico, IECA ou BRA"]
  P1 --> D4{"Ainda não controlada com as três classes em doses adequadas?"}
  D4 -->|Não| C4(["Manter a combinação. Reavaliar adesão e PA fora do consultório"])
  D4 -->|Sim| P2["Avaliar potássio, TFGe e contraindicações antes da quarta linha; espironolactona se elegível"]
  P2 --> D5{"Ainda não controlada após a quarta linha?"}
  D5 -->|Não| C5(["Manter o esquema otimizado. Reavaliar adesão, potássio, função renal e PA fora do consultório"])
  D5 -->|Sim| C6(["HAS resistente: seguir o caminho usual. Zilebesiran é add-on investigacional de fase 2 — não é padrão atual nem substituto da primeira linha"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

Suspeita de lesão aguda de órgão-alvo exige avaliação urgente; não aguardar MAPA, adesão ou investigação eletiva para tratar uma emergência.

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
- Desfecho de infarto, AVC ou morte — KARDIA-2 e KARDIA-1 não demonstram redução desses eventos.

## Tudo com Tudo

- **Hipertensão:** esta árvore é o caminho da não controlada e da resistente; zilebesiran não abre um atalho.
- **Farmacologia:** o siRNA anti-angiotensinogênio permanece investigacional; ver o documento de o que é e o que ainda não é.
- **Cardiorrenal:** quarta linha com espironolactona exige potássio e função renal; o braço zilebesiran do KARDIA-2 teve mais hipercalemia e lesão renal aguda que o placebo.
- **Prevenção e lipídios:** controlar a PA reduz risco; o ensaio não prova que o siRNA reduz eventos.
- **Comunicação clínica:** “ainda não é tratamento padrão; o próximo passo é conferir se a medicação está sendo tomada e se a pressão fora do consultório confirma o descontrole.”

## Atualização KARDIA-3

Atualização do programa: no KARDIA-3, apresentado no ESC 2025, o critério de significância do desfecho primário não foi atingido após controle de multiplicidade. A redução nominal de PAS com 300 mg não torna o ensaio positivo. Fonte: comunicado Roche/Alnylam de 30/08/2025; dados de congresso, sem comprovação de redução de eventos cardiovasculares.
