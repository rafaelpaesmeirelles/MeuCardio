---
title: "Dor torácica e SCA por vasoespasmo coronariano induzido por cocaína"
slug: fluxograma-dor-toracica-e-sca-por-vasoespasmo-coronariano-induzido-por-cocaina
theme: "Geral"
kind: fluxograma
summary: "Conduta imediata na dor torácica associada ao uso recente de cocaína: benzodiazepínico como primeira linha, nitrato e bloqueador de canal de cálcio para o vasoespasmo, investigação de SCA em paralelo — e a regra que não pode falhar, nunca betabloqueador isolado no agudo."
review_status: revisado
source_refs: ["Lange RA, Cigarroa RG, Yancy CW Jr, et al. Cocaine-Induced Coronary-Artery Vasoconstriction. N Engl J Med. 1989;321(23):1557-1562. DOI: 10.1056/NEJM198912073212301. PMID: 2573838 — mecanismo, vasoconstricção coronariana mediada por alfa-adrenérgico, revertida por fentolamina", "Lange RA, Cigarroa RG, Flores ED, et al. Potentiation of Cocaine-Induced Coronary Vasoconstriction by Beta-Adrenergic Blockade. Ann Intern Med. 1990;112(12):897-903. DOI: 10.7326/0003-4819-112-12-897. PMID: 1971166 — ensaio randomizado, duplo-cego, controlado por placebo: propranolol intracoronariano piora o vasoespasmo já induzido pela cocaína", "Weber JE, Shofer FS, Larkin GL, Kalaria AS, Hollander JE. Validation of a Brief Observation Period for Patients with Cocaine-Associated Chest Pain. N Engl J Med. 2003;348(6):510-517. DOI: 10.1056/NEJMoa022206. PMID: 12571258 — coorte prospectiva, 302 pacientes, protocolo de observação de 9-12h com ECG e troponina seriados", "Richards JR, Garber D, Laurin EG, Albertson TE, Derlet RW, Amsterdam EA, Olson KR, Ramoska EA, Lange RA. Treatment of cocaine cardiovascular toxicity: a systematic review. Clin Toxicol (Phila). 2016;54(5):345-364. DOI: 10.3109/15563650.2016.1142090. PMID: 26919414 — revisão sistemática do manejo farmacológico agudo por classe de fármaco (benzodiazepínico, bloqueador de canal de cálcio, nitrato, betabloqueador puro vs. combinado)", "Anderson JL, Adams CD, Antman EM, et al. 2012 ACCF/AHA focused update incorporated into the ACCF/AHA 2007 guidelines for the management of patients with unstable angina/non-ST-elevation myocardial infarction. J Am Coll Cardiol. 2013;61(23):e179-e347. PMID: 23639841 — aprova labetalol para SCA associada a cocaína/metanfetamina", "Richards JR, Le JK. Cocaine Toxicity. In: StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; atualizado em 08/06/2023. PMID: 28613695. NCBI Bookshelf NBK430976 — fonte terciária usada só para a síntese prática de classes de fármaco, não para número", "McCord J, Jneid H, Hollander JE, et al. Management of cocaine-associated chest pain and myocardial infarction: a scientific statement from the American Heart Association Acute Cardiac Care Committee of the Council on Clinical Cardiology. Circulation. 2008;117(14):1897-1907. DOI: 10.1161/CIRCULATIONAHA.107.188950. PMID: 18347214 — declaração científica de referência da AHA sobre a conduta na dor torácica associada à cocaína; abstract indisponível no PubMed e texto integral não acessado nesta sessão (confirmado por WebFetch em 03/08/2026), citada aqui pela conduta de investigação/angiografia coronariana, verificada por fonte secundária abaixo", "Emergency Care BC. Cocaine-Associated Chest Pain – Diagnosis and Treatment. Clinical Summary, lido integralmente por WebFetch em 03/08/2026 — fonte secundária que sintetiza a declaração da AHA acima: bloqueador de canal de cálcio como adjuvante para sintomas isquêmicos persistentes apesar de nitroglicerina, angiografia coronariana com ICP preferida a fibrinolítico com consulta à cardiologia se supradesnível de ST e/ou sintomas isquêmicos persistirem apesar da terapia, e uso de betabloqueador no agudo descrito como controverso e atualmente não recomendado por efeito alfa-adrenérgico sem oposição"]
---

# Dor torácica e SCA por vasoespasmo coronariano induzido por cocaína

