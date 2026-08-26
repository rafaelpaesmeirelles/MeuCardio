---
title: "Fluxograma: intoxicação por betabloqueador ou bloqueador de canal de cálcio"
slug: fluxograma-intoxicacao-por-betabloqueador-ou-bloqueador-de-canal-de-calcio
theme: "Farmacologia"
kind: fluxograma
fonte_producao: chatgpt
summary: "Árvore de decisão para intoxicação aguda por betabloqueador ou bloqueador de canal de cálcio com bradicardia e/ou hipotensão, escalonando de atropina e cálcio IV até insulina em altas doses (HIET), emulsão lipídica ou glucagon conforme a resposta e o fármaco predominante."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026 contra a atualização AHA 2023 e o consenso de intoxicação por BCC. Corrigidos atropina (1 mg), papel precoce e concomitante de HIET/vasopressor, reposição cautelosa de potássio, observação dependente do fármaco/formulação e indicações de resgate. Mantida pendência de revisão médica/toxicológica antes da publicação clínica."
source_refs:
  - "Lavonas EJ, Akpunonu PD, Arens AM, et al. 2023 American Heart Association Focused Update on the Management of Patients With Cardiac Arrest or Life-Threatening Toxicity Due to Poisoning. Circulation. 2023;148(16):e149-e184. PMID 37721023."
  - "St-Onge M, Anseeuw K, Cantrell FL, et al. Experts Consensus Recommendations for the Management of Calcium Channel Blocker Poisoning in Adults. Crit Care Med. 2017;45(3):e306-e315. PMID 27749343."
  - "Engebretsen KM, Kaczmarek KM, Morgan J, Holger JS. High-dose insulin therapy in beta-blocker and calcium channel-blocker poisoning. Clin Toxicol (Phila). 2011;49(4):277-283. PMID 21563902."
---

# Fluxograma: intoxicação por betabloqueador ou bloqueador de canal de cálcio

Intoxicação por betabloqueador ou bloqueador de canal de cálcio pode deteriorar rapidamente e costuma exigir tratamento multimodal. Na toxicidade com risco de vida, a AHA recomenda insulina em altas doses precocemente; no choque por bloqueador de canal de cálcio, cálcio, HIET e noradrenalina/epinefrina são terapias de primeira linha escolhidas e combinadas conforme o fenótipo hemodinâmico, sem esperar falha sequencial prolongada.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Suspeita de intoxicação aguda por betabloqueador ou bloqueador<br/>de canal de cálcio (bradicardia e/ou hipotensão após<br/>ingestão ou uso excessivo)"]
  X1["Medidas iniciais: ABC, monitorização contínua, acesso venoso,<br/>ECG de 12 derivações, glicemia capilar; considerar carvão ativado<br/>se ingestão há menos de 1-2h e via aérea protegida;<br/>contato com centro de toxicologia"]
  D1{"Instabilidade hemodinâmica (hipotensão sintomática,<br/>bradicardia com hipoperfusão, ou choque)?"}
  C1(["Observação monitorizada definida com toxicologia segundo<br/>agente, dose, formulação e coingestões; ingestão potencialmente<br/>tóxica de BCC geralmente requer cerca de 24h, e formulações<br/>de liberação prolongada exigem janela ampliada"])
  X2["Atropina 1 mg IV se bradicardia sintomática; cálcio IV<br/>se BCC; iniciar noradrenalina/epinefrina no choque e HIET<br/>precocemente se toxicidade grave/disfunção miocárdica"]
  D2{"A resposta hemodinâmica permanece inadequada após<br/>início das terapias de primeira linha?"}
  C2(["Manter monitorização intensiva e as terapias iniciadas;<br/>titular HIET/vasopressor e repetir cálcio quando indicado;<br/>vigiar recorrência da instabilidade"])
  X3["Intensificar HIET: bolus de insulina regular 1 U/kg + glicose,<br/>seguido de 1 U/kg/h, titulável até 10 U/kg/h; titular glicose,<br/>monitorar glicemia e K+; repor potássio com cautela somente<br/>quando necessário, evitando sobrecorreção"]
  D3{"Há resposta hemodinâmica adequada à HIET<br/>após início e titulação protocolados?"}
  C3(["Manter HIET, glicose e vasopressor conforme o fenótipo,<br/>com glicemia e potássio seriados; desmamar apenas após<br/>estabilidade sustentada, sob cuidado intensivo"])
  D4{"Choque/periparada persiste apesar de HIET em dose crescente,<br/>cálcio e vasopressores adequados?"}
  C4(["Considerar emulsão lipídica IV como resgate e ECMO-VA<br/>se choque refratário tiver componente cardiogênico;<br/>acionar precocemente toxicologia e centro com ECMO"])
  C5(["No predomínio de betabloqueador, considerar glucagon;<br/>marca-passo apenas se bradicardia/BAV instável sem disfunção<br/>miocárdica importante; avaliar depuração extracorpórea<br/>para betabloqueadores dializáveis selecionados"])

  R0 --> X1
  X1 --> D1
  D1 -->|"Não — estável, apenas bradicardia leve ou assintomática"| C1
  D1 -->|"Sim — instável"| X2
  X2 --> D2
  D2 -->|"Não — resposta adequada"| C2
  D2 -->|"Sim — refratário"| X3
  X3 --> D3
  D3 -->|"Sim"| C3
  D3 -->|"Não — choque refratário"| D4
  D4 -->|"Sim — refratário"| C4
  D4 -->|"Não, mas persistem bradicardia<br/>ou toxicidade específica por betabloqueador"| C5

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## O que a árvore não mostra

- **Coingestão com outros cardiotóxicos** (antidepressivo tricíclico, digoxina) muda o manejo — cada classe tem antídoto/estratégia própria, e a intoxicação mista exige abordagem combinada não detalhada aqui.
- **Formulações de liberação prolongada podem causar deterioração tardia.** A janela depende do agente e da formulação; em ingestão potencialmente tóxica de BCC, o consenso prefere cerca de 24 horas de monitorização hospitalar.
- **A HIET exige monitorização glicêmica e de potássio muito frequente.** A queda de K+ é sobretudo redistributiva; reposição excessiva pode causar hipercalemia de rebote, portanto deve ser cautelosa e protocolada.
- **Emulsão lipídica IV é terapia de resgate, não substituto inicial de HIET/vasopressor.** A evidência em BCC e betabloqueadores é de baixa qualidade e seu uso deve ocorrer com apoio toxicológico.
- **Carvão ativado só deve ser considerado com via aérea protegida e ingestão recente** — em paciente já bradicárdico/hipotenso ou com rebaixamento de consciência, o risco de aspiração pode superar o benefício.
- **Disponibilidade de ECMO é limitada** e a decisão de acioná-la depende de estrutura local e tempo de transporte — não é uma opção universalmente disponível no momento do choque refratário.
