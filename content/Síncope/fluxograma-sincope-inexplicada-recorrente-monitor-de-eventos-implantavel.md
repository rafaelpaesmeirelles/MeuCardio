---
title: "Fluxograma: Investigação da síncope inexplicada recorrente — escolha da monitorização e monitor implantável (ESC 2018)"
slug: fluxograma-sincope-inexplicada-recorrente-monitor-de-eventos-implantavel
theme: "Síncope"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Auditoria científica independente do lote Claude em 26/08/2026: a tabela de recomendações e a seção 4.2.4 da diretriz ESC 2018 (PMID 29562304) foram reconferidas. Retirada a exigência incorreta de tilt test antes do monitor implantável; separadas as indicações Classe I A para pacientes sem alto risco e para pacientes de alto risco após investigação completa negativa; acrescentada a escolha por frequência dos sintomas; e substituído o rendimento 55% versus 19% pelos resultados publicados pela própria diretriz. Mantida pendência de revisão médica antes da publicação clínica."
source_refs: ["Brignole M, Moya A, de Lange FJ, et al.; ESC Scientific Document Group. 2018 ESC Guidelines for the diagnosis and management of syncope. Eur Heart J. 2018;39(21):1883-1948. DOI: 10.1093/eurheartj/ehy037. PMID: 29562304 — seção 4.2.4 e tabela de recomendações de monitorização eletrocardiográfica; texto integral reconferido.", "Tilt testing evolves: faster and still accurate. European Heart Journal. 2023;44(27):2480. https://academic.oup.com/eurheartj/article/44/27/2480/7198277 — contexto metodológico do tilt test."]
---

# Fluxograma: Investigação da síncope inexplicada recorrente — escolha da monitorização e monitor implantável (ESC 2018)

Quando a avaliação inicial e a estratificação de risco não fecham o diagnóstico e a
síncope se repete, a diretriz ESC 2018 escolhe a monitorização pela frequência esperada
dos eventos e pelo risco. O monitor de eventos implantável (ILR) pode entrar cedo, sem
exigir tilt test prévio, quando não há critérios de alto risco e a recorrência é provável
dentro da vida útil do dispositivo. Também é indicação Classe I A após investigação
completa negativa em pacientes de alto risco sem indicação convencional de CDI ou
marca-passo.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Síncope recorrente sem diagnóstico definido<br/>após avaliação inicial completa e<br/>avaliação cardiológica básica"] --> D1{"Há suspeita de cardiopatia estrutural<br/>ou isquêmica significativa, ou o ECG mostra<br/>característica de alto risco?"}

  D1 -->|"Sim"| C1(["Investigação intensiva dirigida:<br/>telemetria, ecocardiograma, teste de esforço<br/>ou estudo eletrofisiológico conforme o achado;<br/>tratar causa ou indicação convencional<br/>de CDI/marca-passo quando identificada"])

  C1 --> D2{"Após investigação completa,<br/>permanece sem causa, sem tratamento específico<br/>e sem indicação convencional de CDI/marca-passo?"}
  D2 -->|"Sim"| C2(["Monitor de eventos implantável indicado<br/>Classe I, Nível A, ESC 2018"])
  D2 -->|"Não"| C3(["Tratar o mecanismo ou a doença identificada"])

  D1 -->|"Não, sem alto risco"| D3{"Qual a frequência esperada<br/>de nova síncope ou pré-síncope?"}
  D3 -->|"Pelo menos 1 episódio/semana"| C4(["Considerar Holter<br/>Classe IIa, Nível B"])
  D3 -->|"Intervalo entre sintomas<br/>de até 4 semanas"| C5(["Considerar monitor de alça externo<br/>precocemente após o evento índice<br/>Classe IIa, Nível B"])
  D3 -->|"Eventos menos frequentes"| D4{"Síncope recorrente de origem incerta<br/>e alta probabilidade de recorrência<br/>dentro da vida útil do dispositivo?"}
  D4 -->|"Sim"| C6(["Monitor de eventos implantável<br/>em fase precoce da avaliação<br/>Classe I, Nível A"])
  D4 -->|"Não"| C7(["Reavaliar diagnóstico, frequência esperada<br/>e estratégia de seguimento; o ILR não deve<br/>ser implantado sem chance razoável de capturar<br/>um evento clinicamente útil"])

  C4 --> D5{"Monitorização não documentou o mecanismo<br/>e os eventos continuam inexplicados?"}
  C5 --> D5
  D5 -->|"Sim, recorrência segue provável"| C6
  D5 -->|"Não"| C8(["Tratar o mecanismo documentado<br/>ou reavaliar a hipótese diagnóstica"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

- **O protocolo do tilt test em si não está detalhado aqui.** Jejum de 2 a 4 horas, fase
  supina de pelo menos 5 minutos (ou 20 minutos com canulação venosa), fase de inclinação
  passiva de 20 a 45 minutos e, se negativa, provocação farmacológica com nitroglicerina
  sublingual ou isoproterenol intravenoso — está descrito no documento próprio desta pasta.
- **O tilt test não é pré-requisito para o ILR.** Deve ser considerado quando a avaliação
  inicial sugere síncope reflexa, hipotensão ortostática tardia, falência autonômica ou
  POTS, ou para ajudar a separar síncope de pseudossíncope psicogênica. Um resultado
  negativo não cria, isoladamente, indicação de monitor implantável.
- **O rendimento precisa ser apresentado no contexto correto.** Na meta-análise de cinco
  ensaios (660 pacientes) citada pela ESC, a estratégia inicial com ILR aumentou em 3,7
  vezes (IC 95% 2,7–5,0) a probabilidade relativa de diagnóstico versus a estratégia
  convencional. Após investigação completa negativa, nove estudos com 506 pacientes
  documentaram correlação sintoma–ECG em 35%; entre esses registros, 56% mostraram
  assistolia/bradicardia, 11% taquicardia e 33% ausência de arritmia.
- **Vídeo gravado por smartphone durante um episódio espontâneo** passa a ser aceito pela
  diretriz como ferramenta diagnóstica auxiliar, e pode encurtar a investigação quando
  disponível — não é um ramo separado porque depende de oportunidade, não de indicação
  programável.
- **Tilt cardioinibitório não equivale automaticamente a indicação de marca-passo.** A
  ESC reserva a estimulação para pacientes altamente selecionados, em geral com 40 anos
  ou mais, episódios reflexos graves, recorrentes, imprevisíveis e risco de trauma; a
  susceptibilidade hipotensiva associada pode reduzir a resposta ao dispositivo.
- **Estudo eletrofisiológico não é indicado de rotina** quando o paciente tem ECG normal,
  ausência de cardiopatia estrutural e ausência de palpitação — geralmente não acrescenta
  informação nesse perfil, mesmo dentro do ramo de "suspeita estrutural" da árvore.
