---
title: "Fluxograma: Tromboembolismo Pulmonar — diagnóstico e estratificação (ESC 2019)"
slug: fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019
theme: "Tromboembolismo"
kind: fluxograma
summary: "Os dois caminhos diagnósticos do TEP agudo, separados pela estabilidade hemodinâmica: probabilidade pré-teste com D-dímero ajustado pela idade no paciente estável, e angiotomografia imediata no instável."
review_status: revisado
source_refs: ["2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS) · European Heart Journal · 2020 · 41(4):543-603 · https://academic.oup.com/eurheartj/article/41/4/543/5556136", "2019 ESC Guidelines for the Diagnosis and Management of Acute PE · American College of Cardiology · 2020 · https://www.acc.org/Latest-in-Cardiology/Articles/2020/07/10/08/44/2019-ESC-Guidelines-for-the-Diagnosis-and-Management-of-Acute-PE"]
---

# Fluxograma: Tromboembolismo Pulmonar agudo (ESC 2019)

A diretriz ESC 2019 mantém **dois algoritmos diagnósticos distintos**, e a
bifurcação vem antes de qualquer exame: a presença ou ausência de instabilidade
hemodinâmica muda tanto a urgência quanto a ordem dos testes.

## Caminho decisório

```mermaid
flowchart TD
  A["Suspeita de TEP agudo"] --> B{"Instabilidade<br/>hemodinâmica?"}

  B -->|Sim| C["TEP de alto risco suspeito"]
  B -->|Não| D["Avaliar probabilidade pré-teste<br/>escore de Wells ou Genebra revisado"]

  C --> E["Angiotomografia de artérias pulmonares<br/>como teste inicial<br/>na alta probabilidade clínica"]
  C --> F["Ecocardiograma à beira do leito<br/>quando a TC não for viável de imediato"]
  F --> G{"Sobrecarga ou disfunção<br/>de ventrículo direito?"}
  G -->|Ausente| H["TEP praticamente afastado<br/>como causa da instabilidade"]
  G -->|Presente| I["Tratar como TEP de alto risco"]
  E --> I

  D --> J{"Probabilidade clínica"}
  J -->|"Baixa ou intermediária"| K["D-dímero<br/>corte ajustado pela idade"]
  J -->|Alta| L["Angiotomografia de<br/>artérias pulmonares"]

  K --> M{"D-dímero"}
  M -->|Negativo| N["TEP afastado<br/>sem necessidade de imagem"]
  M -->|Positivo| L

  L --> O{"TEP confirmado?"}
  O -->|Não| P["Investigar diagnóstico alternativo"]
  O -->|Sim| Q["Estratificação prognóstica"]

  I --> R["Reperfusão"]
  Q --> Q1["sPESI"]
  Q --> Q2["Função do ventrículo direito"]
  Q --> Q3["Biomarcadores"]
```

## O que define instabilidade hemodinâmica

A diretriz é explícita, e qualquer um dos três basta:

- **parada cardíaca**;
- **choque obstrutivo** — pressão arterial sistólica < 90 mmHg, ou necessidade de
  vasopressor para atingir PAS ≥ 90 mmHg, acompanhada de hipoperfusão de
  órgão-alvo;
- **hipotensão persistente** — PAS < 90 mmHg, ou queda da PAS ≥ 40 mmHg com
  duração superior a 15 minutos, não atribuível a outra causa identificável.

## D-dímero ajustado pela idade

A especificidade do D-dímero cai progressivamente com a idade. Por isso a
diretriz recomenda o corte ajustado: **idade × 10 µg/L para pacientes acima de
50 anos**. O objetivo declarado do refinamento dos algoritmos foi aumentar a
especificidade da combinação probabilidade pré-teste + D-dímero, **limitando
angiotomografias desnecessárias**.

## O valor do ecocardiograma no instável

No paciente hemodinamicamente instável, o ecocardiograma tem um papel que a
angiotomografia não substitui quando o transporte é inviável: a **ausência de
sinais de sobrecarga ou disfunção do ventrículo direito praticamente afasta o
TEP como causa da instabilidade**, redirecionando a investigação.

## Estratificação depois do diagnóstico

A avaliação prognóstica inicial é recomendada em todo paciente com TEP suspeito
ou confirmado, e combina parâmetros clínicos — incluindo o **sPESI** —, a função
do ventrículo direito, a hemodinâmica e os biomarcadores elevados. Não é um
único escore que decide, é a convergência desses eixos.
