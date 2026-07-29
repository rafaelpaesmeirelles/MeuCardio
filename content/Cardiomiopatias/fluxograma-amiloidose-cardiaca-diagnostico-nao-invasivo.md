---
title: "Fluxograma: Amiloidose cardíaca — algoritmo diagnóstico não invasivo e tipagem genética"
slug: fluxograma-amiloidose-cardiaca-diagnostico-nao-invasivo
theme: "Cardiomiopatias"
kind: fluxograma
summary: "Árvore do algoritmo não invasivo do position statement da ESC: a pesquisa de proteína monoclonal vem antes da cintilografia na ordem de leitura, porque captação óssea grau 2 ou 3 só fecha diagnóstico de ATTR quando as três provas de clonalidade são normais — caso contrário exige histologia com tipagem."
review_status: revisado
source_refs: ["Garcia-Pavia P, Rapezzi C, Adler Y, et al. Diagnosis and treatment of cardiac amyloidosis: a position statement of the ESC Working Group on Myocardial and Pericardial Diseases · European Heart Journal · 2021 · 42(16):1554-1568 · DOI: 10.1093/eurheartj/ehab072 · PMID: 33825853 (co-publicado no European Journal of Heart Failure, DOI: 10.1002/ejhf.2140, versões idênticas salvo diferenças de estilo)", "Maurer MS, Schwartz JH, Gundapaneni B, et al. Tafamidis treatment for patients with transthyretin amyloid cardiomyopathy (ATTR-ACT) · New England Journal of Medicine · 2018 · 379(11):1007-1016 · DOI: 10.1056/NEJMoa1805689 · PMID: 30145929"]
---

# Fluxograma: Amiloidose cardíaca — algoritmo diagnóstico não invasivo e tipagem genética

O algoritmo não invasivo mudou a amiloidose cardíaca de diagnóstico de exceção,
que dependia de biópsia, para diagnóstico alcançável no consultório. Mas ele tem
uma regra de leitura que, invertida, produz o erro mais grave possível nesta
doença: **tratar uma amiloidose AL como se fosse ATTR**.

A regra é esta. A cintilografia com traçador ósseo positiva **não prova ATTR
sozinha** — captação miocárdica grau 2 ou 3 aparece em mais de 10% dos pacientes
com amiloidose de cadeia leve. Por isso a pesquisa de proteína monoclonal não é
exame complementar: ela é **condição de validade** da cintilografia. Se qualquer
uma das três provas de clonalidade estiver alterada, a cintilografia deixa de
poder estabelecer o diagnóstico, por mais intensa que seja a captação.

Os dois exames são pedidos juntos. É a leitura que é hierárquica.

## Quando levantar a suspeita

O gatilho estrutural é **espessura de parede do ventrículo esquerdo de 12 mm ou
mais, sem explicação**, em ventrículo não dilatado. Esse achado em idoso com
insuficiência cardíaca de fração de ejeção preservada, com diagnóstico de
cardiomiopatia hipertrófica ou com estenose aórtica grave — sobretudo o candidato
a TAVI — deve disparar a investigação: **a ATTR foi encontrada em até 7 a 19%
dos pacientes nesses cenários**.

Somam-se a isso os sinais de alerta:

| Cardíacos | Extracardíacos |
|---|---|
| baixa voltagem do QRS desproporcional à espessura de parede; padrão de pseudoinfarto ao ECG; distúrbio de condução atrioventricular; hipotensão; NT-proBNP desproporcionalmente elevado; elevação persistente de troponina; aspecto granular brilhante ao ecocardiograma; derrame pericárdico | síndrome do túnel do carpo bilateral; ruptura do tendão do bíceps; estenose de canal lombar; polineuropatia; disautonomia; equimoses cutâneas; macroglossia; depósitos vítreos; insuficiência renal e proteinúria; história familiar |

## Árvore de decisão: diagnóstico

