---
title: "Escore GWTG-HF: Mortalidade Intra-Hospitalar na Insuficiência Cardíaca Aguda"
slug: escore-gwtg-hf-mortalidade-intra-hospitalar-na-insuficiencia-cardiaca-aguda
theme: "Calculadoras"
kind: calculadora
review_status: revisado
source_refs: ["Peterson PN, Rumsfeld JS, Liang L, et al; American Heart Association Get With the Guidelines-Heart Failure Program. A validated risk score for in-hospital mortality in patients with heart failure from the American Heart Association get with the guidelines program. Circ Cardiovasc Qual Outcomes. 2010;3(1):25-32. DOI: 10.1161/CIRCOUTCOMES.109.854877. PMID: 20123668"]
legacy_source: "Documento novo — o Seattle Heart Failure Model já registrado nesta pasta estima sobrevida de longo prazo (1-3 anos) em IC crônica ambulatorial. O GWTG-HF responde pergunta diferente e complementar: risco de morte intra-hospitalar numa internação aguda por IC, calculado com dado disponível já na admissão."
---

# Escore GWTG-HF: Mortalidade Intra-Hospitalar na Insuficiência Cardíaca Aguda

## Aplicacao
Complementa o Seattle Heart Failure Model já registrado nesta pasta, que estima sobrevida de longo prazo (1 a 3 anos) em insuficiência cardíaca (IC) crônica ambulatorial. O GWTG-HF responde a uma pergunta diferente: qual o risco de morte **durante a própria internação** por IC aguda, estimado com variáveis já disponíveis na admissão — útil para triagem de gravidade e decisão de nível de cuidado logo na entrada do paciente, não para prognóstico ambulatorial de longo prazo.

## O estudo de derivacao e validacao (peterson, circ cardiovasc qual outcomes 2010)
Peterson PN et al.; American Heart Association Get With the Guidelines-Heart Failure Program. Circ Cardiovasc Qual Outcomes. 2010;3(1):25-32 (PMID 20123668). Coorte de **39.783 pacientes** internados por IC entre 01/01/2005 e 26/06/2007 em **198 hospitais** participantes do registro GWTG-HF, dividida em amostra de derivação (70%, n=27.850) e de validação (30%, n=11.933):
- **Mortalidade intra-hospitalar de 2,86%** (1.139 óbitos) na coorte total
- **Regressão logística multivariável** identificou como preditores independentes: idade, pressão arterial sistólica, ureia (blood urea nitrogen), frequência cardíaca, sódio sérico, doença pulmonar obstrutiva crônica e raça não negra
- **Discriminação boa e semelhante** nas amostras de derivação e validação — **índice C de 0,75 em ambas**
- **Gradiente de risco muito acentuado**: probabilidade prevista de mortalidade intra-hospitalar variou **mais de 24 vezes entre decis de risco** (de 0,4% a 9,7%), com correspondência próxima entre mortalidade prevista e observada
- **Mesmas características operacionais do modelo** em pacientes com função sistólica do ventrículo esquerdo preservada e com função reduzida — aplicável a ambos os fenótipos de IC

## Conclusao do proprio estudo
**"O escore de risco GWTG-HF usa variáveis clínicas comumente disponíveis para prever mortalidade intra-hospitalar e fornece aos clínicos uma ferramenta validada de estratificação de risco aplicável a um amplo espectro de pacientes com insuficiência cardíaca, incluindo aqueles com função sistólica do ventrículo esquerdo preservada."**

## Sintese pratica
O GWTG-HF preenche uma lacuna real e distinta do Seattle Heart Failure Model já registrado: enquanto aquele estima sobrevida ambulatorial de longo prazo em IC crônica, o GWTG-HF foi derivado e validado especificamente para o momento da internação aguda, com variáveis já disponíveis à admissão (idade, pressão arterial sistólica, ureia, frequência cardíaca, sódio, DPOC, raça) — sem exigir dado que só surge depois de dias de internação. O gradiente de risco de mais de 24 vezes entre decis é a característica mais útil na prática: permite diferenciar, logo na entrada, o paciente de baixíssimo risco (0,4%) do de risco muito alto (9,7%) usando os mesmos dados de rotina da admissão. É válido tanto para ICFEr quanto para ICFEp, o que amplia sua aplicabilidade além de escores desenhados só para um fenótipo.

## Armadilhas clinicas
- Confundir o GWTG-HF com o Seattle Heart Failure Model já registrado nesta pasta — são ferramentas para momentos e perguntas diferentes: mortalidade **intra-hospitalar** na IC aguda (GWTG-HF) versus sobrevida de **longo prazo** na IC crônica ambulatorial (Seattle)
- Aplicar o escore fora do contexto de admissão por IC aguda descompensada — o modelo foi derivado especificamente para esse cenário, com variáveis coletadas na admissão hospitalar
- Tratar o índice C de 0,75 como discriminação excepcional — é discriminação boa e consistente entre derivação e validação, mas não excepcionalmente alta; a força prática do modelo está no gradiente de risco muito acentuado entre decis, não isoladamente na estatística de discriminação
- Ignorar que a coorte é de 2005-2007, período anterior à ampla adoção de terapias atuais para IC (por exemplo, inibidores de SGLT2) — o escore estima risco de mortalidade intra-hospitalar com base nas variáveis clínicas de admissão, e não incorpora terapia em curso como variável preditora
