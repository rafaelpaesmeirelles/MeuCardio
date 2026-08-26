---
title: "Fluxograma: Teste de vasorreatividade aguda na HAP idiopática/hereditária e a decisão pelo bloqueador de canal de cálcio"
slug: fluxograma-vasorreatividade-aguda-hap-idiopatica-bloqueador-canal-calcio
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado 'teste-de-vasorreatividade-aguda-na-hap-idiopatica-e-hereditaria-o-criterio-de-sitbon.md' desta pasta. O critério numérico de resposta positiva, a distinção entre resposta aguda e sustentada, a reavaliação em 3-4 meses e os critérios de resposta crônica foram conferidos contra Sitbon et al. e a ESC/ERS 2022. Corrigida em 26/08/2026 a lista de agentes: a ESC/ERS 2022 recomenda óxido nítrico inalado ou iloprosta inalada e admite epoprostenol IV como alternativa; adenosina IV foi removida por não integrar a recomendação contemporânea. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["Sitbon O, Humbert M, Jaïs X, Ioos V, Hamid AM, Provencher S, Garcia G, Parent F, Hervé P, Simonneau G. Long-term response to calcium channel blockers in idiopathic pulmonary arterial hypertension. Circulation. 2005;111(23):3105-3111. DOI: 10.1161/CIRCULATIONAHA.104.488486. PMID: 15939821 — já citado em 'teste-de-vasorreatividade-aguda-na-hap-idiopatica-e-hereditaria-o-criterio-de-sitbon.md' desta pasta.", "Bhatt A, Sharma J. Management of Pulmonary Arterial Hypertension. Curr Cardiovasc Risk Rep. 2020;14:23. DOI: 10.1007/s12170-020-00663-3. PMID: 33224405. PMCID: PMC7671829 — dose-alvo de bloqueador de canal de cálcio atribuída a Sitbon et al. 2005 e Rich et al. 1992, já citada com a mesma ressalva de fonte secundária em 'teste-de-vasorreatividade-aguda-na-hap-idiopatica-e-hereditaria-o-criterio-de-sitbon.md' desta pasta.", "Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548 — reavaliação com cateterismo direito em 3-4 meses após início do bloqueador de canal de cálcio em dose alta, já citada em 'teste-de-vasorreatividade-aguda-na-hap-idiopatica-e-hereditaria-o-criterio-de-sitbon.md' desta pasta."]
---

# Fluxograma: Teste de vasorreatividade aguda na HAP idiopática/hereditária e a decisão pelo bloqueador de canal de cálcio

Antes de iniciar terapia combinada específica para HAP, um pequeno subgrupo de pacientes
com HAP idiopática, hereditária ou induzida por droga/toxina — ainda sem tratamento —
pode responder a um bloqueador de canal de cálcio em dose alta em vez da terapia
padrão. Identificar esse subgrupo exige um teste específico e uma reavaliação posterior,
porque resposta aguda e resposta sustentada não são a mesma coisa.

## Árvore de decisão

```mermaid
flowchart TD
  R0["HAP idiopática, hereditária ou induzida<br/>por droga/toxina, confirmada por cateterismo<br/>direito, virgem de tratamento específico"] --> P1["Teste de vasorreatividade aguda no cateterismo<br/>direito — óxido nítrico inalado ou iloprosta inalada;<br/>epoprostenol IV pode ser usado como alternativa"]

  P1 --> D1{"Resposta positiva pelo critério de Sitbon?<br/>queda de PAPm de pelo menos 10mmHg,<br/>atingindo PAPm final igual ou inferior a 40mmHg,<br/>com débito cardíaco mantido ou aumentado"}

  D1 -->|"Não"| C1(["Terapia específica combinada para HAP —<br/>ver fluxograma de estratificação de risco<br/>e terapia combinada inicial desta pasta"])

  D1 -->|"Sim"| P2["Iniciar bloqueador de canal de cálcio oral<br/>em dose alta sob monitorização — nifedipino,<br/>diltiazem ou amlodipino; evitar verapamil"]

  P2 --> D2{"Reavaliação completa em 3 a 4 meses,<br/>incluindo cateterismo direito: CF-OMS I/II<br/>e melhora hemodinâmica marcada<br/>(PAPm <30 mmHg e RVP <4 UW)?"}

  D2 -->|"Sim"| C2(["Manter bloqueador de canal de cálcio<br/>em dose alta, com seguimento clínico e<br/>hemodinâmico periódico"])

  D2 -->|"Não, resposta insuficiente"| C3(["Iniciar terapia específica para HAP;<br/>considerar manter o bloqueador de canal<br/>de cálcio se sua retirada causar<br/>deterioração clínica (ESC/ERS 2022)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## O que a árvore não mostra

- **Adenosina IV não é uma alternativa neste fluxo.** Embora apareça em séries
  e protocolos históricos, ela não integra os agentes recomendados pela
  ESC/ERS 2022 para o teste contemporâneo; não deve ser recolocada por analogia.

- **O teste só tem valor discriminativo nesta etiologia.** Ele não deve ser realizado por
  rotina em HAP associada a doença do tecido conjuntivo (resposta sustentada rara mesmo
  quando agudamente positiva), em doença veno-oclusiva pulmonar/hemangiomatose capilar
  pulmonar (risco de edema pulmonar grave) nem nos grupos 2 e 3 de hipertensão pulmonar,
  onde o vasodilatador agudo pode precipitar congestão sem orientar conduta — ver
  documento específico desta pasta sobre vasorreatividade nos grupos 2 e 3.
- **Resposta aguda é minoria, e resposta sustentada é dupla minoria.** No estudo de
  Sitbon et al. (557 pacientes com HAP idiopática), 12,6% tiveram resposta aguda positiva,
  mas só 6,8% do total — pouco mais da metade dos respondedores agudos — sustentaram a
  resposta em pelo menos 1 ano de monoterapia com bloqueador de canal de cálcio. É por
  isso que a árvore não trata resposta aguda positiva como decisão terapêutica definitiva:
  a reavaliação em 3 a 4 meses é o passo que separa as duas.
- **As doses não são ramos da árvore.** A ESC/ERS 2022 recomenda iniciar em dose baixa
  e titular progressivamente até dose alta tolerada, sob acompanhamento em centro de
  hipertensão pulmonar; hipotensão, síncope e falência de ventrículo direito são riscos
  de usar bloqueador de canal de cálcio sem resposta vasorreativa documentada. A tabela
  de doses da própria diretriz deve orientar a prescrição individual, não uma transcrição
  isolada de séries históricas.
- **A árvore não cobre a escolha de terapia combinada em quem tem teste negativo** — esse
  desdobramento (estratificação de risco de 3 e 4 estratos, mono/dupla/tripla) está no
  fluxograma próprio desta pasta sobre terapia combinada inicial na HAP.
