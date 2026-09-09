---
title: "Duração da Hipotermia Terapêutica Após a Parada Cardiorrespiratória: o Ensaio ICECAP"
slug: duracao-da-hipotermia-terapeutica-pos-parada-cardiorrespiratoria-o-ensaio-icecap
theme: "Terapia intensiva"
kind: estudo
summary: "O ensaio ICECAP (JAMA, agosto de 2026), multicêntrico, adaptativo bayesiano, em 71 hospitais dos EUA, randomizou 1.158 comatosos pós-parada cardíaca extra-hospitalar (883 com ritmo não chocável, 275 com ritmo chocável) para durações de hipotermia a 33°C entre 6 e 72 horas. Aumentar a duração do resfriamento NÃO melhorou o desfecho neurológico em 90 dias — a duração mais curta testada (6 horas) teve probabilidade posterior de ser a ótima. Fecha uma lacuna distinta da já coberta pelos documentos de TTM/TTM2/HYPERION/BOX desta pasta: aqueles respondem 'que temperatura manter' e 'que meta de PAM/oxigenação usar'; nenhum documento desta pasta respondia 'por quanto tempo manter o resfriamento'."
review_status: revisado
source_refs: ["Meurer WJ, Yeatts SD, Geocadin RG, et al; SIREN Investigators. Duration of Therapeutic Hypothermia After Out-of-Hospital Cardiac Arrest: The ICECAP Randomized Clinical Trial. JAMA. 2026 Aug 5:e2610247. DOI: 10.1001/jama.2026.10247. PMID: 42554995. PMCID: PMC13445112", "Meurer WJ, Silbergleit R, Roy A, et al. Influence of Cooling duration on Efficacy in Cardiac Arrest Patients (ICECAP): study protocol for a multicenter, randomized, adaptive allocation clinical trial. Trials. 2024;25(1):485. DOI: 10.1186/s13063-024-08290-y. PMID: 39044295 — usado só para confirmar o desenho adaptativo bayesiano e o registro ClinicalTrials.gov NCT04217551, não para nenhum resultado de eficácia"]
legacy_source: "Documento novo. Verificado por grep em toda a pasta content/Terapia_intensiva/ (title, corpo e slug) que nenhum documento existente menciona 'ICECAP', 'duração da hipotermia' ou 'duração do resfriamento' — os três documentos que tratam de controle de temperatura pós-parada (controle-de-temperatura-pos-parada-cardiorrespiratoria-ttm-e-ttm2.md, evolucao-historica-do-controle-de-temperatura-pos-parada-de-haca-bernard-2002-ao-ttm2.md, hipotermia-terapeutica-em-ritmo-nao-chocavel-pos-parada-o-ensaio-hyperion.md) respondem qual temperatura-alvo usar (33°C vs. 36°C/normotermia no TTM/TTM2; hipotermia em ritmo não chocável no HYPERION), e o documento de BOX responde meta de PAM e de oxigenação — nenhum deles trata da variável duração do resfriamento, que é exatamente o que o ICECAP testa. Abstract completo lido verbatim via E-utilities do PubMed (efetch, retmode=text) nesta sessão antes da redação; nenhum número foi escrito de memória."
---

# Duração da Hipotermia Terapêutica Após a Parada Cardiorrespiratória: o Ensaio ICECAP

Os documentos já existentes desta pasta sobre controle de temperatura
pós-parada — TTM, TTM2 e a evolução histórica do tema — respondem **qual
temperatura-alvo** usar (33°C induzido versus 36°C, ou hipotermia versus
normotermia com controle ativo de febre). O documento de HYPERION amplia essa
pergunta para o ritmo não chocável. Nenhum deles responde a uma pergunta
prática diferente e igualmente relevante à beira do leito: uma vez decidido
induzir hipotermia a 33°C, **por quantas horas mantê-la**? É essa lacuna que
o ensaio ICECAP (*Influence of Cooling duration on Efficacy in Cardiac Arrest
Patients*) fecha, com o desfecho publicado em agosto de 2026 na *JAMA*.

## O problema que motivou o desenho

A duração convencional de manutenção da hipotermia terapêutica em 33°C nos
grandes ensaios anteriores (incluindo o TTM original) foi fixada em **24
horas**, mas esse número nunca foi ele mesmo testado de forma randomizada
contra outras durações — foi herdado de protocolos observacionais e da
prática clínica que precedeu os próprios ensaios de eficácia da hipotermia.
O ICECAP foi desenhado explicitamente para responder qual duração de
resfriamento maximiza a recuperação neurológica, usando um desenho adaptativo
que permite testar um espectro amplo de durações sem expor um número fixo de
pacientes a cada braço.

## Desenho: ensaio multicêntrico, adaptativo bayesiano

Meurer WJ et al.; SIREN Investigators. *JAMA*. 2026 Aug 5:e2610247 (PMID
42554995, PMCID PMC13445112). Ensaio multicêntrico, randomizado, de alocação
adaptativa, conduzido em **71 hospitais dos Estados Unidos**, com
recrutamento entre **junho de 2020 e junho de 2025**.

- **População**: adultos com parada cardiorrespiratória extra-hospitalar que
  permaneceram inconscientes, atingiram temperatura-alvo abaixo de 34°C em
  até 4 horas do evento, e já tinham dispositivo definitivo de controle de
  temperatura instalado.
