---
title: "GSCRI: risco cardíaco perioperatório no paciente idoso"
slug: gscri-risco-cardiaco-geriatrico-pre-operatorio
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "Geriatric-Sensitive Cardiac Risk Index para pacientes com 65 anos ou mais, com árvore de decisão e comparação com RCRI e Gupta MICA."
source_refs:
  - "Alrezk R, Jackson N, Al Rezk M, et al. Derivation and Validation of a Geriatric-Sensitive Perioperative Cardiac Risk Index. J Am Heart Assoc. 2017;6(11):e006648. PMID: 29146612. DOI: 10.1161/JAHA.117.006648."
---

# GSCRI — Geriatric-Sensitive Cardiac Risk Index

O GSCRI foi desenvolvido especificamente para pacientes com **idade ≥65 anos** submetidos a cirurgia não cardíaca, com o objetivo de estimar risco de **infarto do miocárdio ou parada cardíaca perioperatória**.

A derivação usou 210.914 pacientes geriátricos do ACS-NSQIP 2013 e a validação 172.905 pacientes geriátricos do ACS-NSQIP 2012.

## Variáveis do modelo final

O modelo final utiliza sete grupos de informação:

- história de AVC;
- classe ASA;
- categoria cirúrgica;
- status funcional;
- creatinina >1,5 mg/dL;
- diabetes;
- história de insuficiência cardíaca.

## Árvore de decisão metodológica

```mermaid
flowchart TD
    A["Paciente ≥65 anos candidato a cirurgia não cardíaca"] --> B["Registrar AVC prévio"]
    B --> C["Definir classe ASA"]
    C --> D["Definir categoria cirúrgica"]
    D --> E["Avaliar independência funcional"]
    E --> F["Creatinina >1,5 mg/dL?"]
    F --> G["Classificar diabetes conforme modelo"]
    G --> H["Registrar história de insuficiência cardíaca"]
    H --> I["Aplicar equação GSCRI validada"]
    I --> J["Resultado: probabilidade de IAM/parada cardíaca perioperatória"]
    J --> K{"Risco elevado ou condição cardiovascular ativa/modificador?"}
    K -->|"Não"| L["Integrar capacidade funcional e risco do procedimento"]
    K -->|"Sim"| M["Avaliação perioperatória intensificada e decisão multidisciplinar"]
    L --> N{"DASI >34?"}
    N -->|"Sim"| O["Em geral prosseguir sem teste cardíaco indiscriminado"]
    N -->|"Não / desconhecido"| P{"Teste adicional mudará manejo?"}
    P -->|"Não"| Q["Prosseguir conforme contexto"]
    P -->|"Sim"| R["Biomarcadores ± investigação adicional conforme diretriz"]
```

## Desempenho na validação geriátrica

Na coorte de validação, a área sob a curva foi:

- **GSCRI: 0,76**;
- **Gupta MICA: 0,70**;
- **RCRI: 0,63**.

O estudo também relatou deterioração do desempenho do Gupta MICA e subestimação do risco quando aplicado ao subconjunto geriátrico.

## Por que não há calculadora local ativa ainda

A publicação confirma as sete variáveis e o desempenho do modelo, porém a transcrição integral dos coeficientes por categoria cirúrgica **não foi validada nesta sessão contra a tabela original completa**. Portanto, conforme a regra de governança da Corvia, a implementação matemática permanece:

**VERIFICAÇÃO HUMANA NECESSÁRIA**

Até essa validação, o GSCRI deve aparecer como metodologia científica/árvore de decisão, não como calculadora que produz um percentual potencialmente incorreto.

## Regra prática

Em pacientes ≥65 anos, o GSCRI é especialmente útil para lembrar que **dependência funcional, categoria cirúrgica e vulnerabilidade geriátrica** acrescentam informação que pode não ser capturada adequadamente pelo RCRI tradicional.
