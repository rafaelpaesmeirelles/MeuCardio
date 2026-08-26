---
title: "Fluxograma: Hipertensão Arterial Pulmonar — terapia combinada inicial e escalonamento por estratificação de risco"
slug: fluxograma-hap-estratificacao-risco-terapia-combinada-inicial
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir da ESC/ERS 2022, AMBITION (PMID 26308684) e TRITON (PMID 34593120). A dupla oral inicial ERA + PDE5i aplica-se a pacientes de baixo/intermediário risco sem comorbidades cardiopulmonares relevantes; nesses pacientes com comorbidades, a diretriz propõe monoterapia inicial individualizada (IIa/C). Tripla inicial com prostaciclina IV/SC também pode ser considerada no risco intermediário com comprometimento hemodinâmico grave. No seguimento em risco intermediário-baixo apesar da dupla, deve-se considerar adicionar selexipague (IIa/B) ou trocar PDE5i por riociguate (IIb/B), em vez de apenas manter a dupla. Em risco intermediário-alto/alto, adicionar prostaciclina IV/SC e encaminhar para avaliação de transplante deve ser considerado. Nenhum PMID novo foi introduzido."
source_refs: ["Humbert M, Kovacs G, Hoeper MM, et al. 2022 ESC/ERS Guidelines for the diagnosis and treatment of pulmonary hypertension. Eur Heart J. 2022;43(38):3618-3731. DOI: 10.1093/eurheartj/ehac237. PMID: 36017548 — modelo de estratificação de risco de 3 estratos ao diagnóstico e de 4 estratos no seguimento, já citado em 'estratificacao-de-risco-e-terapia-combinada-inicial-na-hipertensao-arterial-pulmonar.md' desta pasta.", "Galiè N, Barberà JA, Frost AE, et al.; AMBITION Investigators. Initial Use of Ambrisentan plus Tadalafil in Pulmonary Arterial Hypertension. N Engl J Med. 2015;373(9):834-844. DOI: 10.1056/NEJMoa1413687. PMID: 26308684 — já citado em 'estratificacao-de-risco-e-terapia-combinada-inicial-na-hipertensao-arterial-pulmonar.md' desta pasta.", "Chin KM, Sitbon O, Doelberg M, et al. Three- Versus Two-Drug Therapy for Patients With Newly Diagnosed Pulmonary Arterial Hypertension. J Am Coll Cardiol. 2021;78(14):1393-1403. DOI: 10.1016/j.jacc.2021.07.057. PMID: 34593120 — já citado em 'terapia-tripla-inicial-versus-dupla-na-hap-o-ensaio-triton.md' desta pasta, usado aqui só para justificar a régua de quando a tripla inicial entra."]
---

# Fluxograma: Hipertensão Arterial Pulmonar — terapia combinada inicial e escalonamento por estratificação de risco

Depois de confirmada a hipertensão arterial pulmonar (grupo 1) por cateterismo direito
e afastada — ou não indicada — a resposta ao teste de vasorreatividade aguda (ver
fluxograma próprio desta pasta sobre HAP idiopática/hereditária), a pergunta seguinte é
com que intensidade começar o tratamento farmacológico, e quando escalonar. Este
fluxograma organiza essa decisão em dois momentos: a escolha inicial pela estratificação
de risco de 3 estratos, e o escalonamento no seguimento pela estratificação de 4 estratos.

## Árvore de decisão

