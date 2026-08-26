---
title: "Fluxograma: Marca-passo transvenoso versus sem eletrodo (leadless) — critérios de seleção"
slug: fluxograma-marca-passo-transvenoso-versus-sem-eletrodo-leadless-selecao
theme: "Dispositivos"
kind: fluxograma
fonte_producao: chatgpt
summary: "Depois de confirmada a indicação de marcapasso definitivo pela ESC 2021, a escolha entre sistema transvenoso e sem eletrodo (leadless) depende da necessidade de múltiplas câmaras, da sincronia atrioventricular exigida e de fatores de risco de complicação de bolsa/eletrodo — não é uma preferência genérica de tecnologia."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities (esummary) nesta sessão: 34455430 (ESC 2021 diretriz de estimulação cardíaca e TRC, Glikson M, Eur Heart J 42(35):3427-3520), 26551877 (Micra Transcatheter Pacing Study, Reynolds D, NEJM 374(6):533-541) e 31709982 (MARVEL 2 — Micra AV, Steinwender C, JACC Clin Electrophysiol 6(1):94-106). Título, revista, volume/página e autor conferidos contra o registro oficial antes de citar."
source_refs: ["2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy · European Heart Journal · 2021 · 42(35):3427-3520 · https://pubmed.ncbi.nlm.nih.gov/34455430/", "A Leadless Intracardiac Transcatheter Pacing System (Micra Transcatheter Pacing Study) · New England Journal of Medicine · 2016 · 374(6):533-541 · https://pubmed.ncbi.nlm.nih.gov/26551877/", "Atrioventricular Synchronous Pacing Using a Leadless Ventricular Pacemaker: Results From the MARVEL 2 Study · JACC Clinical Electrophysiology · 2020 · 6(1):94-106 · https://pubmed.ncbi.nlm.nih.gov/31709982/"]
---

# Fluxograma: Marca-passo transvenoso versus sem eletrodo (leadless)

A discussão sobre marca-passo sem eletrodo só começa depois que a indicação de
estimulação definitiva já está confirmada pela diretriz ESC 2021. A partir
daí, a escolha de plataforma não é preferência de tecnologia — depende de três
perguntas objetivas: se a estimulação exigida é de múltiplas câmaras, se há
necessidade real de sincronia atrioventricular, e se existem fatores que
elevam o risco de complicação de bolsa ou de eletrodo transvenoso.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Indicação de marcapasso<br/>definitivo confirmada (ESC 2021)"] --> D1{"Necessita estimulação de<br/>múltiplas câmaras (biventricular<br/>ou atrial) ou terapia associada<br/>de CDI no mesmo sistema?"}

  D1 -->|"Sim"| C1(["Sistema transvenoso convencional —<br/>não há plataforma sem eletrodo<br/>multicâmara disponível para essa<br/>indicação"])

  D1 -->|"Não, estimulação<br/>ventricular isolada é suficiente"| D2{"Há necessidade real de<br/>sincronia atrioventricular<br/>(ritmo sinusal, estimulação<br/>ventricular frequente esperada)?"}

  D2 -->|"Sim"| D3{"Leadless com sincronia AV<br/>(ex. Micra AV) disponível e<br/>critérios anatômicos/eletrofisiológicos<br/>adequados (MARVEL 2)?"}
  D3 -->|"Sim"| C2(["Marca-passo sem eletrodo com<br/>sincronia atrioventricular<br/>(ex. Micra AV)"])
  D3 -->|"Não"| C3(["Marca-passo transvenoso<br/>bicameral convencional"])

  D2 -->|"Não — FA permanente ou<br/>estimulação ocasional/backup"| D4{"Fatores de risco para complicação<br/>de bolsa/eletrodo (acesso venoso<br/>difícil, diálise, alto risco de<br/>infecção, expectativa de vida<br/>limitada, questão cosmética)?"}
  D4 -->|"Sim"| C4(["Preferir marca-passo sem eletrodo<br/>unicameral (leadless)"])
  D4 -->|"Não"| D5{"Preferência do paciente e<br/>disponibilidade institucional<br/>favorecem o sistema sem eletrodo?"}
  D5 -->|"Sim"| C5(["Marca-passo sem eletrodo<br/>unicameral (leadless)"])
  D5 -->|"Não"| C6(["Marca-passo transvenoso<br/>unicameral convencional"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**O Micra Transcatheter Pacing Study estabeleceu a segurança do implante e a
ausência de complicação relacionada a bolsa/eletrodo em 96% dos pacientes em
6 meses**, e é essa evidência — não uma preferência tecnológica — que sustenta
o ramo de leadless quando o risco de complicação de bolsa/eletrodo é alto.

**O MARVEL 2 avaliou sincronia AV mecânica, não elétrica**, comparando o
algoritmo de detecção mecânica de contração atrial do Micra AV contra
estimulação assíncrona — a decisão de usar essa plataforma depende de o
paciente manter ritmo sinusal e de haver expectativa real de estimulação
ventricular frequente, não é indicada indistintamente a todo paciente elegível
a marcapasso unicameral.

**Extração de um sistema leadless em caso de infecção ou necessidade de
upgrade** segue via própria, tecnicamente diferente da extração de eletrodo
transvenoso — essa diferença pesa na decisão em paciente jovem com expectativa
de múltiplas trocas ao longo da vida, mas não está representada como ramo
porque é consideração de planejamento de longo prazo, não critério de seleção
inicial.

**RM condicional e compatibilidade de longo prazo** variam por modelo e
geração de dispositivo em ambas as plataformas — checar a ficha técnica do
sistema específico antes do implante, não presumir pela categoria
(transvenoso versus leadless).
