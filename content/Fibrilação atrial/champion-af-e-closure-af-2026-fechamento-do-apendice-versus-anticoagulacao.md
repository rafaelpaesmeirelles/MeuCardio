---
title: "CHAMPION-AF e CLOSURE-AF 2026 — fechamento do apêndice atrial versus anticoagulação"
slug: champion-af-e-closure-af-2026-fechamento-do-apendice-versus-anticoagulacao
theme: "Fibrilação atrial"
kind: estudo
summary: "Leitura conjunta dos dois grandes ensaios randomizados de 2026 sobre fechamento percutâneo do apêndice atrial esquerdo versus anticoagulação/terapia médica, com resultados aparentemente divergentes e árvore de decisão para aplicabilidade."
review_status: pendente_revisao
fonte_producao: chatgpt
source_refs: ["Left Atrial Appendage Closure or Anticoagulation for Atrial Fibrillation (CHAMPION-AF). N Engl J Med. 2026;394:2083-2094. DOI: 10.1056/NEJMoa2517213. PMID: 41910347.", "Landmesser U, Skurk C, Kirchhof P, et al. Left Atrial Appendage Closure or Medical Therapy in Atrial Fibrillation (CLOSURE-AF). N Engl J Med. 2026;394:1270-1280. DOI: 10.1056/NEJMoa2513310. PMID: 41849741."]
---

# CHAMPION-AF e CLOSURE-AF — por que dois ensaios de 2026 chegaram a mensagens diferentes?

Em março de 2026, dois grandes ensaios randomizados publicados no **New England Journal of Medicine** compararam fechamento percutâneo do apêndice atrial esquerdo (LAA closure/LAAC) com terapia anticoagulante/médica na fibrilação atrial. Os resultados precisam ser lidos juntos porque estudaram **populações diferentes** e usaram **desfechos diferentes**.

## CHAMPION-AF

### População

**3.000 pacientes** com FA que eram candidatos adequados a anticoagulação oral:

- 1.499 fechamento do apêndice;
- 1.501 NOAC;
- idade média 71,7 anos;
- CHA₂DS₂-VASc médio 3,5.

### Eficácia em 3 anos

Composto de morte cardiovascular, AVC ou embolia sistêmica:

- LAAC: **5,7%**;
- NOAC: **4,8%**;
- diferença absoluta **0,9 ponto percentual**;
- IC95% −0,8 a 2,6;
- **P<0,001 para não inferioridade**.

### Sangramento não relacionado ao procedimento

- LAAC: **10,9%**;
- NOAC: **19,0%**;
- HR **0,55**;
- IC95% 0,45–0,67;
- **P<0,001 para superioridade**.

Portanto, nessa população elegível a NOAC, LAAC foi não inferior no desfecho composto de eficácia e reduziu sangramento não procedimental.

## CLOSURE-AF

### População

Ensaio alemão com **912 pacientes** de risco substancialmente maior:

- idade média 77,9 anos;
- CHA₂DS₂-VASc médio **5,2**;
- HAS-BLED médio **3,0**;
- alto risco simultâneo de AVC e sangramento.

A análise primária incluiu 446 pacientes no dispositivo e 442 na terapia médica dirigida pelo médico, incluindo DOAC quando elegível.

### Desfecho primário

Composto de AVC, embolia sistêmica, sangramento maior ou morte cardiovascular/inexplicada:

- LAAC: **16,8 eventos/100 pacientes-ano**;
- tratamento médico: **13,3 eventos/100 pacientes-ano**.

A não inferioridade **não foi demonstrada**:

- diferença no restricted mean survival time: −0,36 ano;
- IC95% −0,70 a −0,01;
- **P=0,44 para não inferioridade**.

Eventos adversos graves ocorreram em 82,5% no grupo dispositivo e 77,4% no grupo médico.

## Por que os resultados não são contraditórios de forma simples

### Populações diferentes

CHAMPION-AF estudou pacientes considerados candidatos a anticoagulação. CLOSURE-AF recrutou população mais idosa e com **alto risco simultâneo de AVC e sangramento**, aproximando-se de um grupo mais frágil e complexo.

### Desfechos diferentes

CHAMPION-AF separou o desfecho de eficácia do sangramento não procedimental. CLOSURE-AF colocou **sangramento maior dentro do próprio composto primário**, juntamente com AVC, embolia e morte.

### Estratégias médicas diferentes

CHAMPION-AF comparou diretamente dispositivo com NOAC. CLOSURE-AF usou melhor terapia médica determinada pelo médico, com anticoagulação quando apropriada.

### Risco procedimental importa

LAAC troca parte do risco hemorrágico crônico de anticoagulação por um **risco inicial do procedimento/dispositivo**. Quanto mais frágil e multimórbido o paciente, mais esse risco procedimental pode pesar.

## Árvore de decisão — como usar os dois ensaios

```mermaid
flowchart TD
    A[Paciente com FA e indicação de prevenção de AVC] --> B{Tolera e é elegível a DOAC de longo prazo?}
    B -- Não --> C[LAAC permanece opção relevante conforme indicação, anatomia e diretriz]
    B -- Sim --> D[Avaliar risco de AVC, sangramento, fragilidade e preferência]
    D --> E{Perfil semelhante ao CHAMPION-AF: elegível a OAC, risco moderado e candidato a procedimento?}
    E -- Sim --> F[LAAC pode ser discutido como alternativa: não inferior para eficácia e menos sangramento não procedimental]
    E -- Não --> G{Muito idoso/frágil e alto risco simultâneo de AVC + sangramento?}
    G -- Sim --> H[CLOSURE-AF exige cautela: LAAC não demonstrou não inferioridade ao tratamento médico]
    G -- Não --> I[Individualizar com diretrizes, anatomia, risco procedimental e preferências]
    F --> J[Decisão compartilhada: risco do procedimento versus exposição crônica a anticoagulação]
    H --> J
    I --> J
```

## Como explicar ao paciente

Uma comunicação equilibrada pode ser:

> O fechamento do apêndice evita anticoagulação crônica em muitos pacientes, mas envolve um procedimento com riscos próprios. Em um grande estudo de pacientes aptos a usar anticoagulante, o dispositivo teve eficácia global não inferior e menos sangramento não procedimental. Em outro estudo com pacientes mais idosos e de maior risco, o dispositivo não conseguiu demonstrar resultado global tão bom quanto o tratamento médico. A escolha depende de qual população se parece mais com você.

## O que NÃO concluir

- Não afirmar que CHAMPION-AF provou que LAAC é superior a DOAC para prevenção de AVC isoladamente.
- Não afirmar que CLOSURE-AF provou que LAAC é sempre inferior.
- Não escolher dispositivo apenas pelo HAS-BLED alto sem considerar fragilidade e risco procedimental.
- Não omitir que o risco do dispositivo ocorre sobretudo no período procedimental, enquanto sangramento do DOAC é exposição contínua.
- Não usar um único dos dois ensaios para aconselhamento sem mencionar o outro em pacientes elegíveis a ambas as estratégias.

## Regra prática

**Depois de 2026, a pergunta deixou de ser simplesmente “Watchman ou anticoagulante?”. A pergunta correta é: este paciente se aproxima mais da população em que LAAC foi uma alternativa eficaz ao NOAC ou da população muito frágil em que o tratamento médico teve melhor desempenho global?**