---
title: "Fluxograma: Revascularização percutânea versus cirúrgica na doença multiarterial e de tronco (ESC/EACTS 2018)"
slug: fluxograma-revascularizacao-pci-versus-cabg-multiarterial-e-tronco
theme: "Doença coronariana"
kind: fluxograma
fonte_producao: chatgpt
summary: "Caminho decisório do Heart Team na doença coronariana multiarterial ou de tronco: complexidade anatômica (SYNTAX), risco cirúrgico, diabetes e expectativa/preferência do paciente como eixos que separam ICP de CRM."
review_status: revisado
review_note: "PMIDs conferidos nesta sessão via PubMed E-utilities (esearch/esummary): 30165437 (2018 ESC/EACTS Guidelines on myocardial revascularization, Eur Heart J. 2019;40(2):87-165), 34011163 (SYNTAX Extended Survival Study, 10 anos, Circulation. 2021;144(2):96-109) e 23121323 (FREEDOM, Farkouh ME et al., NEJM. 2012;367(25):2375-2384) — título, revista, ano e volume/páginas batendo exatamente com o texto do documento. O escore SYNTAX não é recalculado no documento; a árvore assume que ele já foi calculado antes da entrada em D2."
source_refs: ["Neumann FJ, Sousa-Uva M, Ahlsson A, et al. 2018 ESC/EACTS Guidelines on myocardial revascularization · European Heart Journal · 2019 · 40(2):87-165 · PMID: 30165437", "Takahashi K, Serruys PW, Gao C, et al. Ten-Year All-Cause Death According to Completeness of Revascularization in Patients With Three-Vessel Disease or Left Main Coronary Artery Disease: Insights From the SYNTAX Extended Survival Study · Circulation · 2021 · 144(2):96-109 · PMID: 34011163", "Farkouh ME, Domanski M, Sleeper LA, et al. Strategies for multivessel revascularization in patients with diabetes (FREEDOM) · New England Journal of Medicine · 2012 · 367(25):2375-2384 · PMID: 23121323"]
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

  D1 -->|"Não"| D2{"Escore SYNTAX baixo/intermediário (≤32) E<br/>anatomia tecnicamente favorável à ICP completa?"}

  D2 -->|"Não — SYNTAX alto ou<br/>anatomia desfavorável"| D3{"Risco cirúrgico proibitivo (EuroSCORE II/STS<br/>muito elevado) ou comorbidade que contraindique CRM?"}

  D3 -->|"Sim"| C2(["ICP, mesmo com complexidade anatômica alta,<br/>como alternativa à cirurgia proibitiva —<br/>decisão do Heart Team"])

  D3 -->|"Não"| C3(["Cirurgia de revascularização miocárdica (CRM)"])

  D2 -->|"Sim"| D4{"Paciente é diabético?"}

  D4 -->|"Sim"| D5{"Heart Team multidisciplinar avalia<br/>o risco cirúrgico como aceitável?"}

  D5 -->|"Sim"| C4(["Preferir CRM — benefício de sobrevida em<br/>diabéticos com doença multiarterial, mesmo com<br/>SYNTAX baixo/intermediário (FREEDOM)"])

  D5 -->|"Não"| C5(["ICP como alternativa, buscando<br/>revascularização completa quando possível"])

  D4 -->|"Não"| D6{"Expectativa de vida limitada, fragilidade<br/>moderada ou recusa informada de esternotomia<br/>favorecem evitar cirurgia?"}

  D6 -->|"Sim"| C6(["ICP com revascularização completa guiada<br/>por fisiologia (FFR/iFR), quando a anatomia permitir"])

  D6 -->|"Não"| C7(["Decisão compartilhada entre ICP e CRM pelo<br/>Heart Team — CRM com maior evidência de<br/>durabilidade a longo prazo (SYNTAXES, 10 anos)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5,C6,C7 conduta;
```

## O que a árvore não mostra

**O escore SYNTAX não é recalculado aqui.** A árvore assume que ele já foi
calculado (número de lesões, localização, complexidade de bifurcação,
calcificação, tortuosidade) antes de entrar em D2. O ponto de corte de 32 é o
da diretriz ESC/EACTS 2018; ele separa "baixo/intermediário" de "alto", mas
não substitui a avaliação qualitativa da anatomia (uma lesão tecnicamente
difícil pode existir mesmo com SYNTAX numericamente baixo).

**O benefício de sobrevida da CRM no diabético vem do FREEDOM, um ensaio de
2012 com stents farmacológicos de 1ª geração.** A magnitude do benefício em
relação à ICP com stents atuais (com plataformas e antiproliferativos mais
novos) é objeto de debate — a diretriz mantém a recomendação, mas isso não é
equivalente a repetir o ensaio com a tecnologia de hoje.

**Risco cirúrgico não é um número único.** EuroSCORE II e STS são as
ferramentas mais citadas, mas nenhuma delas incorpora bem fragilidade,
calcificação de aorta ou disfunção cognitiva — fatores que o Heart Team pesa
clinicamente e que a árvore resume na pergunta de D3 e D6.

**Revascularização completa versus só a lesão culpada** (no contexto de
infarto multiarterial) é uma pergunta distinta desta árvore, tratada em
documento próprio da biblioteca — aqui o cenário é eletivo ou subagudo, não
STEMI com múltiplas lesões na fase aguda.
