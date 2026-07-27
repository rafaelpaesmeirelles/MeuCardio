---
title: "Fluxograma: Síndrome aórtica aguda — da dor torácica ao tratamento (ESC 2024)"
slug: fluxograma-sindrome-aortica-aguda-esc-2024
theme: "Aorta e doença arterial periférica"
kind: fluxograma
summary: "Caminho decisório da suspeita de síndrome aórtica aguda: escore ADD-RS combinado ao D-dímero para selecionar quem vai à imagem, angio-TC sincronizada ao ECG do pescoço à pelve como exame de primeira linha, e a separação de conduta entre tipo A e tipo B."
review_status: revisado
source_refs: ["2024 ESC Guidelines for the management of peripheral arterial and aortic diseases · European Heart Journal · 2024 · 45(36):3538-3700 · 10.1093/eurheartj/ehae179", "Commentary: 2024 European Society of Cardiology Guidelines on Peripheral Arterial and Aortic Diseases · European Cardiology Review · https://www.ecrjournal.com/articles/commentary-2024-european-society-cardiology-guidelines-peripheral-arterial-and-aortic", "Diagnostic accuracy of the aortic dissection detection risk score alone or with D-dimer for acute aortic syndromes: systematic review and meta-analysis · PLOS ONE · 2024 · 19(6):e0304401 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11192411/", "2024 ESC Guidelines for PAD and Aortic Diseases: Key Points · American College of Cardiology · 2024 · https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2024/09/03/18/59/2024-esc-guidelines-for-pad-esc-2024"]
---

# Fluxograma: Síndrome aórtica aguda (ESC 2024)

A ESC 2024 fundiu, pela primeira vez, as recomendações de doença arterial
periférica e de doença aórtica em um documento único, substituindo as
diretrizes de 2017 e de 2014. Para a síndrome aórtica aguda, duas mudanças
organizam o raciocínio: um **algoritmo diagnóstico multiparamétrico
ancorado no escore ADD-RS** (Classe I, nível B) e uma **nova classificação
TEM**, que descreve o caso por tipo de síndrome, localização da porta de
entrada e presença de má perfusão.

## Caminho decisório

```mermaid
flowchart TD
  A["Dor toracica, dorsal ou abdominal<br/>com suspeita de sindrome aortica aguda"] --> B["Calcular o ADD-RS<br/>escore de 0 a 3"]

  B --> C{"Instabilidade hemodinamica<br/>ou ADD-RS de 2 a 3?"}
  C -->|Sim| D["Imagem imediata<br/>sem esperar D-dimero"]

  C -->|Nao| E{"ADD-RS igual a 0 ou 1"}
  E --> F["Dosar D-dimero"]

  F --> G{"D-dimero maior ou igual<br/>a 500 ng/mL FEU?"}
  G -->|Sim| D
  G -->|Nao| H["Risco muito baixo<br/>imagem dispensavel<br/>investigar diagnostico alternativo"]

  D --> I["Angio-TC sincronizada ao ECG<br/>do pescoco a pelve<br/>exame de primeira linha"]

  I --> J{"Sindrome aortica aguda<br/>confirmada?"}
  J -->|Nao| H

  J -->|Sim| K["Classificar em TEM<br/>tipo, porta de entrada, ma perfusao"]

  K --> L{"Acomete a aorta ascendente?"}
  L -->|Sim| M["Tipo A<br/>cirurgia aberta"]
  L -->|Nao| N["Tipo B"]

  N --> O{"Complicada?<br/>ma perfusao, ruptura, dor ou<br/>hipertensao refrataria, expansao"}
  O -->|Sim| P["Reparo endovascular na fase aguda<br/>se a anatomia for favoravel<br/>cirurgia aberta como alternativa"]
  O -->|Nao| Q["Tratamento clinico e<br/>reparo endovascular na fase subaguda<br/>deve ser considerado"]

  M --> R["Ecocardiograma transesofagico<br/>para guiar o perioperatorio e<br/>detectar complicacao precoce"]
  P --> R
```

