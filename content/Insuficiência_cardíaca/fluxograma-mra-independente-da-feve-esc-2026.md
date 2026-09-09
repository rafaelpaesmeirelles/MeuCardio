---
title: 'Fluxograma: ARM independente da FEVE — ESC 2026'
slug: fluxograma-mra-independente-da-feve-esc-2026
theme: Insuficiência cardíaca
kind: fluxograma
review_status: revisado
source_refs:
- Køber L et al. 2026 ESC Guidelines for the management of heart failure. Eur Heart J. 2026. DOI 10.1093/eurheartj/ehag100.
  PMID 42661420.
- Solomon SD, McMurray JJV, Vaduganathan M, et al.; FINEARTS-HF Investigators. Finerenone in Heart Failure with Mildly Reduced
  or Preserved Ejection Fraction. N Engl J Med. 2024;391:1475-1485. DOI 10.1056/NEJMoa2407107. PMID 39225278. NCT04435626.
- Damman K, Herrington WG, et al. 2026 ESC Guidelines for the management of cardiovascular disease and chronic kidney disease,
  in collaboration with the ERA. Eur Heart J. 2026. DOI 10.1093/eurheartj/ehag098. PMID 42661426.
- 'Solomon SD et al. Finerenone in heart failure with mildly reduced or preserved ejection fraction: Rationale and design
  of FINEARTS-HF. Eur J Heart Fail. 2024;26:1324–1333. https://academic.oup.com/eurjhf/article/26/6/1324/8328700'
- 'Heidenreich PA et al. 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure. DOI: 10.1016/j.jacc.2021.12.012.'
review_note: Fluxograma reconstruído para corrigir extrapolação perigosa de TFGe ≥25/K ≤5 a todo ARM. Separados esteroides
  >30/<5, finerenona FINEARTS, dose ≤60/>60, total do ensaio versus subgrupo ≥50 e indicação renal. Fontes primárias e tabelas
  ESC verificadas. Conexões temáticas selecionadas e links por slugs da fila conferidos.
summary: 'A ESC 2026 recomenda antagonista do receptor mineralocorticoide (ARM) na IC sintomática independentemente da FEVE,
  Classe I A: ARM esteroide na ICFEr e esteroide ou não esteroide na ICFEp. Na nomenclatura da diretriz, ICFEr corresponde
  a FEVE <50% e ICFEp a FEVE ≥50%. A escolha da molécula exige verificar sua evidência, indicação e segurança próprias.'
tags: []
source_tier: A
gaps: []
published: true
---

# Fluxograma: ARM independente da FEVE — ESC 2026

A ESC 2026 recomenda antagonista do receptor mineralocorticoide (ARM) na **IC sintomática independentemente da FEVE, Classe I A**: ARM esteroide na ICFEr e esteroide ou não esteroide na ICFEp. Na nomenclatura da diretriz, ICFEr corresponde a FEVE <50% e ICFEp a FEVE ≥50%. A escolha da molécula exige verificar sua evidência, indicação e segurança próprias.

## Árvore de decisão

```mermaid
flowchart TD
  A["IC sintomática: avaliar ARM e demais terapias indicadas"] --> B{"Fenótipo pela FEVE"}
  B -->|"FEVE <50%"| C["ARM esteroide na ICFEr"]
  B -->|"FEVE ≥50%"| D["ARM esteroide ou não esteroide na ICFEp"]
  C --> E{"Espironolactona/eplerenona: TFGe >30 e K <5,0?"}
  D -->|"Escolha de esteroide"| E
  D -->|"Escolha de finerenona"| F{"Critérios FINEARTS: TFGe ≥25 e K ≤5,0?"}
  E -->|"Sim e sem outras contraindicações"| G(["Iniciar/titular o ARM esteroide indicado e monitorar K e função renal"])
  E -->|"Não"| H(["Não iniciar por esta via. Corrigir fatores reversíveis e individualizar com especialista"])
  F -->|"Sim e indicação/bula compatíveis"| I(["Finerenona: seguir dose por TFGe, potássio e tolerância. Monitorar após início e titulação"])
  F -->|"Não"| J(["Fora da elegibilidade do FINEARTS; não extrapolar automaticamente o ensaio"])
  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f
  class G,H,I,J conduta
```

Os critérios de início de espironolactona/eplerenona acima são os de segurança da diretriz AHA/ACC/HFSA: **TFGe >30 mL/min/1,73 m² e K <5,0 mmol/L**. O corte renal ≥25 do FINEARTS **não deve ser aplicado a todo ARM**. Rever interações, suplementação de potássio, hipovolemia e função renal; não associar dois ARM. A monitorização acompanha o início e cada ajuste.

## O que FINEARTS-HF demonstrou

O ensaio incluiu **FEVE ≥40%**, portanto atravessa os dois fenótipos da nomenclatura ESC 2026. Seus números representam a população total, e não um subgrupo exclusivo de FEVE ≥50%: 6.001 participantes, seguimento mediano de 32 meses; 1.083 eventos primários em 624/3.003 com finerenona versus 1.283 em 719/2.998 com placebo. Razão de taxas **0,84 (IC95% 0,74–0,95), P=0,007**, para eventos totais de piora de IC ou morte cardiovascular. Morte CV isolada **8,1% vs 8,7%; HR 0,93 (0,78–1,11)**, sem redução estatisticamente demonstrada.

**Dose no protocolo:** TFGe ≤60: 10 mg/dia inicialmente e máximo 20 mg/dia; TFGe >60: 20 mg/dia inicialmente e máximo 40 mg/dia, condicionados a potássio e tolerância. O regime da indicação de DRC diabética é diferente; não transferir automaticamente a dose de 40 mg. Hipercalemia >6,0 mmol/L ocorreu em 3,0% vs 1,4%; hospitalização por hipercalemia em 0,5% vs 0,2%.

## Quando também existe DRC diabética

A ESC 2026 CVD-CKD recomenda finerenona em DM2 com DRC, TFGe ≥25 e RAC ≥30 mg/g (I A), respeitando potássio, bloqueio do SRAA indicado e segurança. Esta é a evidência cardiorrenal do FIDELIO/FIGARO, com critérios e doses próprios; não se funde seu composto renal com os eventos do FINEARTS. Finerenona não substitui iSGLT2.

## Tudo com Tudo

- [FINEARTS-HF: finerenona na IC com FEVE ≥40%](/biblioteca/finearts-hf-finerenona-ic-feve-maior-igual-40)
- [DAPA-HF não é DELIVER: FEVE reduzida não é preservada](/biblioteca/dapa-hf-nao-e-deliver-feve-reduzida-nao-e-preservada)
- [PARAGON-HF não é PARADIGM e não é PARADISE-MI](/biblioteca/paragon-hf-nao-e-paradigm-nem-e-paradise)
