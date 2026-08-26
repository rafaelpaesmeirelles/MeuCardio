---
title: "Fluxograma: Teste de vasorreatividade aguda na HAP idiopática/hereditária e a decisão pelo bloqueador de canal de cálcio"
slug: fluxograma-vasorreatividade-aguda-hap-idiopatica-bloqueador-canal-calcio
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir do documento já publicado e revisado 'teste-de-vasorreatividade-aguda-na-hap-idiopatica-e-hereditaria-o-criterio-de-sitbon.md' desta pasta, sem consulta a fonte nova. O critério numérico de resposta positiva (queda de PAPm de pelo menos 10mmHg até valor absoluto igual ou inferior a 40mmHg, com débito cardíaco mantido ou aumentado), a distinção entre resposta aguda (12,6% dos 557 pacientes de Sitbon et al. 2005) e resposta sustentada em 1 ano (6,8%), a régua de reavaliação em 3-4 meses e as doses-alvo de bloqueador de canal de cálcio (fonte secundária Bhatt & Sharma 2020, PMID 33224405, já citada com a mesma ressalva no documento de origem) foram conferidos contra esse texto antes de montar a árvore. Nenhum PMID novo foi buscado para este fluxograma."
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
  R0["HAP idiopática, hereditária ou induzida<br/>por droga/toxina, confirmada por cateterismo<br/>direito, virgem de tratamento específico"] --> P1["Teste de vasorreatividade aguda no cateterismo<br/>direito — óxido nítrico inalado, epoprostenol<br/>ou adenosina intravenosos, ou iloprost inalado"]

  P1 --> D1{"Resposta positiva pelo critério de Sitbon?<br/>queda de PAPm de pelo menos 10mmHg,<br/>atingindo PAPm final igual ou inferior a 40mmHg,<br/>com débito cardíaco mantido ou aumentado"}

  D1 -->|"Não"| C1(["Terapia específica combinada para HAP —<br/>ver fluxograma de estratificação de risco<br/>e terapia combinada inicial desta pasta"])

  D1 -->|"Sim"| P2["Iniciar bloqueador de canal de cálcio oral<br/>em dose alta sob monitorização — nifedipino,<br/>diltiazem ou amlodipino; evitar verapamil"]

  P2 --> D2{"Reavaliação clínica e hemodinâmica em<br/>3 a 4 meses: classe funcional OMS I ou II<br/>mantida e melhora hemodinâmica sustentada<br/>ao cateterismo direito repetido?"}

  D2 -->|"Sim"| C2(["Manter bloqueador de canal de cálcio<br/>como monoterapia definitiva,<br/>com seguimento periódico"])

  D2 -->|"Não, resposta não sustentada"| C3(["Suspender ou reduzir o bloqueador de canal<br/>de cálcio e migrar para terapia específica<br/>combinada para HAP"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3 conduta;
```

## O que a árvore não mostra

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
- **As doses-alvo dos bloqueadores de canal de cálcio não são ramos da árvore** — são
  parâmetros de titulação (nifedipino 120 a 240mg/dia; diltiazem 240 a 720mg/dia,
  algumas séries chegando a 900mg/dia; amlodipino até 20mg/dia, preferido quando há
  bradicardia relativa ou distúrbio de condução) obtidos de fonte secundária que atribui
  o esquema a Sitbon et al. 2005 e a Rich et al. 1992 — o esquema de titulação passo a
  passo do protocolo original não foi localizado em texto integral aberto, e por isso
  segue com verificação humana necessária antes de uso em protocolo institucional, como
  já registrado no documento de origem.
- **A árvore não cobre a escolha de terapia combinada em quem tem teste negativo** — esse
  desdobramento (estratificação de risco de 3 e 4 estratos, mono/dupla/tripla) está no
  fluxograma próprio desta pasta sobre terapia combinada inicial na HAP.
