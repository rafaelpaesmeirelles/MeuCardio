---
title: "Fluxograma: Hipertensão Arterial Pulmonar — terapia combinada inicial e escalonamento por estratificação de risco"
slug: fluxograma-hap-estratificacao-risco-terapia-combinada-inicial
theme: "Hipertensão pulmonar"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Árvore construída a partir de dois documentos já publicados e revisados nesta pasta, sem consulta a fonte nova: 'estratificacao-de-risco-e-terapia-combinada-inicial-na-hipertensao-arterial-pulmonar.md' (modelo de 3 estratos ao diagnóstico e de 4 estratos no seguimento, ESC/ERS 2022; ensaio AMBITION, PMID 26363732 conferido no texto-fonte) e 'terapia-tripla-inicial-versus-dupla-na-hap-o-ensaio-triton.md' (TRITON, PMID 34593120 — usado só para justificar por que a tripla inicial não é indicada de rotina fora do alto risco, e por que a escalada para a via da prostaciclina no seguimento é guiada por risco, não por um ensaio que a tenha comprovado como estratégia inicial universal). Os cortes de risco e a lógica de escalonamento foram conferidos contra o texto desses dois documentos antes de montar a árvore; nenhum PMID novo foi buscado para este fluxograma."
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
  R0["HAP (grupo 1) confirmada por cateterismo direito —<br/>teste de vasorreatividade aguda negativo<br/>ou não indicado nesta etiologia"] --> D1{"Estratificação de risco ao diagnóstico<br/>(modelo de 3 estratos, ESC/ERS 2022):<br/>mortalidade estimada em 1 ano"}

  D1 -->|"Risco baixo — menor que 5%"| P1["Terapia combinada oral dupla inicial<br/>antagonista do receptor de endotelina<br/>mais inibidor de PDE5"]

  D1 -->|"Risco intermediário — 5 a 20%"| P2["Terapia combinada oral dupla inicial<br/>antagonista do receptor de endotelina<br/>mais inibidor de PDE5"]

  D1 -->|"Risco alto — maior que 20%"| C1(["Terapia combinada tripla inicial,<br/>incluindo prostaciclina parenteral<br/>ou subcutânea — encaminhar a<br/>centro de referência em HAP"])

  P1 --> D2{"Reavaliação clínica em 3 a 6 meses<br/>(modelo de 4 estratos, ESC/ERS 2022):<br/>classe funcional, teste de caminhada de 6<br/>minutos e BNP/NT-proBNP"}

  P2 --> D2b{"Reavaliação clínica em 3 a 6 meses<br/>(modelo de 4 estratos, ESC/ERS 2022):<br/>classe funcional, teste de caminhada de 6<br/>minutos e BNP/NT-proBNP"}

  D2 -->|"Risco baixo"| C2(["Manter terapia combinada dupla<br/>seguimento periódico com reavaliação<br/>de risco a cada 3 a 6 meses"])

  D2 -->|"Risco intermediário-baixo"| C3(["Manter terapia combinada dupla,<br/>reforçar adesão e otimizar a dose<br/>já prescrita antes de escalonar"])

  D2 -->|"Risco intermediário-alto ou alto"| C4(["Escalonar para a via da prostaciclina<br/>(terapia tripla) e reavaliar elegibilidade<br/>a transplante pulmonar"])

  D2b -->|"Risco baixo"| C2b(["Manter terapia combinada dupla<br/>seguimento periódico com reavaliação<br/>de risco a cada 3 a 6 meses"])

  D2b -->|"Risco intermediário-baixo"| C3b(["Manter terapia combinada dupla,<br/>reforçar adesão e otimizar a dose<br/>já prescrita antes de escalonar"])

  D2b -->|"Risco intermediário-alto ou alto"| C4b(["Escalonar para a via da prostaciclina<br/>(terapia tripla) e reavaliar elegibilidade<br/>a transplante pulmonar"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C2b,C3b,C4b conduta;
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
- **A árvore não cobre a HAP com resposta positiva ao teste de vasorreatividade agudo**
  (candidata a bloqueador de canal de cálcio em vez de terapia combinada) nem o manejo da
  hipertensão pulmonar tromboembólica crônica — ambos têm fluxograma próprio nesta pasta.
