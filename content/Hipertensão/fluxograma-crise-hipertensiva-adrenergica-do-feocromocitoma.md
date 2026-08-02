---
title: "Crise hipertensiva adrenérgica do feocromocitoma"
slug: fluxograma-crise-hipertensiva-adrenergica-do-feocromocitoma
theme: "Hipertensão"
kind: fluxograma
summary: "Árvore de conduta imediata da crise hipertensiva adrenérgica do feocromocitoma: bloqueio alfa IV de resgate antes de qualquer betabloqueador, titulação até controle pressórico, e encaminhamento para ressecção cirúrgica definitiva somente após estabilização e preparo adequado."
review_status: revisado
source_refs: ["Lenders JW, Duh QY, Eisenhofer G, Gimenez-Roqueplo AP, Grebe SK, Murad MH, Naruse M, Pacak K, Young WF Jr; Endocrine Society. Pheochromocytoma and paraganglioma: an Endocrine Society clinical practice guideline. J Clin Endocrinol Metab. 2014;99(6):1915-1942. DOI: 10.1210/jc.2014-1498. PMID: 24893135 — recomendação de bloqueio pré-operatório universal e dieta hipersódica", "Buitenwerf E, Osinga TE, Timmers HJLM, Lenders JWM, Feelders RA, Eekhoff EMW, Haak HR, Corssmit EPM, Bisschop PHLT, Valk GD, Veldman RG, Dullaart RPF, Links TP, Voogd MF, Wietasch GJKG, Kerstens MN. Efficacy of α-Blockers on Hemodynamic Control during Pheochromocytoma Resection: A Randomized Controlled Trial (PRESCRIPT). J Clin Endocrinol Metab. 2020;105(7):2381-2391. DOI: 10.1210/clinem/dgz188. PMID: 31714582. PMCID: PMC7261201 — ClinicalTrials.gov NCT01379898, 134 pacientes", "van den Born BJM, Lip GYH, Brguljan-Hitij J, Cremer A, Segura J, Morales E, Mahfoud F, Amraoui F, Persu A, Kahan T, Agabiti Rosei E, de Simone G, Gosse P, Williams B. ESC Council on hypertension position document on the management of hypertensive emergencies. Eur Heart J Cardiovasc Pharmacother. 2019;5(1):37-46. DOI: 10.1093/ehjcvp/pvy032 — seção específica sobre crise hipertensiva por feocromocitoma: fentolamina, nitroprussiato, urapidil e nicardipina como opções de bloqueio agudo, e risco de agravamento da hipertensão com betabloqueador (labetalol) sem bloqueio alfa prévio"]
---

# Crise hipertensiva adrenérgica do feocromocitoma

