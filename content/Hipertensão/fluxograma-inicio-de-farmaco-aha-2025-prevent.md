---
title: 'Fluxograma: iniciar fármaco na HAS — AHA/ACC 2025 e PREVENT ≥7,5%'
slug: fluxograma-inicio-de-farmaco-aha-2025-prevent
theme: Hipertensão
kind: fluxograma
review_status: revisado
source_refs:
- 'Jones DW et al. J Am Coll Cardiol. 2025;86(18):1567-1678. DOI: 10.1016/j.jacc.2025.05.007. PMID: 40815242.'
- 'Khan SS et al. Circulation. 2024;149(6):430-449. PMID: 37947085.'
review_note: 'Árvore confrontada com AHA2025: explicitados limiares sistólico OU diastólico, população não gestante, finalidade
  início e risco total; evitada suspensão por PA controlada. Conexões temáticas selecionadas e links por slugs da fila conferidos.'
summary: Aplicável ao início de tratamento em adultos não grávidos. PA já controlada com medicamento não implica suspensão.
  PREVENT estima risco cardiovascular total em 10 anos; usar na faixa etária elegível. Emergência hipertensiva requer protocolo
  próprio.
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: iniciar fármaco na HAS — AHA/ACC 2025 e PREVENT ≥7,5%

Aplicável ao início de tratamento em adultos não grávidos. PA já controlada com medicamento não implica suspensão. PREVENT estima risco cardiovascular total em 10 anos; usar na faixa etária elegível. Emergência hipertensiva requer protocolo próprio.

## Árvore de decisão

```mermaid
flowchart TD
  R0["PA de consultório confirmada fora do consultório"] --> D1{"Categoria"}
  D1 -->|"Menor que 130/80"| C1(["Estilo de vida. Sem fármaco por HAS neste degrau"])
  D1 -->|"PAS >=140 ou PAD >=90"| D2{"Fragilidade, institucionalização ou vida limitada?"}
  D2 -->|"Não"| C2(["Fármaco + estilo de vida. Meta menor que 130/80"])
  D2 -->|"Sim"| C3(["Fármaco com meta individualizada"])
  D1 -->|"130-139 ou 80-89"| D3{"DCV, AVC, diabetes, DRC ou PREVENT >=7,5%?"}
  D3 -->|"Sim"| D4{"Fragilidade, institucionalização ou vida limitada?"}
  D4 -->|"Não"| C4(["Fármaco + estilo de vida agora. Meta menor que 130/80"])
  D4 -->|"Sim"| C5(["Fármaco com meta individualizada"])
  D3 -->|"Não"| P1["Estilo de vida 3 a 6 meses"]
  P1 --> D5{"PAS permanece >=130 ou PAD >=80?"}
  D5 -->|"Não"| C6(["Manter estilo de vida e reavaliar"])
  D5 -->|"Sim"| C7(["Iniciar fármaco. Meta menor que 130/80"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## Tudo com Tudo

- [Equação PREVENT e o limiar de 7,5% na diretriz AHA/ACC 2025 de hipertensão](/biblioteca/equacao-prevent-aha-e-o-limiar-75-na-diretriz-2025)
- [ESC 2026 STAMP e PREVENT: duas portas de rastreio que o clínico geral não pode perder](/biblioteca/esc-2026-stamp-e-prevent-duas-portas-de-rastreio-que-o-clinico-geral-nao-pode-perder)
- [Alvo 140/90 na gestante — não é a meta 130/80](/biblioteca/alvo-140-90-na-gestante-nao-e-a-meta-130-80)
