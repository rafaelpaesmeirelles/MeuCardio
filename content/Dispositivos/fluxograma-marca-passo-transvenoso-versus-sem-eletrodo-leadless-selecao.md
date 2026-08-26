---
title: "Fluxograma: Marca-passo transvenoso versus sem eletrodo (leadless) — critérios de seleção"
slug: fluxograma-marca-passo-transvenoso-versus-sem-eletrodo-leadless-selecao
theme: "Dispositivos"
kind: fluxograma
fonte_producao: chatgpt
summary: "Depois de confirmada a indicação de marcapasso definitivo, a escolha entre sistema transvenoso e sem eletrodo (leadless) depende da terapia necessária — atrial, ventricular, bicameral, TRC ou CDI —, da disponibilidade regulatória e de fatores de risco de complicação de bolsa/eletrodo."
review_status: revisado
review_note: "PMIDs conferidos individualmente no PubMed via E-utilities: 34455430 (ESC 2021 estimulação/TRC), 26551877 (Micra), 31709982 (MARVEL 2) e 37212442 (ensaio de marcapasso leadless bicameral, Knops RE et al., NEJM 2023;388:2360-2370, DOI 10.1056/NEJMoa2300080). O último foi acrescentado para remover a afirmação desatualizada de que nenhuma plataforma multicâmara existe; disponibilidade e autorização regulatória local ainda precisam ser confirmadas no momento da indicação. Pendente revisão médica independente antes de uso assistencial."
source_refs: ["2021 ESC Guidelines on cardiac pacing and cardiac resynchronization therapy · European Heart Journal · 2021 · 42(35):3427-3520 · https://pubmed.ncbi.nlm.nih.gov/34455430/", "A Leadless Intracardiac Transcatheter Pacing System (Micra Transcatheter Pacing Study) · New England Journal of Medicine · 2016 · 374(6):533-541 · https://pubmed.ncbi.nlm.nih.gov/26551877/", "Atrioventricular Synchronous Pacing Using a Leadless Ventricular Pacemaker: Results From the MARVEL 2 Study · JACC Clinical Electrophysiology · 2020 · 6(1):94-106 · https://pubmed.ncbi.nlm.nih.gov/31709982/", "A Dual-Chamber Leadless Pacemaker · New England Journal of Medicine · 2023 · 388:2360-2370 · DOI: 10.1056/NEJMoa2300080 · PMID: 37212442."]
---

# Fluxograma: Marca-passo transvenoso versus sem eletrodo (leadless)

A discussão sobre marca-passo sem eletrodo só começa depois que a indicação de
estimulação definitiva já está confirmada pela diretriz ESC 2021. A partir
daí, a escolha de plataforma não é preferência de tecnologia — depende de três
perguntas objetivas: qual terapia precisa ser fornecida, se a estimulação
atrial verdadeira ou apenas sincronia atrioventricular é necessária, quais
plataformas estão autorizadas/disponíveis e se existem fatores que elevam o
risco de complicação de bolsa ou de eletrodo transvenoso.

## Árvore de decisão

```mermaid
flowchart TD
  R0["Indicação de marcapasso<br/>definitivo confirmada (ESC 2021)"] --> D1{"Necessita TRC/biventricular ou<br/>terapia de CDI no mesmo sistema?"}

  D1 -->|"Sim"| C1(["Sistema capaz de fornecer TRC e/ou<br/>terapia de CDI; marcapasso leadless<br/>isolado ou bicameral não substitui<br/>essas funções"])

  D1 -->|"Não"| D0{"Há indicação de estimulação atrial<br/>verdadeira (por exemplo, disfunção<br/>sinusal), e não apenas sincronia AV?"}

  D0 -->|"Sim"| D7{"Sistema leadless bicameral autorizado,<br/>disponível e adequado ao paciente?"}
  D7 -->|"Sim"| C0(["Pode-se considerar sistema leadless<br/>bicameral após avaliação especializada;<br/>ponderar evidência mais recente e<br/>experiência do centro"])
  D7 -->|"Não"| C3(["Marca-passo transvenoso<br/>bicameral convencional"])

  D0 -->|"Não, estimulação<br/>ventricular é suficiente"| D2{"Há necessidade real de<br/>sincronia atrioventricular<br/>(ritmo sinusal, estimulação<br/>ventricular frequente esperada)?"}

  D2 -->|"Sim"| D3{"Leadless com sincronia AV<br/>(ex. Micra AV) disponível e<br/>critérios anatômicos/eletrofisiológicos<br/>adequados (MARVEL 2)?"}
  D3 -->|"Sim"| C2(["Marca-passo sem eletrodo com<br/>sincronia atrioventricular<br/>(ex. Micra AV)"])
  D3 -->|"Não"| C3(["Marca-passo transvenoso<br/>bicameral convencional"])

  D2 -->|"Não — FA permanente ou<br/>estimulação ocasional/backup"| D4{"Fatores de risco para complicação<br/>de bolsa/eletrodo: ausência de acesso<br/>venoso superior, hemodiálise, infecção<br/>prévia de CIED ou alto risco<br/>infeccioso?"}
  D4 -->|"Sim"| C4(["Considerar preferencialmente<br/>marca-passo sem eletrodo unicameral,<br/>após avaliação anatômica e do risco<br/>de perfuração vascular/cardíaca"])
  D4 -->|"Não"| D5{"Preferência do paciente e<br/>disponibilidade institucional<br/>favorecem o sistema sem eletrodo?"}
  D5 -->|"Sim"| C5(["Marca-passo sem eletrodo<br/>unicameral (leadless)"])
  D5 -->|"Não"| C6(["Marca-passo transvenoso<br/>unicameral convencional"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C0,C1,C2,C3,C4,C5,C6 conduta;
```

## O que a árvore não mostra

**O Micra Transcatheter Pacing Study encontrou 96% de liberdade de complicação
maior relacionada ao sistema ou procedimento em 6 meses.** Isso não equivale
a ausência universal de complicações: perfuração/tamponamento e complicações
do acesso femoral permanecem possíveis, embora não exista bolsa ou eletrodo
transvenoso.

**O MARVEL 2 avaliou sincronia AV mecânica, não elétrica**, comparando o
algoritmo de detecção mecânica de contração atrial do Micra AV contra
estimulação assíncrona — a decisão de usar essa plataforma depende de o
paciente manter ritmo sinusal e de haver expectativa real de estimulação
ventricular frequente, não é indicada indistintamente a todo paciente elegível
a marcapasso unicameral. O estudo foi curto e não demonstrou desfechos clínicos
de longo prazo equivalentes aos de um sistema bicameral convencional.

**Sistemas leadless bicamerais passaram a existir depois da diretriz ESC
2021.** O ensaio pivotal de 2023 demonstrou desempenho inicial de dois módulos
intracardíacos comunicantes, mas isso não fornece TRC nem terapia de CDI e não
elimina a necessidade de confirmar indicação, autorização local, experiência
do centro e dados de seguimento mais longo.

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
