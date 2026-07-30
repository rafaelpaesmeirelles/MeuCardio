---
title: "Framingham Risk Score (FRS)"
slug: framingham-risk-score-frs
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: ["D'Agostino RB Sr, Vasan RS, Pencina MJ, et al. General cardiovascular risk profile for use in primary care: the Framingham Heart Study. Circulation. 2008;117(6):743-753. DOI: 10.1161/CIRCULATIONAHA.107.699579. PMID: 18212285", "Fontenelle LF, Sarti TD, Quinte GC, Almeida APSC, Mill JG. Agreement between Framingham, Pooled Cohort Equations, and Globorisk-LAC in the Estimation of Cardiovascular Risk in Brazil, 2013. Arq Bras Cardiol. 2025;122(6):e20240405. DOI: 10.36660/abc.20240405. PMID: 40736124"]
legacy_source: "calculadoras/calculadora-framingham-risk-score.md"
---

# Framingham Risk Score (FRS)

## Nome
Framingham Risk Score (FRS)

## Aplicacao
Estimativa de risco de doença cardiovascular em 10 anos, um dos primeiros e mais tradicionais escores de risco cardiovascular, ainda usado como referência histórica e em algumas diretrizes regionais

## Variaveis
- Idade
- Sexo
- Colesterol total
- Colesterol HDL
- Pressão arterial sistólica (tratada ou não tratada)
- Tabagismo atual
- Diabetes

## Pontuacao idade
- **faixas homens**: [{'faixa': '35-39', 'pontos': 2}, {'faixa': '40-44', 'pontos': 5}, {'faixa': '45-49', 'pontos': 7}, {'faixa': '50-54', 'pontos': 8}, {'faixa': '55-59', 'pontos': 10}, {'faixa': '60-64', 'pontos': 11}, {'faixa': '65-69', 'pontos': 12}, {'faixa': '70-74', 'pontos': 14}, {'faixa': '≥75', 'pontos': 15}]
- **faixas mulheres**: [{'faixa': '35-39', 'pontos': 2}, {'faixa': '40-44', 'pontos': 4}, {'faixa': '45-49', 'pontos': 5}, {'faixa': '50-54', 'pontos': 7}, {'faixa': '55-59', 'pontos': 8}, {'faixa': '60-64', 'pontos': 9}, {'faixa': '65-69', 'pontos': 10}, {'faixa': '70-74', 'pontos': 11}, {'faixa': '≥75', 'pontos': 12}]
- **fonte**: VERIFICAÇÃO HUMANA NECESSÁRIA — estas tabelas de pontos estão em mmol/L e não correspondem ao modelo de D'Agostino RB Sr et al., Circulation 2008;117:743-753, que é a referência do FRS geral. Parecem vir de uma adaptação regional não identificada; conferir a procedência antes de usar

## Pontuacao hdl mmol l
- **faixa**: >1,60; **pontos**: -2
- **faixa**: 1,30-1,60; **pontos**: -1
- **faixa**: 1,20-1,29; **pontos**: 0
- **faixa**: 0,90-1,19; **pontos**: 1
- **faixa**: <0,90; **pontos**: 2

## Pontuacao colesterol total mmol l
- **faixa**: 4,10-5,19; **pontos homem**: 1; **pontos mulher**: 1
- **faixa**: 5,20-6,19; **pontos homem**: 2; **pontos mulher**: 3
- **faixa**: 6,20-7,20; **pontos homem**: 3; **pontos mulher**: 4
- **faixa**: >7,20; **pontos homem**: 4; **pontos mulher**: 5

## Pontuacao pas mmhg
Varia conforme tratado/não tratado e sexo: ex. <120 (-2 homem não tratado / -3 mulher não tratada); ≥160 (3 pontos homem não tratado / 5 pontos mulher não tratada) — tabela completa requer consulta detalhada

## Fator historia familiar
Regra especial: dobrar o percentual de risco cardiovascular calculado em indivíduos de 30-59 anos sem diabetes, se houver história familiar de doença cardiovascular prematura em parente de 1º grau (antes de 55 anos em homens, antes de 65 anos em mulheres)

## Interpretacao
- **mulheres**: Risco alto: ≥18 pontos; Risco intermediário: 13-17 pontos
- **homens**: Risco alto: ≥15 pontos; Risco intermediário: 11-14 pontos
- **classificacao percentual**: Alto se risco ≥20%; Intermediário se 10-19%; Baixo se <10%

## Particularidade
Ferramenta também calcula 'idade cardíaca' (heart age), um conceito de comunicação de risco que traduz o risco calculado em uma idade cardiovascular equivalente, facilitando compreensão pelo paciente

## Limitacoes
Desenvolvido em coorte predominantemente branca americana; desempenho pode ser inferior a escores mais contemporâneos (SCORE2) em populações europeias ou não caucasianas

**Desempenho medido especificamente na população brasileira — acrescentado em 30/07/2026** (Fontenelle LF, Sarti TD, Quinte GC, Almeida APSC, Mill JG. Agreement between Framingham, Pooled Cohort Equations, and Globorisk-LAC in the Estimation of Cardiovascular Risk in Brazil, 2013. Arq Bras Cardiol. 2025;122(6):e20240405. DOI: 10.36660/abc.20240405. PMID: 40736124): estudo transversal com 4.416 participantes de 40-74 anos, sem doença cardiovascular prévia, dados da Pesquisa Nacional de Saúde (PNS) 2013. **O Framingham nunca foi recalibrado para a população brasileira** — nem o Pooled Cohort Equations (PCE); só o Globorisk-LAC foi recalibrado para a América Latina. Risco mediano estimado em 10 anos: **9,2% pelo Framingham vs. 3,6% pelo PCE vs. 4,7% pelo Globorisk-LAC** — o Framingham estimou risco sistematicamente mais alto que os outros dois nesta amostra brasileira. Concordância (razão entre 0,80 e 1,25x): Framingham com Globorisk-LAC em apenas **6,4%** dos casos, com PCE em **1,8%** — enquanto PCE e Globorisk-LAC concordaram em 34,7%. Coeficiente de concordância por categoria de risco (Gwet AC1): Framingham×Globorisk-LAC 0,454, Framingham×PCE 0,489, PCE×Globorisk-LAC 0,874 — **os três escores concordam pouco entre si**, e o Framingham é o mais discrepante dos três. Conclusão dos próprios autores: o Globorisk-LAC é forte candidato a substituir o Framingham nas diretrizes brasileiras de dislipidemia.

## Fonte
Canadian Cardiovascular Society — pista importante sobre a procedência: as tabelas de pontos em mmol/L acima provavelmente vêm da adaptação canadense do escore, não do modelo de D'Agostino RB Sr et al., Circulation 2008;117:743-753, que é a referência do FRS geral. VERIFICAÇÃO HUMANA NECESSÁRIA para confirmar a origem e decidir qual das duas versões o documento descreve.
