---
title: "Fluxograma: Hipotensão ortostática — diagnóstico, causa e manejo escalonado"
slug: fluxograma-hipotensao-ortostatica-diagnostico-causa-e-manejo-escalonado
theme: "Síncope"
kind: fluxograma
summary: "Do teste de ortostatismo ativo à prescrição: como confirmar a hipotensão ortostática clássica, separar a forma medicamentosa, a hipovolêmica e a neurogênica pela resposta da frequência cardíaca, esgotar as medidas não farmacológicas e só então escolher entre midodrina, fludrocortisona e droxidopa sem agravar a hipertensão supina."
review_status: revisado
review_note: "Produção científica assistida (Claude) e revisão editorial e científica independente (Codex), concluídas em 26/08/2026. Fontes primárias, coerência clínica, lógica dos fluxos, metadados e links foram conferidos; correções incorporadas. Publicação sujeita à aprovação do responsável técnico."
source_refs:
  - "Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304. Texto integral lido em PDF: https://www.eusem.org/images/ESC_guideline_2018.pdf (seções 4.2.2.1, 5.3.1-5.3.10, Tabelas 3 e 8 e tabela Treatment of orthostatic hypotension)."
  - "Brignole M, Moya A, de Lange FJ, et al. Practical Instructions for the 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):e43-e80. DOI: 10.1093/eurheartj/ehy071. Texto integral lido em PDF: https://www.gimsi.it/wp-content/uploads/2018/07/ESC-guidelines-2018-Practical-Instructions.pdf (seção de síndromes de intolerância ortostática, Web Table 1)."
  - "Gibbons CH, Schmidt P, Biaggioni I, et al. The recommendations of a consensus panel for the screening, diagnosis, and treatment of neurogenic orthostatic hypotension and associated supine hypertension. J Neurol. 2017;264(8):1567-1582. DOI: 10.1007/s00415-016-8375-x. PMID: 28050656. PMCID: PMC5533816. Texto integral lido em https://pmc.ncbi.nlm.nih.gov/articles/PMC5533816/"
  - "Freeman R, Wieling W, Axelrod FB, et al. Consensus statement on the definition of orthostatic hypotension, neurally mediated syncope and the postural tachycardia syndrome. Clin Auton Res. 2011;21(2):69-72. DOI: 10.1007/s10286-011-0119-5. PMID: 21431947. Registro conferido via PubMed E-utilities; texto integral não acessado (Springer bloqueou o acesso)."
  - "Midodrine hydrochloride tablets, USP. Bula (DailyMed, NLM). https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=4f5e1689-9691-471b-a39c-26120d6ce073"
  - "Fludrocortisone acetate tablets, USP. Bula (DailyMed, NLM). https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=51363453-6d33-4aee-8426-37ac0bf3cc10"
  - "NORTHERA (droxidopa) capsules. Bula (DailyMed, NLM). https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2179f02c-48d7-48eb-8007-5ae43d8d16bc"
  - "Derivado de hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial.md, fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial.md, fluxograma-sincope-idoso-investigacao-diferenciada.md e sincope-diagnostico-e-manejo-esc-2018.md (Síncope), e de fluxograma-hipertensao-no-idoso-e-no-fragil-quando-iniciar-alvo-e-desintensificacao-esc-2024.md (Cardiologia geriátrica), já publicados no acervo."
---

# Fluxograma: Hipotensão ortostática — diagnóstico, causa e manejo escalonado