O uso recente de cocaína (intranasal, inalada ou intravenosa) causa vasoconstricção coronariana por estímulo alfa-adrenérgico não contraposto, com dor torácica e infarto possíveis mesmo sem placa aterosclerótica estabelecida. A conduta reflexa de síndrome coronariana — betabloqueador — **piora** esse espasmo em vez de tratá-lo, e é o ponto de maior risco de erro neste protocolo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Dor torácica em paciente com uso recente de cocaína<br/>(intranasal, inalada ou intravenosa),<br/>confirmado ou suspeito"]
  P1["ECG de 12 derivações e monitorização contínua,<br/>acesso venoso e troponina;<br/>benzodiazepínico IV como primeira linha<br/>para ansiedade, taquicardia e hipertensão"]
  D1{"ECG mostra supradesnível de ST ou alteração isquêmica,<br/>ou dor torácica/hipertensão/taquicardia persistem<br/>apesar do benzodiazepínico?"}
  C1(["Observação com ECG e troponina seriados;<br/>considerar alta em 9-12h se critério<br/>de baixo risco mantido"])
  P2["Associar nitrato e bloqueador de canal de cálcio<br/>não di-hidropiridínico ao benzodiazepínico<br/>para tratar o vasoespasmo coronariano"]
  D2{"Dor torácica ou alteração isquêmica persiste<br/>apesar de benzodiazepínico + nitrato +<br/>bloqueador de canal de cálcio?"}
  C5(["Suspeitar de trombose sobreposta ao vasoespasmo:<br/>manter investigação de SCA (ECG e troponina seriados)<br/>e encaminhar para angiografia coronariana"])
  D3{"Ainda é necessário controlar<br/>frequência cardíaca ou pressão arterial residual?"}
  C2(["Manter benzodiazepínico + nitrato +<br/>bloqueador de canal de cálcio;<br/>observação clínica"])
  D4{"Qual classe de betabloqueio considerar?"}
  C3(["CONTRAINDICADO: NUNCA betabloqueador isolado<br/>no agudo por cocaína — bloqueio beta sem oposição<br/>alfa piora o vasoespasmo coronariano e a hipertensão"])
  C4(["Labetalol pode ser usado com segurança<br/>para hipertensão e taquicardia residuais —<br/>exceção validada dentro da classe"])

  R0 --> P1
  P1 --> D1
  D1 -->|"Não"| C1
  D1 -->|"Sim, suspeita de vasoespasmo"| P2
  P2 --> D2
  D2 -->|"Sim, persiste"| C5
  D2 -->|"Não, vasoespasmo respondeu"| D3
  D3 -->|"Não"| C2
  D3 -->|"Sim"| D4
  D4 -->|"Betabloqueador puro (isolado)"| C3
  D4 -->|"Beta/alfa-bloqueador combinado (labetalol)"| C4

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Por que nunca betabloqueador isolado

Bloquear o receptor beta sem bloquear também o alfa deixa a vasoconstricção coronariana mediada por alfa **sem oposição**. No ensaio randomizado, duplo-cego, controlado por placebo de Lange et al. (Ann Intern Med. 1990), o propranolol intracoronariano administrado após a cocaína **piorou** o quadro medido objetivamente: o fluxo sanguíneo no seio coronariano, que já havia caído com a cocaína, caiu ainda mais após o betabloqueador, e a resistência vascular coronariana subiu ainda mais — mesmo sem alteração adicional da pressão arterial. A exceção é o beta/alfa-bloqueador combinado (labetalol, carvedilol): a revisão sistemática de Richards et al. (2016) não registrou evento adverso com essa combinação, e a atualização focada ACCF/AHA 2012 aprova especificamente o labetalol para SCA associada a cocaína ou metanfetamina.

## O que se repete em todo ramo, e por isso não está no diagrama

**Reavaliação seriada.** ECG e troponina são repetidos ao longo de toda a observação, em qualquer ramo da árvore — não é um passo único, é vigilância contínua enquanto o paciente permanece em risco.

**Orientação de cessação do uso de cocaína antes da alta**, em todo paciente liberado. Na coorte de validação do protocolo de observação de 9-12h (Weber et al., 2003), os únicos infartos não fatais em 30 dias ocorreram em pacientes que mantiveram o uso de cocaína após a alta — a orientação de cessação é parte do desfecho de segurança demonstrado, não um adendo genérico.

**Cuidado de suporte geral** (hidratação, controle de agitação/hipertermia associados à intoxicação, ambiente calmo) corre em paralelo em qualquer ponto da árvore e não muda a sequência de decisão farmacológica acima.

**Extrapolação indevida da janela de observação de 9-12h**: os números de segurança de Weber (risco de morte cardiovascular em 30 dias próximo de zero) valem para a população de risco baixo a intermediário validada no estudo — não para quem chega com alteração isquêmica franca ao ECG, troponina já alterada ou instabilidade hemodinâmica, que são critério de exclusão dessa coorte, não de inclusão.
