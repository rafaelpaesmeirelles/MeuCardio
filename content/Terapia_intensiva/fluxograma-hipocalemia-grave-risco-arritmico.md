---
title: "Hipocalemia grave e risco arrítmico"
slug: fluxograma-hipocalemia-grave-risco-arritmico
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão conservadora para hipocalemia no adulto: ECG e sintomas definem urgência, magnésio é corrigido em paralelo, reposição oral é preferida quando possível e a única dose acelerada reproduzida é a da parada hipocalêmica conforme ERC 2025."
review_status: revisado
source_refs: ["Lott C, Karageorgos V, Abelairas-Gomez C, et al. European Resuscitation Council Guidelines 2025: Special Circumstances in Resuscitation. Resuscitation. 2025;215:110753. DOI: 10.1016/j.resuscitation.2025.110753. PMID: 41117569 — hipocalemia no adulto e esquema específico da parada cardíaca hipocalêmica.", "Resuscitation Council UK. Special circumstances Guidelines 2025 — resumo oficial que reproduz a recomendação ERC para hipocalemia e referencia o artigo primário.", "Krogager ML, Kragholm K, Tamargo J, Torp-Pedersen C. Update on management of hypokalaemia and goals for the lower potassium level in patients with cardiovascular disease. Eur Heart J Cardiovasc Pharmacother. 2021;7(6):557-567. DOI: 10.1093/ehjcvp/pvab038."]
legacy_source: "Fluxo novo criado em 23/08/2026 como complemento do protocolo hipocalemia-grave-risco-arritmico-e-reposicao-segura. Revisão documental independente concluída em 24/08/2026 com ERC 2025 e revisão do Working Group da ESC; doses de alto risco continuam sujeitas ao protocolo institucional."
review_note: "Revisão de 26/08/2026: removidos os alertas residuais após conferência do artigo primário ERC 2025 (PMID 41117569) e do resumo oficial do Resuscitation Council UK. O fluxo reproduz dose somente na parada hipocalêmica adulta (20 mmol IV/IO em 2–3 min, depois 10 mmol em 2 min); não extrapola esse esquema para peri-parada ou hipocalemia estável."
---

# Hipocalemia grave e risco arrítmico

> **STATUS DE CURADORIA: `revisado`.** Este fluxo mantém os esquemas de reposição acelerada isolados nos ramos peri-parada/parada e não deve ser usado como prescrição automática.

## Árvore de decisão

```mermaid
flowchart TD
  A["K⁺ < 3,5 mmol/L ou forte suspeita clínica"] --> B["ABCDE + repetir/confirmar K⁺ quando apropriado<br/>avaliar Mg²⁺, creatinina/eGFR, glicemia e causa"]
  B --> C{"K⁺ < 3,0 mmol/L,<br/>sintomas importantes ou risco arrítmico?"}
  C -->|"Não"| D["Preferir reposição oral quando tolerada<br/>+ corrigir causa/perdas<br/>+ reavaliar K⁺ e função renal"]
  C -->|"Sim"| E["ECG 12 derivações + monitorização do ritmo<br/>procurar onda U, T achatada/invertida,<br/>ST deprimido, PR prolongado e arritmias"]

  E --> F{"Parada cardíaca atribuída<br/>ou fortemente associada à hipocalemia?"}
  F -->|"Sim"| G["ALS + confirmar causa reversível;<br/>KCl 20 mmol IV/IO em 2–3 min,<br/>depois 10 mmol em 2 min;<br/>monitorar K⁺, ajustar a infusão e corrigir Mg²⁺"]

  F -->|"Não"| I{"Peri-parada, arritmia grave,<br/>fraqueza/paralisia importante<br/>ou K⁺ ≤ 2,4 mmol/L?"}
  I -->|"Sim"| J["Emergência: KCl IV em ambiente monitorizado;<br/>taxa e acesso conforme protocolo de infusão local;<br/>corrigir Mg²⁺ em paralelo quando baixo"]

  I -->|"Não"| L{"K⁺ 2,5–2,9 mmol/L<br/>e sintomático ou sem via oral?"}
  L -->|"Sim"| M["Reposição IV monitorizada<br/>+ tratar causa + corrigir Mg²⁺"]
  L -->|"Não"| D

  D --> N["Investigar mecanismo: renal/diurético,<br/>GI, deslocamento intracelular, baixa ingestão"]
  M --> N
  J --> N
  G --> N

  N --> O{"Contexto cardiovascular de alto risco?"}
  O -->|"Digoxina"| P["Conectar intoxicação digitálica<br/>e monitorizar arritmias"]
  O -->|"QT longo / TV polimórfica"| Q["Conectar torsades/QT longo<br/>e corrigir K⁺ + Mg²⁺"]
  O -->|"IC + diurético"| R["Rever estratégia diurética, congestão,<br/>função renal e terapia modificadora"]
  O -->|"HAS + hipocalemia"| S["Investigar aldosteronismo primário<br/>quando o fenótipo for compatível"]
  O -->|"Nenhum específico"| T["Seguimento etiológico e laboratorial"]
```

