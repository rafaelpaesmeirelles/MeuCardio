---
title: "Fluxograma: DAC crônica estável — tratamento clínico otimizado versus revascularização (ISCHEMIA-informado, ESC 2024)"
slug: fluxograma-dac-cronica-estavel-tratamento-clinico-vs-revascularizacao
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: chatgpt
summary: "Depois que o diagnóstico anatômico e/ou funcional da DAC crônica estável já está fechado, a pergunta muda: tratar clinicamente ou revascularizar? A árvore separa a indicação por prognóstico (anatomia de alto risco, independente de sintomas) da indicação por sintomas (angina refratária ao tratamento otimizado), e usa o ISCHEMIA para justificar por que isquemia moderada/grave isolada, sem anatomia de alto risco, não obriga estratégia invasiva inicial."
review_status: revisado
review_note: "PMIDs conferidos nesta sessão via PubMed E-utilities (esummary): 39210710 (Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes, Eur Heart J. 2024;45(36):3415-3537, DOI 10.1093/eurheartj/ehae177), 32227755 (Maron DJ, Hochman JS, Reynolds HR, et al. Initial Invasive or Conservative Strategy for Stable Coronary Disease — ISCHEMIA, N Engl J Med. 2020;382(15):1395-1407, DOI 10.1056/NEJMoa1915922) e 30165437 (Neumann FJ, Sousa-Uva M, Ahlsson A, et al. 2018 ESC/EACTS Guidelines on myocardial revascularization, Eur Heart J. 2019;40(2):87-165, DOI 10.1093/eurheartj/ehy394) — título, revista, ano e volume/páginas batendo exatamente com o texto do documento. Este fluxograma cobre a decisão terapêutica (tratamento clínico versus revascularização) em quem já tem diagnóstico anatômico/funcional fechado; não duplica 'fluxograma-sindrome-coronariana-cronica-esc-2024' (que para na escolha do exame diagnóstico), nem 'fluxograma-revascularizacao-pci-versus-cabg-multiarterial-e-tronco' (que assume revascularização já indicada e decide a técnica), nem 'fluxograma-angina-estavel-refrataria-manejo-escalonado' (que trata de quem já esgotou tratamento clínico e revascularização). A lista de critérios anatômicos de alto risco é resumida de forma genérica a partir do corpo consolidado das diretrizes de revascularização (tronco, DA proximal com isquemia extensa, trivascular com diabetes, único vaso patente); nenhum corte numérico foi inventado além dos já publicados nesses documentos-fonte."
source_refs: ["Vrints C, Andreotti F, Koskinas KC, et al. 2024 ESC Guidelines for the management of chronic coronary syndromes · European Heart Journal · 2024 · 45(36):3415-3537 · DOI: 10.1093/eurheartj/ehae177 · PMID: 39210710", "Maron DJ, Hochman JS, Reynolds HR, et al. Initial Invasive or Conservative Strategy for Stable Coronary Disease (ISCHEMIA) · New England Journal of Medicine · 2020 · 382(15):1395-1407 · DOI: 10.1056/NEJMoa1915922 · PMID: 32227755", "Neumann FJ, Sousa-Uva M, Ahlsson A, et al. 2018 ESC/EACTS Guidelines on myocardial revascularization · European Heart Journal · 2019 · 40(2):87-165 · DOI: 10.1093/eurheartj/ehy394 · PMID: 30165437"]
---

# Fluxograma: DAC crônica estável — tratamento clínico otimizado versus revascularização

O algoritmo diagnóstico da síndrome coronariana crônica (ESC 2024) termina
quando o exame confirma ou afasta DAC obstrutiva. O que ele não responde é a
pergunta seguinte, que é terapêutica: **uma vez confirmada a doença, quem
precisa de revascularização e quem pode ser tratado só clinicamente?**

O ISCHEMIA (2020) mudou a resposta para um grupo específico: pacientes com
isquemia moderada ou grave, mas **sem anatomia de alto risco** (sem lesão de
tronco relevante, sem disfunção ventricular grave), em que uma estratégia
invasiva inicial **não reduziu** morte cardiovascular, infarto ou hospitalização
por angina instável em comparação com tratamento clínico otimizado, ao longo
de seguimento mediano de 3,2 anos. A árvore abaixo organiza a decisão em duas
perguntas distintas — **prognóstico** (a anatomia obriga revascularizar,
independente de sintoma) e **sintoma** (a angina obriga revascularizar,
independente de isquemia) — e só recorre ao ISCHEMIA quando nenhuma das duas
se aplica.

## Árvore de decisão

