---
title: "Fluxograma: Falência Aguda de Ventrículo Direito — causa precipitante e o risco de expandir volume"
slug: fluxograma-falencia-aguda-de-ventriculo-direito
theme: "Terapia intensiva"
kind: fluxograma
summary: "Árvore de decisão da falência aguda de ventrículo direito: identificar a causa precipitante antes de agir, decidir a reposição volêmica pela resposta hemodinâmica — não pelo reflexo do choque hipovolêmico — e escolher vasopressor, inotrópico e suporte circulatório mecânico conforme o consenso ACVC/ESC 2024."
review_status: revisado
source_refs: ["Diagnosis and treatment of right ventricular failure secondary to acutely increased right ventricular afterload (acute cor pulmonale): a clinical consensus statement of the Association for Acute CardioVascular Care (ACVC) of the European Society of Cardiology. Eur Heart J Acute Cardiovasc Care. 2024;13(3):304-312. DOI: 10.1093/ehjacc/zuad157. PMID: 38135288. Texto integral lido em 31/07/2026 via PMC10927027 — o registro do PubMed traz apenas o título, sem resumo", "Konstantinides SV, Meyer G, Becattini C, et al; ESC Scientific Document Group. 2019 ESC Guidelines for the diagnosis and management of acute pulmonary embolism developed in collaboration with the European Respiratory Society (ERS). Eur Heart J. 2020;41(4):543-603. DOI: 10.1093/eurheartj/ehz405. PMID: 31504429 — reaproveitada de tromboembolismo-pulmonar-agudo-diagnostico-e-manejo-escers-2019.md, nesta mesma base: trombólise sistêmica como reperfusão de escolha no TEP de alto risco com instabilidade, e remoção intervencionista de trombo (cateter ou cirurgia) como alternativa Classe IIa quando há contraindicação ou deterioração", "Siopi SA, Antonitsis P, Karapanagiotidis GT, Tagarakis G, Voucharas C, Anastasiadis K. Mechanical circulatory support in cardiogenic shock: a contemporary head-to-head comparison. Heart Fail Rev. 2026;31(1):44. PMID: 41874823. DOI: 10.1007/s10741-026-10612-8 (PMC13013270) — reaproveitada de choque-cardiogenico-suporte-circulatorio-mecanico-temporario.md, nesta mesma pasta: distinção entre falência primária e secundária de VD sob suporte mecânico", "Shams P, Parks LJ. Right Ventricular Myocardial Infarction. In: StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; atualizado em 23/03/2026. NBK431048. https://www.ncbi.nlm.nih.gov/books/NBK431048/ — texto lido via WebFetch em 03/08/2026, fonte nova adicionada porque o documento-fonte ACVC/ESC 2024 cita isquemia miocárdica como causa de falência de VD mas não detalha a conduta (reperfusão urgente; evitar nitrato e diurético)"]
---

# Fluxograma: Falência Aguda de Ventrículo Direito

O ventrículo direito é uma câmara de parede fina, adaptada a trabalhar contra
resistência baixa. Aumento **agudo** de pós-carga o faz dilatar, aumentar a
tensão de parede e entrar num ciclo que a conduta reflexa do choque
hipovolêmico **piora** — dar volume por reflexo diante de hipotensão é o erro
mais citado no consenso ACVC/ESC 2024. Por isso a primeira pergunta é a causa
precipitante, porque ela muda a conduta; a segunda é se o paciente responde a
volume ou já está congesto, nunca o oposto.

## Árvore de decisão: causa precipitante

```mermaid
flowchart TD
  R0["Falência aguda de VD:<br/>hipotensão com VD dilatado<br/>ou disfuncionante"]
  R0 --> D1
  D1{"Causa precipitante mais provável?"}

  D1 -->|"TEP maciço (obstrução proximal),<br/>com instabilidade hemodinâmica"| D2
  D2{"Contraindicação absoluta<br/>à trombólise?"}
  D2 -->|"Não"| C1
  D2 -->|"Sim"| C2
  C1(["Trombólise sistêmica:<br/>terapia de reperfusão de escolha<br/>no TEP de alto risco<br/>com instabilidade"])
  C2(["Embolectomia cirúrgica ou<br/>tratamento percutâneo por cateter;<br/>manter suporte hemodinâmico<br/>(árvores de manejo abaixo)"])

  D1 -->|"SDRA em ventilação mecânica<br/>(obstrução distal)"| C3
  C3(["Ventilação protetora — volume<br/>corrente 6 mL/kg, PEEP inicialmente<br/>menor que 10 cmH2O, platô menor<br/>que 27 cmH2O ou driving pressure<br/>menor que 17 cmH2O, evitar PaCO2<br/>maior que 60 mmHg; posição prona<br/>para descarregar o VD"])

  D1 -->|"Hipertensão pulmonar preexistente<br/>descompensada (agudo sobre crônico:<br/>infecção, arritmia, embolia)"| C4
  C4(["Tratar o gatilho da descompensação;<br/>NÃO iniciar vasodilatador pulmonar<br/>novo na fase aguda (sem sustentação<br/>fora do grupo 1); manter suporte<br/>hemodinâmico (árvores abaixo)"])

  D1 -->|"Isquemia miocárdica /<br/>infarto de ventrículo direito"| C5
  C5(["Reperfusão coronariana urgente<br/>(angioplastia primária, ou trombólise<br/>se PCI indisponível em tempo);<br/>evitar nitrato e diurético;<br/>manter suporte hemodinâmico<br/>(árvores abaixo)"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2,C3,C4,C5 conduta;
```

No TEP maciço, oxigenoterapia por cânula nasal de alto fluxo deve ser usada
inicialmente, e a intubação evitada quando possível: a ventilação mecânica
associou-se a risco de mortalidade **três vezes maior** nesse grupo, e muitos
sedativos usados na indução podem agravar a instabilidade hemodinâmica.

