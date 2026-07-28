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

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de TEP agudo"] --> D1{"Instabilidade<br/>hemodinâmica?"}

  D1 -->|"Sim — TEP de alto risco suspeito"| D2{"Angiotomografia viável<br/>de imediato?"}

  D2 -->|Sim| P1["Angiotomografia de<br/>artérias pulmonares"]
  P1 --> D3{"TEP confirmado?"}
  D3 -->|Sim| C1(["Tratar como TEP de alto risco<br/>reperfusão"])
  D3 -->|Não| C2(["Investigar diagnóstico alternativo"])

  D2 -->|Não| P2["Ecocardiograma<br/>à beira do leito"]
  P2 --> D4{"Sobrecarga ou disfunção<br/>de ventrículo direito?"}
  D4 -->|Presente| C3(["Tratar como TEP de alto risco<br/>reperfusão"])
  D4 -->|Ausente| C4(["TEP praticamente afastado<br/>como causa da instabilidade"])

  D1 -->|Não| P3["Avaliar probabilidade pré-teste<br/>escore de Wells ou Genebra revisado"]
  P3 --> D5{"Probabilidade clínica"}

  D5 -->|"Baixa ou intermediária"| P4["D-dímero<br/>corte ajustado pela idade"]
  P4 --> D6{"D-dímero"}
  D6 -->|Negativo| C5(["TEP afastado<br/>sem necessidade de imagem"])

  D6 -->|Positivo| P5["Angiotomografia de<br/>artérias pulmonares"]
  P5 --> D7{"TEP confirmado?"}
  D7 -->|Sim| C6(["Estratificação prognóstica<br/>sPESI, função do ventrículo direito<br/>e biomarcadores"])
  D7 -->|Não| C7(["Investigar diagnóstico alternativo"])

  D5 -->|Alta| P6["Angiotomografia de<br/>artérias pulmonares"]
  P6 --> D8{"TEP confirmado?"}
  D8 -->|Sim| C8(["Estratificação prognóstica<br/>sPESI, função do ventrículo direito<br/>e biomarcadores"])
  D8 -->|Não| C9(["Investigar diagnóstico alternativo"])

  classDef conduta fill:#eef5f8,stroke:#1c7293,color:#0b2e45;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
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