```mermaid
flowchart TD
  R0["HAP (grupo 1) confirmada por cateterismo direito —<br/>teste de vasorreatividade aguda negativo<br/>ou não indicado nesta etiologia"] --> D0{"Comorbidades cardiopulmonares relevantes<br/>(fenótipo de risco para ICFEp ou doença<br/>pulmonar/baixa DLCO)?"}

  D0 -->|"Sim"| C0(["Considerar monoterapia inicial com<br/>PDE5i ou antagonista do receptor de<br/>endotelina, com escalonamento<br/>individualizado — Classe IIa, Nível C"])

  D0 -->|"Não"| D1{"Estratificação de risco ao diagnóstico<br/>(modelo de 3 estratos, ESC/ERS 2022):<br/>mortalidade estimada em 1 ano"}

  D1 -->|"Risco baixo — menor que 5%"| P1["Terapia combinada oral dupla inicial<br/>antagonista do receptor de endotelina<br/>mais inibidor de PDE5"]

  D1 -->|"Risco intermediário — 5 a 20%"| D1b{"Comprometimento hemodinâmico grave<br/>(ex. PAD ≥20 mmHg, IC <2,0 L/min/m²,<br/>IVS <31 mL/m² ou RVP ≥12 UW)?"}

  D1b -->|"Não"| P2["Terapia combinada oral dupla inicial<br/>antagonista do receptor de endotelina<br/>mais inibidor de PDE5"]

  D1b -->|"Sim"| C1

  D1 -->|"Risco alto — maior que 20%"| C1(["Terapia combinada tripla inicial,<br/>incluindo prostaciclina IV ou SC —<br/>encaminhar a centro de referência<br/>em HAP"])

  P1 --> D2{"Reavaliação clínica em 3 a 6 meses<br/>(modelo de 4 estratos, ESC/ERS 2022):<br/>classe funcional, teste de caminhada de 6<br/>minutos e BNP/NT-proBNP"}

  P2 --> D2b{"Reavaliação clínica em 3 a 6 meses<br/>(modelo de 4 estratos, ESC/ERS 2022):<br/>classe funcional, teste de caminhada de 6<br/>minutos e BNP/NT-proBNP"}

  D2 -->|"Risco baixo"| C2(["Manter terapia combinada dupla<br/>seguimento periódico com reavaliação<br/>de risco a cada 3 a 6 meses"])

  D2 -->|"Risco intermediário-baixo"| C3(["Considerar adicionar selexipague ou<br/>trocar PDE5i por riociguate; nunca<br/>combinar PDE5i com riociguate"])

  D2 -->|"Risco intermediário-alto ou alto"| C4(["Adicionar prostaciclina IV/SC e<br/>encaminhar para avaliação de<br/>transplante pulmonar"])

  D2b -->|"Risco baixo"| C2b(["Manter terapia combinada dupla<br/>seguimento periódico com reavaliação<br/>de risco a cada 3 a 6 meses"])

  D2b -->|"Risco intermediário-baixo"| C3b(["Considerar adicionar selexipague ou<br/>trocar PDE5i por riociguate; nunca<br/>combinar PDE5i com riociguate"])

  D2b -->|"Risco intermediário-alto ou alto"| C4b(["Adicionar prostaciclina IV/SC e<br/>encaminhar para avaliação de<br/>transplante pulmonar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C2b,C3b,C4b conduta;
```

## O que a árvore não mostra

- **As variáveis que compõem cada estrato de risco não são ramos da árvore.** O modelo de
  3 estratos ao diagnóstico combina até 18 parâmetros (hemodinâmica incluída); o de 4
  estratos no seguimento se apoia sobretudo em classe funcional da OMS, distância no
  teste de caminhada de 6 minutos e BNP/NT-proBNP, com outras variáveis conforme
  necessário — são entradas do mesmo cálculo, não decisões sequenciais.
- **Por que existem dois modelos, e não um só.** A diretriz mudou de 3 para 4 estratos no
  seguimento porque 60 a 76% dos pacientes caíam na categoria intermediária com o modelo
  de 3 estratos — o de 4 discrimina melhor esse grupo grande e heterogêneo. O modelo de 3
  estratos continua sendo o do diagnóstico, não do seguimento.
- **A terapia tripla inicial não é a conduta padrão fora do risco alto.** O ensaio TRITON
  comparou tripla oral inicial (incluindo selexipague) contra dupla inicial em paciente
  recém-diagnosticado e não mostrou diferença na resistência vascular pulmonar em 26
  semanas — a redução foi de 54% na tripla e 52% na dupla, sem diferença estatística. Os
  sinais de possível benefício em progressão de doença e mortalidade foram exploratórios,
  em ensaio sem poder para esses desfechos. Por isso a árvore reserva a tripla inicial ao
  risco alto — onde a prostaciclina parenteral já tem indicação estabelecida
  independentemente do TRITON — e não a generaliza para risco baixo ou intermediário.
  A exceção é o risco intermediário com comprometimento hemodinâmico grave,
  em que tripla inicial com prostaciclina IV/SC também pode ser considerada.
- **REVEAL 2.0 é uma ferramenta alternativa de estratificação, não mostrada aqui.**
  Derivada do registro americano REVEAL, tem desempenho estatístico comparativamente
  superior a outras estratégias de risco em sua população de origem (ver documento
  próprio desta pasta) — a árvore segue o modelo ESC/ERS por ser o mais usado nesta
  biblioteca, mas as duas ferramentas coexistem na prática, sem uma substituir
  automaticamente a outra.
- **Comorbidades e causas secundárias tratáveis** (apneia do sono, disfunção tireoidiana,
  anemia, entre outras) devem ser investigadas e tratadas em paralelo, em qualquer estrato
  de risco — não é um ramo de decisão porque vale para todos os pacientes, não é
  exclusivo de um caminho da árvore.
- **Comorbidades cardiopulmonares mudam o algoritmo inicial.** Obesidade,
  hipertensão, diabetes, doença coronária e doença pulmonar/baixa DLCO podem
  aumentar intolerância à dupla terapia; a escalada deve ser individualizada.
- **A árvore não cobre a HAP com resposta positiva ao teste de vasorreatividade agudo**
  (candidata a bloqueador de canal de cálcio em vez de terapia combinada) nem o manejo da
  hipertensão pulmonar tromboembólica crônica — ambos têm fluxograma próprio nesta pasta.
