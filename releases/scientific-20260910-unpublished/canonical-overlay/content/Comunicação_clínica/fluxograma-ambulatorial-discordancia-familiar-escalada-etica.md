---
slug: fluxograma-ambulatorial-discordancia-familiar-escalada-etica
title: 'Fluxograma ambulatorial: discordância familiar — mediar vs. retorno vs. escalar ética'
kind: fluxograma
theme: Comunicação clínica
summary: 'Árvore ambulatorial: fato/papéis/capacidade → mediação; impasse, coerção ou conflito de substitutos →
  escalar ética; retorno precoce quando o conflito é emotivo sem urgência decisória.'
tags: []
source_refs:
- 'AMA Code of Medical Ethics. Opinion 2.1.2: Decisions for Adult Patients Who Lack Capacity. https://code-medical-ethics.ama-assn.org/ethics-opinions/decisions-adult-patients-who-lack-capacity'
- 'Schneiderman LJ, Gilmer T, Teetzel HD, et al. Effect of ethics consultations on nonbeneficial life-sustaining
  treatments in the intensive care setting: a randomized controlled trial. JAMA. 2003;290(9):1166-1172. DOI: 10.1001/jama.290.9.1166.
  PMID: 12952998'
- 'Aulisio MP, Arnold RM, Youngner SJ; for the Society for Health and Human Values–Society for Bioethics Consultation
  Task Force on Standards for Bioethics Consultation. Health care ethics consultation: nature, goals, and competencies.
  Ann Intern Med. 2000;133(1):59-69. DOI: 10.7326/0003-4819-133-1-200007040-00012. PMID: 10877742'
- 'DuVal G, Sartorius L, Clarridge B, Gensler G, Danis M. What triggers requests for ethics consultations? J Med
  Ethics. 2001;27(suppl 1):i24-i29. DOI: 10.1136/jme.27.suppl_1.i24. PMID: 11314608'
evidence_level: null
source_tier: A
review_status: revisado
gaps: []
published: false
---

# Fluxograma ambulatorial: discordância familiar — destino

Prosa: [sinalizadores-ambulatoriais-discordancia-familiar-escalada-etica-cardiologia](/biblioteca/sinalizadores-ambulatoriais-discordancia-familiar-escalada-etica-cardiologia). Checklist: [checklist-ambulatorial-discordancia-familiar-quando-escalar-etica](/biblioteca/checklist-ambulatorial-discordancia-familiar-quando-escalar-etica). Capacidade/SDM: [documentacao-de-decisao-compartilhada-e-consentimento-informado-no-prontuario-e-litigio-em-cardiologia](/biblioteca/documentacao-de-decisao-compartilhada-e-consentimento-informado-no-prontuario-e-litigio-em-cardiologia).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial com discordância<br/>familiar ou paciente–família<br/>em decisão preferência-sensível"] --> D0{"Há urgência clínica<br/>cardiovascular agora?"}

  D0 -->|"Sim"| C0(["Estabilizar / encaminhar PS<br/>Ética NÃO substitui segurança"])

  D0 -->|"Não"| DS{"Ameaça/coerção com risco imediato?"}
  DS -->|"Sim"| CS(["Proteção imediata e equipe institucional<br/>Entrevistar paciente em segurança"])
  DS -->|"Não"| D1{"Dúvida de capacidade<br/>ou ambiente inadequado?<br/>(ver pacote avaliação de capacidade/consentimento)"}

  D1 -->|"Sim / dúvida"| C1(["PAUSAR deliberação<br/>preferência-sensível<br/>→ avaliar capacidade e consentimento"])

  D1 -->|"Não"| D2{"O conflito é principalmente<br/>fato incompleto, papel confuso<br/>ou choque pós má notícia?"}

  D2 -->|"Sim"| C2(["MEDIAR agora:<br/>alinhar fatos, ouvir paciente capaz,<br/>nomear valores; ou retorno 24–72 h<br/>com reunião familiar estruturada"])

  D2 -->|"Não / já mediou"| D3{"Impasse persistente, coerção<br/>sobre paciente capaz, conflito<br/>entre substitutos, ou pedido<br/>explícito de revisão ética?"}

  D3 -->|"Sim"| C3(["ESCALAR ética<br/>canal institucional<br/>(consulta/comitê) — facilitação,<br/>não tribunal; documentar"])

  D3 -->|"Não"| C4(["SDM / consentimento padrão<br/>+ documentar preferências<br/>e plano de retorno"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  classDef alerta fill:#fdecea,stroke:#b3261e,color:#3b0a0a;
  class C0,C1,C3 alerta;
  class C2,C4 conduta;
```

## Notas

- **D0** = segurança clínica primeiro.
- **D1** = não confundir discordância familiar com incapacidade (avaliação de capacidade/consentimento).
- **D2** = mediação alinhada a DuVal (conflito/família difícil) e Aulisio (facilitação).
- **D3** = escalada quando mediação esgota ou há coerção/impasse — Schneiderman mostra utilidade da consulta ética em conflitos de valor (contexto UTI; extrapolação operacional).
- Não decide incapacidade legal, substituto, doses nem teach-back.

## Autonomia, capacidade e proteção

Capacidade é específica para esta decisão e para este momento: avaliar compreensão, apreciação das consequências, raciocínio e expressão de escolha; oferecer comunicação acessível e corrigir causas reversíveis. Discordar da equipe ou da família não prova incapacidade. Coerção compromete a voluntariedade e requer conversa protegida, sem presumir incapacidade cognitiva.

A escolha informada e voluntária do paciente capaz prevalece; familiares participam com seu consentimento. Se faltar capacidade, identificar representação conforme normas locais e buscar preferências prévias confiáveis. Quando desconhecidas e não inferíveis com segurança, usar melhor interesse, considerando benefícios, ônus e valores disponíveis; não inventar vontade anterior. Ética apoia conflitos e casos sem representante, sem substituir proteção imediata contra ameaça/abuso nem retardar cuidado urgente. O prazo de 24–72 h só vale quando a espera for clinicamente segura.
