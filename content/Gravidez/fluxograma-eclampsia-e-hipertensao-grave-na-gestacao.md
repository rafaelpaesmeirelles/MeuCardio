---
title: "Eclâmpsia e hipertensão grave na gestação"
slug: fluxograma-eclampsia-e-hipertensao-grave-na-gestacao
theme: "Gravidez"
kind: fluxograma
summary: "Conduta imediata na gestante com PA ≥ 160/110 mmHg ou convulsão: a primeira bifurcação é convulsão presente (eclâmpsia) versus ausente (pré-eclâmpsia grave), o sulfato de magnésio como conduta central nas duas — tratamento na eclâmpsia, profilaxia na pré-eclâmpsia grave — e a escolha do anti-hipertensivo agudo conforme acesso venoso disponível."
review_status: revisado
source_refs: ["Altman D, Carroli G, Duley L, Farrell B, Moodley J, et al; Magpie Trial Collaboration Group. Do women with pre-eclampsia, and their babies, benefit from magnesium sulphate? The Magpie Trial: a randomised placebo-controlled trial. Lancet. 2002;359(9321):1877-1890. PMID: 12057549 — 10.141 mulheres randomizadas em 33 países", "Easterling T, Mundle S, Bracken H, Parvekar S, Mool S, et al. Oral antihypertensive regimens (nifedipine retard, labetalol, and methyldopa) for management of severe hypertension in pregnancy: an open-label, randomised controlled trial. Lancet. 2019;394(10203):1011-1021. PMID: 31378394 — NCT01912677 e CTRI/2013/08/003866, 894 randomizadas em dois hospitais públicos de Nagpur, Índia. Financiamento: PREEMPT, com aporte da Bill & Melinda Gates Foundation", "Preeclampsia and Eclampsia · Merck Manual Professional Edition · https://www.merckmanuals.com/professional/gynecology-and-obstetrics/antenatal-complications/preeclampsia-and-eclampsia — dose de sulfato de magnésio (ataque 4,5 g IV/20min + manutenção 1,5 g/hora) e critérios ACOG de pré-eclâmpsia grave, conforme já reaproveitado em pre-eclampsia-grave-hellp-e-arritmias-supraventriculares-na-gestacao.md nesta mesma pasta", "Emergency Treatment for Severe Hypertension in Pregnancy (resumo do ACOG Committee Opinion sobre terapia emergencial na hipertensão grave aguda na gestação) · The ObG Project · https://www.obgproject.com/2017/04/16/acog-guidance-emergency-treatment-severe-hypertension/ — consultado em 03/08/2026, doses de hidralazina e labetalol intravenosos e nifedipino oral de liberação imediata"]
---

# Eclâmpsia e hipertensão grave na gestação

Diante de PA ≥ 160/110 mmHg confirmada ou de convulsão na gestante ou puérpera, a
primeira pergunta que separa as condutas é se a convulsão já aconteceu. O sulfato
de magnésio é a conduta central nos dois ramos — tratamento na eclâmpsia
estabelecida, profilaxia na pré-eclâmpsia grave sem convulsão — e depois, nos
dois ramos, a hipertensão grave em si precisa de anti-hipertensivo agudo, cuja
via (venosa ou oral) decide qual fármaco entra primeiro.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Gestante ou puérpera com PA ≥ 160/110 mmHg<br/>confirmada, e/ou convulsão"] --> D1{"Convulsão presente?"}

  D1 -->|"Sim — eclâmpsia"| P1["Sulfato de magnésio IV: ataque de 4,5 g<br/>em 20 min + manutenção de 1,5 g/hora<br/>(Magpie: reduz risco de nova convulsão em 58%)"]

  D1 -->|"Não — hipertensão grave sem convulsão<br/>(pré-eclâmpsia grave)"| P2["Sulfato de magnésio IV profilático:<br/>mesmo esquema de ataque + manutenção<br/>(Magpie: eclâmpsia 0,8% vs. 1,9% com placebo,<br/>11 casos a menos por 1.000 tratadas)"]

  P1 --> D2{"Acesso venoso disponível<br/>para o anti-hipertensivo?"}

  D2 -->|"Sim"| C1(["Anti-hipertensivo IV: hidralazina<br/>ou labetalol, doses tituladas até<br/>controle (detalhes abaixo do diagrama)"])
  D2 -->|"Não"| C2(["Anti-hipertensivo oral (Easterling 2019):<br/>nifedipino, labetalol ou metildopa<br/>(detalhes abaixo do diagrama)"])

  P2 --> D3{"Acesso venoso disponível<br/>para o anti-hipertensivo?"}

  D3 -->|"Sim"| C3(["Anti-hipertensivo IV: hidralazina<br/>ou labetalol, doses tituladas até<br/>controle (detalhes abaixo do diagrama)"])
  D3 -->|"Não"| C4(["Anti-hipertensivo oral (Easterling 2019):<br/>nifedipino, labetalol ou metildopa<br/>(detalhes abaixo do diagrama)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Sulfato de magnésio: dose e duração

**Ataque de 4,5 g IV em 20 minutos, seguido de manutenção em infusão contínua de
1,5 g/hora** — o mesmo esquema serve para tratar a eclâmpsia já instalada e para
a profilaxia na pré-eclâmpsia grave. Na profilaxia, **manter por 12 a 24 horas
após o parto**. A dose é ajustada quando há insuficiência renal.

**Um em cada quatro tem efeito colateral** com o sulfato (24% vs. 5% com placebo
no Magpie) — é a contrapartida do benefício de 58% de redução relativa (11
mulheres a menos com eclâmpsia por 1.000 tratadas, número absoluto pequeno porque
a eclâmpsia é rara).

## Anti-hipertensivo agudo: doses por via

**Se há acesso venoso:**
- **Hidralazina IV**: 5 a 10 mg, repetir a cada 20 a 40 minutos se necessário
- **Labetalol IV**: 10 a 20 mg iniciais, escalonando 20 a 80 mg a cada 10 a 30
  minutos, até dose total máxima de 300 mg

**Se não há acesso venoso** — via oral, conforme o ensaio de Easterling (2019),
que testou justamente esse cenário em serviço público de poucos recursos:
- **Nifedipino de liberação imediata 10 mg VO**, com escalonamento horário —
  desfecho de controle pressórico em 6h em 84% (a maior frequência entre os três,
  como droga isolada)
- **Labetalol 200 mg VO**, com escalonamento horário — 77%
- **Metildopa 1.000 mg VO em dose única, sem escalonamento** — 76%

A ressalva do próprio ensaio vale aqui: nifedipino e labetalol tinham
escalonamento horário e a metildopa não, então a comparação é entre regimes, não
entre fármacos em condições iguais — mas **os três são opções orais viáveis
quando não há via endovenosa disponível de imediato**, e adiar o tratamento por
falta de acesso venoso não é justificado pelo achado do ensaio.

## O que não está nesta árvore

**Antecipação do parto versus conduta expectante** na hipertensão grave é decisão
obstétrica que depende de idade gestacional, condição fetal e resposta ao
tratamento — o documento-fonte não detalha os critérios dessa decisão, e por
isso ela não entra como ramo aqui.

**Reavaliação periódica da pressão e do quadro neurológico** se repete em todos
os ramos e por isso também não é ramo: a pressão é reavaliada a cada dose de
anti-hipertensivo, e o quadro neurológico (reflexos, cefaleia, distúrbio visual)
é reavaliado enquanto o sulfato de magnésio estiver em infusão.
