---
title: "Fluxograma: Cardiomiopatia hipertrófica — diagnóstico, risco de morte súbita e obstrução (ESC 2023)"
slug: fluxograma-cardiomiopatia-hipertrofica-esc-2023
theme: "Cardiomiopatias"
kind: fluxograma
summary: "Caminho decisório da cardiomiopatia hipertrófica: critério de espessura parietal, investigação etiológica por fenótipo, estratificação de morte súbita pelo HCM Risk-SCD com as faixas de 5 anos e os modificadores de risco, e a escala terapêutica da obstrução da via de saída."
review_status: revisado
source_refs: ["2023 ESC Guidelines for the management of cardiomyopathies · European Heart Journal · 2023 · 44(37):3503-3626 · https://academic.oup.com/eurheartj/article/44/37/3503/7246608", "2023 ESC Guidelines for Management of Cardiomyopathies: Key Points · American College of Cardiology · 2023 · https://www.acc.org/Latest-in-Cardiology/ten-points-to-remember/2023/08/30/02/53/2023-esc-guidelines-for-cardiomyopathies-esc-2023", "Validation of Guideline Recommendation on Sudden Cardiac Death Prevention in Hypertrophic Cardiomyopathy · JACC: Heart Failure · 2025 · https://www.jacc.org/doi/10.1016/j.jchf.2024.12.006", "Critical analysis of the 2023 ESC guidelines on cardiomyopathy management · European Heart Journal Supplements · 2025 · 27(Suppl 1):i31 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11836687/"]
---

# Fluxograma: Cardiomiopatia hipertrófica (ESC 2023)

A diretriz ESC 2023 de cardiomiopatias trocou a organização por doença
nomeada pela organização **por fenótipo**: primeiro se reconhece o padrão
morfofuncional, depois se persegue a etiologia. Na cardiomiopatia
hipertrófica, isso significa que o achado de hipertrofia não encerra o
raciocínio — abre a busca por *red flags* de fenocópias, que têm tratamento
próprio.

## Do achado de hipertrofia ao diagnóstico

```mermaid
flowchart TD
  A["Hipertrofia ventricular esquerda<br/>espessura parietal maior ou igual a 15 mm<br/>nao explicada por condicao de sobrecarga"] --> B["Cardiomiopatia hipertrofica"]

  B --> C["Caracterizacao por imagem multimodal<br/>ressonancia magnetica cardiaca para<br/>caracterizacao tecidual"]

  B --> D["Teste genetico com<br/>aconselhamento genetico"]

  C --> E{"Red flags de etiologia especifica?"}
  D --> E

  E -->|Sim| F["Perseguir a fenocopia<br/>amiloidose, doenca de Fabry,<br/>ataxia de Friedreich, sindromes<br/>de RASopatia, doencas de deposito"]
  E -->|Nao| G["Cardiomiopatia hipertrofica<br/>sarcomerica ou de causa nao identificada"]

  F --> H["Tratamento dirigido a etiologia<br/>quando existir"]

  G --> I["Duas perguntas independentes<br/>seguem em paralelo"]
  H --> I

  I --> J["1. Qual o risco de morte subita?"]
  I --> K["2. Ha obstrucao da via de saida?"]

  J --> L["Rastreamento familiar em cascata"]
  K --> L
```

O ponto de corte diagnóstico é **espessura de parede do ventrículo esquerdo
de pelo menos 15 mm**, sem outra causa que explique a hipertrofia. Em
familiares de primeiro grau de caso conhecido, o limiar é menor, porque a
probabilidade pré-teste é outra.

## Estratificação de morte súbita

A diretriz é explícita: **as ferramentas validadas de predição — HCM
Risk-SCD em adultos e HCM Risk-Kids em crianças — são o primeiro passo** da
prevenção de morte súbita, não um complemento opcional. A decisão sobre o
cardioversor-desfibrilador implantável é então discutida e acordada com o
paciente.

