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
  R0["Hipertrofia ventricular esquerda<br/>espessura parietal maior ou igual a 15 mm<br/>não explicada por condição de sobrecarga"] --> P1["Cardiomiopatia hipertrófica — caracterização<br/>por imagem multimodal, com ressonância<br/>magnética para caracterização tecidual, e teste<br/>genético com aconselhamento"]

  P1 --> D1{"Red flags de<br/>etiologia específica?"}

  D1 -->|Sim| C1(["Perseguir a fenocópia — amiloidose,<br/>doença de Fabry, ataxia de Friedreich,<br/>RASopatias, doenças de depósito — e aplicar<br/>o tratamento dirigido à etiologia<br/>quando existir"])

  D1 -->|Não| C2(["Cardiomiopatia hipertrófica sarcomérica<br/>ou de causa não identificada"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

Qualquer que seja o ramo, o diagnóstico abre em seguida duas perguntas
independentes — **qual o risco de morte súbita** e **há obstrução da via de
saída** —, cada uma com sua própria árvore abaixo, e o **rastreamento familiar
em cascata**. Nenhum dos três é alternativa ao outro, e por isso não aparecem
como folhas da árvore acima.

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
  R0["Cardiomiopatia hipertrófica<br/>sem parada cardíaca prévia nem<br/>taquicardia ventricular sustentada"] --> P1["Calcular o HCM Risk-SCD<br/>risco estimado em 5 anos"]

  P1 --> D1{"Faixa de risco em 5 anos"}

  D1 -->|"Maior ou igual a 6%<br/>alto risco"| C1(["CDI deve ser considerado,<br/>em decisão compartilhada"])

  D1 -->|"4% a menos de 6%<br/>risco intermediário"| C2(["Decisão individualizada, com julgamento<br/>clínico adicional e reavaliação<br/>periódica do escore"])

  D1 -->|"Menor que 4%<br/>baixo risco"| D2{"Realce tardio extenso na RMC<br/>maior ou igual a 15%, ou fração<br/>de ejeção menor que 50%?"}

  D2 -->|Sim| C3(["Pode ser considerado na decisão<br/>compartilhada sobre CDI profilático<br/>Classe IIb, nível B"])

  D2 -->|Não| C4(["CDI em geral não indicado — manter<br/>vigilância e reavaliação periódica<br/>do escore"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
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
  R0["Cardiomiopatia hipertrófica sintomática"] --> D1{"Gradiente na via de saída,<br/>em repouso ou provocado,<br/>maior ou igual a 50 mmHg?"}

  D1 -->|Não| C1(["Fenótipo não obstrutivo<br/>tratar sintoma e comorbidade"])

  D1 -->|Sim| P1["Terapia médica máxima tolerada"]

  P1 --> D2{"Permanece sintomático?"}

  D2 -->|Não| C2(["Manter o tratamento e reavaliar"])

  D2 -->|Sim| P2["Inibidor de miosina cardíaca<br/>mavacanteno deve ser considerado"]

  P2 --> D3{"Permanece sintomático em classe<br/>funcional NYHA III-IV apesar<br/>da terapia máxima?"}

  D3 -->|Não| C3(["Manter o tratamento e reavaliar"])

  D3 -->|Sim| D4{"Paciente pediátrico, ou adulto com<br/>outra lesão que exige cirurgia<br/>no mesmo tempo?"}

  D4 -->|Sim| C4(["Miectomia septal — recomendada em vez da<br/>ablação alcoólica nesse cenário — por<br/>operador experiente, em equipe<br/>multidisciplinar especializada em CMH"])

  D4 -->|Não| C5(["Terapia de redução septal: miectomia septal<br/>ou ablação septal alcoólica, por operador<br/>experiente, em equipe multidisciplinar<br/>especializada em CMH"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
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