O documento `feocromocitoma-preparo-pre-operatorio-com-bloqueio-alfa-o-ensaio-prescript.md`, nesta mesma pasta, trata do preparo pré-operatório **eletivo** — bloqueio alfa oral por 2 a 3 semanas antes de uma cirurgia programada. Este fluxograma cobre a situação diferente: o paciente **já está em crise**, com liberação maciça e súbita de catecolaminas — paroxismo de cefaleia, sudorese e taquicardia, com pressão arterial muito elevada — e a conduta precisa de bloqueio alfa **por via intravenosa e de ação rápida**, não pelo esquema de titulação oral de semanas.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Crise hipertensiva paroxística: cefaleia,<br/>sudorese e taquicardia, em paciente com<br/>feocromocitoma confirmado ou suspeito"] --> D1{"Paciente já recebeu ou está em uso de<br/>betabloqueador nesta crise, sem bloqueio<br/>alfa estabelecido antes?"}

  D1 -->|"Sim — erro em curso"| C1(["Suspender o betabloqueador agora.<br/>Betabloqueio sem alfa prévio pode precipitar<br/>crise hipertensiva PARADOXAL por vasoconstrição<br/>alfa sem oposição — é o erro mais perigoso<br/>deste protocolo. Iniciar bloqueio alfa IV de<br/>resgate (fentolamina ou nitroprussiato de sódio)<br/>e seguir a mesma titulação e a mesma lógica de<br/>betabloqueio tardio desta árvore"])

  D1 -->|"Não"| P1["Bloqueio alfa IV de ação rápida como<br/>primeira conduta: fentolamina em bolus<br/>repetido ou nitroprussiato de sódio em<br/>infusão contínua, titulado pela resposta<br/>pressórica, com monitorização hemodinâmica<br/>contínua. NUNCA betabloqueador isolado<br/>nesta fase"]

  P1 --> D2{"PA responde e fica controlada<br/>com o bloqueio alfa IV?"}

  D2 -->|"Não, crise persiste"| C2(["Otimizar/intensificar o bloqueio alfa IV<br/>(aumentar fentolamina ou nitroprussiato).<br/>NÃO acrescentar betabloqueador enquanto a<br/>PA não estiver controlada. Reavaliar via<br/>aérea, volemia e causas associadas"])

  D2 -->|"Sim, PA controlada"| D3{"Taquicardia persistente após o<br/>bloqueio alfa já estabelecido?"}

  D3 -->|"Sim"| C3(["Associar betabloqueador IV (ex.: esmolol)<br/>somente agora, com bloqueio alfa já em curso,<br/>para controlar a frequência. Após estabilização,<br/>encaminhar para preparo pré-operatório eletivo<br/>e ressecção cirúrgica definitiva — nunca operar<br/>na fase aguda da crise"])

  D3 -->|"Não"| C4(["Manter o bloqueio alfa isolado, sem<br/>necessidade de betabloqueador. Após<br/>estabilização, encaminhar para preparo<br/>pré-operatório eletivo e ressecção cirúrgica<br/>definitiva — nunca operar na fase aguda da crise"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4 conduta;
```

## Por que o ramo do betabloqueador isolado é o erro mais perigoso

Bloquear o receptor beta sem bloqueio alfa prévio deixa a vasoconstrição alfa-adrenérgica **sem oposição**: a queda da vasodilatação mediada por beta-2 some, o efeito cronotrópico negativo reduz o débito cardíaco compensatório, e a resistência vascular periférica sobe ainda mais — o resultado é agravamento paradoxal da crise hipertensiva, não controle dela. É por isso que a árvore trata esse cenário como um ramo próprio de correção de erro (nó `C1`), e não como uma variação menor do fluxo principal: se o betabloqueador já foi dado sem bloqueio alfa estabelecido, a primeira ação é suspendê-lo, não apenas "adicionar" o bloqueio alfa por cima.

## Doses de referência, e o que exige verificação institucional

- **Fentolamina IV**: bloqueador alfa não seletivo de ação curta (10 a 15 minutos), usado em bolus repetido conforme resposta pressórica. A faixa mais citada na literatura é de 1 a 5 mg por bolus, podendo ser repetida a cada poucos minutos. `VERIFICAÇÃO HUMANA NECESSÁRIA` para o protocolo exato de dose/intervalo do serviço, pela variação entre fontes.
- **Nitroprussiato de sódio IV**: infusão contínua, titulada minuto a minuto pela resposta pressórica, exige monitorização de PA idealmente invasiva pelo risco de hipotensão abrupta. `VERIFICAÇÃO HUMANA NECESSÁRIA` para a faixa de mcg/kg/min do protocolo do serviço.
- **Nicardipina e urapidil** aparecem como alternativas de bloqueio agudo na literatura de hipertensão, mas sem posologia detalhada nas fontes consultadas para este documento — `VERIFICAÇÃO HUMANA NECESSÁRIA` antes de usar como primeira escolha.
- **Betabloqueador (ex.: esmolol)**, quando indicado pela taquicardia persistente com bloqueio alfa já estabelecido: dose a confirmar no protocolo do serviço — `VERIFICAÇÃO HUMANA NECESSÁRIA`.

## O que se repete em todo ramo, e por isso não está na árvore

**Monitorização contínua** de pressão arterial (idealmente invasiva) e ECG, com acesso venoso calibroso, do primeiro minuto até a estabilização — vale para qualquer ramo do fluxograma.

**Reavaliação frequente**, a cada poucos minutos durante a titulação IV: tanto o bloqueio alfa quanto o eventual betabloqueador são ajustados pela resposta hemodinâmica, não por uma dose fixa única.

**Buscar fator desencadeante identificável** — manipulação ou palpação do tumor, alguns antieméticos (ex.: metoclopramida), contraste iodado, corticoide em dose alta — e afastá-lo quando possível, em paralelo ao tratamento farmacológico.

**A ressecção cirúrgica definitiva nunca é conduta da fase aguda.** Depois de estabilizada a crise, o caminho é o preparo pré-operatório eletivo descrito no documento `feocromocitoma-preparo-pre-operatorio-com-bloqueio-alfa-o-ensaio-prescript.md` — bloqueio alfa oral (fenoxibenzamina ou doxazosina) por 2 a 3 semanas, dieta hipersódica, expansão volêmica e, se necessário, betabloqueador oral somente depois do bloqueio alfa em curso — e não uma cirurgia de urgência guiada pela crise que acabou de ser controlada.
