---
title: "GSCRI: risco cardíaco perioperatório no paciente idoso"
slug: gscri-risco-cardiaco-geriatrico-pre-operatorio
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
revisado_por_voce: false
summary: "GSCRI para pacientes ≥65 anos, com fórmula original, coeficientes, cálculo percentual e árvores de decisão."
source_refs:
  - "Alrezk R, Jackson N, Al Rezk M, et al. J Am Heart Assoc. 2017;6(11):e006648. PMID: 29146612. PMCID: PMC5721761. DOI: 10.1161/JAHA.117.006648."
---

# GSCRI — Geriatric-Sensitive Cardiac Risk Index

Desenvolvido para pacientes **≥65 anos** submetidos a cirurgia não cardíaca, estimando **IAM ou parada cardíaca perioperatória**. Derivação: 210.914 pacientes geriátricos do ACS-NSQIP 2013; validação: 172.905 do ACS-NSQIP 2012.

## Fórmula

`p = exp(x) / [1 + exp(x)]`, com constante **−6,79**.

Coeficientes clínicos da Tabela 3: AVC +2,08; ASA II +0,28, III +1,34, IV +2,04, V +3,63; parcialmente dependente +0,23; totalmente dependente +0,72; creatinina >1,5 mg/dL +0,57; IC +0,60; diabetes sem insulina +0,09; com insulina +0,47.

Coeficientes cirúrgicos, com hérnia como referência: anorretal +1,02; aórtica +1,32; bariátrica +0,31; encefálica +0,24; mama −1,14; ORL +0,32; GI alto/HPB +1,03; vesícula/apêndice/adrenal/baço ou intestinal +1,13; pescoço −0,04; obstétrica/ginecológica +0,12; ortopédica +0,47; abdominal outra +0,16; vascular periférica +0,82; pele +0,41; coluna +0,42; torácica +1,06; venosa +1,35; urológica +0,55.

## Árvore de cálculo

```mermaid
flowchart TD
 A["Paciente candidato a cirurgia não cardíaca"] --> B{"Idade ≥65 anos?"}
 B -->|"Não"| C["Não usar GSCRI"]
 B -->|"Sim"| D["AVC prévio + ASA + categoria cirúrgica"]
 D --> E["Status funcional + creatinina >1,5 + IC + diabetes"]
 E --> F["Somar constante −6,79 + coeficientes"]
 F --> G["Aplicar função logística"]
 G --> H["Risco percentual de IAM/PCR perioperatória"]
```

## Árvore de uso clínico

```mermaid
flowchart TD
 A["GSCRI calculado"] --> B{"Condição cardiovascular ativa/instável?"}
 B -->|"Sim"| C["Tratar condição ativa quando possível"]
 B -->|"Não"| D["Integrar risco + procedimento + fragilidade"]
 D --> E["DASI/METs"]
 E --> F{"Capacidade adequada e sintomas estáveis?"}
 F -->|"Sim"| G["Em geral, prosseguir sem teste isquêmico rotineiro"]
 F -->|"Não/desconhecido"| H["Biomarcadores conforme indicação"]
 H --> I{"Exame adicional mudará manejo?"}
 I -->|"Não"| J["Otimizar e planejar monitorização"]
 I -->|"Sim"| K["Investigar conforme diretriz"]
```

## Desempenho na validação geriátrica

- GSCRI: **AUC 0,76**;
- Gupta MICA: **0,70**;
- RCRI: **0,63**.

## Limitações

Validado apenas para idade ≥65; endpoint é IAM/PCR, não mortalidade global. ASA e categoria cirúrgica devem ser classificadas corretamente. Fragilidade, capacidade funcional e doença cardiovascular ativa continuam necessárias. O resultado não é indicação automática de teste de estresse, CCTA, coronariografia ou adiamento cirúrgico.

## Regra prática

A calculadora interativa da Corvia usa os coeficientes da **Tabela 3 do artigo original**, não uma reprodução secundária.