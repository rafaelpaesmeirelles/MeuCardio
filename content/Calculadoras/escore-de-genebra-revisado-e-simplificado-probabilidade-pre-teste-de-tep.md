---
title: "Escore de Genebra Revisado e Simplificado: Probabilidade Pré-Teste de TEP"
slug: escore-de-genebra-revisado-e-simplificado-probabilidade-pre-teste-de-tep
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Le Gal G, Righini M, Roy PM, Sanchez O, Aujesky D, Bounameaux H, Perrier A. Prediction of pulmonary embolism in the emergency department: the revised Geneva score. Ann Intern Med. 2006;144(3):165-171. DOI: 10.7326/0003-4819-144-3-200602070-00004. PMID: 16461960 — derivação e validação externa em dois estudos de manejo independentes", "Klok FA, Mos ICM, Nijkeuter M, Righini M, Perrier A, Le Gal G, Huisman MV. Simplification of the revised Geneva score for assessing clinical probability of pulmonary embolism. Arch Intern Med. 2008;168(19):2131-2136. DOI: 10.1001/archinte.168.19.2131. PMID: 18955643 — validação em 1.049 pacientes de dois ensaios diagnósticos prospectivos"]
legacy_source: "Documento novo, escrito em 31/07/2026. O tema Calculadoras já tinha o escore de Wells para TVP e TEP e o PESI/sPESI (gravidade), mas não o escore de Genebra — que é a alternativa ao Wells para probabilidade pré-teste e tem uma vantagem específica: não depende de julgamento subjetivo do médico."
---

# Escore de Genebra Revisado e Simplificado: Probabilidade Pré-Teste de TEP

## Por que existe uma alternativa ao wells
O diagnóstico de TEP começa por estimar a **probabilidade pré-teste** — é ela que define se um D-dímero negativo basta para afastar, ou se é preciso ir direto à imagem. O escore de Wells cumpre esse papel, mas tem um item que é fonte conhecida de variabilidade: **"diagnóstico alternativo menos provável que TEP"**, que depende do julgamento implícito de quem avalia.

Os autores do Genebra revisado enunciam exatamente esse objetivo: construir um escore **inteiramente baseado em variáveis clínicas e independente do julgamento implícito do médico**.

## Escore de genebra revisado — os oito itens e seus pontos
Le Gal G et al., Ann Intern Med. 2006;144(3):165-171 (PMID 16461960). Derivado e validado externamente em dois estudos de manejo independentes, em prontos-socorros de três hospitais universitários europeus:

| Variável | Pontos |
|---|---|
| Idade acima de 65 anos | **1** |
| TVP ou TEP prévios | **3** |
| Cirurgia ou fratura no último mês | **2** |
| Neoplasia maligna ativa | **2** |
| Dor unilateral em membro inferior | **3** |
| Hemoptise | **2** |
| Frequência cardíaca **75 a 94 bpm** | **3** |
| Frequência cardíaca **95 bpm ou mais** | **5** |
| Dor à palpação venosa profunda de membro inferior **e** edema unilateral | **4** |

**Nenhum item depende de impressão clínica** — é a diferença central em relação ao Wells.

## Faixas e prevalencia observada na validacao
| Categoria | Pontuação | Prevalência de TEP |
|---|---|---|
| **Baixa** probabilidade | 0 a 3 | **8%** |
| **Intermediária** | 4 a 10 | **28%** |
| **Alta** | 11 ou mais | **74%** |

## A versao simplificada, e por que ela e util
Klok FA et al., Arch Intern Med. 2008;168(19):2131-2136 (PMID 18955643). O problema apontado: **os itens têm pesos diferentes, o que pode gerar erro de cálculo no atendimento agudo**. A simplificação atribui **1 ponto a cada item** do escore original.

**Validação em 1.049 pacientes** de dois ensaios diagnósticos prospectivos, com prevalência global de tromboembolismo venoso de 23%:
- **Acurácia diagnóstica praticamente idêntica**: área sob a curva **0,75** (IC95% 0,71-0,78) para o revisado vs. **0,74** (0,70-0,77) para o simplificado
- **Segurança de afastar TEP**, em 3 meses de seguimento, combinando o escore com **D-dímero de alta sensibilidade normal**: **nenhum** paciente teve tromboembolismo venoso diagnosticado — probabilidade baixa **0%** (IC95% 0,0-1,7), intermediária **0%** (0,0-2,8), e "TEP improvável" pela regra dicotomizada **0%** (0,0-1,2)

**Conclusão:** simplificar não reduziu acurácia nem utilidade clínica — e reduz a chance de errar a conta à beira do leito.

## Como usar na pratica
- **O escore não faz diagnóstico**: ele define a **estratégia**. Probabilidade baixa ou intermediária (ou "TEP improvável") **com D-dímero de alta sensibilidade normal** permite afastar TEP com segurança — é exatamente essa combinação que foi validada
- **Probabilidade alta não se resolve com D-dímero** — vai para imagem
- **A escolha entre Wells e Genebra é de preferência e contexto.** O Genebra dispensa julgamento subjetivo, o que ajuda em serviço com muitos avaliadores diferentes; o Wells é mais difundido. O escore de Wells está em `escore-de-wells-dvt-e-embolia-pulmonar-criterios-completos.md`, nesta mesma pasta
- **Não confundir com o PESI**: Genebra e Wells estimam **probabilidade de haver TEP**; o PESI estima **gravidade de quem já tem TEP** — ver `pesi-e-spesi-escore-de-gravidade-do-tromboembolismo-pulmonar.md`

## Armadilhas clinicas
- **Usar o escore para excluir TEP sem D-dímero** — a segurança validada é da **combinação** escore + D-dímero de alta sensibilidade
- **Aplicar D-dímero em probabilidade alta** — nessa faixa (74% de prevalência) o exame não afasta
- **Somar os pontos de frequência cardíaca duas vezes** — as duas faixas são mutuamente excludentes: 3 pontos **ou** 5 pontos
- **Confundir probabilidade pré-teste com gravidade** — são escores diferentes, para perguntas diferentes
- **Usar o simplificado com as faixas do revisado** — as pontuações não são intercambiáveis, porque na versão simplificada cada item vale 1
- **Ignorar a limitação declarada do estudo original**: a **concordância entre observadores dos itens não foi estudada**
