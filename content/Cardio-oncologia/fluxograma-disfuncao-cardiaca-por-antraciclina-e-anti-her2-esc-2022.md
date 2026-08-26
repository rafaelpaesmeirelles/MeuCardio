---
title: "Fluxograma: Disfunção cardíaca relacionada ao tratamento oncológico — antraciclina e terapia anti-HER2 (ESC 2022)"
slug: fluxograma-disfuncao-cardiaca-por-antraciclina-e-anti-her2-esc-2022
theme: "Cardio-oncologia"
kind: fluxograma
summary: "Duas árvores da diretriz ESC 2022 de cardio-oncologia, e elas divergem de propósito: na antraciclina, a CTRCD moderada assintomática manda interromper; na terapia anti-HER2, a mesma faixa de fração de ejeção manda continuar com cardioproteção. Confundir as duas custa tratamento oncológico."
review_status: revisado
review_note: "Revisado em 26/08/2026 contra o texto primário oficial da ESC 2022, DOI 10.1093/eurheartj/ehac244: Tabela 3 e Tabelas de Recomendação 24-25/Figuras 25-26. A árvore anti-HER2 foi completada com os critérios de reinício após recuperação (assintomático e FEVE >=40%, idealmente >=50%), a vigilância por ecocardiograma e biomarcadores a cada dois ciclos nos quatro primeiros ciclos após reinício e a exceção restrita ao paciente já assintomático cuja FEVE persiste abaixo de 40%, com câncer avançado responsivo e sem alternativa eficaz. Sintomas de IC persistentes bloqueiam o reinício nesta árvore. Nenhuma classe ou nível de evidência foi inferido a partir da apresentação gráfica. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Lyon AR, López-Fernández T, Couch LS, et al. 2022 ESC Guidelines on cardio-oncology developed in collaboration with the European Hematology Association (EHA), the European Society for Therapeutic Radiology and Oncology (ESTRO) and the International Cardio-Oncology Society (IC-OS) · European Heart Journal · 2022 · 43(41):4229-4361 · DOI: 10.1093/eurheartj/ehac244 — Tabela 3 (definição e graduação de CTRCD), Tabela de Recomendação 24 (manejo durante quimioterapia com antraciclina) e Tabela de Recomendação 25/Figura 26 (manejo durante terapia anti-HER2, interrupção, reinício e vigilância)"]
---

# Fluxograma: Disfunção cardíaca relacionada ao tratamento oncológico — antraciclina e terapia anti-HER2 (ESC 2022)

A diretriz ESC 2022 fez duas coisas que mudam a conduta à beira do leito. Primeiro,
**graduou** a disfunção cardíaca relacionada ao tratamento do câncer — a CTRCD —
em leve, moderada, grave e muito grave, em vez de tratá-la como categoria única.
Segundo, ligou cada grau a uma conduta específica sobre **continuar, interromper
temporariamente ou suspender** a quimioterapia.

E aqui está a razão de existirem duas árvores separadas neste documento: **as
condutas não são as mesmas para antraciclina e para terapia dirigida ao HER2**.
Um paciente assintomático com fração de ejeção de 40 a 49% deve ter a antraciclina
**interrompida**; o mesmo paciente, em terapia anti-HER2, deve **continuar** o
tratamento oncológico com cardioproteção associada e monitorização frequente. A
diferença não é descuido de redação — reflete que a cardiotoxicidade da antraciclina
é tipicamente cumulativa e menos reversível, enquanto a da terapia anti-HER2 costuma
ser reversível.

## Como a CTRCD é graduada (Tabela 3 da diretriz)

**CTRCD sintomática**, isto é, com insuficiência cardíaca manifesta:

| Grau | Definição |
|---|---|
| Muito grave | insuficiência cardíaca exigindo suporte inotrópico, suporte circulatório mecânico ou consideração de transplante |
| Grave | internação por insuficiência cardíaca |
| Moderada | necessidade de intensificação ambulatorial do diurético e da terapia de insuficiência cardíaca |
| Leve | sintomas leves, sem necessidade de intensificar o tratamento |

**CTRCD assintomática**:

| Grau | Definição |
|---|---|
| Grave | nova redução da FEVE para menos de 40% |
| Moderada | nova redução da FEVE de 10 pontos percentuais ou mais, chegando a 40–49%; **ou** redução de menos de 10 pontos até 40–49% **associada a** queda relativa nova do GLS maior que 15% **ou** nova elevação de biomarcador cardíaco |
| Leve | FEVE de 50% ou mais **com** queda relativa nova do GLS maior que 15% **e/ou** nova elevação de biomarcador cardíaco |

**Queda significativa do GLS, nesta diretriz, é redução relativa maior que 15%**
em relação ao valor basal. A Diretriz Brasileira de Cardio-oncologia de 2020 usa
o corte de redução **igual ou maior que 15%** — a diferença está na borda, e vale
saber de qual documento veio o número que se está aplicando.

## Árvore de decisão: CTRCD durante quimioterapia com antraciclina