```mermaid
flowchart TD
  R0["DAC crônica estável,<br/>diagnóstico anatômico e/ou funcional já confirmado"] --> P1["Iniciar ou otimizar tratamento clínico:<br/>terapia anti-isquêmica e modificadores de doença<br/>(estatina de alta intensidade, antiagregante, IECA/BRA se indicado)"]
  P1 --> D1{"FEVE gravemente reduzida (< 35%)<br/>por miocardiopatia isquêmica?"}
  D1 -->|"Sim"| C1(["Via da disfunção ventricular isquêmica grave:<br/>sair deste fluxograma<br/>(revascularização guiada por viabilidade — ver documento próprio REVIVED-BCIS2)"])
  D1 -->|"Não"| D2{"Critério anatômico de alto risco prognóstico presente?<br/>(tronco significativo, DA proximal com isquemia extensa,<br/>trivascular com diabetes, único vaso coronário patente)"}
  D2 -->|"Sim"| P2["Discutir estratégia de revascularização em Heart Team"]
  P2 --> C2(["Revascularização indicada por prognóstico,<br/>independente de sintomas —<br/>escolher ICP ou CRM (ver fluxograma PCI versus CABG)"])
  D2 -->|"Não"| D3{"Angina persiste apesar de tratamento clínico<br/>otimizado (dose máxima tolerada de ao menos 2 classes antianginosas)?"}
  D3 -->|"Sim"| D4{"Anatomia coronariana favorável<br/>a revascularização percutânea ou cirúrgica?"}
  D4 -->|"Sim"| C3(["Revascularização indicada para alívio sintomático<br/>(ESC 2024, Classe I) —<br/>escolher técnica em Heart Team"])
  D4 -->|"Não"| C4(["Via da angina refratária sem opção de revascularização:<br/>seguir fluxograma de angina estável refratária"])
  D3 -->|"Não"| D5{"Isquemia moderada ou grave documentada em teste funcional,<br/>sem os critérios anatômicos de alto risco acima?"}
  D5 -->|"Sim"| C5(["Manter tratamento clínico otimizado como estratégia inicial<br/>(informado pelo ISCHEMIA): estratégia invasiva inicial não reduziu<br/>eventos duros nesta população;<br/>revascularização reservada para falha clínica ou decisão compartilhada"])
  D5 -->|"Não"| C6(["Manter tratamento clínico otimizado e seguimento clínico;<br/>sem indicação de revascularização neste momento"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## As duas indicações que independem uma da outra

**Indicação por prognóstico** entra primeiro na árvore porque não depende de
sintoma: tronco significativo, artéria descendente anterior proximal com
isquemia extensa, doença trivascular em diabético ou único vaso patente
remanescente são cenários em que a revascularização reduz eventos duros,
esteja o paciente sintomático ou não. É o mesmo corpo de critérios que
fundamenta a diretriz de revascularização (ESC/EACTS 2018) e que a árvore de
PCI-versus-CABG deste tema já detalha na escolha de técnica — aqui a pergunta
é anterior: **precisa revascularizar, sim ou não**, e só depois qual técnica.

**Indicação por sintoma** é independente da anterior: um paciente sem nenhum
critério anatômico de alto risco, mas com angina limitante apesar de
tratamento clínico otimizado, tem indicação de revascularização — porque o
ganho aqui é qualidade de vida, não sobrevida, e esse ganho é sustentado por
evidência própria de controle sintomático mesmo quando estudos com desfecho
duro (como o ISCHEMIA) não mostram redução de eventos.

## Onde o ISCHEMIA entra — e onde ele não entra

O ISCHEMIA só é citado no ramo em que **nenhuma das duas indicações acima se
aplica**: sem anatomia de alto risco, sem angina refratária, mas com isquemia
moderada/grave documentada em teste funcional — exatamente a população
randomizada no estudo. Nesse grupo, tratamento clínico otimizado como
estratégia inicial não foi inferiorizado por revascularização de rotina em
morte cardiovascular, infarto ou hospitalização por angina instável (16,4%
vs. 18,2% em 5 anos; diferença −1,8 ponto percentual, IC95% −4,7 a 1,0) nem em
mortalidade total (HR 1,05; IC95% 0,83–1,32). A leitura correta não é "não
revascularizar isquemia": é que a **presença isolada de isquemia moderada ou
grave, sem anatomia de alto risco e sem sintoma refratário, não obriga**
estratégia invasiva imediata.

## O que a árvore não mostra

**Pacientes com doença de tronco clinicamente significativa foram excluídos
do ISCHEMIA.** Por isso o critério de tronco aparece antes, no ramo de
prognóstico (D2), e nunca chega ao ramo informado pelo ISCHEMIA (D5) — são
populações estatisticamente diferentes, e misturá-las seria extrapolar o
estudo para fora da amostra em que foi testado.

**FEVE gravemente reduzida (< 35%) também foi critério de exclusão do
ISCHEMIA.** Por isso esse grupo sai do fluxograma já na primeira bifurcação
(D1), antes de qualquer critério anatômico ou de sintoma: a decisão de
revascularizar miocárdio isquêmico com disfunção ventricular grave segue
lógica própria (viabilidade miocárdica), tratada em documento específico da
biblioteca.

**Preferência do paciente informada** é parte da decisão em todos os ramos
não urgentes desta árvore, sobretudo no ramo do ISCHEMIA (C5): a diretriz
recomenda decisão compartilhada, com o paciente participando da escolha entre
aceitar o risco residual de sintoma sob tratamento clínico ou antecipar a
revascularização — isso não está representado como bifurcação porque não é
um critério clínico objetivo, é um eixo transversal à árvore.

**A técnica de revascularização (ICP versus CRM) não é decidida aqui.** Uma
vez que a árvore chega a C2 ou C3, a escolha entre angioplastia e cirurgia
segue o algoritmo do escore SYNTAX, diabetes e risco cirúrgico, já detalhado
no fluxograma de revascularização multiarterial e de tronco deste tema.