- **Intervenção**: hipotermia terapêutica a **33°C**, com alocação
  randomizada adaptativa para durações de **6, 12, 18, 24, 30, 36, 42, 48,
  60 ou 72 horas**. Os primeiros 200 pacientes foram randomizados apenas
  entre 12, 24 e 48 horas, na proporção 1:1:1; a partir daí, um algoritmo de
  randomização responsiva a resposta (*response-adaptive randomization*)
  passou a alocar preferencialmente para as durações mais prováveis de
  serem ótimas, construindo a curva duração-resposta **separadamente para
  cada tipo de ritmo inicial** (chocável e não chocável).
- **Desfecho primário**: função neurológica em 90 dias, medida por um
  **escore de Rankin modificado ponderado** (*weighted modified Rankin
  Scale*), analisado por um **modelo bayesiano de duração-resposta**. A
  análise primária estimou a probabilidade posterior de cada duração ser a
  "ótima" — definida como a **duração mais curta** consistente com o melhor
  desfecho observado em qualquer duração testada.

## Resultado: aumentar a duração não melhorou o desfecho neurológico

**1.158 pacientes** foram randomizados — **883 com ritmo inicial não
chocável** e **275 com ritmo inicial chocável**. Idade mediana de 61 anos
(IQR 50-70), 39,6% mulheres.

**O ensaio atingiu uma regra de interrupção pré-especificada na análise
interina.**

- **Coorte de ritmo não chocável**: a probabilidade posterior de que **6
  horas** fosse a duração mais curta que atingia o escore de Rankin
  modificado ponderado médio máximo foi de **0,51**.
- **Coorte de ritmo chocável**: resultado semelhante.
- **Nenhuma diferença foi observada em desfechos secundários ou em
  mortalidade** entre as diferentes durações de resfriamento testadas.

**Conclusão do próprio ensaio, verbatim do abstract**: entre sobreviventes
comatosos de parada cardiorrespiratória extra-hospitalar tratados com
hipotermia terapêutica a 33°C, **aumentar a duração do resfriamento não
melhorou o desfecho neurológico**.

## Leitura clínica

O ICECAP não questiona **se** induzir hipotermia (essa é a pergunta que
TTM/TTM2 já abordaram, com resultado neutro entre 33°C e 36°C/normotermia
ativamente controlada) — ele testa, dado que a equipe já decidiu induzir
hipotermia a 33°C, por quanto tempo mantê-la. A probabilidade posterior de
apenas 0,51 para 6 horas (a duração mais curta testada) na coorte de ritmo
não chocável, combinada com a ausência de diferença em qualquer duração
maior, sustenta a leitura de que **prolongar o resfriamento além do
mínimo necessário para atingir a meta térmica não trouxe benefício
neurológico adicional mensurável neste ensaio** — não que 6 horas seja
comprovadamente superior a 24 ou 48 horas, mas que nenhuma duração testada
se mostrou melhor que outra.

**Isto não equivale a "hipotermia não funciona"** — os documentos de TTM/
TTM2 já registram que a comparação central de temperatura-alvo (33°C vs.
36°C/normotermia) também foi neutra, e a leitura combinada de toda essa
linha de evidência aponta consistentemente para o **controle ativo de
febre** como a intervenção com sustentação mais robusta, não para a
indução de frio profundo nem para o prolongamento do resfriamento em si.

## Armadilhas clínicas

- Interpretar o ICECAP como evidência de que hipotermia deve ser **abolida**
  — o ensaio não comparou hipotermia contra ausência de controle de
  temperatura; comparou durações diferentes de hipotermia entre si, em
  pacientes que a equipe já havia decidido resfriar a 33°C.
- Concluir que **6 horas é a duração recomendada** — a probabilidade
  posterior de 0,51 é discretamente acima do acaso, e o próprio desenho
  bayesiano do ensaio define "ótimo" como a duração mais curta compatível
  com o melhor desfecho observado, não como superioridade estatística clara
  de 6 horas sobre as demais.
- Extrapolar o resultado para pacientes que atingem a temperatura-alvo **além
  de 4 horas** do evento, ou que não têm dispositivo definitivo de controle
  de temperatura já instalado — são critérios de elegibilidade explícitos do
  ICECAP.
- Confundir o desenho adaptativo bayesiano deste ensaio (que redistribui a
  alocação de pacientes ao longo do tempo conforme os dados acumulam) com um
  ensaio de grupos paralelos de tamanho fixo, como TTM2 e BOX — a
  interpretação estatística e o significado de "atingir a regra de
  interrupção pré-especificada" são próprios desse desenho.
- Tratar a coorte de ritmo chocável (275 pacientes, resultado "semelhante"
  segundo o próprio abstract, sem número de probabilidade posterior
  detalhado no resumo) como tendo a mesma robustez amostral que a coorte de
  ritmo não chocável (883 pacientes) — **VERIFICAÇÃO HUMANA NECESSÁRIA** para
  o valor exato da probabilidade posterior na coorte de ritmo chocável, que
  o abstract não numera; o texto completo do artigo deve ser consultado
  antes de citar um número específico para esse subgrupo.
