---
title: "Fluxograma ambulatorial: discordância familiar — mediar vs. retorno vs. escalar ética"
slug: fluxograma-ambulatorial-discordancia-familiar-escalada-etica
theme: "Comunicação clínica"
kind: fluxograma
fonte_producao: grok
summary: "Árvore ambulatorial: fato/papéis/capacidade → mediação; impasse, coerção ou conflito de substitutos → escalar ética; retorno precoce quando o conflito é emotivo sem urgência decisória."
review_status: pendente_revisao
review_note: "Irmão de sinalizadores-ambulatoriais-discordancia-familiar-escalada-etica-cardiologia (07/09/2026). Schneiderman PMID 12952998; Aulisio PMID 11329633; DuVal PMID 11314608. Anti-colisão #832 e #856."
source_refs:
  - "Schneiderman LJ, Gilmer T, Teetzel HD, et al. Effect of ethics consultations on nonbeneficial life-sustaining treatments in the intensive care setting: a randomized controlled trial. JAMA. 2003;290(9):1166-1172. DOI: 10.1001/jama.290.9.1166. PMID: 12952998"
  - "Aulisio MP, Arnold RM, Youngner SJ; for the Society for Health and Human Values–Society for Bioethics Consultation Task Force on Standards for Bioethics Consultation. Health care ethics consultation: nature, goals, and competencies. Ann Intern Med. 2000;133(1):59-69. DOI: 10.7326/0003-4819-133-1-200007040-00012. PMID: 11329633"
  - "DuVal G, Sartorius L, Clarridge B, Gensler G, Danis M. What triggers requests for ethics consultations? J Med Ethics. 2001;27(suppl 1):i24-i29. DOI: 10.1136/jme.27.suppl_1.i24. PMID: 11314608"
---

# Fluxograma ambulatorial: discordância familiar — destino

Prosa: [`sinalizadores-ambulatoriais-discordancia-familiar-escalada-etica-cardiologia`](sinalizadores-ambulatoriais-discordancia-familiar-escalada-etica-cardiologia.md). Checklist: [`checklist-ambulatorial-discordancia-familiar-quando-escalar-etica`](checklist-ambulatorial-discordancia-familiar-quando-escalar-etica.md). Capacidade/SDM: [`fluxograma-ambulatorial-capacidade-sdm-e-mas-noticias-destino`](fluxograma-ambulatorial-capacidade-sdm-e-mas-noticias-destino.md).

## Árvore de decisão

```mermaid
flowchart TD
  R0["Consulta ambulatorial com discordância<br/>familiar ou paciente–família<br/>em decisão preferência-sensível"] --> D0{"Há urgência clínica<br/>cardiovascular agora?"}

  D0 -->|"Sim"| C0(["Estabilizar / encaminhar PS<br/>Ética NÃO substitui segurança"])

  D0 -->|"Não"| D1{"Dúvida de capacidade<br/>ou ambiente inadequado?<br/>(ver pacote #856)"}

  D1 -->|"Sim / dúvida"| C1(["PAUSAR deliberação<br/>preferência-sensível<br/>→ gate capacidade/SDM #856"])

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
- **D1** = não confundir discordância familiar com incapacidade (#856).
- **D2** = mediação alinhada a DuVal (conflito/família difícil) e Aulisio (facilitação).
- **D3** = escalada quando mediação esgota ou há coerção/impasse — Schneiderman mostra utilidade da consulta ética em conflitos de valor (contexto UTI; extrapolação operacional).
- Não decide incapacidade legal, substituto, doses nem teach-back.
