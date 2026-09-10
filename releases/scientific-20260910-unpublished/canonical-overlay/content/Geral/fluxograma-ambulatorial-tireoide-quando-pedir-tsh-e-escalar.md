---
slug: fluxograma-ambulatorial-tireoide-quando-pedir-tsh-e-escalar
title: 'Fluxograma ambulatorial: tireoide no retorno cardiológico — quando pedir TSH e escalar'
kind: fluxograma
theme: Geral
summary: 'Fluxograma de investigação tireoidiana no retorno cardiológico: reconhecimento de emergência, interpretação
  de TSH e hormônios, avaliação especializada e seguimento específico da amiodarona.'
tags: []
source_refs:
- 'Garber JR et al. Clinical practice guidelines for hypothyroidism in adults. Endocr Pract. 2012;18:988-1028. DOI:
  10.4158/EP12280.GL. PMID: 23246686.'
- 'Klein I, Danzi S. Thyroid disease and the heart. Circulation. 2007;116(15):1725-1735. DOI: 10.1161/CIRCULATIONAHA.106.678326.
  PMID: 17923583'
- 'Ross DS, Burch HB, Cooper DS, et al. 2016 American Thyroid Association Guidelines for Diagnosis and Management
  of Hyperthyroidism and Other Causes of Thyrotoxicosis. Thyroid. 2016;26(10):1343-1421. DOI: 10.1089/thy.2016.0229.
  PMID: 27521067'
- 'Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation.
  Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176'
- 'Jabbar A, Pingitore A, Pearce SH, Zaman A, Iervasi G, Razvi S. Thyroid hormones and cardiovascular disease. Nat
  Rev Cardiol. 2017;14(1):39-55. DOI: 10.1038/nrcardio.2016.174. PMID: 27811932'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: tireoide — quando pedir TSH e escalar

Prosa: [`sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico`](/biblioteca/sinalizadores-ambulatoriais-de-disfuncao-tireoidiana-no-retorno-cardiologico). Checklist: [`checklist-ambulatorial-tireoide-no-paciente-cardiologico`](/biblioteca/checklist-ambulatorial-tireoide-no-paciente-cardiologico). Amiodarona: [monitoramento clínico da amiodarona](/biblioteca/fluxograma-monitoramento-amiodarona-ambulatorial).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Retorno cardiológico<br/>FA / HAS / IC / bradicardia / LDL / derrame"] --> DU{"Síndrome clínica grave de tireoide?"}
  DU -->|"Sim"| CU["Emergência: não esperar laboratório"]
  DU -->|"Não"| D0{"Usa amiodarona?"}

  D0 -->|"Sim"| C0(["Ir ao pacote de monitoramento<br/>amiodarona e disfunção tireoidiana"])

  D0 -->|"Não"| D1{"Há pista clínica ou fenótipo<br/>que dispara TSH?"}

  D1 -->|"Não"| C1(["Plano CV habitual<br/>Não medicalizar TSH<br/>sem indicação"])

  D1 -->|"Sim"| P1["Dosar TSH<br/>(+ T4 livre se TSH anormal)"]
  P1 --> D2{"Resultado"}

  D2 -->|"TSH normal"| C2(["Buscar outra causa CV<br/>Reavaliar se nova pista"])

  D2 -->|"Sugere hipo"| D3{"Sinais de gravidade?<br/>hipotermia, rebaixamento,<br/>hipotensão, hipoventilação"}
  D3 -->|"Sim"| C3(["Emergência / UTI<br/>Coma mixedematoso —<br/>ver verbete hipotireoidismo"])
  D3 -->|"Não"| C4(["Confirmar padrão e persistência;<br/>decidir indicação de reposição<br/>com endocrino/clínico<br/>Ajustar expectativas CV<br/>(bradicardia, LDL, derrame pericárdico)"])

  D2 -->|"Sugere hiper / tireotoxicose"| D4{"Instabilidade CV OU disfunção sistêmica?<br/>hipertermia, alteração mental, GI/hepática grave<br/>IC/taquiarritmia com repercussão"}
  D4 -->|"Sim"| C5(["Estabilizar + lab urgente<br/>+ endocrino<br/>Não só subir betabloqueador"])
  D4 -->|"Não"| C6(["Endocrino para tipagem<br/>e terapia<br/>Plano de ritmo/FA em paralelo<br/>(ESC 2024); cardioversão:<br/>doc FA+subclínico"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class CU,C3,C5 alerta;
  class C0,C1,C2,C4,C6 conduta;
```

## Notas

- **D0**: amiodarona tem calendário e decisões próprios, após excluir emergência.
- **D1**: filtro de probabilidade (Klein/Danzi; Jabbar) — não TSH universal.
- **D2/D4**: ATA 2016 ancora tireotoxicose como causa tratável; ESC 2024 FA pede causa precipitante.
- Não decide dose de levotiroxina, tionamida, I-131 nem suspende GDMT automaticamente.

## Interpretar a síndrome, não o TSH isolado

TSH baixo com FA estável não é tempestade tireotóxica; esta exige tireotoxicose grave com disfunção sistêmica, incluindo hipertermia, alteração mental e manifestações GI/hepáticas/cardíacas. TSH alto isolado não é coma mixedematoso: suspeitar pela síndrome de hipotermia, alteração de consciência, hipoventilação, hipotensão/bradicardia grave em contexto apropriado. Não esperar laboratório para estabilizar suspeita clínica grave.

TSH normal não exclui hipotireoidismo central quando houver doença hipofisária ou suspeita clínica; nesse cenário, avaliar T4 livre. TSH anormal exige T4 livre; em TSH suprimido com T4 livre normal/inconclusivo, considerar T3 total. Doença sistêmica aguda e fármacos alteram exames; não iniciar tratamento crônico por resultado isolado sem contexto. Bradicardia, LDL alto e derrame pericárdico são inespecíficos. Repetir exames recentes se mudança clínica, gestação, amiodarona/lítio ou interferentes. FA segue seu algoritmo de ritmo/frequência e anticoagulação: não atrasar OAC indicada esperando eutireoidismo; cardioversão eletiva é individualizada.

[Disfunção tireoidiana por amiodarona](/biblioteca/disfuncao-tireoidiana-associada-a-amiodarona-diferenciar-tipo-1-de-tipo-2-e-decidir-sobre-suspender).
