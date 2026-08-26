---
title: "Fluxograma: hipercalemia em uso de IECA, BRA ou espironolactona"
slug: fluxograma-hipercalemia-em-uso-de-ieca-bra-ou-espironolactona
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para hipercalemia associada a bloqueador do sistema renina-angiotensina-aldosterona (IECA, BRA, espironolactona ou eplerenona), separando estabilização de urgência, correção de causa reversível e a escolha entre suspender ou manter o fármaco com quelante de potássio quando a indicação tem alto valor prognóstico."
review_status: revisado
review_note: "Verificado em 26/08/2026: PMIDs conferidos via PubMed E-utilities (esearch/esummary) — título, revista, volume e páginas batendo integralmente com o texto citado; nenhum PMID ou dado numérico foi inventado. Recomendação de preservar o bloqueador do SRAA com quelante de potássio em vez de suspender, quando a indicação tem alto valor prognóstico (ICFEr, nefropatia diabética), cruzada contra os artigos de revisão e consenso citados."
source_refs:
  - "Silva-Cardoso J, Brito D, Frazão JM, et al. Management of RAASi-associated hyperkalemia in patients with cardiovascular disease. Heart Fail Rev. 2021;26(4):891-896. PMID 33599908."
  - "Savarese G, Izquierdo MJ, Bonanad C, et al. Interdisciplinary recommendations for recurrent hyperkalaemia: insights from the GUARDIAN-HK European Steering Committee. Eur Heart J Cardiovasc Pharmacother. 2025;11(7):630-637. PMID 40685253."
  - "Weir MR, Bakris GL, Bushinsky DA, et al. Patiromer in patients with kidney disease and hyperkalemia receiving RAAS inhibitors (OPAL-HK). N Engl J Med. 2015;372(3):211-221. PMID 25415805."
  - "Kosiborod M, Rasmussen HS, Lavin P, et al. Effect of sodium zirconium cyclosilicate on potassium lowering for 28 days among outpatients with hyperkalemia: the HARMONIZE randomized clinical trial. JAMA. 2014;312(21):2223-2233. PMID 25402495."
---

# Fluxograma: hipercalemia em uso de IECA, BRA ou espironolactona

Hipercalemia associada a bloqueador do sistema renina-angiotensina-aldosterona é o motivo mais comum de suspensão precoce de um fármaco que reduz mortalidade — e a suspensão reflexa costuma ser a resposta errada. Quando a indicação tem alto valor prognóstico (insuficiência cardíaca com fração de ejeção reduzida, nefropatia diabética), a estratégia validada por ensaios como o OPAL-HK (patiromer) e o HARMONIZE (ciclossilicato de sódio e zircônio) é reduzir a dose e associar um quelante crônico de potássio, preservando o benefício do bloqueio do SRAA, em vez de simplesmente suspender.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Hipercalemia (K+ >5,5 mEq/L) em paciente em uso de<br/>IECA, BRA, espironolactona ou eplerenona"]
  D1{"Alteração eletrocardiográfica de hipercalemia (onda T apiculada,<br/>alargamento de QRS, perda de onda P, padrão sinusoidal), K+ ≥6,5 mEq/L<br/>ou arritmia/instabilidade hemodinâmica?"}
  X1["Estabilização de membrana e redistribuição imediatas:<br/>gluconato de cálcio 10% IV (se alteração de ECG); insulina regular IV<br/>+ glicose; beta-2 agonista inalatório em dose alta;<br/>considerar bicarbonato se acidose metabólica associada"]
  D2{"K+ e ECG normalizaram após as medidas de urgência?"}
  C1(["Terapia renal substitutiva de urgência (hemodiálise);<br/>suspender temporariamente IECA/BRA/espironolactona;<br/>acionar nefrologia"])
  D3{"Conduta em relação ao bloqueador do SRAA após estabilização?"}
  C2(["Suspender o bloqueador do SRAA; reavaliar K+ em 24-72h;<br/>considerar reintrodução em dose menor após correção,<br/>guiada pela indicação clínica (IC, nefroproteção)"])
  C3(["Iniciar patiromer ou ciclossilicato de sódio e zircônio como<br/>terapia crônica de remoção de potássio, mantendo o bloqueador<br/>do SRAA; monitorar K+ seriado"])
  D4{"Há causa reversível evidente (dieta rica em potássio,<br/>lesão renal aguda, outro fármaco hipercalemiante,<br/>uso excessivo do bloqueador do SRAA)?"}
  C4(["Corrigir a causa reversível (ajuste dietético, tratar a LRA,<br/>suspender o outro hipercalemiante) mantendo o bloqueador<br/>do SRAA quando possível; reavaliar K+ em poucos dias"])
  D5{"A indicação do IECA/BRA/espironolactona tem alto valor<br/>prognóstico (ex.: ICFEr, nefropatia diabética)?"}
  C5(["Reduzir a dose do bloqueador do SRAA e associar quelante<br/>de potássio (patiromer ou ciclossilicato de sódio e zircônio)<br/>em vez de suspender, para preservar o benefício de<br/>mortalidade/nefroproteção"])
  C6(["Reduzir a dose ou suspender o bloqueador do SRAA;<br/>reavaliar K+ e função renal em 1-2 semanas"])

  R0 --> D1
  D1 -->|"Sim — hipercalemia grave ou sintomática"| X1
  X1 --> D2
  D2 -->|"Não — hipercalemia refratária"| C1
  D2 -->|"Sim — estabilizado"| D3
  D3 -->|"Suspender temporariamente"| C2
  D3 -->|"Manter, com indicação forte de continuar (IC com FEr,<br/>nefroproteção), associando quelante de potássio"| C3
  D1 -->|"Não — hipercalemia leve a moderada, assintomática,<br/>sem alteração de ECG"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não — hipercalemia persistente sem causa reversível clara"| D5
  D5 -->|"Sim"| C5
  D5 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **Pseudo-hipercalemia por hemólise da amostra é a primeira coisa a descartar** diante de um valor limítrofe e inesperado, sobretudo sem alteração de ECG — repetir a coleta sem torniquete prolongado antes de agir sobre um número isolado.
- **Patiromer e ciclossilicato de sódio e zircônio levam horas a dias para reduzir o potássio de forma relevante** — não servem para a fase aguda/grave, que depende das medidas de estabilização de membrana e redistribuição.
- **Gluconato de cálcio não reduz o potássio sérico** — estabiliza a membrana miocárdica por minutos, ganhando tempo para as medidas de redistribuição e remoção fazerem efeito; é preciso associar, não substituir.
- **O corte de K+ que justifica reintrodução do bloqueador do SRAA** varia por diretriz e por comorbidade — a árvore usa o critério prático de reavaliação em 24-72h ou 1-2 semanas, mas o limiar exato é decisão clínica individualizada.
- **Dieta com baixo teor de potássio e revisão de outros fármacos hipercalemiantes** (AINE, trimetoprima, suplementos de potássio) deveriam ser checados em todo paciente, não apenas no ramo de "causa reversível" — a árvore simplifica isso para manter a estrutura de decisão única.
- **Diálise de urgência exige acesso vascular e disponibilidade de máquina/equipe**, nem sempre imediatos — enquanto isso, as medidas de redistribuição continuam sendo repetidas.