Os fluxogramas de síncope desta pasta tratam a hipotensão ortostática (HO) como um dos três grupos etiológicos e param na confirmação do nexo com a síncope. Este começa onde eles param: a HO como entidade, com ou sem síncope. A decisão importa porque a causa mais comum é medicamentosa e se resolve retirando um fármaco, porque a forma neurogênica muda a investigação (Parkinson, atrofia de múltiplos sistemas, diabetes, amiloidose) e porque os dois fármacos com recomendação — midodrina e fludrocortisona — sobem a pressão também deitado. A ESC 2018 organiza o tratamento em degraus: educação e volume para todos, retirada do agente causador, medidas físicas e, só se os sintomas persistirem, o fármaco. A árvore segue essa ordem.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Sintomas de intolerância ortostática, síncope ou queda<br/>teste de ortostatismo ativo: PA e FC deitado após 5 min<br/>e em pé ao 1 e 3 min"]
  D1{"Queda sustentada de PAS de 20 mmHg ou mais, PAD de 10 mmHg<br/>ou mais, ou PAS abaixo de 90 mmHg em até 3 min?"}
  P1["HO clássica documentada: confirmada se reproduz os sintomas<br/>espontâneos, provável se assintomática com história compatível"]
  D2{"Sintomas nos primeiros segundos após levantar<br/>ou só depois de 3 min em pé?"}
  C1(["Suspeitar HO inicial ou tardia: medida contínua batimento<br/>a batimento ou teste prolongado além de 3 min, MAPA se dúvida"])
  C2(["HO não demonstrada: seguir o diferencial da síncope reflexa<br/>versus cardíaca, considerar POTS se FC sobe mais de 30 bpm<br/>sem queda pressórica"])
  D3{"Fármaco vasoativo ou hipotensor em uso? anti-hipertensivo,<br/>diurético, nitrato, alfabloqueador, antidepressivo,<br/>antipsicótico, dopaminérgico"}
  C3(["HO medicamentosa: retirar ou reduzir o agente, trocar por IECA,<br/>BRA ou bloqueador de cálcio se a hipertensão exigir tratamento,<br/>repetir o teste após o ajuste"])
  D4{"Depleção de volume ou causa aguda? hemorragia,<br/>diarreia, vômito, baixa ingestão, febre"}
  C4(["Repor volume e tratar a causa, repetir o teste<br/>de ortostatismo após a correção"])
  D5{"FC sobe menos de 15 bpm em pé apesar da queda pressórica,<br/>sem cronotrópico negativo em uso?"}
  P2["HO neurogênica provável: investigar falência autonômica<br/>primária ou secundária, iniciar medidas não farmacológicas"]
  P3["HO não neurogênica: descondicionamento, hipovolemia crônica,<br/>pós-prandial, anemia, iniciar medidas não farmacológicas"]
  D6{"Sintomas persistem apesar das<br/>medidas não farmacológicas?"}
  C5(["Manter medidas, revisar fármacos a cada consulta,<br/>MAPA para hipertensão noturna na falência autonômica"])
  D7{"Hipertensão supina, sistólica deitado de 150 mmHg ou mais<br/>ou diastólica de 90 mmHg ou mais, ou insuficiência cardíaca?"}
  C6(["Midodrina 2,5 a 10 mg três vezes ao dia ou fludrocortisona<br/>0,1 a 0,3 mg ao dia, monitorar PA supina, potássio e edema,<br/>droxidopa como alternativa na forma neurogênica"])
  C7(["Evitar fludrocortisona nos dois casos; na hipertensão supina,<br/>tratá-la antes: cabeceira elevada, midodrina só diurna, com cautela<br/>e última dose 4 h antes de deitar, anti-hipertensivo de curta ação<br/>ao deitar se sistólica supina acima de 180 ou diastólica acima<br/>de 110 mmHg; na insuficiência cardíaca ou cardiopatia grave,<br/>midodrina contraindicada ou só com cautela, droxidopa idem"])
  D8{"Sintomas persistem apesar das<br/>medidas não farmacológicas?"}
  C8(["Manter medidas, reavaliar volemia<br/>e fármacos periodicamente"])
  C9(["Reinvestigar a causa, tratar anemia e hipotensão pós-prandial,<br/>considerar fludrocortisona 0,1 a 0,3 mg ao dia ou midodrina<br/>se não houver hipertensão nem insuficiência cardíaca"])

  R0 --> D1
  D1 -->|"Sim"| P1
  D1 -->|"Não"| D2
  D2 -->|"Sim"| C1
  D2 -->|"Não"| C2
  P1 --> D3
  D3 -->|"Sim"| C3
  D3 -->|"Não"| D4
  D4 -->|"Sim"| C4
  D4 -->|"Não"| D5
  D5 -->|"Sim"| P2
  D5 -->|"Não"| P3
  P2 --> D6
  D6 -->|"Não"| C5
  D6 -->|"Sim"| D7
  D7 -->|"Não"| C6
  D7 -->|"Sim"| C7
  P3 --> D8
  D8 -->|"Não"| C8
  D8 -->|"Sim"| C9

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8,C9 conduta;
```

## O teste e os três subtipos

A ESC 2018 indica a medida intermitente de PA e FC com esfigmomanômetro, deitado e durante 3 minutos em pé, na avaliação inicial de toda síncope (Classe I, nível C). O consenso de Gibbons 2017 detalha o protocolo: pelo menos 5 minutos deitado, medida imediatamente antes de levantar e ao 1 e 3 minutos em pé (a medida sentado-em pé é aceita como alternativa quando a supina é impraticável). O critério pressórico é o da diretriz — queda progressiva e sustentada de 20 mmHg ou mais na sistólica, 10 mmHg ou mais na diastólica, ou sistólica abaixo de 90 mmHg —, e a diretriz explica que o corte absoluto de 90 mmHg foi acrescentado ao consenso de Freeman 2011 por ser útil sobretudo em quem tem sistólica deitado abaixo de 110 mmHg. Queda isolada da diastólica é rara e de relevância limitada.

| Subtipo | Critério | Como documentar |
|---|---|---|
| HO inicial | Queda acima de 40 mmHg na sistólica e/ou 20 mmHg na diastólica nos primeiros 15 s, com recuperação espontânea em menos de 40 s | Só com medida contínua batimento a batimento — o esfigmomanômetro não passa de quatro medidas por minuto |
| HO clássica | Critério pressórico acima, em até 3 min em pé ou em tilt | Esfigmomanômetro é adequado |
| HO tardia | Mesmo critério pressórico, mas só depois de 3 min | Prolongar o teste ou usar tilt; a ausência de bradicardia distingue da síncope reflexa |

A Tabela 8 da diretriz gradua o nexo com a síncope: queda sintomática que reproduz os sintomas confirma (Classe I); queda assintomática com história muito sugestiva, ou queda sintomática com história incompleta, torna provável (Classe IIa); queda assintomática com história pouco sugestiva torna possível (Classe IIb); sem queda anormal, o nexo fica não provado. A história muito sugestiva inclui sintomas em pé que somem deitado, predileção pela manhã e piora após exercício, refeição ou calor, sem ativação autonômica. O ramo sem queda documentada devolve o paciente ao diferencial geral (ver fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial); a POTS, com aumento de FC acima de 30 bpm sem HO, está em hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial.

## Causa: fármaco, volume ou falência autonômica

A Tabela 3 da ESC 2018 chama a HO medicamentosa de causa mais comum e cita vasodilatadores, diuréticos, fenotiazinas e antidepressivos; o texto da seção 5.3.3 acrescenta nitratos, neurolépticos e dopaminérgicos, e observa que três ou mais anti-hipertensivos, ou o alvo abaixo de 140/90 mmHg, predizem HO. IECA, BRA e bloqueadores de cálcio se associam menos à HO que betabloqueadores e tiazídicos, e a diretriz recomenda usá-los preferencialmente em quem tem risco de queda. A tabela de Gibbons 2017 amplia a lista: dopaminérgicos, tricíclicos, anticolinérgicos, inibidores da fosfodiesterase 5, alfabloqueadores, agonistas alfa-2 centrais, bloqueadores de cálcio, betabloqueadores, IECA e BRA. A regra da diretriz para a forma induzida por fármaco é eliminar o agente; e a metanálise que mostra que o achado assintomático em si não justifica desescalonar o anti-hipertensivo está em hipotensao-ortostatica-nao-e-motivo-para-desescalonar-o-anti-hipertensivo — o ramo C3 vale para HO sintomática documentada.

A resposta cronotrópica separa a forma neurogênica: a ESC 2018 descreve aumento de FC embotado ou ausente, em geral não acima de 10 bpm, na HO neurogênica, e aumento exagerado na anemia e na hipovolemia. Gibbons 2017 usa o corte de 15 bpm em 3 minutos — aumento menor sugere HO neurogênica, maior sugere forma não neurogênica —, com a ressalva de que o critério só vale com queda pressórica presente e sem fármaco que embote a FC nem marca-passo ou arritmia que impeça a resposta cronotrópica. A árvore usa o corte de Gibbons por ser o operacional. As causas neurogênicas da Tabela 3 são a falência autonômica primária (falência autonômica pura, atrofia de múltiplos sistemas, doença de Parkinson, demência com corpos de Lewy) e a secundária (diabetes, amiloidose, lesão medular, neuropatias autonômicas autoimune e paraneoplásica, insuficiência renal). Na suspeita de HO neurogênica, a manobra de Valsalva e o teste de respiração profunda são Classe IIa, nível B, e a MAPA é Classe I, nível B para detectar hipertensão noturna na falência autonômica (ver sincope-diagnostico-e-manejo-esc-2018).

## Manejo não farmacológico para todos

| Medida | ESC 2018 | Números (Gibbons 2017, salvo indicação) |
|---|---|---|
| Educação, evitar gatilhos e situações | Classe I, nível C | Evitar refeições grandes ricas em carboidrato, álcool e calor ambiente; ganho pressórico pequeno, 10 a 15 mmHg, mas funcionalmente relevante (ESC) |
| Hidratação e sal | Classe I, nível C | 2 a 3 L de líquido e 10 g de cloreto de sódio ao dia, apenas na ausência de hipertensão, insuficiência cardíaca ou doença renal que contraindique expansão; bolo de 500 mL de água pode ser usado em situações selecionadas |
| Modificar ou retirar hipotensores | Classe IIa, nível B | Ver seção anterior |
| Manobras de contrapressão isométrica | Classe IIa, nível C | Cruzar as pernas e agachar em quem tem pródromo e consegue executar (ESC) |
| Cinta abdominal e/ou meias compressivas | Classe IIa, nível B | Compressão de 30 a 40 mmHg; cinta abdominal inflável a 40 mmHg foi tão eficaz quanto midodrina |
| Cabeceira elevada ao dormir | Classe IIa, nível C | Mais de 10 graus (ESC); 15 a 23 cm acima dos pés (Gibbons); reduz poliúria noturna e a hipertensão noturna |

A ESC 2018 acrescenta, em "conselhos adicionais", que em HO estabelecida com risco de queda o tratamento anti-hipertensivo agressivo deve ser evitado, com alvo sistólico revisto para 140 a 150 mmHg e retirada de medicação considerada. O recorte geriátrico dessa desintensificação está em fluxograma-hipertensao-no-idoso-e-no-fragil-quando-iniciar-alvo-e-desintensificacao-esc-2024.

## Fármacos: só se os sintomas persistirem

| Fármaco | ESC 2018 | Dose e limites |
|---|---|---|
| Midodrina | Classe IIa, nível B, se os sintomas persistem; 2,5 a 10 mg três vezes ao dia, eficaz em três ensaios randomizados contra placebo | Bula: 10 mg três vezes ao dia, com intervalo de cerca de 4 h, última dose até 18 h e pelo menos 4 h antes de deitar; tarja de hipertensão supina; contraindicada em cardiopatia grave, doença renal aguda, retenção urinária, feocromocitoma, tireotoxicose e hipertensão supina persistente e excessiva. Gibbons: 2,5 a 15 mg, uma a três vezes ao dia, não nas 5 h antes de dormir |
| Fludrocortisona | Classe IIa, nível C, se os sintomas persistem; 0,1 a 0,3 mg uma vez ao dia, evidência de dois estudos observacionais e um ensaio duplo-cego com 60 pacientes | Gibbons: 0,1 a 0,2 mg ao dia, início de efeito em 3 a 7 dias. Bula: HO não é indicação aprovada; alerta para hipertensão, edema, cardiomegalia, insuficiência cardíaca e hipocalemia, com eletrólitos periódicos |
| Droxidopa | Sem classe; quatro ensaios curtos com 485 pacientes mostraram ganho modesto na sistólica em pé e em sintomas às 2 semanas, perdido às 8 semanas | Bula Northera: HO neurogênica sintomática por Parkinson, atrofia de múltiplos sistemas, falência autonômica pura, deficiência de dopamina beta-hidroxilase ou neuropatia autonômica não diabética; 100 mg três vezes ao dia, subir 100 mg por dose a cada 24 a 48 h, máximo 600 mg três vezes ao dia, última dose 3 h antes de deitar; eficácia além de 2 semanas não estabelecida |

Os efeitos adversos da midodrina na bula, no ensaio de 3 semanas, foram parestesia do couro cabeludo em 18,3%, piloereção em 13,4% e hipertensão supina em 7,3%, além de sintomas urinários. Gibbons 2017 orienta titular um agente até a dose máxima tolerada antes de associar o segundo e cita piridostigmina 30 a 60 mg, uma a três vezes ao dia, como opção menos estabelecida; a ESC lista desmopressina na poliúria noturna, octreotida na hipotensão pós-prandial e eritropoetina na anemia como terapias adicionais de eficácia menos comprovada. Na síncope vasovagal, os mesmos dois fármacos têm classe mais fraca (IIb) — ver tratamento-da-sincope-vasovagal-recorrente-medidas-nao-farmacologicas-e-farmacos.

## Hipertensão supina concomitante

Gibbons 2017 define hipertensão supina como sistólica de 150 mmHg ou mais ou diastólica de 90 mmHg ou mais deitado, e gradua a resposta: até 160 mmHg, observar sem tratar se os sintomas de HO melhoram; 160 a 180 mmHg, intervenção individualizada; acima de 180 mmHg ou diastólica acima de 110 mmHg, anti-hipertensivo de curta ação ao deitar. A cabeceira elevada é a primeira medida, e as bulas de midodrina e droxidopa exigem reduzir ou suspender o fármaco se a hipertensão supina não for controlada com ela. A ESC 2018 acrescenta que a MAPA identifica hipertensão supina ou noturna em pacientes tratados, e a hipotensão pós-prandial, que se soma à HO no idoso, tem manejo próprio em hipotensao-pos-prandial-no-idoso-cardiopata-mecanismo-prevalencia-e-manejo.

## Limitações e o que confirmar

- Freeman 2011 não foi lido na íntegra (acesso Springer bloqueado); as definições de HO inicial e tardia foram tomadas das Practical Instructions da ESC 2018, que o citam como fonte.
- A meta de sal reproduz a ESC 2018 em gramas de cloreto de sódio; não se deve convertê-la para “gramas de sódio” sem cálculo explícito.
- O corte de FC da árvore (15 bpm) é o de Gibbons 2017; a ESC 2018 descreve "em geral não acima de 10 bpm". Nenhum dos dois é validado como critério diagnóstico isolado.
- A árvore não fixa o tempo de espera antes de chamar os sintomas de refratários às medidas não farmacológicas; nenhuma das fontes lidas estabelece esse intervalo.
- As doses de midodrina e fludrocortisona são as da ESC 2018 e das bulas americanas; a fludrocortisona não tem HO como indicação em bula, e a droxidopa não tem registro no Brasil conferido nesta sessão.
- A conduta em hipertensão supina (limiares de 160 e 180 mmHg) é opinião de consenso, não recomendação de diretriz com classe.

## Tudo com Tudo

- [Hipotensão Ortostática e Síndrome de Taquicardia Postural (POTS): Diagnóstico Diferencial na Síncope](/biblioteca/hipotensao-ortostatica-e-sindrome-de-taquicardia-postural-pots-diagnostico-diferencial)
- [Fluxograma: Síncope reflexa versus cardíaca versus hipotensão ortostática — diagnóstico diferencial (ESC 2018)](/biblioteca/fluxograma-sincope-reflexa-versus-cardiaca-diagnostico-diferencial)
- [Fluxograma: Síncope e queda no idoso — investigação diferenciada de causas ortostáticas, reflexas e cardíacas](/biblioteca/fluxograma-sincope-idoso-investigacao-diferenciada)
- [Fluxograma: Hipertensão no idoso e no frágil — quando iniciar, alvo e desintensificação (ESC 2024)](/biblioteca/fluxograma-hipertensao-no-idoso-e-no-fragil-quando-iniciar-alvo-e-desintensificacao-esc-2024)
- [Hipotensão Ortostática Não é Motivo para Desescalonar o Anti-Hipertensivo](/biblioteca/hipotensao-ortostatica-nao-e-motivo-para-desescalonar-o-anti-hipertensivo)
- [Tratamento da Síncope Vasovagal Recorrente: Medidas Não Farmacológicas e Fármacos](/biblioteca/tratamento-da-sincope-vasovagal-recorrente-medidas-nao-farmacologicas-e-farmacos)
- [Hipotensão Pós-Prandial no Idoso Cardiopata: Mecanismo, Prevalência e Manejo](/biblioteca/hipotensao-pos-prandial-no-idoso-cardiopata-mecanismo-prevalencia-e-manejo)
