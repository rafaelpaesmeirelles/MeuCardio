---
title: "Crise hipertensiva adrenérgica do feocromocitoma"
slug: fluxograma-crise-hipertensiva-adrenergica-do-feocromocitoma
theme: "Hipertensão"
kind: fluxograma
summary: "Árvore de conduta imediata da emergência hipertensiva por feocromocitoma/paraganglioma: monitorização intensiva, bloqueio alfa ou vasodilatador IV titulável, nunca betabloqueio antes de alfa-bloqueio e cirurgia preferencialmente após estabilização."
review_status: revisado
source_refs: ["Lenders JW, Duh QY, Eisenhofer G, et al.; Endocrine Society. Pheochromocytoma and paraganglioma: an Endocrine Society clinical practice guideline. J Clin Endocrinol Metab. 2014;99(6):1915-1942. DOI: 10.1210/jc.2014-1498. PMID: 24893135 — diretriz de diagnóstico, bloqueio pré-operatório e tratamento definitivo; não é protocolo específico de crise", "van den Born BJM, Lip GYH, Brguljan-Hitij J, et al. ESC Council on hypertension position document on the management of hypertensive emergencies. Eur Heart J Cardiovasc Pharmacother. 2019;5(1):37-46. DOI: 10.1093/ehjcvp/pvy032. PMID: 30165588 — consenso oficial: fentolamina, nitroprussiato e urapidil foram usados no manejo perioperatório; nicardipina é alternativa; labetalol já acelerou hipertensão em relatos", "Corrigendum to: ESC Council on hypertension position document on the management of hypertensive emergencies. Eur Heart J Cardiovasc Pharmacother. 2019;5(1):46. DOI: 10.1093/ehjcvp/pvy040. PMID: 30339228 — registra múltiplos erros de dose na Tabela 4, posteriormente corrigidos; por segurança, este fluxo não reproduz posologia IV", "Whitelaw BC, Prague JK, Mustafa OG, et al. Phaeochromocytoma crisis. Clin Endocrinol (Oxf). 2014;80(1):13-22. DOI: 10.1111/cen.12324. PMID: 24102156 — atualização de prática baseada em casos: evidência fraca, alfa-bloqueio associado a sobrevivência, suporte circulatório no choque e cirurgia diferida até estabilização quando possível", "Scholten A, Cisco RM, Vriens MR, et al. Pheochromocytoma crisis is not a surgical emergency. J Clin Endocrinol Metab. 2013;98(2):581-591. DOI: 10.1210/jc.2012-3020. PMID: 23284003 — revisão de 97 casos: cirurgia de emergência teve mais complicações e maior mortalidade que cirurgia urgente/eletiva após estabilização"]
review_note: "Revisão de 26/08/2026: removidos quatro marcadores de verificação humana e as doses não suficientemente sustentadas. Corrigido erro farmacológico do texto anterior, que agrupava nitroprussiato como bloqueador alfa; ele é vasodilatador titulável, enquanto fentolamina é o alfa-bloqueador. A árvore foi limitada à emergência hipertensiva com lesão aguda de órgão-alvo, incluiu a possibilidade de transição para choque e substituiu a frase absoluta de que a cirurgia nunca ocorre na fase aguda por preferência por estabilização, preservando exceções de deterioração, ruptura ou sangramento. A fonte ESC tem corrigendum por erros de dose, portanto a posologia deve vir do protocolo institucional/farmácia clínica e não deste documento."
---

# Crise hipertensiva adrenérgica do feocromocitoma

Este fluxo começa quando a pressão muito elevada está acompanhada de **lesão
aguda de órgão-alvo** ou deterioração clínica atribuível ao excesso de
catecolaminas em feocromocitoma/paraganglioma (PPGL) confirmado ou fortemente
suspeito. Paroxismo de cefaleia, sudorese e palpitações aumenta a suspeita, mas
não basta para definir emergência hipertensiva.

