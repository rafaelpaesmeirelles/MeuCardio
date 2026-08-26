---
title: "Fluxograma: Protocolo SPIKES para Más Notícias em Cardiologia"
slug: fluxograma-protocolo-spikes-mas-noticias-cardiologia
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Protocolo SPIKES para Comunicação de Más Notícias, Aplicado à Cardiologia' (slug: protocolo-spikes-de-mas-noticias-aplicado-a-ic-avancada-cdi-e-prognostico-pos-iam), de onde vêm os seis passos, os três cenários cardiológicos e as armadilhas usados nesta árvore."
  - "Baile WF, Buckman R, Lenzi R, Glober G, Beale EA, Kudelka AP. SPIKES-A six-step protocol for delivering bad news: application to the patient with cancer. The Oncologist. 2000;5(4):302-311. DOI: 10.1634/theoncologist.5-4-302. PMID: 10964998 — protocolo original citado no documento-fonte."
  - "Servotte JC, Bragard I, Szyld D, Van Ngoc P, Scholtes B, Van Cauwenberge I, Donneau AF, Dardenne N, Goosse M, Pilote B, Guillaume M, Ghuysen A. Efficacy of a Short Role-Play Training on Breaking Bad News in the Emergency Department. West J Emerg Med. 2019;20(6):893-902. DOI: 10.5811/westjem.2019.8.43441. PMID: 31738716 — ensaio de eficácia do treinamento no protocolo, citado no documento-fonte."
---

# Fluxograma: Protocolo SPIKES para Más Notícias em Cardiologia

Esta árvore segue os seis passos do SPIKES (Setting, Perception, Invitation, Knowledge, Emotions, Strategy) tal como aplicados, no documento-fonte, a três cenários cardiológicos concretos: indicação de CDI de prevenção primária, insuficiência cardíaca avançada dependente de inotrópico e prognóstico pós-infarto extenso. O ramo escolhido em cada decisão determina qual variante do passo seguinte se aplica — não é uma lista de dicas soltas, é a sequência que o documento descreve como a diferença entre o erro mais comum (pular Setting/Perception/Invitation e ir direto para a informação) e a conversa estruturada.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Necessidade de comunicar má notícia em cardiologia (IC avançada, indicação de CDI, prognóstico pós-IAM)"] --> N1["S - Setting: preparar o cenário (sentar, privacidade, celular silenciado, tempo reservado, confirmar quem o paciente quer presente)"]
  N1 --> N2["P - Perception: perguntar o que o paciente já entende sobre o motivo da internação/exame"]
  N2 --> D1{"Qual é o cenário clínico da má notícia?"}

  D1 -->|"IC avançada dependente de inotrópico, sem candidatura a transplante ou DAV"| N3["I - Invitation: perguntar como o paciente imagina os próximos meses, antes de falar em prazo"]
  N3 --> N4["K - Knowledge: entregar a expectativa em fatias curtas, uma frase por vez, sem sequência de valores técnicos"]
  N4 --> D2{"Reação do paciente/família após a notícia?"}
  D2 -->|"Reação emocional intensa (silêncio, choro, raiva)"| C1(["E - Emotions: nomear e validar a emoção (NURSE) antes de qualquer novo dado. S - Strategy: só depois, definir passo seguinte e sinal de alarme, reforçando que o acompanhamento continua"])
  D2 -->|"Pergunta prática objetiva sobre o que muda agora"| C2(["S - Strategy: responder objetivamente - o que muda no tratamento, retorno agendado, sinal de alarme, quem procurar"])

  D1 -->|"Indicação de CDI de prevenção primária"| N5["I - Invitation: perguntar o que o paciente já entende sobre o encaminhamento ao eletrofisiologista, antes de falar em risco de morte súbita"]
  N5 --> D3{"O paciente quer saber a quantificação do risco de morte súbita?"}
  D3 -->|"Sim, quer números/probabilidade"| N6["K - Knowledge: explicar a indicação em fatias curtas, incluindo a quantificação pedida, sem jargão"]
  N6 --> D4{"Reação do paciente após a notícia?"}
  D4 -->|"Reação emocional intensa"| C3(["E - Emotions: nomear a emoção antes de prosseguir. S - Strategy: explicitar que o CDI é prevenção, não sentença de morte iminente, com data do implante"])
  D4 -->|"Pergunta prática sobre o procedimento"| C4(["S - Strategy: explicar quando o dispositivo será implantado, o que muda no dia a dia, e que a indicação não significa morte iminente"])

  D3 -->|"Não, prefere não quantificar, quer conversar mais com a família"| N7["K - Knowledge: explicar a indicação em termos qualitativos, envolvendo a família na conversa, sem impor números"]
  N7 --> D5{"Reação do paciente/família após a notícia?"}
  D5 -->|"Reação emocional intensa"| C5(["E - Emotions: nomear a emoção antes de prosseguir. S - Strategy: reforçar que o CDI previne morte súbita e não é diagnóstico de morte próxima"])
  D5 -->|"Aceitação ou pergunta prática"| C6(["S - Strategy: agendar implante, explicar rotina pós-implante, reforçar que a indicação não é sentença de morte iminente"])

  D1 -->|"Prognóstico pós-IAM extenso com disfunção ventricular significativa"| N8["I - Invitation: perguntar quanto detalhe quantitativo (fração de ejeção, classe Killip) o paciente quer receber"]
  N8 --> D6{"Reação após a notícia sobre a extensão do infarto e a função ventricular?"}
  D6 -->|"Reação emocional intensa"| C7(["E - Emotions: nomear a emoção antes de prosseguir. S - Strategy: fechar com retorno agendado e sinal de alarme"])
  D6 -->|"Pergunta prática sobre reabilitação ou próximos passos"| C8(["S - Strategy: traçar plano concreto - retorno, reabilitação cardíaca, sinal de alarme, reforçando que o acompanhamento não termina aqui"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## Sobre os critérios usados nesta árvore

O ponto de bifurcação em cada "Invitation" (quanto o paciente quer saber) não é um detalhe protocolar — o documento-fonte descreve que o passo Knowledge seguinte muda de conteúdo conforme essa resposta, especialmente na indicação de CDI, onde "a conversa sobre CDI implica falar de risco de morte de forma explícita, e nem todo paciente quer essa quantificação antes de decidir". Da mesma forma, o passo Emotions (E) sempre precede qualquer novo dado quando a reação é intensa — o documento nomeia isso como o erro mais comum: "continuar informando enquanto a emoção está alta é o erro que mais frequentemente faz a pessoa sair da sala sem ter entendido o plano seguinte".

A evidência de que treinar esse protocolo (não apenas lê-lo) muda desempenho vem do ensaio de Servotte et al. (West J Emerg Med 2019, PMID 31738716): 68 estudantes/residentes randomizados para rodízio padrão versus rodízio mais 4 horas de simulação sobre o SPIKES tiveram ganho significativo (p<0,001) em autoeficácia, no processo avaliado pelo formulário de competência SPIKES e nas habilidades de comunicação — com estudantes de pouca experiência prévia alcançando, após o treinamento, desempenho equivalente ao de colegas mais experientes do grupo controle.

Esta árvore não substitui `roteiro-de-conversa-dificil-em-cardiologia.md` (script de frases prontas para IC avançada e paliativo) nem `protocolo-spikes-de-mas-noticias-aplicado-a-ic-avancada-cdi-e-prognostico-pos-iam.md` (o documento didático completo, com a explicação de cada letra e as armadilhas). É a representação, em árvore de decisão, da sequência que esse último documento descreve.