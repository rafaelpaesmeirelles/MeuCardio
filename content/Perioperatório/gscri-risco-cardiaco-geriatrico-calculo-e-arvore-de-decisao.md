---
title: "GSCRI: risco cardíaco perioperatório no paciente geriátrico"
slug: gscri-risco-cardiaco-geriatrico-calculo-e-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Modelo específico para pacientes ≥65 anos que estima IAM ou parada cardíaca perioperatória e supera RCRI/Gupta MICA no subconjunto geriátrico da validação original."
source_refs:
  - "Alrezk R, Jackson N, Al Rezk M, et al. J Am Heart Assoc. 2017;6(11):e006648. PMID: 29146612. PMCID: PMC5721761. DOI: 10.1161/JAHA.117.006648."
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
---

# GSCRI — Geriatric-Sensitive Perioperative Cardiac Risk Index

## Para quem foi desenvolvido

O GSCRI foi derivado especificamente para pacientes **com idade ≥65 anos** submetidos a cirurgia não cardíaca. O endpoint é **infarto do miocárdio ou parada cardíaca perioperatória (MICA)**.

A derivação utilizou o NSQIP 2013; a validação foi realizada no NSQIP 2012. Na população geriátrica de validação, o GSCRI apresentou **AUC 0,76**, contra **0,70** para Gupta MICA e **0,63** para RCRI.

## Variáveis do modelo

- história de AVC;
- classe ASA;
- categoria da cirurgia;
- status funcional;
- creatinina >1,5 mg/dL;
- história de insuficiência cardíaca;
- diabetes mellitus, distinguindo uso de insulina.

O modelo é uma regressão logística. A constante publicada é **−6,79** e os coeficientes individuais constam na Tabela 3 do artigo original.

## Árvore de elegibilidade

```mermaid
flowchart TD
  A["Paciente em avaliação pré-operatória"] --> B{"Idade ≥65 anos?"}
  B -->|"Não"| C["Não usar GSCRI; escolher ferramenta validada para população geral"]
  B -->|"Sim"| D["Confirmar cirurgia não cardíaca"]
  D --> E["Preencher AVC, ASA, tipo de cirurgia, status funcional, creatinina, IC e diabetes"]
  E --> F["Aplicar regressão logística GSCRI"]
  F --> G["Resultado: risco percentual de IAM ou parada cardíaca"]
```

## Árvore de interpretação

```mermaid
flowchart TD
  A["GSCRI calculado"] --> B{"Há condição cardiovascular ativa/instável?"}
  B -->|"Sim"| C["A condição ativa prevalece sobre o escore: avaliar/tratar antes da cirurgia quando possível"]
  B -->|"Não"| D["Integrar risco absoluto do GSCRI ao risco do procedimento"]
  D --> E["Avaliar capacidade funcional por DASI/METs"]
  E --> F{"DASI >34 / capacidade adequada e sintomas estáveis?"}
  F -->|"Sim"| G["Em geral, prosseguir sem teste isquêmico de rotina"]
  F -->|"Não / desconhecido"| H["Considerar biomarcadores em cirurgia de risco elevado"]
  H --> I{"Teste adicional mudará manejo?"}
  I -->|"Não"| J["Não testar por rotina; otimizar e planejar monitorização"]
  I -->|"Sim"| K["Considerar teste de estresse/CCTA conforme diretriz e contexto"]
```

## Coeficientes — transparência do cálculo

A calculadora interativa da Corvia utiliza exatamente os coeficientes da Tabela 3 da publicação:

- AVC: +2,08;
- ASA II +0,28; III +1,34; IV +2,04; V +3,63;
- status funcional parcialmente dependente +0,23; totalmente dependente +0,72;
- creatinina >1,5 mg/dL +0,57;
- IC +0,60;
- diabetes sem insulina +0,09; com insulina +0,47;
- os coeficientes da categoria cirúrgica variam de −1,14 (mama) a +1,35 (cirurgia venosa), tendo hérnia como referência.

Probabilidade = `exp(x) / [1 + exp(x)]`, com `x = −6,79 + soma dos coeficientes`.

## Por que não substituir todos os outros scores pelo GSCRI

O GSCRI é uma ferramenta **específica de geriatria**, com endpoint MICA. Ele não substitui:

- avaliação de fragilidade;
- DASI/capacidade funcional;
- biomarcadores quando indicados;
- avaliação de doença cardiovascular ativa;
- scores voltados a mortalidade geral ou complicações cirúrgicas não cardíacas.

## Mensagem prática

No paciente ≥65 anos, sobretudo frágil ou funcionalmente dependente, o GSCRI adiciona uma estimativa de risco mais alinhada à população geriátrica do que simplesmente aplicar o RCRI e assumir que sua calibração é idêntica em idosos.
