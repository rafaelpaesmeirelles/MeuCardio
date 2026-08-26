---
title: "Fluxograma: Infecção de bolsa de gerador — conduta"
slug: fluxograma-infeccao-de-bolsa-de-gerador-conduta
theme: "Dispositivos"
kind: fluxograma
fonte_producao: chatgpt
summary: "Diante de suspeita de infecção de bolsa de CIED, a árvore separa envolvimento sistêmico/endovascular e erosão — que exigem extração completa do sistema sem exceção — de achado limitado à bolsa, onde confirmação microbiológica decide entre extração e conduta conservadora do hematoma."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 28919379 (consenso HRS 2017 de manejo e extração de eletrodo de CIED, Kusumoto FM, Heart Rhythm 14(12):e503-e551) e 30883056 (WRAP-IT, Tarakji KG, NEJM 380(20):1895-1905). Título, revista, volume/página e autor conferidos contra o registro oficial antes de citar."
source_refs: ["2017 HRS expert consensus statement on cardiovascular implantable electronic device lead management and extraction · Heart Rhythm · 2017 · 14(12):e503-e551 · https://pubmed.ncbi.nlm.nih.gov/28919379/", "Antibacterial Envelope to Prevent Cardiac Implantable Device Infection (WRAP-IT) · New England Journal of Medicine · 2019 · 380(20):1895-1905 · https://pubmed.ncbi.nlm.nih.gov/30883056/"]
---

# Fluxograma: Infecção de bolsa de gerador — conduta

O ponto que a árvore protege é uma regra sem exceção do consenso HRS 2017:
**erosão do dispositivo através da pele é infecção do sistema**, mesmo sem
febre, sem hemocultura positiva e sem sinal florido de flogose — e infecção de
sistema, uma vez estabelecida, exige extração completa (gerador e todos os
eletrodos), nunca troca isolada do gerador ou desbridamento local mantendo o
eletrodo. A árvore percorre esse critério antes de qualquer outro, e só chega
à conduta conservadora quando infecção foi razoavelmente afastada.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de infecção de bolsa<br/>do CIED (eritema, drenagem,<br/>deiscência, dor local)"] --> D1{"Sinais sistêmicos (febre,<br/>calafrio, hemocultura positiva) ou<br/>envolvimento endovascular<br/>(vegetação em eletrodo/valva<br/>ao ecocardiograma)?"}

  D1 -->|"Sim"| C1(["Infecção sistêmica/endocardite<br/>relacionada ao dispositivo: extração<br/>completa do sistema (gerador e<br/>todos os eletrodos) e<br/>antibioticoterapia prolongada<br/>guiada por cultura"])

  D1 -->|"Não, achado<br/>aparentemente limitado à bolsa"| D2{"Erosão do gerador/eletrodo<br/>através da pele, ou deiscência<br/>da bolsa?"}

  D2 -->|"Sim"| C2(["Erosão equivale a infecção do<br/>sistema: extração completa do<br/>gerador e eletrodos, com<br/>antibioticoterapia"])

  D2 -->|"Não"| D3{"Confirmação microbiológica<br/>(cultura de secreção/hematoma)<br/>ou eritema/flogose evidente<br/>da bolsa?"}

  D3 -->|"Sim"| C3(["Infecção de bolsa confirmada:<br/>extração completa do sistema;<br/>reimplante contralateral só após<br/>controle da infecção"])

  D3 -->|"Não — achado inespecífico<br/>ou hematoma sem flogose"| D4{"Hematoma volumoso, ou<br/>paciente em anticoagulante/<br/>antiagregante?"}

  D4 -->|"Sim"| C4(["Conduta conservadora do<br/>hematoma: compressão, ajustar/<br/>suspender anticoagulação conforme<br/>risco, vigilância; considerar<br/>antibiótico profilático se risco<br/>elevado; reavaliar em 48-72h"])

  D4 -->|"Não"| C5(["Observação clínica ambulatorial e<br/>reavaliação precoce; sem indicação<br/>de extração neste momento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

**"Extração completa" significa gerador e todos os eletrodos, mesmo os
eletrodos abandonados de trocas anteriores.** O consenso HRS 2017 é explícito
em não aceitar extração parcial como tratamento de infecção de sistema —
deixar um eletrodo antigo para trás mantém o reservatório de biofilme que
sustenta a recorrência.

**O antibiótico profilático não substitui a decisão de extrair.** Quando a
árvore chega a "erosão" ou "infecção de bolsa confirmada", nenhum esquema de
antibiótico isolado é conduta aceitável — a extração é a intervenção
definidora, e o antibiótico é complemento, não alternativa.

**O envelope antibacteriano (WRAP-IT) é medida de prevenção no implante ou na
reintervenção, não de tratamento da infecção já instalada.** O ensaio reduziu
infecção maior de CIED em 40% em procedimentos de risco (trocas, upgrades,
revisões) — pertence à decisão de prevenir antes do procedimento seguinte, não
a esta árvore de manejo da infecção já suspeita.

**O momento do reimplante depois da extração** depende de hemocultura
negativa sustentada e ausência de vegetação residual, com prazos que variam
conforme o organismo isolado e a extensão do envolvimento — não está detalhado
na árvore por ser decisão de acompanhamento posterior à extração, não critério
de quando extrair.