```mermaid
flowchart TD
  A["Cardiomiopatia hipertrofica<br/>sem parada cardiaca previa nem<br/>taquicardia ventricular sustentada"] --> B["Calcular o HCM Risk-SCD<br/>risco estimado em 5 anos"]

  B --> C{"Faixa de risco"}

  C -->|"Maior ou igual a 6%<br/>alto risco"| D["CDI deve ser considerado"]
  C -->|"4% a menos de 6%<br/>risco intermediario"| E["Decisao individualizada<br/>com julgamento clinico adicional"]
  C -->|"Menor que 4%<br/>baixo risco"| F["CDI em geral nao indicado"]

  E --> G{"Modificadores de risco presentes?"}
  F --> G

  G -->|"Realce tardio extenso<br/>maior ou igual a 15% na RMC"| H["Pode ser considerado na<br/>decisao compartilhada<br/>Classe IIb, nivel B"]
  G -->|"Fracao de ejecao<br/>menor que 50%"| H
  G -->|Nao| I["Manter vigilancia<br/>e reavaliacao periodica do escore"]

  H --> J["Decisao compartilhada<br/>sobre CDI profilatico"]
  D --> J
```

As faixas de risco em 5 anos usadas pela ESC são: **baixo, abaixo de 4%;
intermediário, de 4% a 6%; alto, a partir de 6%**. A capacidade
discriminatória do modelo nas recomendações de 2023 foi medida em validação
independente, com área sob a curva de 0,73 (IC 95% 0,68–0,78) para eventos
em 5 anos — bom o bastante para orientar, insuficiente para decidir sozinho,
que é exatamente o motivo dos modificadores.

Os dois modificadores incorporados formalmente à decisão na faixa de risco
baixo são o **realce tardio extenso (≥ 15%) na ressonância** e a **fração de
ejeção abaixo de 50%**, ambos como Classe IIb, nível B. Aneurisma apical,
genética e resposta hipotensiva ao exercício não entraram nessa recomendação
específica.

## Obstrução da via de saída: escala terapêutica

```mermaid
flowchart TD
  A["Cardiomiopatia hipertrofica sintomatica"] --> B{"Gradiente na via de saida<br/>em repouso ou provocado<br/>maior ou igual a 50 mmHg?"}

  B -->|Nao| C["Fenotipo nao obstrutivo<br/>tratar sintoma e comorbidade"]

  B -->|Sim| D["Terapia medica maxima tolerada"]

  D --> E{"Permanece sintomatico?"}
  E -->|Nao| F["Manter e reavaliar"]

  E -->|Sim| G["Inibidor de miosina cardiaca<br/>mavacanteno deve ser considerado"]

  G --> H{"Permanece sintomatico em<br/>classe funcional NYHA III-IV<br/>apesar da terapia maxima?"}
  H -->|Nao| F

  H -->|Sim| I["Terapia de reducao septal<br/>por operador experiente, em equipe<br/>multidisciplinar especializada em CMH"]

  I --> J{"Qual tecnica?"}
  J -->|"Paciente pediatrico"| K["Miectomia septal"]
  J -->|"Adulto com outra lesao que<br/>exige cirurgia no mesmo tempo"| K
  J -->|"Demais adultos"| L["Miectomia septal ou<br/>ablacao septal alcoolica"]
```

Dois critérios delimitam a indicação de terapia de redução septal, e valem
juntos: **gradiente na via de saída, em repouso ou máximo provocado, de pelo
menos 50 mmHg**, e **classe funcional NYHA/Ross III–IV apesar da terapia
medicamentosa máxima tolerada**.

A escolha entre miectomia e ablação alcoólica não é livre: a **miectomia
septal é recomendada em vez da ablação alcoólica** em pacientes pediátricos
com indicação de redução septal, e em adultos que tenham, além da obstrução,
outra lesão exigindo intervenção cirúrgica no mesmo procedimento.

## O que a diretriz enfatiza como cuidado transversal

Os pilares valem para todas as cardiomiopatias, não só a hipertrófica:
controle de sintomas, identificação e prevenção das complicações da doença —
morte súbita, insuficiência cardíaca e acidente vascular cerebral —,
individualização da prescrição de exercício com avaliação de risco, modelo
de cuidado multidisciplinar e avaliação pré-operatória nos pacientes de alto
risco.
