---
title: 'Fluxograma: interpretação dos ensaios históricos de GPI na SCA'
slug: fluxograma-gpi-pursuit-prism-plus-gusto-iv-early-acs
theme: Doença coronariana
kind: fluxograma
summary: Síntese dos ensaios PURSUIT, PRISM-PLUS, GUSTO-IV, EARLY-ACS e PARAGON. Distingue cenários, regimes e desfechos históricos,
  com limitações para aplicação como algoritmo de prescrição atual.
review_status: revisado
fonte_producao: grok
review_note: 'Revisados os cinco resumos primários completos: GUSTO-IV, EARLY-ACS, PRISM-PLUS, PARAGON e PURSUIT. Explicitados
  comparadores, tempos e propósito educacional; retirada interpretação categórica de caixas Não como proibição individual.
  Sinais tardios não substituem desfechos primários.'
source_refs:
- 'PURSUIT Investigators. N Engl J Med. 1998;339(7):436-443. PMID: 9705684.'
- 'PRISM-PLUS Investigators. N Engl J Med. 1998;338(21):1488-1497. PMID: 9599103.'
- 'Simoons ML. GUSTO IV-ACS. Lancet. 2001;357(9272):1915-1924. PMID: 11425411.'
- 'Giugliano RP, et al. EARLY ACS. N Engl J Med. 2009;360(21):2176-2190. PMID: 19332455.'
- 'PARAGON Investigators. Circulation. 1998;97(24):2386-2395. PMID: 9641689.'
- 'Rao SV et al. 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes. DOI:
  10.1161/CIR.0000000000001309. https://www.ahajournals.org/doi/pdf/10.1161/CIR.0000000000001309'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: interpretação dos ensaios históricos de GPI na SCA

```mermaid
flowchart TD
  R0["Qual cenário foi estudado para GPI (IIb/IIIa)?"] --> D1{"Onde?"}

  D1 -->|"Enfermaria, sem ida precoce ao cateter<br/>(GUSTO-IV ACS, abciximabe)"| C1(["Sem benefício significativo em morte/IAM aos 30 d<br/>Placebo 8,0%; abciximabe 24 h 8,2%; 48 h 9,1%"])

  D1 -->|"Infusão ≥12 h antes da angio<br/>(EARLY-ACS, eptifibatida)"| C2(["Sem superioridade: primário em 96 h<br/>9,3% vs 10,0% P=0,23<br/>Mais sangramento"])

  D1 -->|"Tirofibana sem heparina<br/>(PRISM-PLUS, braço isolado)"| C3(["Braço isolado interrompido por morte em 7 d<br/>4,6% vs 1,1%"])

  D1 -->|"Era 1998, heparina+AAS, eptifibatida<br/>(PURSUIT)"| C4(["Primário 14,2% vs 15,7% P=0,04<br/>Não é a prática 2026 de rotina"])

  D1 -->|"Lamifibana no tratamento clínico (PARAGON-A)"| C5(["Primário em 30 d sem diferença significativa<br/>P=0,668; sinal em 6 meses não substitui o primário"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Mensagem prática

**GUSTO-IV estudou tratamento sem revascularização precoce; EARLY-ACS comparou uso antecipado de rotina com uso seletivo em uma estratégia invasiva planejada.** Não são o mesmo cenário. Esses ensaios não estabelecem uso universal de GPI na prática contemporânea. A seleção de terapia na ICP deve seguir a diretriz vigente e o contexto angiográfico/hemorrágico. PRISM-PLUS não apoia tirofibana isolada sem anticoagulação no regime estudado. PURSUIT é evidência histórica e não um protocolo contemporâneo universal.

GPI significa inibidor da glicoproteína IIb/IIIa. As caixas resumem efeitos dos estudos, não são um algoritmo de prescrição ou contraindicação individual.

## Tudo com Tudo

- [PURSUIT: eptifibatida reduz morte ou IAM em 30 dias na SCA sem supra — 1,5 pp](/biblioteca/pursuit-eptifibatida-na-sca-sem-supra) — Conecta a interpretação do fluxograma ao ensaio PURSUIT, sua redução absoluta e contexto histórico de SCA sem supra.
