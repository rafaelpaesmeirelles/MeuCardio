---
title: "Fluxograma: Miocardite aguda — diagnóstico, estratificação de risco e tratamento (ESC 2025)"
slug: fluxograma-miocardite-aguda-esc-2025
theme: "Cardiomiopatias"
kind: fluxograma
summary: "Duas árvores da diretriz ESC 2025: a do diagnóstico, em que a estratificação em alto, intermediário e baixo risco decide internação e biópsia endomiocárdica, e a do tratamento, em que imunossupressão de rotina com função ventricular preservada é Classe III."
review_status: revisado
source_refs: ["Schulz-Menger J, Collini V, Gröschel J, Adler Y, et al. 2025 ESC Guidelines for the management of myocarditis and pericarditis · European Heart Journal · 2025 · 46(40):3952-4041 · DOI: 10.1093/eurheartj/ehaf192 · PMID: 40878297"]
---

# Fluxograma: Miocardite aguda — diagnóstico, estratificação de risco e tratamento (ESC 2025)

A diretriz europeia de 2025 organiza a miocardite em torno de uma decisão que
vem antes de qualquer tratamento: **em que faixa de risco esse paciente está**.
Alto, intermediário ou baixo risco não é adjetivo — é o que define internar,
biopsiar e vigiar.

Três pontos que a diretriz fixa e que mudam conduta:

- **Imunossupressão de rotina na miocardite aguda com função ventricular
  preservada é Classe III** — não é neutra, é recomendada contra, porque não
  demonstrou benefício de desfecho.
- **A restrição de exercício é Classe I**, até a remissão e por pelo menos
  1 mês, para atletas e não atletas.
- **Betabloqueador por pelo menos 6 meses** deve ser considerado na miocardite
  aguda, sobretudo com troponina elevada.

## Árvore de decisão: diagnóstico e estratificação de risco

