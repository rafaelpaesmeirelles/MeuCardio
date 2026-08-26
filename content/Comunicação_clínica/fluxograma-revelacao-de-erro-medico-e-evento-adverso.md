---
title: "Fluxograma: Revelação de Erro Médico e Evento Adverso ao Paciente"
slug: fluxograma-revelacao-de-erro-medico-e-evento-adverso
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: chatgpt
review_status: revisado
review_note: "Verificado por Claude em 26/08/2026: fonte primaria conferida; conteudo derivado de documento(s) ja publicado(s) no acervo, listado(s) em source_refs."
source_refs:
  - "Documento já publicado no acervo (tema Comunicação clínica): 'Revelação de erro médico e evento adverso ao paciente e à família: estrutura prática da conversa' (slug: revelacao-de-erro-medico-e-evento-adverso-estrutura-pratica-da-conversa), de onde vêm a sequência temporal, a separação entre reconhecer o fato e apurar a causa, e a ramificação por quem segue o cuidado após a revelação."
  - "Massachusetts Coalition for the Prevention of Medical Errors. When Things Go Wrong: Responding to Adverse Events — A Consensus Statement of the Harvard Hospitals. Março de 2006. Disponível em www.macoalition.org — fonte da janela de 24h, da frase-modelo de empatia e da orientação sobre quem conduz a conversa quando a equipe muda."
  - "Agency for Healthcare Research and Quality (AHRQ). Disclosure Checklist — Communication and Optimal Resolution (CANDOR) Toolkit. Revisado em agosto de 2022. https://www.ahrq.gov/patient-safety/settings/hospital/candor/modules/checklist5.html — fonte da janela de 60 minutos e da etapa formal de desculpa cedo na conversa."
  - "Gallagher TH, Garbutt JM, Waterman AD, et al. Choosing your words carefully: how physicians would disclose harmful medical errors to patients. Arch Intern Med. 2006;166(15):1585-1593. DOI: 10.1001/archinte.166.15.1585. PMID: 16908791 — evidência da lacuna entre o que médicos deveriam dizer e o que de fato dizem, citada no documento-fonte."
---

# Fluxograma: Revelação de Erro Médico e Evento Adverso ao Paciente

Esta árvore segue a estrutura prática descrita no documento-fonte, que combina o checklist CANDOR da AHRQ com o consenso de 2006 dos hospitais afiliados a Harvard. A primeira bifurcação separa o que fazer quando a causa do evento ainda não foi apurada (a situação mais comum na primeira conversa) do que fazer quando a causa já está confirmada — as duas fontes tratam essas duas situações de forma diferente, e confundi-las é uma das armadilhas nomeadas no documento-fonte ("não pular para conclusões... antes que todos os fatos sejam conhecidos").

## Árvore de decisão

```mermaid
flowchart TD
  R0["Evento adverso ou possível erro identificado no cuidado prestado ao paciente"] --> D1{"A causa do evento já foi totalmente apurada?"}

  D1 -->|"Não, apuração ainda em andamento (situação mais comum na 1ª conversa)"| N1["Comunicar ao paciente/família, dentro de 60 minutos, que um possível evento adverso ocorreu — mesmo sem os fatos completos (AHRQ CANDOR)"]
  N1 --> N2["Expressar empatia genuína logo no início: 'sinto muito que isso tenha acontecido, é terrível' — antes de qualquer causa ser conhecida"]
  N2 --> N3["Reconhecer o que se sabe até agora, sem especular sobre causa ou culpa; prometer investigação e retorno com os achados"]
  N3 --> D2{"O paciente/família está física e psicologicamente pronto para a conversa completa dentro de 24h?"}

  D2 -->|"Sim"| N4["Conduzir a conversa completa dentro de 24h da descoberta, com quem tem relação de confiança prévia com o paciente"]
  N4 --> D3{"A equipe que revela é a mesma que vai seguir o cuidado do paciente?"}
  D3 -->|"Sim, mesma equipe segue o caso"| C1(["Fechar a conversa combinando o próximo passo e a data da conversa de seguimento, antes de sair da sala"])
  D3 -->|"Não, outra equipe assume (ex.: paciente vai para UTI)"| C2(["Conduzir a conversa com o médico responsável pelo procedimento presente junto ao médico que assume os próximos passos, e então combinar o seguimento"])

  D2 -->|"Não, paciente/família ainda não está em condições"| C3(["Adiar a conversa completa, mas manter contato e informar o atraso com frequência, com desculpa explícita pelo atraso, até que a pessoa esteja pronta"])

  D1 -->|"Sim, causa já apurada e confirmada"| N5["Comunicar o fato já apurado, assumindo postura de responsabilidade pelo cuidado, sem culpar 'o sistema' ou terceiro não confirmado"]
  N5 --> N6["Pedir desculpas de forma específica e sincera pelo erro confirmado, idealmente por quem cometeu o erro, com remorso genuíno"]
  N6 --> D4{"O profissional responsável está emocionalmente apto a conduzir a conversa agora?"}
  D4 -->|"Sim"| N7["Conduzir a conversa pessoalmente, incluindo o que será feito para prevenir recorrência"]
  N7 --> C4(["Agendar conversa de seguimento e registrar em prontuário apenas fatos e planos de seguimento; realizar debriefing com a equipe envolvida"])
  D4 -->|"Não, profissional não está em condições emocionais"| C5(["Outro profissional conduz a conversa junto com o médico responsável pelo cuidado, mantendo a presença deste"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

## Sobre os critérios usados nesta árvore

A janela de 60 minutos para o primeiro aviso e a de 24 horas para a conversa completa vêm de fontes diferentes que o documento-fonte cita lado a lado: o checklist CANDOR da AHRQ pede avisar "dentro de 60 minutos" após o evento ser identificado, enquanto o consenso de Harvard fala em comunicar "assim que reconhecido e assim que o paciente estiver física e psicologicamente pronto, tipicamente dentro de 24 horas". A árvore trata isso como dois momentos sequenciais — o aviso inicial não espera o paciente estar pronto para a conversa completa, mas a conversa completa sim.

A bifurcação entre "causa não apurada" e "causa já apurada" segue a mesma distinção que o documento-fonte extrai das duas fontes primárias: "não especule sobre a causa antes da investigação estar completa" (AHRQ) versus a exigência, quando o erro já é confirmado, de desculpa específica e nomeação de quem cometeu o erro. A ramificação sobre quem segue o cuidado reflete a recomendação de Harvard para procedimento invasivo (cateterismo, angioplastia, implante de dispositivo), citada no documento-fonte como extensão razoável do princípio geral, não achado específico da literatura de cardiologia.

A armadilha mais medida na literatura — 56% dos médicos escolhendo frases que mencionam o evento sem declarar que houve erro, e a chance de revelação explícita caindo de 58% entre clínicos para 19% entre cirurgiões (Gallagher et al., Arch Intern Med 2006, PMID 16908791) — é o motivo pelo qual esta árvore força a explicitação do reconhecimento do fato como primeiro passo em ambos os ramos, antes de qualquer outra ação.