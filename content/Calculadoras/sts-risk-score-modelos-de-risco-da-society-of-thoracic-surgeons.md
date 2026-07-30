---
title: "STS Risk Score: Modelos de Risco da Society of Thoracic Surgeons"
slug: sts-risk-score-modelos-de-risco-da-society-of-thoracic-surgeons
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["O'Brien SM, Feng L, He X, et al. The Society of Thoracic Surgeons 2018 Adult Cardiac Surgery Risk Models: Part 2-Statistical Methods and Results. Ann Thorac Surg. 2018;105(5):1419-1428. DOI: 10.1016/j.athoracsur.2018.03.003. PMID: 29577924", "Shahian DM, Jacobs JP, Badhwar V, et al. The Society of Thoracic Surgeons 2018 Adult Cardiac Surgery Risk Models: Part 1-Background, Design Considerations, and Model Development. Ann Thorac Surg. 2018;105(5):1411-1418. DOI: 10.1016/j.athoracsur.2018.03.002. PMID: 29577925"]
legacy_source: "Documento novo — complementa o EuroSCORE II já registrado nesta pasta, trazendo o principal comparador norte-americano de estimativa de risco cirúrgico cardíaco, citado apenas de passagem naquele documento."
---

# STS Risk Score: Modelos de Risco da Society of Thoracic Surgeons

## Aplicacao
Complementa o EuroSCORE II já registrado nesta pasta — o STS Risk Score é o principal sistema de estimativa de risco cirúrgico cardíaco usado nos Estados Unidos, desenvolvido e mantido pela Society of Thoracic Surgeons (STS) a partir do Adult Cardiac Surgery Database (ACSD), o maior registro de cirurgia cardíaca do mundo. Diferente do EuroSCORE II (modelo único), o STS mantém **modelos separados por tipo de procedimento** e por desfecho.

## Os modelos stS 2018 (o'brien e shahian, ann thorac surg 2018)
O'Brien SM et al. Ann Thorac Surg. 2018;105(5):1419-1428 (PMID 29577924); Shahian DM et al. Ann Thorac Surg. 2018;105(5):1411-1418 (PMID 29577925). Usando dados do ACSD de julho de 2011 a junho de 2014, modelos de risco completamente novos foram desenvolvidos para mortalidade operatória, AVC, insuficiência renal, ventilação prolongada, mediastinite/infecção profunda de ferida esternal, reoperação, composto de morbidade maior ou mortalidade, e tempo de internação pós-operatória prolongado ou curto, em três populações separadas:
- **Revascularização miocárdica isolada (CRM)**: **439.092 pacientes**
- **Cirurgia de valva aórtica ou mitral**: **150.150 pacientes**
- **Cirurgia combinada de valva + revascularização miocárdica**: **81.588 pacientes**
- Modelo separado para cada procedimento e desfecho, exceto mediastinite/infecção de ferida esternal (analisada em modelo combinado, por sua baixa frequência)
- Um painel de cirurgiões selecionou preditores avaliando desempenho do modelo e validade clínica de face de modelos completos e progressivamente mais parcimoniosos
- Dados do ACSD de julho de 2014 a dezembro de 2016 usados para avaliar calibração do modelo e comparar discriminação com os modelos STS anteriores

## Resultados de calibracao e discriminacao
- **Calibração excelente na amostra de validação para todos os modelos**, exceto mediastinite/infecção profunda de ferida esternal, que subestimou levemente o risco (recalibrado em relatórios de retorno)
- **Os índices-c (c-index) dos novos modelos superaram os dos modelos STS publicados anteriormente** para todas as populações e desfechos, **exceto AVC em pacientes valvares**

## Conclusao do proprio estudo
**"Os novos modelos de risco do ACSD da STS têm, de forma geral, excelente calibração e discriminação, e são bem adequados para o ajuste de risco das métricas de desempenho da STS."**

## Sintese pratica
O STS Risk Score e o EuroSCORE II — já registrado nesta pasta — são as duas principais ferramentas de estimativa de risco cirúrgico cardíaco usadas mundialmente, cada uma derivada de população própria (americana no caso do STS, europeia mais ampla no caso do EuroSCORE II) e cada uma com desempenho estatístico próprio. A diferença estrutural mais relevante para a prática é que o STS mantém **modelos separados por tipo de procedimento** (CRM isolada, valva isolada, valva+CRM) e por desfecho específico (não só mortalidade — também AVC, insuficiência renal, reoperação, tempo de internação), enquanto o EuroSCORE II é modelo único voltado a mortalidade. Ambos são usados lado a lado na prática de Heart Team, especialmente na avaliação de candidatos a TAVI/troca valvar percutânea versus cirurgia aberta — nenhum dos dois deve ser usado isoladamente para excluir um paciente de tratamento, e sim como insumo quantitativo à decisão compartilhada.

## Armadilhas clinicas
- Comparar diretamente o percentual do STS Risk Score com o do EuroSCORE II como se fossem a mesma métrica — são modelos derivados de populações e variáveis diferentes, sem equivalência direta estabelecida entre eles
- Usar o STS Risk Score apenas para mortalidade quando o modelo específico do desfecho de interesse (AVC, insuficiência renal, reoperação, tempo de internação) já está disponível e mais adequado à pergunta clínica em questão
- Aplicar o modelo de CRM isolada a um paciente que fará cirurgia combinada de valva+CRM, ou vice-versa — os modelos são desenvolvidos e validados separadamente por tipo de procedimento, com populações de derivação distintas
- Tratar excelente calibração e discriminação populacional como garantia de exatidão para o paciente individual — mesmo modelo bem calibrado no agregado carrega incerteza na estimativa pontual de um paciente específico, e a mediastinite/infecção de ferida esternal foi exceção explícita à boa calibração neste próprio estudo
