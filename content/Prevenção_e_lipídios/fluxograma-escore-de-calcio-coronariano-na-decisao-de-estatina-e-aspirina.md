---
title: "Fluxograma: Escore de Cálcio Coronariano na Decisão de Estatina e de Aspirina em Prevenção Primária"
slug: fluxograma-escore-de-calcio-coronariano-na-decisao-de-estatina-e-aspirina
theme: "Prevenção e lipídios"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Detrano R, Guerci AD, Carr JJ, Bild DE, Burke G, Folsom AR, et al. Coronary calcium as a predictor of coronary events in four racial or ethnic groups. N Engl J Med. 2008;358(13):1336-1345. DOI: 10.1056/NEJMoa072100. PMID: 18367736."
  - "Sandesara PB, Mehta A, O'Neal WT, Kelli HM, Sathiyakumar V, et al. Clinical significance of zero coronary artery calcium in individuals with LDL cholesterol ≥190 mg/dL: The Multi-Ethnic Study of Atherosclerosis. Atherosclerosis. 2020;292:224-229. DOI: 10.1016/j.atherosclerosis.2019.09.014. PMID: 31604582."
  - "Miedema MD, Duprez DA, Misialek JR, Blaha MJ, Nasir K, Silverman MG, Blankstein R, Budoff MJ, Greenland P, Folsom AR. Use of coronary artery calcium testing to guide aspirin utilization for primary prevention: estimates from the multi-ethnic study of atherosclerosis. Circ Cardiovasc Qual Outcomes. 2014;7(3):453-460. DOI: 10.1161/CIRCOUTCOMES.113.000690. PMID: 24803472."
  - "US Preventive Services Task Force; Davidson KW, Barry MJ, Mangione CM, et al. Aspirin Use to Prevent Cardiovascular Disease: US Preventive Services Task Force Recommendation Statement. JAMA. 2022;327(16):1577-1584. DOI: 10.1001/jama.2022.4983. PMID: 35471505."
  - "Derivado de escore-de-calcio-coronariano-o-que-o-mesa-mediu-e-o-que-significa-um-escore-zero.md e aspirina-guiada-por-escore-de-calcio-coronariano-em-prevencao-primaria-o-nnt-do-mesa.md, já publicados no acervo (Prevenção e lipídios)."
---

# Fluxograma: Escore de Cálcio Coronariano na Decisão de Estatina e de Aspirina em Prevenção Primária

O escore de cálcio coronariano (CAC) é usado na prática para duas decisões diferentes, e os dois documentos já publicados nesta pasta — sobre o que o MESA mediu e sobre o NNT/NNH da aspirina guiada por CAC — tratam de cada uma separadamente. Este fluxograma reúne as duas num único ponto de entrada: **o mesmo resultado de CAC leva a condutas diferentes conforme a decisão em aberto seja sobre hipolipemiante ou sobre aspirina.**