## Árvore de decisão: reposição volêmica no choque de VD

```mermaid
flowchart TD
  R0["Choque por falência de VD:<br/>decisão sobre reposição volêmica"]
  R0 --> D1
  D1{"Sinais de pressão de enchimento já<br/>elevada (congestão venosa, VD muito<br/>dilatado) ao ecocardiograma,<br/>PVC ou pressão de artéria pulmonar?"}

  D1 -->|"Não — hipotenso sem sinal<br/>de pressão de enchimento elevada"| C1
  C1(["Expansão volêmica cautelosa,<br/>guiada por ecocardiograma ou por<br/>PVC/pressão de artéria pulmonar —<br/>não é a resposta reflexa<br/>do choque hipovolêmico"])

  D1 -->|"Sim — já congesto"| C2
  C2(["Não expandir volume: risco de<br/>superdistender o VD, piorar a<br/>interdependência ventricular e<br/>reduzir o débito sistêmico;<br/>diurético para a congestão"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Árvore de decisão: vasopressor e inotrópico

```mermaid
flowchart TD
  R0["Choque por falência de VD:<br/>escolha de vasopressor/inotrópico"]
  R0 --> D1
  D1{"Problema hemodinâmico predominante?"}

  D1 -->|"Hipotensão"| C1
  C1(["Noradrenalina: vasopressor de<br/>primeira linha — melhora a<br/>hemodinâmica sistêmica e a perfusão<br/>coronariana, com efeito mínimo<br/>sobre a resistência vascular pulmonar.<br/>Se o débito permanecer inadequado,<br/>acrescentar inotrópico (dobutamina,<br/>inibidor da fosfodiesterase III ou<br/>levosimendana), limitado ao período<br/>de baixo débito e suspenso<br/>assim que possível"])

  D1 -->|"Débito cardíaco inadequado,<br/>sem hipotensão predominante"| C2
  C2(["Inotrópico — dobutamina, inibidor<br/>da fosfodiesterase III ou<br/>levosimendana — limitado ao período<br/>de baixo débito e suspenso<br/>assim que possível"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

## Árvore de decisão: suporte circulatório mecânico

```mermaid
flowchart TD
  R0["Choque por falência de VD refratário<br/>ao manejo clínico otimizado<br/>(volume, vasopressor, inotrópico)"]
  R0 --> D1
  D1{"Falência primária de VD (pressões de<br/>enchimento do VE normais) ou<br/>secundária (VE também com<br/>pressões de enchimento elevadas)?"}

  D1 -->|"Primária — o problema é o VD"| C1
  C1(["Suporte mecânico dedicado ao VD:<br/>Impella RP/RP-Flex ou VA-ECMO com<br/>estratégia de descarga do VE;<br/>balão intra-aórtico isolado<br/>geralmente não é recomendado<br/>para falência isolada de VD"])

  D1 -->|"Secundária — VE também<br/>com pressões elevadas"| C2
  C2(["Tratar o VE como alvo do<br/>suporte mecânico,<br/>não o VD isoladamente"])

  classDef conduta fill:#eef6ef,stroke:#2f7a4f,color:#12301f;
  class C1,C2 conduta;
```

Sinais de que o choque de VD está indo mal e merece essa reavaliação: mais de
48 horas de suporte inotrópico, escore vasoativo-inotrópico acima de 20,
pressões de enchimento persistentemente elevadas, congestão pulmonar e piora
do lactato apesar de volume e drogas vasoativas otimizados.

## O que vale em qualquer causa, e por isso não está na árvore

**Ventilação com pressão positiva piora o VD, sempre.** A pressão positiva
eleva a resistência vascular pulmonar e a pressão intratorácica, reduzindo o
retorno venoso e a pré-carga do VD — a PEEP alta "para melhorar a oxigenação"
tem esse custo em qualquer causa, não só na SDRA. Hipoxemia, hipercapnia e
acidose são vasoconstritoras pulmonares com efeito sinérgico e alimentam o
mesmo ciclo. Evitar ventilação mecânica desnecessária é, portanto, uma
diretriz geral.

**Inotrópico é para o período de baixo débito, não além dele.** O consenso é
explícito: pelos efeitos deletérios potenciais, o uso deve se limitar ao baixo
débito e ser interrompido o mais cedo possível — manter a infusão depois de
resolvido o problema é a armadilha mais comum de escalonamento.

**Vasodilatador pulmonar específico fora do grupo 1 da OMS não tem uso
rotineiro sustentado pela evidência atual**, em nenhuma das causas — inclusive
na hipertensão pulmonar descompensada.

**Reavaliação contínua.** O estágio do choque não é um rótulo fixo da
admissão; quem deteriora volta a percorrer as árvores acima, e quem melhora
tem o suporte desescalonado conforme tolerado.

## Documentos relacionados

`classificacao-scai-de-estagios-do-choque-cardiogenico.md`,
`cateter-de-arteria-pulmonar-no-choque-cardiogenico-escape-e-o-limite-do-dado-observacional.md`,
`choque-cardiogenico-suporte-circulatorio-mecanico-temporario.md`,
`vasopressores-adjuvantes-no-choque-vasodilatador-vasst-vanish-e-athos-3.md` e
`ecmo-venoarterial-no-choque-cardiogenico-do-infarto-ecls-shock-ecmo-cs-e-a-metanalise-de-dados-individuais.md`,
todos nesta mesma pasta. O TEP de alto risco tem fluxograma dedicado em
`fluxograma-tromboembolismo-pulmonar-diagnostico-esc-2019.md`, em
Tromboembolismo.
