---
title: "Fluxograma: cardiotoxicidade grave por bloqueador de canal de sódio (AHA 2025)"
slug: fluxograma-cardiotoxicidade-bloqueador-canal-sodio-aha-2025
theme: "Farmacologia"
kind: fluxograma
summary: "Árvore de decisão para QRS largo, hipotensão, arritmia ventricular ou parada por antidepressivo tricíclico e outros bloqueadores de canal de sódio, com bicarbonato e escalonamento precoce."
tags: ["intoxicação", "bloqueador de canal de sódio", "antidepressivo tricíclico", "QRS largo", "bicarbonato de sódio", "lidocaína", "VA-ECMO"]
review_status: revisado
review_note: "Recomendações e classes conferidas no capítulo oficial AHA 2025 em 26/08/2026. O fluxo não inclui doses: preparação, metas laboratoriais e repetição devem seguir protocolo institucional e orientação toxicológica em tempo real."
source_refs: ["Cao D, Arens AM, Chow SL, et al. Part 10: Adult and Pediatric Special Circumstances of Resuscitation: 2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation and Emergency Cardiovascular Care. Circulation. 2025;152(16_suppl_2):S578-S672. DOI: 10.1161/CIR.0000000000001380. PMID: 41122889.", "American Heart Association. Part 10: Adult and Pediatric Special Circumstances of Resuscitation — seção Toxicology: Sodium Channel Blockers, 2025. https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-and-pediatric-special-circumstances-of-resuscitation"]
legacy_source: "Lacuna comprovada em 26/08/2026: havia documento geral sobre intoxicação exógena, conteúdo específico sobre antidepressivos tricíclicos e monografias de flecainida/propafenona, mas nenhum fluxograma dedicado ao fenótipo de bloqueio de canal de sódio."
---

# Cardiotoxicidade grave por bloqueador de canal de sódio

```mermaid
flowchart TD
  A["Exposição suspeita ou conhecida<br/>+ QRS largo, hipotensão, convulsão,<br/>arritmia ventricular ou parada"]
  B["Suporte padrão imediato:<br/>via aérea, ventilação, RCP/desfibrilação<br/>e vasopressor conforme o cenário"]
  C["Acionar toxicologista/centro de informação toxicológica<br/>+ ECG seriado + gasometria + eletrólitos"]
  D{"Antidepressivo tricíclico/tetracíclico<br/>ou outro bloqueador de canal de sódio<br/>com cardiotoxicidade de risco de vida?"}
  E["Administrar bicarbonato de sódio<br/>conforme protocolo toxicológico"]
  F{"Paciente está em ventilação mecânica<br/>e cardiotoxicidade persiste?"}
  G["Considerar hiperventilação controlada<br/>em conjunto com bicarbonato;<br/>monitorar pH e sódio"]
  H{"Arritmia grave por agente classe Ia/Ic<br/>persiste apesar do tratamento inicial?"}
  I["Lidocaína pode ser considerada<br/>com orientação especializada"]
  J{"Choque cardiogênico ou arritmia<br/>permanece refratária?"}
  K["Acionar precocemente centro com ECLS/VA-ECMO<br/>e discutir candidatura sem esperar colapso irreversível"]
  L["Emulsão lipídica IV pode ser considerada<br/>apenas se refratário a outras modalidades<br/>e no contexto toxicológico adequado"]
  M["Estabilização: ECG e perfusão seriados,<br/>vigilância de recorrência e complicações iatrogênicas"]
  X["Reavaliar causas alternativas de QRS largo/choque<br/>e seguir o protocolo específico do agente identificado"]

  A --> B --> C --> D
  D -->|"Sim"| E --> F
  D -->|"Não ou incerto"| X
  F -->|"Sim"| G --> H
  F -->|"Não"| H
  H -->|"Sim"| I --> J
  H -->|"Não"| J
  J -->|"Sim"| K --> L --> M
  J -->|"Não"| M
```

## Como interpretar as caixas

- Para adultos com cardiotoxicidade de risco de vida por antidepressivo tricíclico ou tetracíclico, bicarbonato de sódio é recomendação classe 1, nível B-NR. Para outros bloqueadores de canal de sódio em adultos e crianças, é razoável (classe 2a, C-EO).
- Em paciente já intubado, hiperventilação em conjunto com bicarbonato é razoável (classe 2a, C-LD). Isso não autoriza alcalose sem controle: pH, sódio, potássio e resposta do QRS precisam ser acompanhados.
- Lidocaína, um antiarrítmico classe Ib, pode ser considerada para cardiotoxicidade por agentes classe Ia ou Ic (classe 2b, C-EO). Não é uma etapa universal para todo QRS largo.
- ECLS/VA-ECMO é razoável no choque cardiogênico refratário (classe 2a, C-EO). Emulsão lipídica tem recomendação mais fraca e fica reservada a toxicidade refratária a outras modalidades (classe 2b, C-EO).

## Fronteiras do fluxo

Cocaína e anestésicos locais também bloqueiam canais de sódio, mas possuem toxíndromes e recomendações próprias na diretriz. O fluxo acima é centrado em antidepressivos tricíclicos/tetracíclicos e outros agentes com fenótipo semelhante; não deve apagar a investigação de isquemia/hiperadrenergia por cocaína nem o manejo específico da toxicidade sistêmica por anestésico local.

## Tudo com Tudo

- [Diretriz AHA 2025: intoxicações cardiotóxicas graves](diretriz-aha-2025-intoxicacoes-cardiotoxicas-graves.md)
- [Cardiotoxicidade por tricíclicos, organofosforados e cloroquina](../Terapia_intensiva/cardiotoxicidade-intoxicacao-exogena-triciclicos-organofosforados-cloroquina.md)
- [Antidepressivos tricíclicos no cardiopata](../Saúde_mental_e_cardiologia/antidepressivos-triciclicos-no-cardiopata-risco-cardiovascular-e-toxicidade-em-superdosagem.md)
- [Flecainida](flecainida.md)
- [Propafenona](propafenona-cloridrato.md)
- [Cardiotoxicidade aguda por cocaína](../Terapia_intensiva/cardiotoxicidade-aguda-por-cocaina-vasoespasmo-bloqueio-de-canal-de-sodio-e-por-que-nao-usar-betabloqueador-isolado.md)
- [Taquicardia de QRS largo sem diagnóstico estabelecido](../Arritmias/fluxograma-taquicardia-de-qrs-largo-esc-2019.md)
- [Parada cardiorrespiratória no adulto](../Terapia_intensiva/fluxograma-parada-cardiorrespiratoria-ritmo-inicial.md)

## Limite operacional

Intoxicação grave é uma emergência dinâmica. O ECG e a pressão podem piorar rapidamente, e a dose total necessária de terapia varia. Este fluxograma organiza prioridades e escalonamento; não substitui orientação toxicológica, tabela de doses, monitorização intensiva ou protocolo local.
