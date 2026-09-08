---
title: 'Fluxograma: Duração e desescalonamento da terapia antiplaquetária dupla (DAPT) após ICP'
slug: fluxograma-duracao-e-desescalonamento-da-dapt-apos-icp
theme: Doença coronariana
kind: fluxograma
fonte_producao: chatgpt
summary: 'Da DAPT padrão de 12 meses pós-SCA à DAPT curta guiada por risco hemorrágico, passando pelo desescalonamento
  farmacológico e pela extensão em muito alto risco isquêmico — organizado pelos dois eixos que a diretriz usa:
  contexto do implante (SCA versus eletivo) e risco de sangramento.'
review_status: revisado
review_note: 'PMIDs conferidos nesta sessão via PubMed E-utilities (esearch/esummary): 37622654 (2023 ESC Guidelines
  for the management of acute coronary syndromes, Eur Heart J. 2023;44(38):3720-3826), 27022822 (DAPT score, Yeh
  RW et al., JAMA. 2016;315(16):1735-1749) e 28290994 (PRECISE-DAPT, Costa F et al., Lancet. 2017;389(10073):1025-1034)
  — título, revista, ano e volume/páginas batendo exatamente com o texto do documento. Não cobre a via de fibrilação
  atrial concomitante (terapia tripla/dupla com anticoagulante oral), tratada em documento próprio. Revisão independente
  de dependência em08/09/2026: P2Y12nãoretiradaautomática; DAPTscoreapós12meses; eventonovoexigeavaliação; ticagmono≥1mselecionados;
  removesuperioridadegenótiponãofonte.'
source_refs:
- 'Byrne RA, Rossello X, Coughlan JJ, et al. 2023 ESC Guidelines for the management of acute coronary syndromes
  · European Heart Journal · 2023 · 44(38):3720-3826 · PMID: 37622654'
- 'Yeh RW, Secemsky EA, Kereiakes DJ, et al. Development and Validation of a Prediction Rule for Benefit and Harm
  of Dual Antiplatelet Therapy Beyond 1 Year After Percutaneous Coronary Intervention (DAPT score) · JAMA · 2016
  · 315(16):1735-1749 · PMID: 27022822'
- 'Costa F, van Klaveren D, James S, et al. Derivation and validation of the PRECISE-DAPT score for prediction of
  bleeding complications · Lancet · 2017 · 389(10073):1025-1034 · PMID: 28290994'
---

# Fluxograma: Duração e desescalonamento da DAPT após ICP

A pergunta "por quanto tempo mantenho os dois antiplaquetários?" mudou de uma
resposta fixa (12 meses para todo mundo) para uma decisão em dois eixos: **o
contexto clínico do implante** (síndrome coronariana aguda versus doença
coronariana crônica eletiva) e **o risco de sangramento versus o risco
isquêmico** de cada paciente. A diretriz ESC 2023 de SCA formalizou esse
segundo eixo com ferramentas específicas — critério ARC-HBR para sangramento,
escores como o PRECISE-DAPT e o DAPT score para apoiar a extensão ou o
encurtamento. O fluxograma abaixo segue essa lógica.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Paciente em DAPT (AAS + inibidor de P2Y12)<br/>após ICP com implante de stent"] --> D1{"Indicação do implante foi síndrome<br/>coronariana aguda (SCA)?"}

  D1 -->|"Não — ICP eletiva por doença<br/>coronariana crônica"| D2{"Risco hemorrágico alto<br/>(critério ARC-HBR)?"}

  D2 -->|"Sim"| C1(["DAPT curta: 1 a 3 meses, seguida de<br/>monoterapia antiplaquetária de manutenção"])

  D2 -->|"Não"| C2(["DAPT por 6 meses, seguida de<br/>monoterapia antiplaquetária de manutenção"])

  D1 -->|"Sim — SCA"| D3{"Risco hemorrágico alto (ARC-HBR) ou<br/>escore validado (ex. PRECISE-DAPT ≥25)<br/>indicando alto risco de sangramento?"}

  D3 -->|"Sim"| C3(["DAPT curta: considerar monoterapia selecionada após<br/>1 a3meses; agente e momento conforme<br/>risco e evidência, sem retirarP2Y12 automaticamente"])

  D3 -->|"Não"| D4{"Após12meses sem evento ou sangramento,<br/>alto risco isquêmico e baixo risco hemorrágico?<br/>DAPTscore pode apoiar a decisão"}

  D4 -->|"Sim"| C4(["Considerar extensão além de12meses,<br/>com esquema e doses respaldados;<br/>não reduzir indistintamente doses de toda classe"])

  D4 -->|"Não"| D5{"Por volta de 1 a 3 meses após o evento, sem<br/>sangramento e sem evento isquêmico recorrente —<br/>candidato a desescalonamento guiado?"}

  D5 -->|"Sim"| C5(["Desescalonar: trocar ticagrelor ou prasugrel por<br/>clopidogrel, orientado por teste de função plaquetária<br/>ou genotipagem CYP2C19 quando disponível,<br/>mantendo DAPT completa por 12 meses"])

  D5 -->|"Não"| C6(["Manter DAPT padrão<br/>(AAS + ticagrelor ou prasugrel) por 12 meses"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**Fibrilação atrial ou outra indicação de anticoagulação oral concomitante
sai completamente desta árvore.** Terapia tripla (AAS + P2Y12 + anticoagulante)
ou dupla (P2Y12 + anticoagulante, sem AAS) segue algoritmo próprio, com prazos
ainda mais curtos de exposição a três antitrombóticos — não é uma variação
desta árvore, é uma via clínica diferente.

**O DAPT score e o PRECISE-DAPT respondem perguntas diferentes e não são
intercambiáveis.** O PRECISE-DAPT (calculado no momento do implante) estima
risco de sangramento e orienta encurtar a DAPT; o DAPT score (calculado após
12 meses sem evento) estima o balanço risco-benefício de estender além de 12
meses — a árvore usa cada um no ponto de decisão correspondente.

**O acesso a teste de função plaquetária ou genotipagem CYP2C19 varia entre serviços.** Onde não
houver acesso a essas ferramentas, a diretriz também aceita desescalonamento
"não guiado" (troca empírica) em pacientes selecionados — a árvore descreve a
versão guiada como uma opção com evidência própria, sem superioridade universal, mas a ausência do teste não
impede a conduta.

**Ticagrelor em monoterapia após pelo menos um mês de DAPT**, em pacientes pós-SCA/ICP selecionados que toleraram o esquema, é estratégia recomendada na ACC/AHA2025 para reduzir sangramento. Não equivale a clopidogrel em monoterapia após um mês nem exige exclusivamente alto risco hemorrágico. A escolha considera risco isquêmico e tolerabilidade. Fonte: diretriz ACC/AHA2025 de SCA, DOI:10.1161/CIR.0000000000001309.

Evento isquêmico novo ou suspeita de trombose de stent exige avaliação imediata da causa e tratamento do evento; não se resolve apenas prolongando DAPT. Evitar desescalonamento rotineiro nos primeiros30dias após SCA. A ausência de indicação de extensão não determina automaticamente desescalonamento.
