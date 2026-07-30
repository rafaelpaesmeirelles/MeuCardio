---
title: "EuroSCORE II: Risco de Mortalidade em Cirurgia Cardíaca"
slug: euroscore-ii-risco-de-mortalidade-em-cirurgia-cardiaca
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Nashef SA, Roques F, Sharples LD, Nilsson J, Smith C, Goldstone AR, Lockowandt U. EuroSCORE II. Eur J Cardiothorac Surg. 2012;41(4):734-744. DOI: 10.1093/ejcts/ezs043. PMID: 22378855"]
legacy_source: "Documento novo — as calculadoras já existentes cobrem risco em síndrome coronariana aguda (TIMI, GRACE 2.0), sangramento em FA (HAS-BLED), tromboembolismo venoso (PESI/sPESI, Wells) e escolha de revascularização (SYNTAX), mas não a estimativa de mortalidade cirúrgica — decisão central antes de indicar qualquer cirurgia cardíaca."
---

# EuroSCORE II: Risco de Mortalidade em Cirurgia Cardíaca

## Aplicacao
Estimativa de mortalidade hospitalar em pacientes candidatos a cirurgia cardíaca de médio a grande porte (troca valvar, revascularização miocárdica, cirurgia combinada, entre outras). É a atualização do EuroSCORE original (1995), desenvolvida porque o modelo antigo passou a superestimar sistematicamente o risco à medida que a mortalidade cirúrgica caiu ao longo dos anos, mesmo em população mais idosa e mais grave.

## O estudo de desenvolvimento (nashef, ejcts 2012)
Nashef SA et al. Eur J Cardiothorac Surg. 2012;41(4):734-744 (PMID 22378855). Coleta prospectiva de dados de risco e desfecho em **22.381 pacientes consecutivos** submetidos a cirurgia cardíaca de grande porte em **154 hospitais de 43 países**, ao longo de um período de 12 semanas (maio-julho de 2010). Conjunto de dados dividido em subconjunto de desenvolvimento (regressão logística) e subconjunto de validação:
- Comparado ao banco de dados original do EuroSCORE de 1995, a população mais recente era mais velha (idade média 64,7 vs. 62,5 anos), com mais mulheres (31% vs. 28%) e mais pacientes em classe funcional NYHA IV, com arteriopatia extracardíaca, disfunção renal e pulmonar
- **Mortalidade geral observada**: 3,9% (vs. 4,6% no banco original de 1995)
- **Os modelos de risco antigos superestimaram a mortalidade** quando aplicados aos dados atuais: mortalidade real 3,9%, predita pelo modelo aditivo original 5,8%, predita pelo modelo logístico original 7,57%
- **EuroSCORE II mostrou boa calibração** no subconjunto de validação (5.553 pacientes): mortalidade real 4,18%, predita 3,95%
- **Discriminação muito boa mantida**: área sob a curva ROC de **0,8095**

## Conclusao do proprio estudo
**"A mortalidade cirúrgica cardíaca reduziu-se significativamente nos últimos 15 anos, apesar de pacientes mais velhos e mais graves. O EuroSCORE II é melhor calibrado que o modelo original e preserva discriminação poderosa. É proposto para a avaliação futura do risco cirúrgico cardíaco."**

## Sintese pratica
O EuroSCORE II resolveu o problema central do modelo original — superestimação sistemática de mortalidade, que crescia justamente porque a cirurgia cardíaca foi ficando mais segura ao longo do tempo mesmo em pacientes mais complexos — mantendo discriminação forte (AUC 0,81). Na prática, ele é usado ao lado de outros escores (STS Risk Score é o principal comparador norte-americano) na avaliação pré-operatória e na decisão compartilhada entre cirurgia, intervenção percutânea e tratamento conservador, especialmente no Heart Team de valvopatia — é insumo de decisão, não substituto do julgamento clínico e da avaliação de fragilidade, que o escore não captura integralmente.

## Armadilhas clinicas
- Usar o EuroSCORE II isoladamente para excluir um paciente de cirurgia — é ferramenta de estimativa de risco populacional, não substituto da avaliação individualizada de fragilidade, capacidade funcional e comorbidade não totalmente capturada pelas variáveis do modelo
- Aplicar o EuroSCORE original (1995) esperando a mesma calibração do EuroSCORE II — o próprio estudo de desenvolvimento demonstrou que o modelo antigo superestima substancialmente a mortalidade na população cirúrgica atual (predição de 5,8-7,57% contra mortalidade real de 3,9%)
- Comparar diretamente o percentual do EuroSCORE II com o de outro escore de risco cirúrgico (como o STS) sem considerar que são modelos com variáveis e populações de derivação diferentes — não são diretamente intercambiáveis
- Presumir que boa discriminação (AUC 0,81) implica precisão exata para o paciente individual — discriminação mede a capacidade de separar grupos de risco na população estudada, não a exatidão da estimativa pontual para um paciente específico
