---
title: "Fluxograma: Pressão arterial elevada e hipertensão — da medida ao alvo (ESC 2024)"
slug: fluxograma-hipertensao-arterial-esc-2024
theme: "Hipertensão"
kind: fluxograma
summary: "Caminho decisório da nova classificação ESC 2024: as três categorias de pressão arterial, a decisão de tratar na faixa de pressão elevada com base no risco cardiovascular em 10 anos pelo SCORE2, e o alvo sistólico de 120–129 mmHg."
review_status: revisado
source_refs: ["2024 ESC Guidelines for the management of elevated blood pressure and hypertension · European Heart Journal · 2024 · 10.1093/eurheartj/ehae178 · https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/elevated-blood-pressure-and-hypertension/", "2024 ESC Guidelines for Management of Elevated BP and Hypertension: Key Points · American College of Cardiology · 2024 · https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2024/09/05/14/11/2024-esc-guidelines-for-bp-esc-2024", "New Definition of Elevated Blood Pressure in the 2024 ESC Guidelines: Increased Prevalence, Uncertain Evidence · Circulation · https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.124.072696", "Navigating the 2024 ESC Hypertension Guidelines: What Is New, Context, and Future Directions · Journal of the American College of Cardiology · 2024 · https://www.jacc.org/doi/10.1016/j.jacc.2024.10.114"]
---

# Fluxograma: Pressão arterial elevada e hipertensão (ESC 2024)

A ESC 2024 fez duas mudanças que alteram a conduta diária. A primeira é
**uma terceira categoria de pressão arterial** — "pressão elevada", entre
120–139 mmHg de sistólica ou 70–89 mmHg de diastólica —, que existe para
identificar quem se beneficia de tratamento antes de cruzar o limiar
clássico de 140/90. A segunda é o **alvo sistólico de 120–129 mmHg** como
ponto de partida da maioria dos tratados, e não como meta opcional: o
documento inverteu a lógica anterior, em que a intensificação era a exceção.

## Caminho decisório

```mermaid
flowchart TD
  A["Medida de pressao arterial<br/>em consultorio"] --> B{"Categoria"}

  B -->|"Menor que 120/70 mmHg"| C["Pressao nao elevada<br/>tratamento medicamentoso<br/>nao recomendado"]

  B -->|"120-139 sistolica ou<br/>70-89 diastolica"| D["Pressao elevada"]

  B -->|"Maior ou igual a 140/90 mmHg"| E["Hipertensao<br/>confirmar prontamente e tratar<br/>na maioria dos individuos"]

  D --> F["Medida fora do consultorio<br/>MAPA ou monitorizacao residencial<br/>recomendada para o diagnostico"]
  E --> F

  F --> G{"Confirma hipertensao<br/>do avental branco ou mascarada?"}
  G -->|"Avental branco"| H["Reclassificar<br/>e acompanhar"]
  G -->|"Mascarada"| E

  D --> I["Medidas de estilo de vida<br/>por 3 meses"]

  I --> J{"Sistolica permanece<br/>entre 130 e 139 mmHg?"}
  J -->|Nao| K["Manter estilo de vida<br/>e reavaliacao periodica"]

  J -->|Sim| L{"Risco alto?"}

  L -->|"Doenca cardiovascular estabelecida,<br/>ou diabetes em adulto de 60 anos ou mais"| M["Tratamento medicamentoso<br/>recomendado"]
  L -->|"SCORE2 ou SCORE2-OP<br/>maior que 10% em 10 anos"| M
  L -->|"Risco de 5% a 10% com<br/>modificadores de risco presentes"| M
  L -->|Nao| K

  E --> N["Tratamento medicamentoso"]
  M --> N

  N --> O["Alvo sistolico de 120 a 129 mmHg"]

  O --> P{"Idade acima de 85 anos, fragilidade,<br/>sintoma ortostatico ou expectativa<br/>de vida limitada?"}
  P -->|Sim| Q["Alvo individualizado<br/>menos intensivo"]
  P -->|Nao| R["Manter o alvo de 120-129 mmHg<br/>se tolerado"]
```

## As três categorias

| Categoria | Definição em consultório | Conduta medicamentosa |
|---|---|---|
| Pressão não elevada | < 120/70 mmHg | Não recomendada |
| Pressão elevada | 120–139 mmHg sistólica **ou** 70–89 mmHg diastólica | Recomendada em indivíduos selecionados, conforme risco cardiovascular e pressão no seguimento |
| Hipertensão | ≥ 140/90 mmHg | Confirmação pronta e tratamento na maioria |

A categoria intermediária foi criada justamente para viabilizar alvos mais
intensivos em quem já tem risco cardiovascular aumentado — não para
transformar toda a faixa em doença tratável com fármaco.

## Quem trata na faixa de pressão elevada

A regra tem três degraus, e o tempo faz parte dela: **3 meses de medidas de
estilo de vida primeiro**. Se, depois desse período, a sistólica permanecer
entre 130 e 139 mmHg, o tratamento medicamentoso é recomendado quando houver:

- condição de alto risco — doença cardiovascular estabelecida, ou diabetes
  em adultos com 60 anos ou mais; **ou**
- risco cardiovascular estimado em 10 anos acima de 10% pelo **SCORE2**
  (40–69 anos) ou **SCORE2-OP** (70 anos ou mais); **ou**
- risco estimado entre 5% e 10% na presença de modificadores de risco.

Na prática, quem tem risco em 10 anos de 10% ou mais, ou comorbidade que já
o coloca em alto risco — diabetes, por exemplo —, começa terapia
anti-hipertensiva a partir de 130/80 mmHg.

## O alvo

O alvo sistólico para adultos em uso de medicação é de **120–129 mmHg**. A
diretriz prevê flexibilização explícita em quatro situações: idade acima de
85 anos, fragilidade, sintomas ortostáticos e expectativa de vida limitada.

A inversão de lógica é o ponto: o alvo intensivo é o primeiro passo do
manejo da maioria, e sai-se dele por circunstância definida ou por
intolerância do paciente — não se entra nele por exceção.

## Medida fora do consultório

A medida fora do consultório — monitorização ambulatorial ou residencial —
é recomendada para fins diagnósticos, porque é o que detecta hipertensão do
avental branco e hipertensão mascarada. As duas mudam a conduta em direções
opostas, e nenhuma das duas é identificável apenas com a medida de
consultório.

## Priorização

A abordagem baseada em risco significa priorizar ativamente os pacientes com
diabetes, doença renal, doença cardiovascular, lesão de órgão-alvo ou
hipercolesterolemia familiar — grupos em que a mesma cifra de pressão tem
consequência maior.
