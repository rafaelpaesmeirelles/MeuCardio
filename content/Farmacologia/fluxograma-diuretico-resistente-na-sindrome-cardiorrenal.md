---
title: "Fluxograma: diurético resistente na síndrome cardiorrenal"
slug: fluxograma-diuretico-resistente-na-sindrome-cardiorrenal
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para escalonar o tratamento diurético na insuficiência cardíaca descompensada com síndrome cardiorrenal e resposta inadequada à furosemida IV, incluindo bloqueio sequencial do néfron com acetazolamida (estratégia ADVOR) e tiazídico, e o critério para encaminhar a ultrafiltração."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026: PMIDs conferidos e protocolo ADVOR revisto. Corrigidos dose/população da acetazolamida (500 mg IV/dia; eGFR ≥20; sem acidose metabólica), uso de inotrópico restrito a hipoperfusão/choque, separação entre tiazídico e hiponatremia e lugar não rotineiro da ultrafiltração. Mantida pendência de revisão médica antes da publicação clínica."
source_refs:
  - "Mullens W, Damman K, Harjola VP, et al. The use of diuretics in heart failure with congestion — a position statement from the Heart Failure Association of the European Society of Cardiology. Eur J Heart Fail. 2019;21(2):137-155. PMID 30600580."
  - "Mullens W, Dauw J, Martens P, et al. Acetazolamide in Acute Decompensated Heart Failure with Volume Overload (ADVOR). N Engl J Med. 2022;387(13):1185-1195. PMID 36027559."
  - "Ronco C, McCullough P, Anker SD, et al. Cardio-renal syndromes: report from the consensus conference of the Acute Dialysis Quality Initiative. Eur Heart J. 2010;31(6):703-711. PMID 20037146."
---

# Fluxograma: diurético resistente na síndrome cardiorrenal

Quando a furosemida IV não produz diurese suficiente num paciente com insuficiência cardíaca descompensada, o primeiro passo é confirmar administração e escalonamento adequados do diurético de alça. Se a resposta continuar insuficiente, o **bloqueio sequencial do néfron** associa um segundo diurético em outro segmento tubular — acetazolamida no túbulo proximal ou tiazídico no túbulo distal — com monitorização estreita. Ultrafiltração não é o degrau automático seguinte e fica reservada a casos selecionados, refratários ou com indicação dialítica.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Insuficiência cardíaca descompensada com síndrome cardiorrenal<br/>e resposta diurética inadequada à furosemida IV em dose otimizada"]
  X1["Confirmar dose e via adequadas: furosemida IV em bolus repetido<br/>ou infusão contínua, em dose equivalente a pelo menos 2-2,5×<br/>a dose oral domiciliar; reavaliar diurese em 2-6h e balanço hídrico"]
  D1{"A resposta diurética permanece inadequada (diurese <100-150 mL/h<br/>ou sódio urinário pontual <50-70 mEq/L) após otimização<br/>da dose de furosemida?"}
  C1(["Manter a furosemida IV otimizada até euvolemia;<br/>transicionar para via oral quando estável"])
  D2{"Há piora aguda da função renal com sinais de baixo débito<br/>predominando sobre a congestão?"}
  C2(["Se houver choque/hipoperfusão, encaminhar à UTI e<br/>considerar inotrópico conforme o perfil hemodinâmico;<br/>não usar inotrópico apenas para 'melhorar a perfusão renal'"])
  D3{"eGFR ≥20 mL/min/1,73m², pressão adequada e<br/>ausência de acidose metabólica ou outra<br/>contraindicação à acetazolamida?"}
  C3(["Associar acetazolamida 500 mg IV 1x/dia à furosemida<br/>(regime e população estudados no ADVOR);<br/>monitorar bicarbonato, eletrólitos e função renal"])
  D4{"Há hiponatremia dilucional clinicamente relevante?"}
  C4(["Considerar tolvaptana em paciente selecionado para<br/>correção de hiponatremia/congestão, sem atribuir<br/>benefício de mortalidade; monitorar sódio de perto"])
  C7(["Associar tiazídico ou diurético tiazídico-símile para<br/>bloqueio distal; monitorar sódio, potássio, magnésio<br/>e função renal de forma seriada"])
  D5{"A congestão refratária persiste apesar do bloqueio<br/>sequencial do néfron (alça + tiazídico ou acetazolamida)?"}
  C5(["Discutir com nefrologia ultrafiltração/terapia renal<br/>substitutiva se persistir congestão verdadeiramente refratária<br/>ou houver outra indicação dialítica; não usar de rotina"])
  C6(["Manter o esquema de bloqueio sequencial até euvolemia,<br/>com reavaliação diária de peso, função renal e eletrólitos"])

  R0 --> X1
  X1 --> D1
  D1 -->|"Não — resposta adequada após otimização"| C1
  D1 -->|"Sim — resistência diurética confirmada"| D2
  D2 -->|"Sim — baixo débito predominante"| C2
  D2 -->|"Não — congestão predominante sem baixo débito"| D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| D4
  C3 --> D5
  D4 -->|"Sim"| C4
  D4 -->|"Não"| C7
  C4 --> D5
  C7 --> D5
  D5 -->|"Sim — refratária"| C5
  D5 -->|"Não"| C6

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

- **A síndrome cardiorrenal tem cinco subtipos** pela classificação da ADQI (agudo/crônico, cardiorrenal/renocardíaco, sistêmico) — esta árvore trata do manejo prático do diurético resistente à beira do leito, não da classificação etiológica completa do subtipo.
- **Piora transitória de creatinina durante descongestionamento agressivo** ("pseudo-piora renal") não deve, sozinha, interromper a diurese em paciente ainda congesto — a decisão de reduzir diurético pelo aumento de creatinina precisa considerar o contexto de volume, não só o número.
- **Monitorização eletrolítica é obrigatória e mais frequente** com bloqueio sequencial do néfron do que com furosemida isolada — hipopotassemia, hipomagnesemia e alcalose metabólica são riscos reais da combinação, e a árvore não substitui a rotina de eletrólitos seriados.
- **Disponibilidade de ultrafiltração varia muito entre serviços** — o encaminhamento do último ramo pode não ser factível em tempo hábil em todo hospital, e a decisão prática às vezes é manter otimização clínica enquanto se organiza a transferência.
- **Albumina associada à furosemida não é estratégia rotineira validada.** Hipoalbuminemia e síndrome nefrótica exigem avaliação individual, sem presumir benefício clínico da infusão de albumina.
