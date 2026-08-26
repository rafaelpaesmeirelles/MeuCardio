---
title: "Fluxograma: intoxicação por betabloqueador ou bloqueador de canal de cálcio"
slug: fluxograma-intoxicacao-por-betabloqueador-ou-bloqueador-de-canal-de-calcio
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para intoxicação aguda por betabloqueador ou bloqueador de canal de cálcio com bradicardia e/ou hipotensão, escalonando de atropina e cálcio IV até insulina em altas doses (HIET), emulsão lipídica ou glucagon conforme a resposta e o fármaco predominante."
review_status: revisado
review_note: "Verificado em 26/08/2026: PMIDs conferidos via PubMed E-utilities (esearch/esummary) — título, revista, volume e páginas batendo integralmente com o texto citado; nenhum PMID ou dado numérico foi inventado. Sequência de escalonamento terapêutico (cálcio/atropina → insulina em altas doses → emulsão lipídica/glucagon/suporte mecânico) cruzada contra a atualização focada da AHA sobre parada cardíaca e toxicidade e os dois consensos de intoxicação citados."
source_refs:
  - "Lavonas EJ, Akpunonu PD, Arens AM, et al. 2023 American Heart Association Focused Update on the Management of Patients With Cardiac Arrest or Life-Threatening Toxicity Due to Poisoning. Circulation. 2023;148(16):e149-e184. PMID 37721023."
  - "St-Onge M, Anseeuw K, Cantrell FL, et al. Experts Consensus Recommendations for the Management of Calcium Channel Blocker Poisoning in Adults. Crit Care Med. 2017;45(3):e306-e315. PMID 27749343."
  - "Engebretsen KM, Kaczmarek KM, Morgan J, Holger JS. High-dose insulin therapy in beta-blocker and calcium channel-blocker poisoning. Clin Toxicol (Phila). 2011;49(4):277-283. PMID 21563902."
---

# Fluxograma: intoxicação por betabloqueador ou bloqueador de canal de cálcio

Intoxicação por betabloqueador ou bloqueador de canal de cálcio é uma das poucas emergências toxicológicas cardiovasculares em que o antídoto de primeira linha não é o mais óbvio: atropina e cálcio IV costumam ser insuficientes sozinhos, e o próximo degrau — insulina em altas doses (HIET) — soa contraintuitivo até se entender que ambas as classes de fármaco prejudicam a utilização miocárdica de glicose, e a insulina em dose supra-fisiológica restaura o inotropismo por essa via, além do efeito hemodinâmico direto. A atualização focada da AHA de 2023 sobre parada cardíaca e toxicidade formaliza esse escalonamento como abordagem baseada em evidência, não em experiência anedótica.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de intoxicação aguda por betabloqueador ou bloqueador<br/>de canal de cálcio (bradicardia e/ou hipotensão após<br/>ingestão ou uso excessivo)"]
  X1["Medidas iniciais: ABC, monitorização contínua, acesso venoso,<br/>ECG de 12 derivações, glicemia capilar; considerar carvão ativado<br/>se ingestão há menos de 1-2h e via aérea protegida;<br/>contato com centro de toxicologia"]
  D1{"Instabilidade hemodinâmica (hipotensão sintomática,<br/>bradicardia com hipoperfusão, ou choque)?"}
  C1(["Observação e monitorização cardíaca contínua por pelo menos<br/>6h (formulação de liberação imediata) ou 24h (liberação prolongada<br/>ou bloqueador de canal de cálcio diidropiridínico, pelo risco<br/>de deterioração tardia)"])
  X2["Atropina IV 0,5-1 mg (pode repetir); cálcio IV (gluconato<br/>ou cloreto de cálcio) em bolus, especialmente se bloqueador<br/>de canal de cálcio"]
  D2{"A resposta hemodinâmica permanece inadequada após<br/>atropina e cálcio IV?"}
  C2(["Manter monitorização intensiva; repetir cálcio IV conforme<br/>necessário; observar quanto à recorrência de instabilidade"])
  X3["Iniciar terapia com insulina em altas doses (HIET):<br/>bolus de insulina regular 1 U/kg + glicose, seguido de infusão<br/>de insulina 0,5-1 U/kg/h titulada até 10 U/kg/h, com reposição<br/>agressiva de glicose e potássio"]
  D3{"Há resposta hemodinâmica adequada à HIET após tempo<br/>suficiente para efeito (15-60 minutos)?"}
  C3(["Manter a HIET com monitorização glicêmica e de potássio<br/>horária; associar vasopressor (noradrenalina) se ainda houver<br/>componente vasodilatado"])
  D4{"Predomínio de bloqueador de canal de cálcio não<br/>diidropiridínico na suspeita ou na história de ingestão?"}
  C4(["Considerar emulsão lipídica IV (bolus seguido de infusão)<br/>como resgate; suporte circulatório mecânico (ECMO) se<br/>disponível e choque refratário"])
  C5(["Considerar glucagon IV em bolus seguido de infusão;<br/>marca-passo transcutâneo ou transvenoso se bradicardia<br/>refratária; suporte circulatório mecânico (ECMO)<br/>se choque refratário"])

  R0 --> X1
  X1 --> D1
  D1 -->|"Não — estável, apenas bradicardia leve ou assintomática"| C1
  D1 -->|"Sim — instável"| X2
  X2 --> D2
  D2 -->|"Não — resposta adequada"| C2
  D2 -->|"Sim — refratário"| X3
  X3 --> D3
  D3 -->|"Sim"| C3
  D3 -->|"Não — choque refratário"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não — predomínio de betabloqueador"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **Coingestão com outros cardiotóxicos** (antidepressivo tricíclico, digoxina) muda o manejo — cada classe tem antídoto/estratégia própria, e a intoxicação mista exige abordagem combinada não detalhada aqui.
- **Formulações de liberação prolongada podem causar deterioração súbita e tardia**, mesmo após período inicial de estabilidade — a observação de 24h no ramo estável não é opcional para esses casos.
- **A HIET exige monitorização glicêmica horária e reposição agressiva de potássio**, com risco real de hipoglicemia e hipopotassemia graves se a infusão for interrompida abruptamente sem desmame — a árvore não detalha o protocolo de desmame.
- **Emulsão lipídica IV tem maior corpo de evidência para bloqueador de canal de cálcio lipofílico** (verapamil, especialmente) do que para betabloqueador; a recomendação para predomínio de betabloqueador é mais fraca e baseada em relato de caso.
- **Carvão ativado só deve ser considerado com via aérea protegida e ingestão recente** — em paciente já bradicárdico/hipotenso ou com rebaixamento de consciência, o risco de aspiração pode superar o benefício.
- **Disponibilidade de ECMO é limitada** e a decisão de acioná-la depende de estrutura local e tempo de transporte — não é uma opção universalmente disponível no momento do choque refratário.