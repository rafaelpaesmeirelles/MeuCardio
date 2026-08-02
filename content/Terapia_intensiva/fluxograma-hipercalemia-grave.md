---
title: "Hipercalemia grave"
slug: fluxograma-hipercalemia-grave
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão da hipercalemia grave: o padrão do ECG — não só o valor numérico de potássio — decide se entra estabilização de membrana com cálcio, e a parada cardiorrespiratória muda o sal de cálcio indicado; redistribuição intracelular e remoção do potássio seguem em todos os ramos."
review_status: revisado
source_refs: ["Long B, Warix JR, Koyfman A. Controversies in Management of Hyperkalemia. J Emerg Med. 2018;55(2):192-205. DOI: 10.1016/j.jemermed.2018.04.004. PMID: 29731287 — revisão de manejo na emergência", "Kosiborod M, Rasmussen HS, Lavin P, Qunibi WY, Spinowitz B, et al. Effect of sodium zirconium cyclosilicate on potassium lowering for 28 days among outpatients with hyperkalemia: the HARMONIZE randomized clinical trial. JAMA. 2014;312(21):2223-2233. DOI: 10.1001/jama.2014.15688. PMID: 25402495 — NCT02088073, fase 3, 258 na fase aberta e 237 randomizados. NOTA: existe Erratum em JAMA 2015;313(5):526, sobre ERRO DE DOSE no texto, registrado mas NÃO lido nesta consulta"]
---

# Hipercalemia grave

Gatilho para este protocolo: **potássio sérico elevado**, **alteração no ECG**
ou **paciente sob bloqueio do SRAA** com hipercalemia. O eixo que separa as
condutas não é o número do potássio isolado — é **o padrão do ECG**, do
paciente sem alteração até o sine-wave, que é emergência com risco de parada
cardiorrespiratória (PCR) iminente.

## Árvore de decisão

```mermaid
flowchart TD
  R["Hipercalemia grave: potássio sérico elevado,<br/>especialmente sob bloqueio do SRAA —<br/>avaliar ECG imediatamente"]
  R --> D1

  D1{"ECG: qual o padrão predominante?"}
  D1 -->|"Sem alteração eletrocardiográfica"| S1
  D1 -->|"Onda T apiculada (alteração leve/moderada)"| D3
  D1 -->|"Alargamento de QRS, perda de onda P ou padrão sine-wave (emergência, risco de PCR iminente)"| D5

  S1["Redistribuição intracelular: insulina<br/>(regular ou análogo de ação curta) + dextrose/glicose IV,<br/>associada a beta-agonista"]
  S1 --> D2

  D2{"Função renal permite diurético<br/>e não há indicação de diálise?"}
  D2 -->|"Sim"| C1
  D2 -->|"Não — insuficiência renal grave ou refratária"| C2

  C1(["Remover potássio: diurético de alça ou tiazídico<br/>+ resina de troca (patiromer ou ciclossilicato<br/>de zircônio e sódio) para reforço da excreção"])
  C2(["Remover potássio: diálise — meio mais eficiente —<br/>associada a resina de troca (patiromer/ciclossilicato)<br/>enquanto se organiza o acesso"])

  D3{"Paciente já em parada cardiorrespiratória?"}
  D3 -->|"Não"| M1
  D3 -->|"Sim, em PCR"| M2

  M1["Estabilização de membrana:<br/>gluconato de cálcio a 10%, 10 mL IV"]
  M1 --> S2

  S2["Redistribuição intracelular: insulina + dextrose/glicose IV,<br/>associada a beta-agonista"]
  S2 --> D4

  D4{"Função renal permite diurético<br/>e não há indicação de diálise?"}
  D4 -->|"Sim"| C3
  D4 -->|"Não — insuficiência renal grave ou refratária"| C4

  C3(["Remover potássio: diurético de alça ou tiazídico<br/>+ resina de troca (patiromer ou ciclossilicato<br/>de zircônio e sódio)"])
  C4(["Remover potássio: diálise — meio mais eficiente —<br/>associada a resina de troca (patiromer/ciclossilicato)<br/>enquanto se organiza o acesso"])

  M2["Estabilização de membrana na parada: CLORETO de cálcio<br/>a 10%, 10 mL IV em bolus (não gluconato) + manobras de RCP"]
  M2 --> C5

  C5(["Redistribuição concomitante assim que possível<br/>(insulina + dextrose/glicose IV) e diálise emergencial<br/>ao retorno da circulação; seguir o protocolo de PCR<br/>para o restante do atendimento"])

  D5{"Paciente já em parada cardiorrespiratória?"}
  D5 -->|"Não"| M3
  D5 -->|"Sim, em PCR"| M4

  M3["Estabilização de membrana urgente: gluconato de cálcio<br/>a 10%, 10 mL IV, repetir se o ECG persistir alterado"]
  M3 --> S3

  S3["Redistribuição intracelular: insulina + dextrose/glicose IV,<br/>associada a beta-agonista"]
  S3 --> C6

  C6(["Remover potássio com urgência: diálise —<br/>meio mais eficiente — associada a resina de troca<br/>(patiromer/ciclossilicato) enquanto se organiza o acesso"])

  M4["Estabilização de membrana na parada: CLORETO de cálcio<br/>a 10%, 10 mL IV em bolus (não gluconato) + manobras de RCP"]
  M4 --> C7

  C7(["Redistribuição concomitante assim que possível<br/>(insulina + dextrose/glicose IV) e diálise emergencial<br/>ao retorno da circulação; seguir o protocolo de PCR<br/>para o restante do atendimento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que vale para todos os ramos, e por isso não está no diagrama

**Nunca usar poliestirenossulfonato de sódio** na hipercalemia aguda — a
revisão de Long et al. afirma literalmente que ele **não é eficaz**, apesar de
ainda ser prescrito por hábito na emergência.

**Monitorização seriada de glicemia** durante e depois da insulina IV, pela
hipoglicemia. **Potássio e ECG seriados** em todos os ramos, para reavaliar a
resposta e a necessidade de repetir a estabilização de membrana.

**Tratar a causa**: revisar e, em geral, suspender temporariamente o
bloqueador do SRAA que motivou ou agravou a hipercalemia, e investigar outras
causas (lesão renal aguda, rabdomiólise, acidose, hemólise) em paralelo ao
tratamento agudo.