```mermaid
flowchart TD
  R0["Suspeita de miocardite:<br/>dor torácica, dispneia, arritmia<br/>ou quadro tipo infarto"] --> P1["Avaliação inicial completa: história, exame físico,<br/>radiografia de tórax, biomarcadores, ECG<br/>e ecocardiograma — Classe I"]

  P1 --> D1{"Síndrome coronariana aguda<br/>é hipótese?"}

  D1 -->|"Sim"| C1(["Coronariografia invasiva ou angio-TC de coronárias,<br/>conforme a probabilidade clínica, para afastar<br/>doença coronariana obstrutiva — Classe I"])

  D1 -->|"Não"| P2["Ressonância magnética cardíaca pelos critérios<br/>de Lake Louise atualizados — Classe I, nível B"]

  P2 --> D2{"Faixa de risco clínico"}

  D2 -->|"Alto risco:<br/>IC aguda ou choque cardiogênico,<br/>parada ou síncope, FV/TV sustentada,<br/>BAV avançado, FEVE < 40%<br/>ou realce tardio extenso"| C2(["Internação — Classe I —<br/>e biópsia endomiocárdica — Classe I —<br/>para definir o subtipo histológico<br/>e pesquisar genoma viral"])

  D2 -->|"Risco intermediário:<br/>dispneia nova ou progressiva,<br/>arritmia ventricular não sustentada,<br/>troponina persistente, FEVE 41 a 49%<br/>ou realce tardio além de dois segmentos"| C3(["Internação — Classe I.<br/>Biópsia endomiocárdica se não houver resposta<br/>ao tratamento convencional — Classe I"])

  D2 -->|"Baixo risco:<br/>oligossintomático, FEVE ≥ 50%,<br/>sem realce tardio ou com<br/>realce limitado"| C4(["Internação deve ser considerada — Classe IIa —<br/>para monitorização e tratamento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Árvore de decisão: tratamento

```mermaid
flowchart TD
  R1["Miocardite aguda<br/>com diagnóstico estabelecido"] --> D3{"Forma fulminante não infecciosa,<br/>com comprometimento hemodinâmico?"}

  D3 -->|"Sim"| C5(["Discussão com Shock Team — Classe I.<br/>Corticoide para estabilizar — Classe IIa.<br/>Suporte circulatório mecânico temporário — Classe IIa"])

  D3 -->|"Não"| D4{"Há disfunção sistólica<br/>do ventrículo esquerdo?"}

  D4 -->|"Sim"| D5{"Refratária ao tratamento<br/>padrão de insuficiência cardíaca?"}

  D5 -->|"Não"| C6(["Tratamento conforme a diretriz de insuficiência<br/>cardíaca da ESC — Classe I —, mantido por pelo<br/>menos 6 meses após a recuperação completa<br/>da função ventricular — Classe IIa"])

  D5 -->|"Sim"| C7(["Corticoide pode ser considerado — Classe IIb"])

  D4 -->|"Não: função preservada"| D6{"Achado clínico predominante"}

  D6 -->|"Sintomas de pericardite<br/>associada"| C8(["AINE com inibidor de bomba de prótons — Classe IIa.<br/>Colchicina na miopericardite, para reduzir<br/>recorrências — Classe IIa, nível B"])

  D6 -->|"Troponina elevada e/ou<br/>arritmia ventricular"| C9(["Betabloqueador por pelo menos 6 meses — Classe IIa.<br/>Antiarrítmico na TV sintomática recorrente<br/>pós-miocardite — Classe IIa"])

  D6 -->|"Oligossintomático,<br/>sem arritmia"| C10(["Não usar imunossupressão de rotina — Classe III.<br/>Reavaliação com exames e imagem<br/>em até 6 meses — Classe I"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C5,C6,C7,C8,C9,C10 conduta;
```

## A tabela de risco por trás do nó `D2`

| | Alto risco | Risco intermediário | Baixo risco |
|---|---|---|---|
| **Clínico** | insuficiência cardíaca aguda ou choque cardiogênico; parada cardíaca ou síncope; fibrilação ventricular ou TV sustentada; bloqueio atrioventricular avançado | dispneia NYHA II–IV refratária ao tratamento; dispneia nova ou progressiva; arritmia ventricular não sustentada; liberação persistente ou recorrente de troponina | sintomas estáveis ou oligossintomático |
| **Imagem** | FEVE recém-reduzida (abaixo de 40%); realce tardio extenso à RM | FEVE recém-levemente reduzida (41 a 49%) e/ou alteração segmentar da contração; FEVE preservada (50% ou mais) com realce tardio além de dois segmentos | FEVE preservada (50% ou mais), sem realce tardio ou com realce limitado (até dois segmentos) |

Repare no que a tabela faz com o paciente de **fração de ejeção normal**: ele
pode estar em qualquer das três faixas, dependendo do realce tardio e da
arritmia. É por isso que a ressonância entra antes da estratificação, e não
depois.

## Por que a biópsia endomiocárdica sobe na árvore

A biópsia é recomendada (Classe I) no **alto risco** e/ou na instabilidade
hemodinâmica, e também no **risco intermediário que não responde** ao tratamento
convencional. A finalidade é dupla e concreta: identificar o subtipo histológico
— miocardite de células gigantes e sarcoidose cardíaca mudam completamente o
tratamento e o risco arrítmico — e avaliar a presença de genoma viral, que
orienta a decisão sobre imunossupressão.

Não biopsiar o paciente grave é aceitar tratar de forma genérica uma doença cujo
tratamento específico depende do que o tecido mostra.

## Sinais de alarme e o que fazer com a suspeita

A própria diretriz alerta que **o maior obstáculo ao diagnóstico é o
reconhecimento**. Os sinais de alarme para síndrome inflamatória miopericárdica
são sinais clínicos acompanhados de biomarcadores sorológicos e/ou de imagem —
e a diretriz é explícita: **sinal de alarme não é risco**. Ele levanta a
suspeita; a estratificação de risco vem depois e é ela que orienta a conduta.

## O que as árvores não mostram

**Miopericardite versus perimiocardite.** Nas formas mistas, o manejo segue o
componente predominante: quem tem **miopericardite é tratado como pericardite**;
quem tem **perimiocardite, como miocardite pura**.

**Seguimento é recomendação formal, não zelo.** Reavaliação clínica com
biomarcadores, ECG, teste de esforço, Holter, ecocardiograma e ressonância em até
6 meses da internação é Classe I em **todos** os pacientes com miocardite, para
identificar progressão ou novo fator de risco. O seguimento de longo prazo é
Classe I na miocardite complicada.

**Restrição de exercício até a remissão, por pelo menos 1 mês**, é Classe I e
vale para atletas e não atletas, com abordagem individualizada.

**Equipe multidisciplinar em centro de referência** é Classe I nos casos de alto
risco ou complicados.

**Miocardite por inibidor de checkpoint imunológico, miocardite de células
gigantes e sarcoidose cardíaca** têm recomendações próprias na mesma diretriz e
não estão representadas aqui — a primeira já tem documento próprio em
Cardio-oncologia nesta biblioteca.