```mermaid
flowchart TD
  R0["Paciente em quimioterapia com antraciclina<br/>e nova alteração cardíaca na vigilância"] --> D1{"Há sintomas de<br/>insuficiência cardíaca?"}

  D1 -->|"Sim, sintomático"| D2{"Grau do quadro sintomático"}

  D2 -->|"Grave ou muito grave: internação por IC,<br/>ou necessidade de inotrópico, suporte circulatório<br/>mecânico ou consideração de transplante"| C1(["Suspender a antraciclina — Classe I, nível C.<br/>Tratamento de insuficiência cardíaca conforme<br/>diretriz — Classe I, nível B"])

  D2 -->|"Moderado: necessidade de intensificação<br/>ambulatorial do diurético e da terapia de IC"| C2(["Interromper temporariamente a antraciclina<br/>— Classe I, nível C —, com a decisão de reiniciar<br/>tomada em equipe multidisciplinar — Classe I, nível C.<br/>Tratamento de IC — Classe I, nível B"])

  D2 -->|"Leve: sintomas leves, sem necessidade<br/>de intensificar o tratamento"| C3(["Interromper ou continuar é decisão da equipe<br/>multidisciplinar — Classe I, nível C.<br/>Tratamento de IC — Classe I, nível B"])

  D1 -->|"Não, assintomático"| D3{"O que mostram a FEVE, o strain longitudinal<br/>global e os biomarcadores?"}

  D3 -->|"Grave: nova FEVE abaixo de 40%"| C4(["Interromper temporariamente a antraciclina<br/>e iniciar terapia de insuficiência cardíaca<br/>— Classe I, nível C. Quando reiniciar é decisão<br/>da equipe multidisciplinar — Classe I, nível C"])

  D3 -->|"Moderada: queda de FEVE de 10 pontos ou mais<br/>até 40 a 49%; ou queda menor que 10 pontos até<br/>40 a 49% com queda relativa do GLS maior que 15%<br/>ou nova elevação de biomarcador"| C5(["Interromper temporariamente a antraciclina<br/>e iniciar terapia de insuficiência cardíaca<br/>— Classe I, nível C. Quando reiniciar é decisão<br/>da equipe multidisciplinar — Classe I, nível C"])

  D3 -->|"Leve: FEVE de 50% ou mais, com queda relativa<br/>do GLS maior que 15% e/ou nova elevação<br/>de biomarcador"| P1["Continuar a antraciclina sem interrupção<br/>— Classe I, nível C —, com monitorização cardíaca<br/>a cada 1 ou 2 ciclos"]

  P1 --> D4{"Qual alteração definiu a CTRCD leve?"}

  D4 -->|"Queda significativa do strain<br/>longitudinal global"| C6(["IECA ou BRA e/ou betabloqueador<br/>devem ser considerados — Classe IIa, nível B"])

  D4 -->|"Elevação de troponina acima do<br/>limite superior de normalidade"| C7(["IECA ou BRA e/ou betabloqueador<br/>devem ser considerados — Classe IIa, nível B"])

  D4 -->|"Elevação de peptídeo natriurético acima<br/>do limite superior de normalidade"| C8(["IECA ou BRA e/ou betabloqueador<br/>podem ser considerados — Classe IIb, nível C"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Árvore de decisão: CTRCD durante terapia dirigida ao HER2

```mermaid
flowchart TD
  R1["Paciente em terapia dirigida ao HER2<br/>com nova disfunção cardíaca"] --> D5{"Há sintomas de<br/>insuficiência cardíaca?"}

  D5 -->|"Sim, sintomático"| D6{"Grau do quadro sintomático"}

  D6 -->|"Moderado ou grave"| C9(["Interromper temporariamente a terapia anti-HER2.<br/>Na CTRCD grave, com FEVE abaixo de 40%, tratar<br/>precocemente conforme a diretriz de insuficiência<br/>cardíaca da ESC de 2021"])

  D6 -->|"Leve"| D10{"Decisão multidisciplinar:<br/>continuar ou interromper<br/>temporariamente a terapia anti-HER2?"}
  D10 -->|"Continuar"| C10a(["Manter a terapia anti-HER2 com tratamento<br/>de insuficiência cardíaca e vigilância<br/>frequente por imagem e biomarcadores"])
  D10 -->|"Interromper"| D8

  D5 -->|"Não, assintomático"| D7{"Faixa da fração de ejeção"}

  D7 -->|"Grave: FEVE abaixo de 40%"| C11(["Interromper temporariamente a terapia anti-HER2<br/>e tratar precocemente conforme a diretriz<br/>de insuficiência cardíaca"])

  D7 -->|"Moderada: FEVE de 40 a 49%"| C12(["Continuar a terapia anti-HER2 e associar<br/>cardioproteção com IECA ou BRA e betabloqueador,<br/>com monitorização cardíaca frequente"])

  D7 -->|"Leve: FEVE de 50% ou mais, com queda<br/>significativa do GLS e/ou elevação<br/>de biomarcador cardíaco"| C13(["Continuar a terapia anti-HER2. Cardioproteção<br/>com IECA ou BRA e/ou betabloqueador<br/>deve ser considerada"])

  C9 --> D8{"Após a interrupção e o tratamento<br/>da IC, os sinais e sintomas resolveram?"}
  D8 -->|"Não — IC ainda sintomática"| C16(["Não reiniciar a terapia anti-HER2 enquanto<br/>persistirem sintomas de IC; tratar a IC e<br/>rediscutir a estratégia oncológica em<br/>equipe multidisciplinar"])
  D8 -->|"Sim — agora assintomático"| D9{"A FEVE recuperou<br/>para pelo menos 40%?"}
  C11 --> D9

  D9 -->|"Sim — idealmente FEVE<br/>recuperada para 50% ou mais"| C14(["Considerar reiniciar a terapia anti-HER2,<br/>mantendo o tratamento de IC. Fazer eco e<br/>biomarcadores a cada 2 ciclos nos primeiros<br/>4 ciclos; reduzir a frequência depois<br/>se função e biomarcadores permanecerem estáveis"])

  D9 -->|"Não — FEVE persiste abaixo de 40%"| D11{"Não existe alternativa oncológica eficaz<br/>e o câncer avançado responde de forma<br/>relevante à terapia anti-HER2?"}

  D11 -->|"Sim"| C15(["A retomada pode ser considerada somente<br/>após decisão multidisciplinar explícita,<br/>ponderando o benefício oncológico contra<br/>o risco cardíaco, com tratamento de IC<br/>e vigilância cardíaca estreita"])
  D11 -->|"Não"| C17(["Manter a terapia anti-HER2 interrompida<br/>e o tratamento de IC; rediscutir a<br/>estratégia oncológica e cardiovascular<br/>em equipe multidisciplinar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C9,C10a,C11,C12,C13,C14,C15,C16,C17 conduta;
```

**Sobre a segunda árvore:** as condutas da terapia anti-HER2 estão reproduzidas
com o verbo da própria diretriz — "é recomendado", "deve ser considerado" —, e
não com rótulo de classe. A fonte primária organiza essas decisões na Tabela de
Recomendação 25 e na Figura 26. Como as colunas gráficas de classe e nível não
foram transcritas neste documento, foram preservados os verbos oficiais em vez de
inferir uma graduação. A árvore inclui também o caminho de reinício após recuperação.
A exceção estreita por câncer avançado responsivo sem alternativa eficaz aplica-se
somente depois da resolução dos sintomas, se a FEVE persistir abaixo de 40%, e exige
decisão multidisciplinar. Sintomas de IC persistentes bloqueiam o reinício nesta árvore.

## Reiniciar antraciclina depois de uma CTRCD

Quando o paciente com CTRCD **moderada ou grave**, sintomática ou não, ainda
precisa de mais antraciclina, a diretriz oferece duas estratégias de redução de
risco, ambas **Classe IIb, nível C**:

- **antraciclina lipossomal**;
- **dexrazoxano** antes de cada ciclo seguinte.

O dexrazoxano tem aprovação formal restrita: adultos com câncer de mama avançado
ou metastático que já receberam dose cumulativa mínima de antraciclina — 300 mg/m²
de doxorrubicina ou equivalente pela agência norte-americana, 350 mg/m² pela
agência europeia. Os dois números existem, são de agências diferentes, e não é
erro de transcrição.

**Monitorização cardíaca a cada 1 ou 2 ciclos é recomendada** em duas situações:
no paciente que reinicia antraciclina após um episódio de CTRCD, e no que segue
com CTRCD leve mantendo a quimioterapia.

## O que as árvores não mostram

**A discussão em equipe multidisciplinar não é formalidade.** Ela aparece como
recomendação Classe I em quatro pontos diferentes da tabela — decidir sobre
interrupção na CTRCD leve sintomática, decidir quando reiniciar após CTRCD
moderada sintomática, e o mesmo para CTRCD moderada e grave assintomáticas.
Retirei da árvore o que valia para todos os ramos.

**Exercício aeróbico é recomendado** para o paciente com câncer que desenvolve
CTRCD. O benefício do exercício antes e durante a quimioterapia com antraciclina
está demonstrado.

**A estratificação de risco basal, antes do primeiro ciclo, é outra árvore** — e
já tem documento próprio nesta biblioteca, com os escores HFA-ICOS. Este
fluxograma começa depois: no paciente que já está em tratamento e cuja vigilância
detectou alteração.

**Sobreviventes de câncer têm recomendação separada.** Avaliação anual de risco
cardiovascular com ECG e peptídeo natriurético é Classe I, nível B em quem recebeu
fármaco potencialmente cardiotóxico ou radioterapia, e a reestratificação de risco
aos 5 anos de tratamento, Classe I, nível C. No sobrevivente que desenvolve CTRCD
moderada assintomática tardiamente, IECA ou BRA e/ou betabloqueador são
recomendados — Classe I, nível C; na CTRCD leve assintomática, podem ser
considerados — Classe IIb, nível C.

**Miocardite por inibidor de checkpoint imunológico não está aqui.** Tem
definição própria na mesma diretriz, com critérios diagnósticos maiores e menores
e diagnóstico histopatológico por biópsia endomiocárdica, e já é tratada em
documento separado desta biblioteca.