## O escore ADD-RS

O *Aortic Dissection Detection Risk Score* não conta fatores isolados: conta
**quantas das três categorias abaixo têm ao menos um item presente**. O
escore vai, portanto, de 0 a 3.

**1. Condições predisponentes de alto risco**

- síndrome de Marfan ou outra doença do tecido conjuntivo
- história familiar de doença aórtica
- doença valvar aórtica conhecida
- manipulação aórtica recente
- aneurisma de aorta torácica conhecido

**2. Características de dor de alto risco**

Dor torácica, dorsal ou abdominal que seja de início abrupto e/ou de
intensidade grave **e** de qualidade dilacerante, rasgante ou em pontada.

**3. Achados de exame físico de alto risco**

- déficit de perfusão — déficit de pulso, diferencial de pressão arterial
  entre membros ou déficit neurológico focal
- sopro novo de insuficiência aórtica acompanhando a dor
- hipotensão ou estado de choque

## Por que combinar ADD-RS com D-dímero

Nenhum dos dois é exame diagnóstico — os dois servem para decidir **quem
precisa de imagem**. A metanálise que sustenta a estratégia mediu as
combinações possíveis:

| Estratégia | Sensibilidade | Especificidade |
|---|---:|---:|
| ADD-RS > 0 | 94,6% | 34,7% |
| ADD-RS > 1 | 43,4% | 89,3% |
| ADD-RS > 0 ou D-dímero > 500 ng/L | 99,8% | 21,8% |
| ADD-RS > 1 ou D-dímero > 500 ng/L | 98,3% | 51,4% |
| ADD-RS > 1, ou ADD-RS = 1 com D-dímero > 500 ng/L | 93,1% | 67,1% |

A leitura prática é direta: o ADD-RS sozinho, com corte em > 0, já é
sensível, mas manda quase todo mundo para a tomografia. Acrescentar o
D-dímero permite escolher onde ficar na troca entre sensibilidade e
especificidade. A combinação de ADD-RS ≤ 1 com D-dímero < 500 ng/mL em
unidades equivalentes de fibrinogênio identifica o grupo de risco muito
baixo, que pode dispensar a imagem.

Probabilidade de dissecção por faixa de escore, na descrição original:
ADD-RS 0 corresponde a risco baixo, ADD-RS 1 a risco moderado e ADD-RS 2–3 a
risco alto.

## A classificação TEM

Substitui a leitura puramente anatômica de Stanford por três eixos com
consequência terapêutica:

- **T** — tipo de síndrome aórtica: dissecção, hematoma intramural ou úlcera
  aterosclerótica penetrante;
- **E** — localização da porta de entrada (*entry tear*);
- **M** — presença de má perfusão.

A má perfusão é o eixo que mais desloca a conduta: é o que transforma um tipo
B em tipo B complicado, com indicação de reparo endovascular na fase aguda.

## Hematoma intramural e úlcera penetrante

As duas entidades seguem a mesma lógica territorial da dissecção:

- **hematoma intramural tipo B complicado** — o reparo endovascular torácico
  passou a recomendação Classe I nesta diretriz;
- **úlcera aterosclerótica penetrante tipo A** — cirurgia;
- **úlcera aterosclerótica penetrante tipo B** — tratamento endovascular.

## Limiares de intervenção no aneurisma, para contexto

O mesmo documento fixa os limiares eletivos que definem quem opera antes de
chegar à síndrome aguda:

- aorta ascendente: cirurgia recomendada com diâmetro máximo ≥ 55 mm
  (Classe I, nível B);
- valva aórtica bicúspide com aneurisma de aorta ascendente: cirurgia deve
  ser considerada a partir de ≥ 45 mm (Classe IIa, nível C);
- a substituição da raiz aórtica com preservação valvar é recomendada em
  centros experientes (Classe I, nível B).
