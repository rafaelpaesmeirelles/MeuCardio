---
title: "Fluxograma: Revascularização percutânea versus cirúrgica na doença multiarterial e de tronco"
slug: fluxograma-revascularizacao-pci-versus-cabg-multiarterial-e-tronco
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: chatgpt
summary: "Caminho decisório do Heart Team na doença coronariana multiarterial ou de tronco: complexidade anatômica (SYNTAX), risco cirúrgico, diabetes e expectativa/preferência do paciente como eixos que separam ICP de CRM."
review_status: revisado
review_note: "Auditoria científica em 26/08/2026: PMIDs 30165437, 34011163, 23121323 e 37632756 conferidos. Corrigida a mistura entre tronco e doença de três vasos: os limiares SYNTAX e as classes de ICP diferem, e o FREEDOM não deve ser extrapolado ao tronco. Incorporada a revisão conjunta ESC/EACTS 2022 para tronco com SYNTAX 0–32. Mantida pendência de revisão médica antes da publicação clínica."
source_refs: ["Neumann FJ, Sousa-Uva M, Ahlsson A, et al. 2018 ESC/EACTS Guidelines on myocardial revascularization · European Heart Journal · 2019 · 40(2):87-165 · PMID: 30165437", "Byrne RA, Fremes S, Capodanno D, et al. 2022 Joint ESC/EACTS review of left main revascularization recommendations · European Heart Journal · 2023 · 44(41):4310-4320 · PMID: 37632756", "Takahashi K, Serruys PW, Gao C, et al. Ten-Year All-Cause Death According to Completeness of Revascularization in Patients With Three-Vessel Disease or Left Main Coronary Artery Disease: Insights From the SYNTAX Extended Survival Study · Circulation · 2021 · 144(2):96-109 · PMID: 34011163", "Farkouh ME, Domanski M, Sleeper LA, et al. Strategies for multivessel revascularization in patients with diabetes (FREEDOM) · New England Journal of Medicine · 2012 · 367(25):2375-2384 · PMID: 23121323"]
---

# Fluxograma: Revascularização percutânea versus cirúrgica na doença multiarterial e de tronco

A pergunta "ICP ou CRM?" na doença multiarterial ou de tronco de coronária
esquerda não tem resposta única — a diretriz ESC/EACTS 2018 organiza a
decisão em torno de quatro eixos que se combinam: **complexidade anatômica**
(escore SYNTAX), **risco cirúrgico**, **presença de diabetes** e
**expectativa de vida/preferência do paciente**, sempre discutidos pelo
Heart Team. O fluxograma abaixo não substitui essa discussão — organiza a
sequência lógica dos eixos que a alimentam.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Doença coronariana obstrutiva multiarterial ou de<br/>tronco de coronária esquerda, com indicação de revascularização"] --> D1{"Choque cardiogênico ou instabilidade<br/>hemodinâmica/elétrica exigindo revascularização<br/>de emergência?"}

  D1 -->|"Sim"| C1(["Revascularização de emergência pela via<br/>mais rápida disponível (em geral ICP da lesão culpada),<br/>sem tempo para discussão eletiva do Heart Team"])

  D1 -->|"Não"| D2{"Risco cirúrgico proibitivo, fragilidade grave<br/>ou comorbidade que inviabiliza CRM?"}
  D2 -->|"Sim"| C2(["Heart Team: considerar ICP se houver possibilidade<br/>de revascularização tecnicamente útil, ou tratamento<br/>clínico quando o risco superar o benefício"])
  D2 -->|"Não — baixo risco cirúrgico"| D3{"Anatomia predominante?"}
  D3 -->|"Tronco da coronária esquerda"| D4{"SYNTAX 0–32 e anatomia adequada<br/>tanto para ICP quanto para CRM?"}
  D4 -->|"Sim"| C3(["CRM: Classe I, Nível A; ICP: Classe IIa, Nível A<br/>(revisão conjunta ESC/EACTS 2022); decidir conforme<br/>preferência, expertise e chance de completude"])
  D4 -->|"Não — SYNTAX ≥33<br/>ou ICP incompleta"| C4(["Preferir CRM; na diretriz 2018, ICP com<br/>SYNTAX ≥33 é Classe III, Nível B,<br/>salvo cirurgia inviável/recusa após aconselhamento"])
  D3 -->|"Doença de três vasos"| D5{"Diabetes mellitus?"}
  D5 -->|"Sim"| D6{"SYNTAX baixo (0–22)?"}
  D6 -->|"Sim"| C5(["Preferir CRM (Classe I, A); ICP é alternativa<br/>Classe IIb, A em anatomia apropriada e decisão<br/>compartilhada — FREEDOM sustenta a preferência"])
  D6 -->|"Não — SYNTAX >22"| C6(["CRM Classe I, A; ICP não recomendada<br/>(Classe III, A) se a cirurgia for viável"])
  D5 -->|"Não"| D7{"SYNTAX baixo (0–22)?"}
  D7 -->|"Sim"| C7(["ICP ou CRM, ambas Classe I, A;<br/>Heart Team pondera completude, invasividade,<br/>durabilidade e preferência do paciente"])
  D7 -->|"Não — SYNTAX >22"| C8(["CRM Classe I, A; ICP não recomendada<br/>(Classe III, A) se a cirurgia for viável"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7,C8 conduta;
```

## O que a árvore não mostra

**Os pontos de corte não são intercambiáveis entre tronco e três vasos.** No
tronco, a revisão conjunta de 2022 reuniu SYNTAX 0–32 para considerar ICP em
anatomia adequada e baixo risco cirúrgico. Em três vasos, SYNTAX >22 continua
favorecendo CRM quando a cirurgia é viável.

**O benefício da CRM no diabético vem do FREEDOM, um ensaio de
2012 com stents farmacológicos de 1ª geração.** A magnitude do benefício em
relação à ICP com stents atuais (com plataformas e antiproliferativos mais
novos) é objeto de debate. O FREEDOM estudou doença multiarterial e excluiu
tronco significativo; por isso não fundamenta o ramo de tronco desta árvore.

**Risco cirúrgico não é um número único.** EuroSCORE II e STS são as
ferramentas mais citadas, mas nenhuma delas incorpora bem fragilidade,
calcificação de aorta ou disfunção cognitiva — fatores que o Heart Team pesa
clinicamente e que a árvore resume na pergunta de D3 e D6.

**Revascularização completa versus só a lesão culpada** (no contexto de
infarto multiarterial) é uma pergunta distinta desta árvore, tratada em
documento próprio da biblioteca — aqui o cenário é eletivo ou subagudo, não
STEMI com múltiplas lesões na fase aguda.
