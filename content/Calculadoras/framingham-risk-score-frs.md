---
title: "Framingham Risk Score (FRS)"
slug: framingham-risk-score-frs
theme: "Calculadoras"
kind: calculadora
review_status: pendente_revisao
source_refs: []
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
- **fonte**: Empendium McMaster

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

## Fonte
Canadian Cardiovascular Society ; Empendium McMaster