```mermaid
flowchart TD
  R0["Espessura de parede do VE de 12 mm ou mais,<br/>sem explicação, em ventrículo não dilatado,<br/>com sinal de alerta clínico"] --> P1["Solicitar em conjunto: cintilografia com traçador ósseo<br/>— 99mTc-DPD, 99mTc-PYP ou 99mTc-HMDP — com SPECT<br/>para confirmar que a captação é miocárdica<br/>e não do compartimento sanguíneo; e as três provas<br/>de proteína monoclonal"]

  P1 --> P2["Provas de proteína monoclonal: eletroforese com<br/>imunofixação no soro, eletroforese com imunofixação<br/>na urina e relação de cadeias leves livres séricas"]

  P2 --> D1{"Alguma das três provas de proteína<br/>monoclonal está alterada?"}

  D1 -->|"Não: as três normais"| D2{"Grau de captação miocárdica<br/>na cintilografia"}

  D2 -->|"Grau 2 ou 3, com achados típicos<br/>ao ecocardiograma ou à ressonância"| C1(["Amiloidose cardíaca por transtirretina estabelecida<br/>sem biópsia. Seguir para tipagem genética"])

  D2 -->|"Grau 1"| C2(["Diagnóstico não invasivo não é possível:<br/>exige confirmação histológica de depósito amiloide,<br/>que pode ser obtida em sítio extracardíaco"])

  D2 -->|"Grau 0"| C3(["Probabilidade muito baixa de amiloidose cardíaca:<br/>ATTR e AL improváveis. Considerar diagnóstico alternativo.<br/>Se a suspeita persistir, ressonância cardíaca e, depois,<br/>biópsia cardíaca ou extracardíaca — a cintilografia pode<br/>ser negativa em algumas variantes de ATTRv"])

  D1 -->|"Sim: ao menos uma alterada"| D3{"Grau de captação miocárdica<br/>na cintilografia"}

  D3 -->|"Grau 2 ou 3"| C4(["Não assumir ATTR. Encaminhar ao hematologista<br/>e obter histologia com tipagem do amiloide,<br/>em geral por biópsia endomiocárdica"])

  D3 -->|"Grau 0 ou 1"| C5(["Demonstração histológica de amiloide, no coração<br/>ou em outro órgão clinicamente acometido,<br/>com tipagem — hipótese de amiloidose AL.<br/>Encaminhar ao hematologista sem retardar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Árvore de decisão: tipagem genética e rastreamento familiar

```mermaid
flowchart TD
  R1["Amiloidose cardíaca por<br/>transtirretina confirmada"] --> P3["Aconselhamento genético e sequenciamento<br/>do gene TTR — indicado inclusive no paciente idoso,<br/>porque parcela relevante deles carrega variante"]

  P3 --> D4{"Há variante patogênica<br/>no gene TTR?"}

  D4 -->|"Não"| C6(["ATTRwt, forma selvagem.<br/>Sem indicação de rastreamento genético familiar"])

  D4 -->|"Sim"| P4["ATTRv, forma hereditária: oferecer aconselhamento<br/>e teste genético em cascata aos familiares"]

  P4 --> D5{"O familiar testado é portador<br/>da variante?"}

  D5 -->|"Não"| C7(["Sem seguimento específico para amiloidose"])

  D5 -->|"Sim, portador<br/>ainda sem fenótipo"| C8(["Seguimento anual com ECG, NT-proBNP, troponina<br/>e ecocardiograma, iniciado cerca de 10 anos antes<br/>da idade de início da doença nos familiares afetados"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C6,C7,C8 conduta;
```

## A graduação de Perugini, que decide o nó `D2`

| Grau | Captação | Leitura |
|---|---|---|
| 0 | ausência de captação miocárdica, captação óssea normal | negativa |
| 1 | captação miocárdica menor que a óssea | insuficiente para diagnóstico não invasivo |
| 2 | captação miocárdica semelhante à óssea | positiva |
| 3 | captação miocárdica maior que a óssea, com captação óssea reduzida ou ausente | positiva |

O **SPECT é obrigatório**, não opcional: sem ele não se distingue captação do
miocárdio de captação do sangue nas câmaras, e o grau atribuído pode ser o de
outra estrutura.

## Os valores de referência da relação de cadeias leves livres

A relação kappa/lambda é o ponto em que o algoritmo mais escorrega, porque o
valor normal **depende do ensaio e da função renal**:

| Situação | Faixa considerada normal |
|---|---|
| Ensaio Freelite | 0,26 a 1,65 |
| Ensaio N Latex | 0,53 a 1,51 |
| Doença renal crônica com TFGe de 45 mL/min/1,73 m² ou menos, com eletroforeses séricas e urinárias normais | até 2,0 |
| Paciente em diálise | até 3,1 |

Ler a relação de um paciente renal crônico pela faixa do paciente com função
renal normal produz uma clonalidade que não existe — e joga para a biópsia um
paciente que teria diagnóstico não invasivo.

## O que as árvores não mostram

**Tratamento modificador da doença vale para os dois genótipos**, ATTRv e ATTRwt,
e por isso saiu do diagrama. O position statement coloca o **tafamidis como agente
de escolha na ATTR cardíaca**, e recomenda que seja considerado no paciente com
expectativa de sobrevida razoável. O ensaio pivotal é o **ATTR-ACT**: 441
pacientes, mortalidade por qualquer causa de 29,5% com tafamidis contra 42,9%
com placebo em 30 meses, e redução das hospitalizações cardiovasculares de 0,70
para 0,48 evento por ano. Os silenciadores gênicos **patisirana** e **inotersena**
e o **transplante hepático** são as outras opções nomeadas para a forma hereditária.

**Este documento é de diagnóstico, não de tratamento da insuficiência cardíaca
que acompanha a doença.** O manejo volumétrico, o cuidado com betabloqueador e
com inibidor do sistema renina-angiotensina no coração restritivo, e a conduta
diante de arritmia e de distúrbio de condução seguem recomendações próprias.

**O prognóstico da ATTR melhorou** nos últimos anos, e a própria diretriz atribui
isso à combinação de diagnóstico mais precoce, seguimento estruturado e terapia
específica — os três, não apenas o fármaco.

**Estenose aórtica grave e amiloidose coexistem com frequência que não é
anedótica.** Investigar antes do TAVI muda a expectativa de benefício do
procedimento, e é um dos cenários em que a diretriz explicitamente manda procurar.