O preparo pré-operatório eletivo é outra pergunta e está descrito no documento
específico do acervo. Na crise, a prioridade é estabilização em UTI/centro com
experiência, porque hipertensão grave pode alternar rapidamente com hipotensão,
edema pulmonar, arritmia, cardiomiopatia e choque.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Emergência hipertensiva com excesso<br/>catecolaminérgico por PPGL confirmado<br/>ou fortemente suspeito"]
  P0["UTI/centro experiente; PA contínua,<br/>ECG, acessos venosos e avaliação imediata<br/>de lesão de órgão-alvo e volemia"]
  D1{"Recebeu betabloqueador nesta crise<br/>antes de alfa-bloqueio adequado?"}
  C1["Interromper novas doses de beta-bloqueador;<br/>acionar endocrinologia, cardiologia e UTI;<br/>iniciar controle vascular titulável"]
  P1["Escolher conforme fenótipo e disponibilidade:<br/>fentolamina IV (alfa-bloqueio) OU vasodilatador<br/>IV titulável, como nitroprussiato;<br/>urapidil/nicardipina são alternativas descritas"]
  D2{"Pressão e lesão de órgão-alvo<br/>respondem sem surgir hipotensão?"}
  C2["Persistência hipertensiva: titular o agente,<br/>considerar combinação em centro experiente<br/>e reavaliar volemia, gatilho e complicações"]
  D3{"Após alfa-bloqueio adequado e reposição<br/>volêmica, persiste taquiarritmia relevante?"}
  C3["Considerar beta-bloqueador de ação curta<br/>(por exemplo, esmolol) somente agora,<br/>com monitorização intensiva"]
  C4["Não acrescentar beta-bloqueador;<br/>manter vigilância e transição para<br/>preparo definitivo após estabilização"]
  S1["Se surgir hipotensão/choque:<br/>suspender a lógica de redução pressórica,<br/>tratar falência orgânica e considerar<br/>suporte circulatório mecânico em centro expert"]
  F1["Após estabilização: alfa-bloqueio e preparo<br/>multidisciplinar para ressecção; cirurgia imediata<br/>fica reservada a deterioração apesar do suporte,<br/>ruptura/sangramento ou outra indicação excepcional"]

  R0 --> P0 --> D1
  D1 -->|"Sim"| C1 --> P1
  D1 -->|"Não"| P1
  P1 --> D2
  D2 -->|"Não, hipertensão persiste"| C2 --> D2
  D2 -->|"Surge hipotensão/choque"| S1 --> F1
  D2 -->|"Sim"| D3
  D3 -->|"Sim"| C3 --> F1
  D3 -->|"Não"| C4 --> F1

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,S1,F1 conduta;
```

## O que a fonte sustenta — e o que ela não sustenta

O posicionamento do Conselho de Hipertensão da ESC descreve **fentolamina**,
**nitroprussiato** e **urapidil** como fármacos usados no manejo do
feocromocitoma e considera **nicardipina** uma alternativa. Esses agentes não
são equivalentes: fentolamina é alfa-bloqueador competitivo; nitroprussiato,
urapidil e nicardipina reduzem pressão por outros mecanismos. A escolha e a
combinação dependem de pressão, volemia, função ventricular, lesão de órgão-alvo
e disponibilidade local.

O mesmo documento registra aceleração paradoxal da hipertensão com
**labetalol** em casos de feocromocitoma. A atualização de Whitelaw et al.
explica a sequência: beta-bloqueio remove a vasodilatação beta-2 e deixa a
vasoconstrição alfa sem oposição. Se houver taquiarritmia relevante, um agente
curto como esmolol só entra **depois** de alfa-bloqueio e ressuscitação volêmica
adequados.

## Por que este fluxo não contém doses

O artigo da ESC recebeu corrigendum por múltiplos erros de posologia em sua
Tabela 4. Além disso, a evidência específica de crise por PPGL é composta
principalmente por séries e relatos, e a disponibilidade das formulações varia.
Por segurança, este documento oferece a **sequência decisória**, mas não
substitui prescrição do protocolo institucional, farmácia clínica e equipe
intensiva. Dose, concentração, velocidade de titulação, contraindicações e
monitorização devem ser conferidas no ponto de cuidado.

## Cirurgia: estabilizar primeiro, sem transformar isso em absoluto

Na revisão de 97 casos de Scholten et al., cirurgia de emergência se associou a
mais complicações intraoperatórias (80% versus 42%), pós-operatórias (71% versus
33%) e maior mortalidade (18% versus 0%) que cirurgia urgente/eletiva após
estabilização. Por isso, a regra é estabilizar e estabelecer bloqueio adequado
antes da ressecção. Ainda assim, deterioração progressiva apesar de suporte,
ruptura tumoral ou sangramento podem exigir decisão cirúrgica excepcional e
multidisciplinar; “nunca operar na crise” seria uma simplificação perigosa.

## Tudo com Tudo

- [Feocromocitoma: preparo pré-operatório e ensaio PRESCRIPT](feocromocitoma-preparo-pre-operatorio-com-bloqueio-alfa-o-ensaio-prescript.md)
- [Aldosteronismo primário e feocromocitoma: testes confirmatórios](aldosteronismo-primario-e-feocromocitoma-testes-confirmatorios-endocrine-society.md)
- [Fluxograma geral de emergência hipertensiva](fluxograma-emergencia-hipertensiva.md)
- [Miocardiopatia catecolaminérgica por feocromocitoma/paraganglioma](../Geral/miocardiopatia-catecolaminergica-por-feocromocitoma-e-paraganglioma-suspeitar-antes-de-atribuir-a-estresse.md)
- [Takotsubo basal/invertido e gatilho catecolaminérgico](../Saúde_mental_e_cardiologia/takotsubo-variante-basal-invertida-reconhecimento-do-padrao-atipico-e-gatilho-catecolaminergico.md)