Um resultado importante orienta toda a árvore: o CAC **reclassifica** risco de forma consistente e independente do escore de risco tradicional (Framingham) — inclusive quando o LDL-C já é muito alto (190 mg/dL ou mais). Fora dos dois valores usados nos estudos que embasam esta árvore (CAC igual a zero e CAC de 100 ou mais), a faixa intermediária de CAC (entre 1 e 99) não foi estratificada com o mesmo detalhe por nenhuma das fontes aqui citadas para a decisão de aspirina — nesse caso, a decisão volta a se apoiar no risco tradicional e no julgamento clínico, sem um corte numérico específico desta árvore.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Adulto em prevenção primária, sem doença cardiovascular<br/>estabelecida, com decisão terapêutica em dúvida após<br/>avaliação inicial de risco (ex.: risco limítrofe, ou LDL-C<br/>de 190 mg/dL ou mais com decisão de estatina/aspirina<br/>ainda incerta)"] --> D1{"Resultado do escore de<br/>cálcio coronariano (CAC)"}

  D1 -->|"CAC igual a zero"| P1["Risco de evento coronariano substancialmente<br/>menor nos próximos anos (MESA: HR ajustado<br/>0,25, mesmo em quem tem LDL-C de<br/>190 mg/dL ou mais)"]
  P1 --> D2{"Qual decisão terapêutica<br/>está em aberto?"}
  D2 -->|"Início ou intensificação<br/>de hipolipemiante"| C1(["Escore zero pode ser usado para reclassificar<br/>o risco para baixo e discutir adiar ou reduzir<br/>a intensidade da terapia hipolipemiante — não<br/>suspender terapia já indicada por hipercolesterolemia<br/>familiar ou doença aterosclerótica estabelecida"])
  D2 -->|"Início de aspirina<br/>em prevenção primária"| C2(["Não iniciar aspirina: a estimativa de dano (NNH<br/>em 5 anos de 442 para sangramento maior) supera<br/>a de benefício mesmo em quem tem risco tradicional<br/>pelo escore de Framingham de 10% ou mais<br/>(NNT de 808 a 2.036, conforme o estrato de risco)"])

  D1 -->|"CAC de 100 ou mais"| P2["Risco de evento coronariano aumentado de<br/>forma consistente (MESA: fator de 7,73 a 9,67<br/>conforme a faixa de escore) e independente<br/>do risco tradicional pelo escore de Framingham"]
  P2 --> D3{"Qual decisão terapêutica<br/>está em aberto?"}
  D3 -->|"Início ou intensificação<br/>de hipolipemiante"| C3(["Escore elevado reforça a indicação de tratar;<br/>usar como reclassificador quando a decisão<br/>inicial ainda estava em dúvida"])
  D3 -->|"Início de aspirina<br/>em prevenção primária"| D4{"Paciente tem risco hemorrágico aumentado<br/>(história de úlcera gastrointestinal, sangramento<br/>recente, ou uso de outro medicamento que<br/>aumente o risco de sangramento)?"}
  D4 -->|"Sim"| C4(["Não iniciar aspirina: risco hemorrágico<br/>aumentado exclui o paciente da população<br/>em que a estimativa de benefício líquido<br/>foi calculada (USPSTF 2022)"])
  D4 -->|"Não"| D5{"Idade do paciente"}
  D5 -->|"60 anos ou mais"| C5(["USPSTF 2022 recomenda CONTRA iniciar<br/>aspirina em prevenção primária nesta faixa<br/>etária (recomendação D), independentemente<br/>do CAC — o estudo do MESA não isolou essa<br/>faixa como exceção"])
  D5 -->|"Menos de 60 anos"| C6(["Considerar iniciar aspirina em baixa dose:<br/>estimativa de benefício líquido favorável<br/>(NNT em 5 anos de 92 a 173, contra NNH<br/>de 442) — decisão individualizada, dentro<br/>de uma prática já cautelosa"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**As estimativas de NNT/NNH da aspirina são modelagem, não ensaio randomizado.** Miedema et al. cruzaram taxas de evento observadas no MESA com uma redução relativa de risco vinda de outra fonte (metanálise) — ninguém no MESA foi alocado a receber ou não aspirina conforme o CAC.

**A recomendação de aspirina mudou depois do estudo que gerou os números de NNT/NNH (2014).** O USPSTF 2022 já é mais restritivo do que a prática da época, incorporando três ensaios randomizados posteriores (ASPREE, ASCEND, ARRIVE); os números desta árvore refinam a decisão **dentro** dessa prática já cautelosa, não a revertem.

**O escore de cálcio não mede estenose nem substitui teste funcional** — não deve ser pedido para investigar dor torácica aguda, e um escore zero não descarta doença coronariana em paciente sintomático, porque placa não calcificada existe.

**Escore zero não é permanente**: descreve o risco dos próximos anos, não da vida inteira, e a repetição do exame depende do risco basal e do que a repetição mudaria na conduta.
