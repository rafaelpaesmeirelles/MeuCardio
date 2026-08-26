---
title: "Fluxograma: Duração da anticoagulação após primeiro episódio de TEV não provocado"
slug: fluxograma-duracao-da-anticoagulacao-apos-tev-nao-provocado
theme: "Tromboembolismo"
kind: fluxograma
fonte_producao: chatgpt
summary: "Depois do curso inicial de 3-6 meses num primeiro TEV não provocado, a decisão entre suspender e estender por tempo indefinido passa pelo risco de sangramento, pelo sexo do paciente e, em mulheres, pelo escore HERDOO2 — com a opção de dose reduzida de apixaban ou rivaroxaban para quem estende."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 31504429 (ESC 2019 diretriz de TEP agudo, seção de duração de anticoagulação, Konstantinides SV, Eur Heart J 41(4):543-603), 28314711 (validação do HERDOO2, Rodger MA, BMJ 356:j1065), 23216615 (AMPLIFY-EXT, Agnelli G, NEJM 368(8):699-708) e 28316279 (EINSTEIN CHOICE, Weitz JI, NEJM 376(13):1211-1222). Título, revista, volume/página e autor conferidos contra o registro oficial antes de citar. Não duplica os fluxogramas já publicados do tema (diagnóstico de TEP e sangramento maior em anticoagulado) — recorte é especificamente a decisão de duração após o curso inicial."
source_refs: ["2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS) · European Heart Journal · 2020 · 41(4):543-603 · https://pubmed.ncbi.nlm.nih.gov/31504429/", "Validating the HERDOO2 rule to guide treatment duration for women with unprovoked venous thrombosis: multinational prospective cohort management study · BMJ · 2017 · 356:j1065 · https://pubmed.ncbi.nlm.nih.gov/28314711/", "Apixaban for extended treatment of venous thromboembolism (AMPLIFY-EXT) · New England Journal of Medicine · 2013 · 368(8):699-708 · https://pubmed.ncbi.nlm.nih.gov/23216615/", "Rivaroxaban or Aspirin for Extended Treatment of Venous Thromboembolism (EINSTEIN CHOICE) · New England Journal of Medicine · 2017 · 376(13):1211-1222 · https://pubmed.ncbi.nlm.nih.gov/28316279/"]
---

# Fluxograma: Duração da anticoagulação após TEV não provocado

O primeiro episódio de tromboembolismo venoso sem fator de risco identificável
carrega risco de recorrência alto o bastante para que a diretriz ESC 2019
trate a decisão de suspender a anticoagulação no fim do curso inicial (3 a 6
meses) como uma escolha ativa, não um desfecho automático. A árvore abaixo
segue a sequência que pesa mais nessa decisão: risco de sangramento primeiro,
depois sexo do paciente e, em mulheres, o escore HERDOO2 — que foi validado
especificamente para identificar quem pode suspender com segurança.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Primeiro episódio de TEV não<br/>provocado, curso inicial de<br/>3-6 meses de anticoagulação<br/>concluído"] --> D1{"Risco de sangramento alto ou<br/>contraindicação a anticoagulação<br/>prolongada?"}

  D1 -->|"Sim"| C1(["Suspender a anticoagulação após o<br/>curso inicial; considerar AAS em<br/>dose baixa, se sem contraindicação,<br/>para redução parcial do risco de<br/>recorrência"])

  D1 -->|"Não"| D2{"Sexo do paciente"}

  D2 -->|"Homem"| C2(["Risco de recorrência elevado:<br/>anticoagulação estendida por tempo<br/>indefinido — considerar dose reduzida<br/>de apixaban ou rivaroxaban após os<br/>primeiros 6 meses, com reavaliação<br/>periódica de risco-benefício"])

  D2 -->|"Mulher"| D3{"Escore HERDOO2: hiperpigmentação/<br/>edema/eritema de perna, D-dímero<br/>≥ 250 mcg/L pós-tratamento, IMC ≥ 30<br/>ou idade ≥ 65 anos — 2 ou mais<br/>critérios presentes?"}

  D3 -->|"Sim, 2 ou mais critérios<br/>(HERDOO2 alto)"| C3(["Risco de recorrência elevado:<br/>anticoagulação estendida por tempo<br/>indefinido — considerar dose reduzida<br/>de apixaban ou rivaroxaban após os<br/>primeiros 6 meses, com reavaliação<br/>periódica de risco-benefício"])

  D3 -->|"Não, 0-1 critério<br/>(HERDOO2 baixo)"| D4{"O evento inicial foi TEP<br/>(e não TVP isolada)?"}

  D4 -->|"Sim"| C4(["Risco de recorrência ainda<br/>relevante mesmo com HERDOO2 baixo:<br/>individualizar a decisão, podendo<br/>considerar estender a anticoagulação<br/>em dose reduzida"])

  D4 -->|"Não — TVP<br/>proximal ou distal isolada"| C5(["Risco de recorrência baixo pelo<br/>HERDOO2: suspender a anticoagulação<br/>com segurança razoável"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**O HERDOO2 foi derivado e validado só em mulheres.** O estudo de validação
multinacional (BMJ 2017) testou a regra prospectivamente em 2.785 mulheres com
TEV não provocado e mostrou taxa de recorrência de apenas 3,0% ao ano nas
classificadas como baixo risco que suspenderam a anticoagulação — a regra não
tem validação equivalente para homens, que é por isso que a árvore não a
aplica a eles.

**AMPLIFY-EXT e EINSTEIN CHOICE testaram dose reduzida especificamente para
extensão, não para o tratamento agudo.** No AMPLIFY-EXT, apixaban 2,5 mg
2x/dia reduziu recorrência sintomática de TEV para 1,7% (versus 8,8% com
placebo) sem aumento de sangramento maior; no EINSTEIN CHOICE, rivaroxaban 10
mg/dia teve desempenho equivalente à dose de 20 mg com menos sangramento — é
essa evidência que sustenta oferecer dose reduzida a quem estende, não uma
opção genérica de "anticoagulante em dose menor".

**Reavaliação periódica não é ramo único porque se repete ao longo do
seguimento.** Risco de sangramento, adesão e preferência do paciente mudam com
o tempo — a diretriz recomenda reconsiderar a decisão de continuar em cada
consulta de seguimento, não só no momento em que o curso inicial termina.

**Trombofilia hereditária, câncer ativo e cenários com estudo próprio** (trombo
de ventrículo esquerdo, TEV do câncer, síndrome antifosfolípide) têm algoritmo
de duração distinto do TEV não provocado sem esses fatores, e não estão
representados aqui — a árvore assume que "não provocado" já significa a
ausência desses fatores identificados na investigação inicial.
