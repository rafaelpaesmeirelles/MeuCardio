---
title: "Fluxograma: hipercalemia em uso de IECA, BRA ou espironolactona"
slug: fluxograma-hipercalemia-em-uso-de-ieca-bra-ou-espironolactona
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para hipercalemia associada a bloqueador do sistema renina-angiotensina-aldosterona (IECA, BRA, espironolactona ou eplerenona), separando estabilização de urgência, correção de causa reversível e a escolha entre suspender ou manter o fármaco com quelante de potássio quando a indicação tem alto valor prognóstico."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026: PMIDs conferidos. Corrigida a extrapolação de OPAL-HK/HARMONIZE, que demonstraram controle do potássio, mas não redução de mortalidade; retirada a manutenção automática do SRAA após hipercalemia grave e incorporado o limite de segurança do MRA. Mantida pendência de revisão médica antes da publicação clínica."
source_refs:
  - "Silva-Cardoso J, Brito D, Frazão JM, et al. Management of RAASi-associated hyperkalemia in patients with cardiovascular disease. Heart Fail Rev. 2021;26(4):891-896. PMID 33599908."
  - "Savarese G, Izquierdo MJ, Bonanad C, et al. Interdisciplinary recommendations for recurrent hyperkalaemia: insights from the GUARDIAN-HK European Steering Committee. Eur Heart J Cardiovasc Pharmacother. 2025;11(7):630-637. PMID 40685253."
  - "Weir MR, Bakris GL, Bushinsky DA, et al. Patiromer in patients with kidney disease and hyperkalemia receiving RAAS inhibitors (OPAL-HK). N Engl J Med. 2015;372(3):211-221. PMID 25415805."
  - "Kosiborod M, Rasmussen HS, Lavin P, et al. Effect of sodium zirconium cyclosilicate on potassium lowering for 28 days among outpatients with hyperkalemia: the HARMONIZE randomized clinical trial. JAMA. 2014;312(21):2223-2233. PMID 25402495."
---

# Fluxograma: hipercalemia em uso de IECA, BRA ou espironolactona

Hipercalemia associada ao bloqueio do sistema renina-angiotensina-aldosterona exige equilibrar a urgência do potássio com a indicação prognóstica do fármaco. OPAL-HK e HARMONIZE demonstraram que patiromer e ciclossilicato de sódio e zircônio reduzem e controlam o potássio; não foram desenhados para demonstrar redução de mortalidade. Na hipercalemia grave, o bloqueador deve ser interrompido temporariamente enquanto se estabiliza o paciente; eventual reintrodução é posterior, individualizada e monitorada.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Hipercalemia (K+ >5,5 mEq/L) em paciente em uso de<br/>IECA, BRA, espironolactona ou eplerenona"]
  D1{"Alteração eletrocardiográfica de hipercalemia (onda T apiculada,<br/>alargamento de QRS, perda de onda P, padrão sinusoidal), K+ ≥6,5 mEq/L<br/>ou arritmia/instabilidade hemodinâmica?"}
  X1["Estabilização de membrana e redistribuição imediatas:<br/>gluconato de cálcio 10% IV (se alteração de ECG); insulina regular IV<br/>+ glicose; beta-2 agonista inalatório em dose alta;<br/>considerar bicarbonato se acidose metabólica associada"]
  D2{"K+ e ECG normalizaram após as medidas de urgência?"}
  C1(["Repetir medidas temporizadoras e acionar nefrologia;<br/>indicar diálise urgente se hipercalemia for refratária,<br/>especialmente com insuficiência renal/oligoanúria;<br/>suspender temporariamente os bloqueadores do SRAA"])
  C2(["Manter bloqueadores do SRAA suspensos na fase aguda;<br/>corrigir causas e reavaliar K+ e função renal em 24–72h;<br/>considerar reintrodução monitorada somente após controle"])
  D4{"Há causa reversível evidente (dieta rica em potássio,<br/>lesão renal aguda, outro fármaco hipercalemiante,<br/>uso excessivo do bloqueador do SRAA)?"}
  C4(["Corrigir a causa reversível (ajuste dietético, tratar a LRA,<br/>suspender o outro hipercalemiante) mantendo o bloqueador<br/>do SRAA quando possível; reavaliar K+ em poucos dias"])
  D5{"A indicação do IECA/BRA/espironolactona tem alto valor<br/>prognóstico (ex.: ICFEr, nefropatia diabética)?"}
  C5(["Reduzir dose e considerar patiromer ou ciclossilicato para<br/>facilitar continuidade do SRAA; se K+ não puder ser mantido<br/>abaixo de 5,5 mEq/L, suspender MRA; não atribuir ao quelante<br/>benefício de mortalidade ainda não demonstrado"])
  C6(["Reduzir dose ou suspender o bloqueador do SRAA;<br/>reavaliar K+ e função renal em 48–72h e novamente<br/>após cada ajuste, conforme gravidade e função renal"])

  R0 --> D1
  D1 -->|"Sim — hipercalemia grave ou sintomática"| X1
  X1 --> D2
  D2 -->|"Não — hipercalemia refratária"| C1
  D2 -->|"Sim — estabilizado"| C2
  D1 -->|"Não — hipercalemia leve a moderada, assintomática,<br/>sem alteração de ECG"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não — hipercalemia persistente sem causa reversível clara"| D5
  D5 -->|"Sim"| C5
  D5 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C4,C5,C6 conduta;
```

## O que a árvore não mostra

- **Pseudo-hipercalemia por hemólise deve ser descartada** diante de valor limítrofe e inesperado, sobretudo sem alteração de ECG. Repetir a coleta corretamente, mas nunca atrasar estabilização quando houver alteração eletrocardiográfica, arritmia ou instabilidade.
- **Patiromer e ciclossilicato não substituem cálcio, insulina/glicose e remoção definitiva na emergência.** O ciclossilicato pode iniciar redução em horas, mas não deve ser usado como monoterapia na hipercalemia com alteração eletrocardiográfica ou instabilidade.
- **Gluconato de cálcio não reduz o potássio sérico** — estabiliza a membrana miocárdica por minutos, ganhando tempo para as medidas de redistribuição e remoção fazerem efeito; é preciso associar, não substituir.
- **O corte de K+ que justifica reintrodução do bloqueador do SRAA** varia por diretriz e por comorbidade — a árvore usa o critério prático de reavaliação em 24-72h ou 1-2 semanas, mas o limiar exato é decisão clínica individualizada.
- **Dieta com baixo teor de potássio e revisão de outros fármacos hipercalemiantes** (AINE, trimetoprima, suplementos de potássio) deveriam ser checados em todo paciente, não apenas no ramo de "causa reversível" — a árvore simplifica isso para manter a estrutura de decisão única.
- **Diálise de urgência exige acesso vascular e disponibilidade de máquina/equipe**, nem sempre imediatos — enquanto isso, as medidas de redistribuição continuam sendo repetidas.
