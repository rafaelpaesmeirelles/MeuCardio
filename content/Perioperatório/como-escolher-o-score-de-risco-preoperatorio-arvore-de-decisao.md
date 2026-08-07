---
title: "Como escolher o score de risco pré-operatório"
slug: como-escolher-o-score-de-risco-preoperatorio-arvore-de-decisao
theme: "Perioperatório"
kind: documento
fonte_producao: chatgpt
review_status: pendente_revisao
summary: "Árvore para selecionar RCRI, Gupta MICA, GSCRI, VSG-CRI, AUB-HAS2, DASI, SORT, S-MPM ou ACS-NSQIP de acordo com a pergunta clínica e a população."
source_refs:
  - "Thompson A, Fleischmann KE, Smilowitz NR, et al. 2024 AHA/ACC perioperative guideline. DOI: 10.1161/CIR.0000000000001285."
  - "Halvorsen S, Mehilli J, Cassese S, et al. 2022 ESC noncardiac surgery guideline. PMID: 36017553. DOI: 10.1093/eurheartj/ehac270."
  - "Gualandro DM, Fornari LS, Caramelli B, et al. Diretriz SBC 2024. PMID: 39442131. DOI: 10.36660/abc.20240590."
---

# Qual metodologia usar?

Não existe um “melhor score” universal. Antes de calcular, definir **qual pergunta se deseja responder**.

## Árvore principal

```mermaid
flowchart TD
  A["Qual é a pergunta clínica?"] --> B{"Capacidade funcional?"}
  B -->|"Sim"| C["DASI"]
  B -->|"Não"| D{"Risco cardiovascular específico?"}
  D -->|"Sim"| E{"População/cirurgia especial?"}
  E -->|"Idade ≥65"| F["GSCRI — MICA geriátrico"]
  E -->|"Cirurgia vascular arterial"| G["VSG-CRI"]
  E -->|"Sem população especial"| H["Gupta MICA ou RCRI; AUB-HAS2 como complemento"]
  D -->|"Não"| I{"Mortalidade cirúrgica global?"}
  I -->|"Sim, modelo percentual"| J["SORT"]
  I -->|"Sim, score simples"| K["S-MPM"]
  I -->|"Quero múltiplas complicações e CPT específico"| L["ACS-NSQIP oficial"]
```

## Segunda árvore: qual score cardiovascular?

```mermaid
flowchart TD
  A["Preciso estimar risco cardíaco perioperatório"] --> B{"Paciente ≥65 anos?"}
  B -->|"Sim"| C["GSCRI é opção específica; comparar com método geral se útil"]
  B -->|"Não"| D{"Cirurgia vascular arterial?"}
  D -->|"Sim"| E["VSG-CRI específico para cirurgia vascular"]
  D -->|"Não"| F{"Deseja percentual contínuo de IAM/PCR?"}
  F -->|"Sim"| G["Gupta MICA"]
  F -->|"Não / triagem simples"| H["RCRI"]
  G --> I{"Deseja incorporar anemia, sintomas e emergência em score simples?"}
  H --> I
  I -->|"Sim"| J["AUB-HAS2 como ferramenta complementar"]
  I -->|"Não"| K["Integrar resultado a DASI + modificadores + diretriz"]
  J --> K
```

## O que cada ferramenta responde

| Ferramenta | Pergunta | Saída principal |
|---|---|---|
| RCRI | risco cardíaco clássico | 0–6 pontos / classes |
| Gupta MICA | IAM ou PCR | percentual individual |
| GSCRI | IAM/PCR no paciente ≥65 anos | percentual individual |
| VSG-CRI | complicações cardíacas em cirurgia vascular arterial | pontos/categoria |
| AUB-HAS2 | morte/IAM/AVC | 0–6 pontos/categoria |
| DASI | capacidade funcional | 0–58,2 pontos |
| SORT | mortalidade global em 30 dias | percentual individual |
| S-MPM | mortalidade global em 30 dias | 0–9 pontos/classes |
| ACS-NSQIP | múltiplas complicações por procedimento | vários riscos percentuais |

## Regras de segurança

1. **Não somar scores diferentes.**
2. **Não fazer média dos percentuais.**
3. Sempre identificar endpoint e horizonte temporal.
4. O score não prevalece sobre SCA, IC descompensada ou arritmia instável.
5. Teste adicional só deve ser solicitado quando puder mudar manejo.
6. DASI/fragilidade podem modificar a interpretação mesmo quando o risco numérico parece baixo.

## Sugestão para a interface Corvia

A tela pode apresentar dois eixos separados:

- **Risco cardiovascular:** RCRI, MICA, GSCRI/VSG-CRI/AUB-HAS2 conforme indicação.
- **Risco cirúrgico global:** SORT/S-MPM/ACS-NSQIP.

O DASI deve ficar entre os dois como **modificador funcional**, não como “mais um risco percentual”.