## Regras de segurança do fluxo

- **ECG e sintomas têm peso decisivo**; o valor isolado não captura todo o risco.
- A ERC 2025 recomenda ECG de 12 derivações e monitorização do ritmo quando **K⁺ <3,0 mmol/L**.
- **Magnésio baixo deve ser corrigido em paralelo.** Deficiência de magnésio agrava a hipocalemia e o risco elétrico.
- Reposição oral é preferível no paciente estável que tolera a via oral.
- Reposição IV rápida exige bomba, acesso apropriado, ECG e controles seriados; **não transformar esquemas de peri-parada/parada em rotina de enfermaria**.
- A dose acelerada do diagrama se aplica **somente ao adulto em parada cardíaca atribuída à hipocalemia**, dentro do ALS; não se aplica à hipocalemia estável nem é uma taxa de infusão de enfermaria.
- O alvo operacional de **K⁺ 4,0 mmol/L** aparece no algoritmo ERC 2025 para a correção aguda; não deve ser interpretado como meta rígida universal crônica.

## Escopo da posologia

A recomendação final da [ERC 2025](https://pubmed.ncbi.nlm.nih.gov/41117569/), também reproduzida no [resumo oficial do Resuscitation Council UK](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/special-circumstances-guidelines), especifica para a **parada cardíaca hipocalêmica adulta**: 20 mmol de KCl IV/IO em 2–3 minutos, seguidos de 10 mmol em 2 minutos; depois, monitorar K⁺ e ajustar a infusão. O fluxo não fornece dose acelerada para peri-parada sem PCR nem para reposição estável, pois esses contextos exigem concentração, acesso, bomba e monitorização definidos pelo protocolo local.

## Tudo com Tudo

- [Hipocalemia grave: risco arrítmico, causas e reposição segura](hipocalemia-grave-risco-arritmico-e-reposicao-segura.md)
- [Hipomagnesemia, risco arrítmico e hipocalemia refratária](hipomagnesemia-risco-arritmico-hipocalemia-refrataria-e-investigacao.md)
- [Torsades, QT longo adquirido e escore de Tisdale](../Arritmias/torsades-de-pointes-e-qt-longo-adquirido-escore-de-tisdale-e-manejo-agudo.md)
- [Intoxicação digitálica e anticorpo antidigoxina](../Arritmias/intoxicacao-digitalica-manejo-agudo-e-anticorpo-antidigoxina-fab.md)
- [Estratégia diurética na insuficiência cardíaca aguda](../Insuficiência_cardíaca/estrategia-diuretica-na-insuficiencia-cardiaca-aguda-descompensada.md)
- [Aldosteronismo primário e feocromocitoma: testes confirmatórios](../Hipertensão/aldosteronismo-primario-e-feocromocitoma-testes-confirmatorios-endocrine-society.md)
- [Hiperaldosteronismo primário subdiagnosticado](../Hipertensão/hiperaldosteronismo-primario-subdiagnosticado-prevalencia-real-e-rastreio-por-arr.md)

## Limites de evidência

A ERC 2025 é a fonte operacional mais atual encontrada para a situação aguda, mas o próprio documento esclarece que vários temas de circunstâncias especiais não foram submetidos a revisão ILCOR específica e que parte das recomendações é consenso do grupo apoiado por revisões adicionais/literatura selecionada. A revisão ESC 2021 sobre hipocalemia cardiovascular enfatiza que metas, frequência de monitorização e alguns detalhes de reposição carecem de ensaios randomizados robustos.
